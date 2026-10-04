#!/usr/bin/env python3
"""Offline simulator for an extension. No network, no model calls.

Usage: simulate.py <extension-dir> triggers [--evals evals/evals.json] [--min-hit 0.8]
       simulate.py <extension-dir> install  [--out DIR]

triggers: lexical PROXY for skill selection. Scores each should/should-not prompt against every skill
          description (TF-IDF cosine) and reports hit/false-positive rates, misrouted prompts, and
          skill pairs whose descriptions overlap too much. It cannot predict Claude's real choices:
          use it to catch weak or colliding descriptions, then confirm with real runs.
install:  packages the extension, extracts it into a clean temp directory (as an installer would), runs the
          validator on the extracted copy, and prints the component inventory with the names a user would see.
Exit: 0 pass, 1 findings, 2 usage.
"""
import json, math, re, subprocess, sys, tempfile, zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOP = set("a an and are as at be by for from has have how i in into is it its me my of on or our that the this to use used using when whenever with you your do does did can could should would will".split())

def toks(s):
    out = []
    for w in re.findall(r"[a-z0-9]+", s.lower()):
        if w in STOP or len(w) < 2: continue
        w = re.sub(r"(ing|ed|es|s)$", "", w) if len(w) > 4 else w
        out.append(w)
    return out

def fm_desc(p):
    t = p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---", t, re.S)
    if not m: return None, ""
    fm, name, desc, cur = m.group(1), None, [], None
    for line in fm.split("\n"):
        if line.startswith("name:"): name = line.split(":", 1)[1].strip().strip("\"'")
        elif line.startswith("description:"):
            v = line.split(":", 1)[1].strip(); cur = True
            if v not in (">", "|", ">-", "|-"): desc.append(v)
        elif cur and (line.startswith("  ") or not line.strip()): desc.append(line.strip())
        elif line and not line.startswith(" "): cur = False
    return name, " ".join(desc)

def load_skills(root):
    return {n: d for n, d in (fm_desc(p) for p in sorted((root / "skills").glob("*/SKILL.md"))) if n}

def vec(tokens, idf):
    c = Counter(tokens); return {w: (1 + math.log(n)) * idf.get(w, 1.0) for w, n in c.items()}

def cos(a, b):
    num = sum(v * b.get(k, 0) for k, v in a.items())
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0

def triggers(root, evals, min_hit):
    skills = load_skills(root)
    if not skills: print("no skills found"); return 1
    docs = {n: toks(d + " " + n.replace("-", " ")) for n, d in skills.items()}
    N = len(docs); df = Counter(w for t in docs.values() for w in set(t))
    idf = {w: math.log((N + 1) / (c + 0.5)) + 1 for w, c in df.items()}
    dv = {n: vec(t, idf) for n, t in docs.items()}
    ev = json.loads(Path(evals).read_text()); tr = ev.get("trigger", {})
    def best(prompt):
        pv = vec(toks(prompt), idf)
        return max(((cos(pv, v), n) for n, v in dv.items()), default=(0.0, None))
    pos = [(p, best(p)) for p in tr.get("should", [])]
    negs = [(p, best(p)) for p in tr.get("should_not", [])]
    # calibrate: threshold that maximizes hit-rate minus false-positive-rate on the supplied sets
    cands = sorted({s for _, (s, _) in pos + negs} | {0.0})
    def rates(th):
        return (sum(1 for _, (s, _) in pos if s > th) / max(len(pos), 1), sum(1 for _, (s, _) in negs if s > th) / max(len(negs), 1))
    th = max(((rates(c)[0] - rates(c)[1], c) for c in cands), key=lambda x: (x[0], x[1]))[1]
    hits = [(p, (s, n if s > th else None)) for p, (s, n) in pos]
    neg = [(p, (s, n if s > th else None)) for p, (s, n) in negs]
    rate, fprate = rates(th)
    sep = min((s for _, (s, _) in pos), default=0) - max((s for _, (s, _) in negs), default=0)
    print(f"### Scratchpad — Trigger Simulation (lexical proxy)\n**Scope:** {len(skills)} skills, {len(hits)} should / {len(neg)} should-not prompts\n")
    print(f"| Metric | Value |\n|---|---|\n| Calibrated threshold | {th:.2f} |\n| Should-trigger hit rate | {rate:.0%} |\n| Should-not false-positive rate | {fprate:.0%} |\n| Score separation (min positive − max negative) | {sep:+.2f} |")
    flags = []
    for p, (s, n) in hits:
        if not n: flags.append(f"MISS (no skill matched, score {s:.2f}): {p}")
    for p, (s, n) in neg:
        if n: flags.append(f"FALSE POSITIVE → {n} ({s:.2f}): {p}")
    names = list(dv)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            c = cos(dv[names[i]], dv[names[j]])
            if c > 0.6: flags.append(f"OVERLAP {c:.2f}: {names[i]} ~ {names[j]} (descriptions too similar)")
    if flags:
        print("\n**Flags**"); [print(f"- {f}") for f in flags]
    bad = rate < min_hit or fprate > 0.25 or any(f.startswith("OVERLAP") for f in flags)
    print("\n**Next:** confirm with real runs (`claude plugin eval` or fresh sessions); this is a proxy.")
    return 1 if bad else 0

