#!/usr/bin/env python3
"""Copy shared files into every skill that needs them, and report copies that drifted.

Usage: sync_shared.py <plugin-dir> [--check]
Config: <plugin-dir>/.claude-plugin/shared-files.json
  {"files": {"shared/scratchpad.md": ["skills/*/references/scratchpad.md"]}}
  Keys are source files; values are target paths. `*` in a folder part matches every existing folder there.
--check  report only (exit 1 when a copy is missing or differs); without it, copies the source over each target.
"""
import json, sys
from pathlib import Path

def targets(root, pattern):
    parts = Path(pattern).parts
    bases = [root]
    for part in parts[:-1]:
        nxt = []
        for b in bases:
            if "*" in part: nxt += sorted(p for p in b.glob(part) if p.is_dir())
            else: nxt.append(b / part)
        bases = nxt
    return [b / parts[-1] for b in bases]

def plan(root):
    """[(source, target, state)]: state is same, differs, missing, or missing-source."""
    root = Path(root)
    cfg = json.loads((root / ".claude-plugin" / "shared-files.json").read_text(encoding="utf-8"))
    out = []
    for src, pats in (cfg.get("files") or {}).items():
        s = root / src
        if not s.is_file(): out.append((src, None, "missing-source")); continue
        data = s.read_bytes()
        for pat in pats if isinstance(pats, list) else [pats]:
            for t in targets(root, pat):
                if t.resolve() == s.resolve(): continue
                rel = t.relative_to(root).as_posix()
                out.append((src, rel, "same" if t.is_file() and t.read_bytes() == data else ("differs" if t.exists() else "missing")))
    return out

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root, check = Path(argv[0]).resolve(), "--check" in argv[1:]
    if not (root / ".claude-plugin" / "shared-files.json").exists(): print("no .claude-plugin/shared-files.json: nothing to sync"); return 0
    rows, bad = plan(root), 0
    for src, dst, state in rows:
        if state == "missing-source": bad += 1; continue
        if state != "same":
            bad += 1
            if not check:
                (root / dst).parent.mkdir(parents=True, exist_ok=True); (root / dst).write_bytes((root / src).read_bytes())
    same = sum(1 for r in rows if r[2] == "same")
    print(f"### Scratchpad: Shared Files\n**Scope:** `{root.name}` ({'check' if check else 'sync'})\n\n| Copy | Result |\n|---|---|")
    for src, dst, state in rows:
        if state != "same": print(f"| {dst or src} | {state if check or state == 'missing-source' else 'updated from ' + src} |")
    print(f"| unchanged | {same} |")
    return 1 if (check and bad) or any(r[2] == "missing-source" for r in rows) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
