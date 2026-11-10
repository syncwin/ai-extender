#!/usr/bin/env python3
"""Find secrets and private data before anything is published: working tree, full git history, built packages.

Usage: scan_secrets.py <dir-or-archive> [...] [--history] [--artifacts <dir-or-zip> ...] [--allowlist FILE] [--json]
  <dir-or-archive>   working tree (only files git would publish when it is a git repo) or a .zip/.plugin file
  --history          also scan every line ever added on any ref (`git log --all -p`) of each <dir> that is a git repo
  --artifacts PATH   also scan inside built .zip/.plugin files (a file, or a folder: dist/ is included)
  --allowlist FILE   false-positive rules (default: .public-safety-allow in each <dir>); format in public_safety.py
Reads files only; sends nothing anywhere. Values are masked in the report. Exit 1 when anything is found (blocking).
Finds: GitHub/OpenAI/Anthropic/AWS/Slack/Google keys, private keys, Bearer tokens, password and key assignments,
high-entropy strings, personal e-mails (not noreply or placeholder), absolute user paths, internal hosts, and files that
must stay private (.env, keys, logs, memory or progress notes).
After a hit: move the value to userConfig with "sensitive": true (or an environment variable), rotate the key FIRST,
then follow `references/public-safety.md` (past leak remediation) when it is already in history or a release.
"""
import json, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_safety as ps  # noqa: E402

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
    def take(rows):
        for r in rows:
            k = (r["file"], r["line"], r["rule"], r["value"], r["where"])
            if k not in seen: seen.add(k); hits.append(r)
    for p in paths:
        rules = ps.load_allowlist(allow or (p / ps.ALLOW_FILE if p.is_dir() else ps.ALLOW_FILE))
        if p.is_file(): take(ps.scan_zip_bytes(p.read_bytes(), p.name, rules))
        elif p.is_dir():
            take(ps.scan_tree(p, rules))
            if hist: take(ps.scan_history(p, rules))
    if arts:
        base = paths[0] if paths and paths[0].is_dir() else Path(".")
        take(ps.scan_artifacts(arts, ps.load_allowlist(allow or base / ps.ALLOW_FILE)))
    if "--json" in argv:
        print(json.dumps(hits, indent=2)); return 1 if hits else 0
    scope = [str(p) for p in paths] + [f"artifacts: {a}" for a in arts] + (["git history"] if hist else [])
    print(f"### Scratchpad: Secret and Private-Data Scan\n**Scope:** {', '.join(scope)}\n")
    if not hits: print("No plain-text secrets or private data found."); return 0
    print("| File | Line | Kind | Value | Where |\n|---|---|---|---|---|")
    for h in hits: print(f"| `{h['file']}` | {h['line'] or '-'} | {h['kind']} | `{h['value']}` | {h['where'] or '-'} |")
    print("\n**Blocking.** Next: move each real value to userConfig with `sensitive: true`, then rotate the key first: copies already shared keep the old one. If it is in git history or a release, follow past leak remediation in `aiaddon-review/references/public-safety.md`; never force-push without the owner's explicit OK. False positives go in `.public-safety-allow`.")
    return 1

if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):  # Windows cp1252 consoles cannot print arrows or dashes
        try: _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError): pass
    sys.exit(main(sys.argv[1:]))
