#!/usr/bin/env python3
"""Package a Claude extension: validate, name, zip.

Usage: package_extension.py <dir> --format plugin|zip [--out DIR] [--skip-validate] [--target T]
  plugin: zip with the plugin root as archive root, extension .plugin (Cowork)
  zip:    zip with the extension folder as the top-level entry (skill upload, manual install)
Filename: "<Visible Name> v<version>.<ext>" (displayName / skill title + metadata.version).
Always creates or checks the Prompt Builder companion prompt (prompts/<title-slug>.json, via companion_prompt.py)
and copies it next to the package. Builds in a temp dir, then copies to --out (default ./dist).
"""
import json, re, shutil, subprocess, sys, tempfile, zipfile
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
        return "plugin", m.get("displayName") or m["name"], str(m.get("version", "0.0.1"))
    sm = root / "SKILL.md"
    if sm.exists():
        t = sm.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        nm = re.search(r"^name:\s*(.+)$", t, re.M)
        if not nm: raise SystemExit("SKILL.md has no name")
        name = nm.group(1).strip().strip("\"'")
        ver = re.search(r"^\s+version:\s*(\S+)", t, re.M)
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        return "skill", (h1.group(1).strip() if h1 else name.replace("-", " ").title()), (ver.group(1).strip("\"'") if ver else "0.0.1")
    raise SystemExit(f"not a plugin or skill directory: {root}")

def files(root):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if p.is_symlink() or p.is_dir() or any(x in EXCLUDE_DIRS for x in rel.parts): continue
        if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIX: continue
        yield p, rel

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root, fmt, out, skip, target = Path(argv[0]).resolve(), None, Path("dist"), False, "all"
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--format": fmt = argv[i+1]; i += 1
        elif a == "--out": out = Path(argv[i+1]); i += 1
        elif a == "--target": target = argv[i+1]; i += 1
        elif a == "--skip-validate": skip = True
        else: print(__doc__); return 2
        i += 1
    if fmt not in ("plugin", "zip"): print(__doc__); return 2
    kind, visible, version = info(root)
    if fmt == "plugin" and kind != "plugin": print(".plugin format requires a plugin directory"); return 2
    cp = Path(__file__).resolve().parent / "companion_prompt.py"
    if cp.exists():
        r = subprocess.run([sys.executable, str(cp), str(root), "--out", str(out)], capture_output=True, text=True)
        if r.returncode != 0: print(r.stdout + r.stderr); print("Companion prompt failed: fix it, then package again."); return 1
    if not skip:
        v = Path(__file__).resolve().parents[2] / "claude-reviewer" / "scripts" / "validate_extension.py"
        if v.exists():
            r = subprocess.run([sys.executable, str(v), str(root), "--target", "cowork" if fmt == "plugin" and target == "all" else target], capture_output=True, text=True)
            if r.returncode != 0: print(r.stdout); print("Validation failed: fix errors or pass --skip-validate."); return 1
    ext = ".plugin" if fmt == "plugin" else ".zip"
    fname = re.sub(r'[\\/:*?"<>|]', "", f"{visible} v{version}{ext}")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / fname
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for p, rel in files(root):
                z.write(p, (rel if fmt == "plugin" else Path(root.name) / rel).as_posix())
        out.mkdir(parents=True, exist_ok=True)
        dest = out / fname
        shutil.copyfile(tmp, dest)
    with zipfile.ZipFile(dest) as z:
        n = len(z.namelist())
    print(f"### Scratchpad — Extension Packager\n**Scope:** {kind} `{root.name}` → {fmt}\n\n| Item | Result |\n|---|---|\n| File | `{dest}` |\n| Entries | {n} |\n| Version | {version} |\n| Companion prompt | `prompts/` checked and copied into `{out}` |")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
