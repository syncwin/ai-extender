#!/usr/bin/env python3
"""Move a file into an archive folder instead of deleting it. Dry-run by default. Stdlib only, Python 3.9+.

Usage: archive.py <root> <relative-file> --archive <dir> [--apply]
Keeps the relative path under the archive, refuses paths outside <root>, never overwrites, never deletes.
Run with: python -B archive.py ...
"""
import shutil
import sys
sys.dont_write_bytecode = True
from pathlib import Path


def main(argv):
    apply_, arch, args, i = False, None, [], 0
    while i < len(argv):
        if argv[i] == "--apply":
            apply_ = True
            i += 1
        elif argv[i] == "--archive" and i + 1 < len(argv):
            arch = Path(argv[i + 1]).resolve()
            i += 2
        elif argv[i].startswith("-"):
            print(__doc__)
            return 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 2 or arch is None:
        print(__doc__)
        return 2
    root = Path(args[0]).resolve()
    src = (root / args[1]).resolve()
    if root not in src.parents or not src.is_file():
        print(f"refused: {args[1]} is not a file inside {root}")
        return 1
    if arch == src or src in arch.parents:
        print("refused: bad archive folder")
        return 1
    dest = arch / src.relative_to(root)
    if dest.exists():
        print(f"refused: {dest} exists (never overwrites)")
        return 1
    print(("MOVE " if apply_ else "DRY-RUN would move ") + f"{src} -> {dest}")
    if apply_:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
