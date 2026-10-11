#!/usr/bin/env python3
"""Compare two versions of an extension: how many files were kept, changed, added, and dropped.

Usage: release_diff.py <old> <new> [--json] [--list]
<old> and <new> are folders, .plugin files, or .zip files (a single top-level folder in a zip is ignored).
Packaging junk (.git, dist, __pycache__, node_modules, .venv, .DS_Store, *.pyc) is ignored, as the packager does.
"""
import hashlib, json, sys, zipfile
from pathlib import Path

SKIP = {".git", ".github", "__pycache__", "node_modules", ".venv", "dist"}

def keep(rel):
    parts = rel.split("/")
    return not (set(parts) & SKIP or parts[-1] == ".DS_Store" or rel.endswith((".pyc", ".plugin", ".zip")))

def digest(b): return hashlib.sha256(b).hexdigest()

def load(path):
    p = Path(path)
    if p.is_dir():
        return {f.relative_to(p).as_posix(): digest(f.read_bytes()) for f in p.rglob("*")
                if f.is_file() and not f.is_symlink() and keep(f.relative_to(p).as_posix())}
    with zipfile.ZipFile(p) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        tops = {n.split("/", 1)[0] for n in names}
        strip = len(tops) == 1 and all("/" in n for n in names) and not any(n.startswith(".claude-plugin/") for n in names)
        out = {}
        for n in names:
            rel = n.split("/", 1)[1] if strip else n
            if keep(rel): out[rel] = digest(z.read(n))
        return out

def diff(old, new):
    a, b = load(old), load(new)
    return {"kept": sorted(k for k in a if k in b and a[k] == b[k]),
            "changed": sorted(k for k in a if k in b and a[k] != b[k]),
            "added": sorted(k for k in b if k not in a),
            "dropped": sorted(k for k in a if k not in b),
            "old_total": len(a), "new_total": len(b)}

def summary(d):
    return f"{d['new_total']} files: {len(d['kept'])} kept, {len(d['changed'])} changed, {len(d['added'])} added, {len(d['dropped'])} dropped (previous {d['old_total']})"

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2: print(__doc__); return 2
    d = diff(*args)
    if "--json" in argv: print(json.dumps(d, indent=2)); return 0
    print(f"### Scratchpad: Release Diff\n**Scope:** `{Path(args[0]).resolve().name}` → `{Path(args[1]).resolve().name}`\n\n| Files | Count |\n|---|---|")
    for k in ("kept", "changed", "added", "dropped"): print(f"| {k.title()} | {len(d[k])} |")
    print(f"| Total (old → new) | {d['old_total']} → {d['new_total']} |")
    if "--list" in argv:
        for k in ("changed", "added", "dropped"):
            if d[k]: print(f"\n**{k.title()}**\n" + "\n".join(f"- `{x}`" for x in d[k]))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
