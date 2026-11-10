#!/usr/bin/env python3
"""Build one zip per skill: skills/<name> -> <out>/<name>.zip (the skill folder is the top-level entry).

Usage: build_skill_zips.py <plugin-dir> [--out dist] [--only name,name]
Each zip holds only that skill's own folder, ready for claude.ai Customize > Skills upload or `npx skills add`.
Skips symlinks and junk files the same way package_extension.py does. Exit 1 if a skill has no SKILL.md.
Also exit 1 if the secret and private-data scan finds anything inside a produced zip (the zip is removed).
"""
import subprocess, sys, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_extension import files  # reuse the packager's exclusion rules

def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 2
    root, out, only = Path(argv[0]).resolve(), Path("dist"), None
    if "--out" in argv: out = Path(argv[argv.index("--out") + 1])
    if "--only" in argv: only = set(argv[argv.index("--only") + 1].split(","))
    skills = sorted(p for p in (root / "skills").glob("*") if p.is_dir() and (not only or p.name in only))
    if not skills: print(f"no skills under {root / 'skills'}"); return 1
    out.mkdir(parents=True, exist_ok=True); bad = 0
    for s in skills:
        if not (s / "SKILL.md").is_file(): print(f"SKIP {s.name}: no SKILL.md"); bad = 1; continue
        dest = out / f"{s.name}.zip"
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            for p, rel in files(s): z.write(p, (Path(s.name) / rel).as_posix())
        scan = Path(__file__).resolve().parents[2] / "aiaddon-review" / "scripts" / "scan_secrets.py"  # blocking: scans inside the produced zip
        if not scan.is_file(): dest.unlink(); print(f"REFUSED {s.name}: aiaddon-review/scripts/scan_secrets.py not found, so the zip cannot be scanned (removed)"); bad = 1; continue
        if scan.is_file():
            r = subprocess.run([sys.executable, str(scan), str(dest)], capture_output=True, text=True)
            if r.returncode != 0: print(r.stdout + r.stderr); dest.unlink(); print(f"REFUSED {s.name}: secret or private data inside the zip (removed)"); bad = 1; continue
        with zipfile.ZipFile(dest) as z: n = len(z.namelist())
        print(f"built {dest} ({n} files)")
    return bad

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
