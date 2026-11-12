#!/usr/bin/env python3
"""Keep-unique proof: every normalized line of the BEFORE tree must still exist in the AFTER tree
(or in the archive folder). Stdlib only, Python 3.9+, read-only.

Usage: prove.py <before-dir> <after-dir> [--archive <dir>] [--ext .md,.json,.py,.yaml,.yml,.txt]
Prints PASS or FAIL with each lost line (file:line). Exit 0 zero lost, 1 lost lines, 2 usage.
Use a copy or `git worktree` of the original as <before-dir>. Run with: python -B prove.py ...
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import norm, trivial, text_files, read, DEFAULT_EXT  # noqa: E402


def lines_of(root, exts, skip=None):
    out = {}
    for p in (text_files(root, exts, skip) if skip is not None else text_files(root, exts)):
        t = read(p)
        if t is None:
            continue
        for no, ln in enumerate(t.split("\n"), 1):
            n = norm(ln)
            if not trivial(n):
                out.setdefault(n, (p.relative_to(root).as_posix(), no))
    return out


def main(argv):
    arch, exts, args, i = None, DEFAULT_EXT, [], 0
    while i < len(argv):
        if argv[i] == "--archive" and i + 1 < len(argv):
            arch = Path(argv[i + 1])
            i += 2
        elif argv[i] == "--ext" and i + 1 < len(argv):
            exts = tuple(e if e.startswith(".") else "." + e for e in argv[i + 1].lower().split(",") if e)
            i += 2
        elif argv[i].startswith("-"):
            print(__doc__)
            return 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 2 or not all(Path(a).is_dir() for a in args):
        print(__doc__)
        return 2
    before = lines_of(Path(args[0]).resolve(), exts)
    kept = set(lines_of(Path(args[1]).resolve(), exts, skip={".git", "__pycache__", "node_modules", ".venv"}))
    if arch and arch.is_dir():
        kept |= set(lines_of(arch.resolve(), exts, skip=set()))
    lost = [(loc, n) for n, loc in before.items() if n not in kept]
    print(f"before: {len(before)} unique lines; after (+archive): {len(kept)}; lost: {len(lost)}")
    for (f, no), n in sorted(lost):
        print(f"LOST {f}:{no}: {n[:140]}")
    print("PASS zero unique lines lost" if not lost else "FAIL unique lines would be lost: add them to a kept file or the plan")
    return 0 if not lost else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
