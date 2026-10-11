#!/usr/bin/env python3
"""Find passwords and API keys stored in plain text, in one extension or in every installed plugin.

Usage: scan_secrets.py [<dir-or-archive> ...] [--installed] [--json]
--installed  also scan the usual plugin and skill folders on this machine: ~/.claude/plugins, ~/.claude/skills,
             and Cowork's mnt/.plugins, mnt/.local-plugins, /mnt/.plugins, /mnt/.local-plugins when present.
Reads files only; sends nothing anywhere. Values are masked in the report. Exit 1 when anything is found.
After a hit: move the value to userConfig with "sensitive": true (or an environment variable), then rotate the key,
because anyone who received a copy still has the old one.
"""
import json, sys, zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_extension import find_secrets, TEXT_SUFFIX  # noqa: E402

SKIP = {".git", "node_modules", "__pycache__", ".venv", "dist"}
SELF = {"validate_extension.py", "scan_secrets.py", "selftest.py"}
MAX = 2_000_000

def wanted(name): return Path(name).suffix in TEXT_SUFFIX or Path(name).name.startswith(".env")

def scan_dir(d):
    for f in sorted(d.rglob("*")):
        try:
            rel = f.relative_to(d)
            if set(rel.parts) & SKIP or f.is_symlink() or not f.is_file() or f.name in SELF: continue
            if f.suffix in (".plugin", ".zip"): yield from scan_zip(f); continue
            if not wanted(f.name) or f.stat().st_size > MAX: continue
            text = f.read_text(encoding="utf-8-sig", errors="replace")
        except OSError: continue
        for no, code, masked in find_secrets(text): yield (str(f), no, code, masked)

def scan_zip(z):
    try:
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith("/") or set(n.split("/")) & SKIP or Path(n).name in SELF or not wanted(n): continue
                if zf.getinfo(n).file_size > MAX: continue
                for no, code, masked in find_secrets(zf.read(n).decode("utf-8", "replace")): yield (f"{z}!{n}", no, code, masked)
    except (OSError, zipfile.BadZipFile): return

def installed_roots():
    home = Path.home()
    cands = [home / ".claude" / "plugins", home / ".claude" / "skills", Path("mnt/.plugins"), Path("mnt/.local-plugins"), Path("/mnt/.plugins"), Path("/mnt/.local-plugins")]
    return [c for c in cands if c.is_dir()]

def main(argv):
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if "--installed" in argv: paths += installed_roots()
    if not paths: print(__doc__); return 2
    hits, seen = [], set()
    for p in paths:
        rows = scan_zip(p) if p.is_file() else scan_dir(p) if p.is_dir() else []
        for r in rows:
            if r not in seen: seen.add(r); hits.append(r)
    if "--json" in argv:
        print(json.dumps([dict(zip(("file", "line", "code", "value"), h)) for h in hits], indent=2)); return 1 if hits else 0
    print(f"### Scratchpad: Secret Scan\n**Scope:** {', '.join(str(p) for p in paths)}\n")
    if not hits: print("No plain-text secrets found."); return 0
    print("| File | Line | Kind | Value |\n|---|---|---|---|")
    for f, no, code, masked in hits: print(f"| `{f}` | {no} | {'known key format' if code == 'X001' else 'key-like value'} | `{masked}` |")
    print("\n**Next:** move each real value to userConfig with `sensitive: true`, then rotate the key: copies already shared keep the old one.")
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