def install(root, out):
    pk = HERE.parents[1] / "claude-packager" / "scripts" / "package_extension.py"
    v = HERE / "validate_extension.py"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td); dest = Path(out) if out else td / "dist"
        r = subprocess.run([sys.executable, str(pk), str(root), "--format", "plugin", "--out", str(dest)], capture_output=True, text=True)
        if r.returncode != 0: print(r.stdout + r.stderr); return 1
        f = next(dest.glob("*.plugin"))
        inst = td / "installed"; zipfile.ZipFile(f).extractall(inst)
        vr = subprocess.run([sys.executable, str(v), str(inst), "--strict"], capture_output=True, text=True)
        man = json.loads((inst / ".claude-plugin" / "plugin.json").read_text())
        name = man["name"]; skills = load_skills(inst)
        agents = sorted(p.stem for p in (inst / "agents").glob("*.md")) if (inst / "agents").exists() else []
        mcp = []
        if (inst / ".mcp.json").exists(): mcp = list(json.loads((inst / ".mcp.json").read_text()).get("mcpServers", {}))
        hooks = list(json.loads((inst / "hooks/hooks.json").read_text()).get("hooks", {})) if (inst / "hooks/hooks.json").exists() else []
        print(f"### Scratchpad — Install Simulation\n**Scope:** `{f.name}` extracted to a clean directory\n")
        print(f"| Check | Result |\n|---|---|\n| Archive root is plugin root | {'yes' if (inst/'.claude-plugin'/'plugin.json').exists() else 'NO'} |\n| Validator on extracted copy (--strict) | {'pass' if vr.returncode == 0 else 'FAIL'} |\n| Router skill = plugin name | {'yes' if name in skills else 'NO'} |")
        print("\n**Components a user would see**")
        for n in skills: print(f"- skill `/{name}:{n}`" if n != name else f"- skill `/{name}:{n}` (router)")
        for a in agents: print(f"- agent `{name}:{a}`")
        for m in mcp: print(f"- connector `plugin:{name}:{m}` (tools `mcp__plugin_{re.sub('[^A-Za-z0-9_-]','_',name)}_{re.sub('[^A-Za-z0-9_-]','_',m)}__*`)")
        for h in hooks: print(f"- hook event `{h}`")
        if vr.returncode != 0: print("\n**Flags**\n" + vr.stdout[-800:])
        return 0 if vr.returncode == 0 and name in skills else 1

def main(argv):
    if len(argv) < 2 or argv[1] not in ("triggers", "install"): print(__doc__); return 2
    root = Path(argv[0]).resolve()
    if not (root / "skills").is_dir(): print(f"no skills/ in {root}"); return 2
    opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
    if argv[1] == "triggers":
        ev = Path(opt("--evals", root / "evals" / "evals.json"))
        if not ev.exists(): print(f"missing {ev}"); return 2
        return triggers(root, ev, float(opt("--min-hit", 0.8)))
    return install(root, opt("--out", None))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
