#!/usr/bin/env python3
"""Find passwords and API keys stored in plain text in the extension folders or archives you name.

Usage: scan_secrets.py <dir-or-archive> [...] [--history] [--artifacts <dir-or-zip> ...] [--allowlist FILE] [--json]
Scans only the paths given on the command line.
Reads files only; sends nothing anywhere. Values are masked in the report. Exit 1 when anything is found.
After a hit: move the value to userConfig with "sensitive": true (or an environment variable), then rotate the key,
because anyone who received a copy still has the old one.

Public-safety additions (every finding is blocking; engine in public_safety.py, pure standard library):
  --history          also scan every line ever added on any ref (`git log --all -p`) of each <dir> that is a git repo
  --artifacts PATH   also scan inside built .zip/.plugin files (a file, or a folder: dist/ is included)
  --allowlist FILE   false-positive rules (default: .public-safety-allow in each <dir>); format in public_safety.py
Besides keys it finds provider tokens (GitHub, OpenAI, Anthropic, AWS, Slack, Google), private keys, Bearer tokens,
password assignments, high-entropy strings, personal e-mails (not noreply or placeholder), absolute user paths, internal
hosts, and private files (.env, key files, logs, memory or progress notes). Past leaks: references/public-safety.md.
"""
import json, sys, zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_extension import find_secrets, TEXT_SUFFIX  # noqa: E402
import public_safety as ps  # noqa: E402

SKIP = {".git", "node_modules", "__pycache__", ".venv", "dist"}
SELF = {"validate_extension.py", "scan_secrets.py", "selftest.py", "public_safety.py"}  # the scanner's own sources, which hold the patterns
MAX = 2_000_000

def wanted(name): return Path(name).suffix in TEXT_SUFFIX or Path(name).name.startswith(".env")

def own_source(path): return Path(path).name in SELF and Path(path).parent.name == "scripts"

def scan_dir(d):
    for f in sorted(d.rglob("*")):
        try:
            rel = f.relative_to(d)
            if set(rel.parts) & SKIP or f.is_symlink() or not f.is_file() or own_source(f): continue
            if f.suffix in (".plugin", ".zip"): yield from scan_zip(f); continue
            if not wanted(f.name) or f.stat().st_size > MAX: continue
            text = f.read_text(encoding="utf-8-sig", errors="replace")
        except OSError: continue
        for no, code, masked in find_secrets(text): yield (str(f), no, code, masked)

def scan_zip(z):
    try:
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith("/") or set(n.split("/")) & SKIP or own_source(n) or not wanted(n): continue
                if zf.getinfo(n).file_size > MAX: continue
                for no, code, masked in find_secrets(zf.read(n).decode("utf-8", "replace")): yield (f"{z}!{n}", no, code, masked)
    except (OSError, zipfile.BadZipFile): return

def engine_rows(paths, arts, allow, hist):
    """Public-safety findings as (file, line, rule, masked, kind, where) tuples."""
    out = []
    def take(rows, base=None):
        for r in rows:
            f = r["file"] if base is None else str(Path(base) / r["file"])
            out.append((f, r["line"], r["rule"], r["value"], r["kind"], r["where"]))
    for p in paths:
        rules = ps.load_allowlist(allow or (p / ps.ALLOW_FILE if p.is_dir() else ps.ALLOW_FILE))
        if p.is_file():
            try: take(ps.scan_zip_bytes(p.read_bytes(), str(p), rules))
            except OSError: pass
        elif p.is_dir():
            take((r for r in ps.scan_tree(p, rules) if not own_source(r["file"])), p)
            if hist: take(ps.scan_history(p, rules), p)
    if arts:
        base = paths[0] if paths and paths[0].is_dir() else Path(".")
        take(ps.scan_artifacts(arts, ps.load_allowlist(allow or base / ps.ALLOW_FILE)))
    return out

def main(argv):
    paths, arts, allow, hist, i = [], [], None, False, 0
    while i < len(argv):
        a = argv[i]
        if a == "--history": hist = True
        elif a == "--artifacts" and i + 1 < len(argv):
            i += 1
            while i < len(argv) and not argv[i].startswith("--"): arts.append(Path(argv[i])); i += 1
            continue
        elif a == "--allowlist" and i + 1 < len(argv): allow = argv[i + 1]; i += 1
        elif not a.startswith("--"): paths.append(Path(a))
        i += 1
    if not paths and not arts: print(__doc__); return 2
    hits, seen = [], set()
    for p in paths:
        rows = scan_zip(p) if p.is_file() else scan_dir(p) if p.is_dir() else []
        for r in rows:
            if r not in seen: seen.add(r); hits.append(r)
    tails = {(f.replace("\\", "/").split("!")[-1], no) for f, no, *_ in hits}  # a line the key scan already reports is not listed twice
    for f, no, rule, masked, kind, where in engine_rows(paths, arts, allow, hist):
        t = f.replace("\\", "/").split("!")[-1]
        if no and any(n == no and (t.endswith(x) or x.endswith(t)) for x, n in tails): continue
        r = (f, no, rule, masked, kind, where)
        if r not in seen: seen.add(r); hits.append(r)
    if "--json" in argv:
        rows = [dict(zip(("file", "line", "code", "value", "kind", "where"), h)) for h in hits]
        for r in rows:
            if "kind" not in r: r["kind"] = "known key format" if r["code"] == "X001" else "key-like value"
        print(json.dumps(rows, indent=2)); return 1 if hits else 0
    print(f"### Scratchpad: Secret Scan\n**Scope:** {', '.join(str(p) for p in paths)}\n")
    if not hits: print("No plain-text secrets found."); return 0
    print("| File | Line | Kind | Value |\n|---|---|---|---|")
    for h in hits:
        f, no, code, masked = h[:4]
        if len(h) > 4: print(f"| `{f}` | {no or '-'} | {h[4]}{' (' + h[5] + ')' if h[5] else ''} | `{masked}` |")
        else: print(f"| `{f}` | {no} | {'known key format' if code == 'X001' else 'key-like value'} | `{masked}` |")
    print("\n**Next:** move each real value to userConfig with `sensitive: true`, then rotate the key: copies already shared keep the old one.")
    if any(len(h) > 4 for h in hits): print("Every finding is blocking. A secret or private value already in git history, a package or a release: rotate first, then follow past leak remediation in `aiaddon-review/references/public-safety.md` (never force-push without the owner's explicit OK). Exact public false positives go in `.public-safety-allow`.")
    return 1

if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):  # Windows cp1252 consoles cannot print arrows or dashes
        try: _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError): pass
    sys.exit(main(sys.argv[1:]))
