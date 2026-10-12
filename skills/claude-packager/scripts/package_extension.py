#!/usr/bin/env python3
"""Package a Claude extension: validate, name, zip.

Usage: package_extension.py <dir> --format plugin|zip [--out DIR] [--skip-validate] [--target T]
                            [--previous FILE|DIR] [--repo owner/repo] [--force] [--require-evals]
  plugin: zip with the plugin root as archive root, extension .plugin (Cowork)
  zip:    zip with one top-level folder named after the skill or plugin `name` (skill upload, manual install),
          whatever the source folder is called
Filename: "<Visible Name> v<version>.<ext>" (displayName / skill title + metadata.version).
Always creates or checks the Prompt Builder companion prompt (prompts/<title-slug>.json, via companion_prompt.py)
and copies it next to the package. A read-only source is staged in a temp copy first, so it is never written to.
Builds in a temp dir, then copies to --out (default ./dist).
Also writes "<Visible Name> v<version> install.md" next to the package (desktop app, web, Code tab, terminal, undo).
Reuse: an existing package whose recorded content hash matches is kept as it is (no re-check, no rebuild) unless --force.
Release diff: against --previous, or the newest other version of the same package in --out (release_diff.py).
Behavior tests: reports whether evals/ results exist and are newer than the last skill change; --require-evals blocks if not.
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

EXCLUDE_DIRS = {".git", ".github", "__pycache__", "node_modules", ".venv", "dist"}
EXCLUDE_SUFFIX = {".plugin", ".zip", ".pyc"}
EXCLUDE_NAMES = {".DS_Store"}

def info(root):
    pj = root / ".claude-plugin" / "plugin.json"
    if pj.exists():
        try: m = json.loads(pj.read_text(encoding="utf-8-sig"))
        except ValueError as e: raise SystemExit(f"plugin.json is not valid JSON: {e}")
        if not isinstance(m, dict) or not m.get("name"): raise SystemExit("plugin.json needs a name")
        return "plugin", m.get("displayName") or m["name"], str(m.get("version", "0.0.1")), m["name"]
    sm = root / "SKILL.md"
    if sm.exists():
        t = sm.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        nm = re.search(r"^name:\s*(.+)$", t, re.M)
        if not nm: raise SystemExit("SKILL.md has no name")
        name = nm.group(1).strip().strip("\"'")
        ver = re.search(r"^\s+version:\s*(\S+)", t, re.M)
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        return "skill", (h1.group(1).strip() if h1 else name.replace("-", " ").title()), (ver.group(1).strip("\"'") if ver else "0.0.1"), name
    raise SystemExit(f"not a plugin or skill directory: {root}")

def files(root):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_symlink() or p.is_dir() or any(x in EXCLUDE_DIRS for x in rel.parts): continue
        if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIX: continue
        yield p, rel

def content_hash(root, fmt):
    h = hashlib.sha256(fmt.encode())
    for p, rel in files(root): h.update(rel.as_posix().encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()

def eval_status(root):
    """(ok, note): evals present, run, passing, and newer than the newest skill/agent/hook change."""
    ev = root / "evals"
    if not ev.is_dir(): return False, "no evals/: behavior untested"
    res = sorted((ev / "results").glob("*/aggregate-result.json"), key=lambda p: p.stat().st_mtime) if (ev / "results").is_dir() else []
    if not res: return False, "evals/ never run here (`claude plugin eval .`, or the manual loop in testing.md)"
    newest = max((p.stat().st_mtime for d in ("skills", "agents", "hooks") if (root / d).is_dir() for p in (root / d).rglob("*") if p.is_file()), default=0)
    last = res[-1]
    try: score = json.loads(last.read_text()).get("aggregates", {}).get("overallScore")
    except (OSError, ValueError): score = None
    if last.stat().st_mtime < newest: return False, f"last eval run ({last.parent.name}) is older than the last skill change"
    return True, f"last run {last.parent.name}, score {score}"

def previous_package(out, visible, version, ext):
    pat = re.compile(re.escape(visible) + r" v(\d+\.\d+\.\d+[^ ]*)" + re.escape(ext) + "$")
    found = [(p.stat().st_mtime, p) for p in out.glob("*" + ext) if (m := pat.match(p.name)) and m.group(1) != version] if out.is_dir() else []
    return max(found)[1] if found else None

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root, fmt, out, skip, target, prev, repo, force, need_evals = Path(argv[0]).resolve(), None, Path("dist"), False, "all", None, "", False, False
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("--format", "--out", "--target", "--previous", "--repo") and i + 1 >= len(argv): print(__doc__); return 2
        if a == "--format": fmt = argv[i+1]; i += 1
        elif a == "--out": out = Path(argv[i+1]); i += 1
        elif a == "--target": target = argv[i+1]; i += 1
        elif a == "--previous": prev = Path(argv[i+1]); i += 1
        elif a == "--repo": repo = argv[i+1]; i += 1
        elif a == "--skip-validate": skip = True
        elif a == "--force": force = True
        elif a == "--require-evals": need_evals = True
        else: print(__doc__); return 2
        i += 1
    if fmt not in ("plugin", "zip"): print(__doc__); return 2
    kind, visible, version, slug = info(root)
    if fmt == "plugin" and kind != "plugin": print(".plugin format requires a plugin directory"); return 2
    staged = None
    if not os.access(root, os.W_OK) or ((root / "prompts").exists() and not os.access(root / "prompts", os.W_OK)):
        staged = tempfile.TemporaryDirectory()
        src, root = root, Path(staged.name) / slug
        shutil.copytree(src, root, ignore=shutil.ignore_patterns(*EXCLUDE_DIRS, "*.pyc"))
        for d, _, fs in os.walk(root):
            for x in [d, *(os.path.join(d, f) for f in fs)]:
                if not os.path.islink(x): os.chmod(x, os.stat(x).st_mode | 0o200)
    here = Path(__file__).resolve().parent
    cp = here / "companion_prompt.py"
    if cp.exists():
        r = subprocess.run([sys.executable, str(cp), str(root), "--out", str(out)], capture_output=True, text=True)
        if r.returncode != 0: print(r.stdout + r.stderr); print("Companion prompt failed: fix it, then package again."); return 1
    ev_ok, ev_note = eval_status(root)
    if need_evals and not ev_ok: print(f"Behavior tests: {ev_note}. Run them, or package without --require-evals."); return 1
    ext = ".plugin" if fmt == "plugin" else ".zip"
    fname = re.sub(r'[\\/:*?"<>|]', "", f"{visible} v{version}{ext}")
    dest = out / fname
    digest = content_hash(root, fmt)
    reused, validated = False, "skipped (--skip-validate)" if skip else "not run (validator not found)"
    if dest.exists() and not force:
        try:
            with zipfile.ZipFile(dest) as z: reused = z.comment.decode("utf-8", "replace") == f"ai-extender:sha256={digest}"
        except (OSError, zipfile.BadZipFile): reused = False
    if not reused:
        if not skip:
            v = here.parents[1] / "claude-reviewer" / "scripts" / "validate_extension.py"
            if v.exists():
                vt = "cowork" if fmt == "plugin" and target == "all" else target
                r = subprocess.run([sys.executable, str(v), str(root), "--cache", "--target", vt], capture_output=True, text=True)
                if r.returncode != 0: print(r.stdout); print("Validation failed: fix errors or pass --skip-validate."); return 1
                counts = re.search(r"\| (\d+) \| (\d+) \| (\d+) \|", r.stdout)
                warns = re.findall(r"^- `(\w+)` ([^\n]+)$", r.stdout.split("**Warnings**")[1].split("**Info**")[0], re.M) if "**Warnings**" in r.stdout else []
                validated = f"passed, target {vt}" + (f" ({counts.group(1)} errors, {counts.group(2)} warnings)" if counts else "") + "".join(f"<br>warning `{c}` {m}" for c, m in warns)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / fname
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
                for p, rel in files(root):
                    z.write(p, (rel if fmt == "plugin" else Path(slug) / rel).as_posix())
                if not skip: z.comment = f"ai-extender:sha256={digest}".encode()
            out.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tmp, dest)
    with zipfile.ZipFile(dest) as z:
        n = len(z.namelist())
    ig = here / "install_guide.py"
    guide = out / f"{fname[:-len(ext)]} install.md"
    if ig.exists():
        args = [sys.executable, str(ig), str(root), "--file", fname, "--out", str(guide)] + (["--repo", repo] if repo else [])
        if subprocess.run(args, capture_output=True, text=True).returncode != 0: guide = None
    rows = [("File", f"`{dest}`" + (" (unchanged since the last build: reused, not re-checked)" if reused else "")), ("Entries", n), ("Version", version), ("Validation", "passed when this package was built" if reused else validated),
            ("Companion prompt", f"`prompts/` checked and copied into `{out}`"), ("Install guide", f"`{guide}`" if guide else "not written"),
            ("Behavior tests", ("ok: " if ev_ok else "flag: ") + ev_note)]
    if staged: rows.append(("Source", "read-only, so a temp copy was packaged; the source folder was not changed and has no `prompts/` folder"))
    prev = prev or previous_package(out, visible, version, ext)
    rd = here.parents[1] / "claude-maintainer" / "scripts" / "release_diff.py"
    if prev and prev.exists() and rd.exists():
        sys.dont_write_bytecode = True; sys.path.insert(0, str(rd.parent))
        from release_diff import diff, summary
        rows.append(("Since " + prev.name, summary(diff(prev, dest))))
    print(f"### Scratchpad: Extension Packager\n**Scope:** {kind} `{root.name}` → {fmt}\n\n| Item | Result |\n|---|---|")
    for k, v in rows: print(f"| {k} | {v} |")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
