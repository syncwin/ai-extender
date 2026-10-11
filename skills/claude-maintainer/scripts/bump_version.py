#!/usr/bin/env python3
"""Write the changelog entry and move every version field together, from one summary.

Usage: bump_version.py <dir> (--summary "<text>" | --summary-file <file>) [--level auto|patch|minor|major|keep]
                       [--title "<entry title>"] [--dry-run]
Summary: lines grouped by "Added:", "Changed:", "Fixed:", "Removed:" (or **Added** / ### Added headings, then bullets).
  Ungrouped lines go under Changed. A line starting "Breaking:" goes under Changed and makes --level auto a major bump.
--level auto (default): major if breaking or anything Removed, minor if anything Added, else patch.
--level keep: no version change; the lines join the current top changelog entry (same release, more fixes).
Updates: plugin.json version and metadata.version, marketplace entries for this plugin that carry a version,
every SKILL.md and agent metadata.version, the README "**Version** x" line, and CHANGELOG.md.
"""
import json, re, sys
from pathlib import Path

GROUPS = ("Added", "Changed", "Fixed", "Removed")

def parse_summary(text):
    groups, cur, breaking = {g: [] for g in GROUPS}, None, False
    for raw in text.splitlines():
        line = raw.strip()
        if not line: continue
        h = re.match(r"^(?:#+\s*|\*\*)?(Added|Changed|Fixed|Removed|Breaking)(?:\*\*)?\s*:?\s*(.*)$", line, re.I)
        if h:
            g = h.group(1).title(); rest = h.group(2).strip().lstrip("-* ").strip()
            if g == "Breaking": breaking, g = True, "Changed"
            cur = g
            if rest: groups[g].append(rest)
            continue
        groups[cur or "Changed"].append(re.sub(r"^[-*]\s+", "", line))
    return groups, breaking

def next_version(v, level):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", v)
    if not m: raise SystemExit(f"version '{v}' is not semver")
    a, b, c = map(int, m.groups())
    return {"major": f"{a+1}.0.0", "minor": f"{a}.{b+1}.0", "patch": f"{a}.{b}.{c+1}", "keep": v}[level]

def set_md_version(p, old, new, changes):
    t = p.read_text(encoding="utf-8")
    t2 = re.sub(rf"^(\s+version:\s*)([\"']?){re.escape(old)}\2\s*$", lambda m: f"{m.group(1)}{m.group(2)}{new}{m.group(2)}", t, count=1, flags=re.M)
    if t2 != t: changes[p] = t2

def changelog(text, groups, new, title, keep):
    block = lambda g, items: f"**{g}**\n" + "".join(f"- {x}\n" for x in items)
    if not text: text = "# Changelog\n\nNewest first.\n"
    if keep:
        m = re.search(r"^## .*$", text, re.M)
        if not m: raise SystemExit("--level keep needs an existing changelog entry")
        nxt = re.search(r"^## ", text[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(text)
        entry = text[m.end():end]
        for g in GROUPS:
            if not groups[g]: continue
            lines = "".join(f"- {x}\n" for x in groups[g])
            gm = re.search(rf"^\*\*{g}\*\*\n((?:- .*\n|  .*\n)*)", entry, re.M)
            if gm: entry = entry[:gm.end()] + lines + entry[gm.end():]
            else: entry = entry.rstrip("\n") + "\n\n" + block(g, groups[g])
        return text[:m.end()] + entry.rstrip("\n") + "\n\n" + text[end:].lstrip("\n") if nxt else text[:m.end()] + entry.rstrip("\n") + "\n"
    body = f"## {new}: {title}\n\n" + "\n".join(block(g, groups[g]) for g in GROUPS if groups[g]) + "\n"
    m = re.search(r"^## ", text, re.M)
    return text[:m.start()] + body + text[m.start():] if m else text.rstrip("\n") + "\n\n" + body

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root, opts, i = Path(argv[0]).resolve(), {"level": "auto", "title": "Update", "summary": None, "dry": False}, 1
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run": opts["dry"] = True
        elif a in ("--summary", "--summary-file", "--level", "--title") and i + 1 < len(argv):
            opts["summary" if a.startswith("--summary") else a[2:]] = Path(argv[i+1]).read_text(encoding="utf-8") if a == "--summary-file" else argv[i+1]; i += 1
        else: print(__doc__); return 2
        i += 1
    if not opts["summary"] or opts["level"] not in ("auto", "patch", "minor", "major", "keep"): print(__doc__); return 2
    groups, breaking = parse_summary(opts["summary"])
    if not any(groups.values()): print("summary has no lines"); return 2
    level = opts["level"]
    if level == "auto": level = "major" if breaking or groups["Removed"] else "minor" if groups["Added"] else "patch"
    pj = root / ".claude-plugin" / "plugin.json"
    changes = {}
    if pj.exists():
        m = json.loads(pj.read_text(encoding="utf-8")); old = str(m.get("version", "0.0.1")); new = next_version(old, level)
        if new != old:
            m["version"] = new
            if isinstance(m.get("metadata"), dict) and "version" in m["metadata"]: m["metadata"]["version"] = new
            changes[pj] = json.dumps(m, indent=2, ensure_ascii=False) + "\n"
            mk = root / ".claude-plugin" / "marketplace.json"
            if mk.exists():
                d = json.loads(mk.read_text(encoding="utf-8"))
                hit = [e for e in d.get("plugins", []) if e.get("name") == m.get("name") and "version" in e]
                for e in hit: e["version"] = new
                if hit: changes[mk] = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
        mds = sorted((root / "skills").glob("*/SKILL.md")) + sorted((root / "agents").glob("*.md"))
    else:
        sm = root / "SKILL.md"
        if not sm.exists(): print("not a plugin or skill directory"); return 2
        vm = re.search(r"^\s+version:\s*[\"']?([^\s\"']+)", sm.read_text(encoding="utf-8"), re.M)
        old = vm.group(1) if vm else "0.0.1"; new = next_version(old, level); mds = [sm]
    if new != old:
        for p in mds: set_md_version(p, old, new, changes)
        rd = root / "README.md"
        if rd.exists():
            t = rd.read_text(encoding="utf-8"); t2 = t.replace(f"**Version** {old}", f"**Version** {new}")
            if t2 != t: changes[rd] = t2
    cl = root / "CHANGELOG.md"
    changes[cl] = changelog(cl.read_text(encoding="utf-8") if cl.exists() else "", groups, new, opts["title"], level == "keep")
    if not opts["dry"]:
        for p, t in changes.items(): p.write_text(t, encoding="utf-8")
    print(f"### Scratchpad: Version and Changelog\n**Scope:** `{root.name}` {old} → {new} ({level}){' (dry run)' if opts['dry'] else ''}\n\n| File | Result |\n|---|---|")
    for p in changes: print(f"| `{p.relative_to(root).as_posix()}` | {'would update' if opts['dry'] else 'updated'} |")
    print(f"| Changelog lines | {sum(len(v) for v in groups.values())} |")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
