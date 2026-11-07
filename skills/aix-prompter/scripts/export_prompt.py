#!/usr/bin/env python3
"""Export a crafted prompt as Prompt Builder JSON (format "prompt-builder-plain", version 2.0).

Usage: export_prompt.py SPEC.json --out DIR [--id HEX32] [--check-only]
       export_prompt.py --md PROMPT.md --title "Title" [--description TEXT] --out DIR [--id HEX32]

SPEC.json: {"title", "description"?, "content", "variables"?}. Without "variables", every {{name}} in content becomes a
Textarea field. Text is normalized to ASCII first (ascii_check.py); anything that cannot be normalized fails the export.
The schema, escaping and checks come from the packager's companion_prompt.py (imported, not copied).
Writes DIR/<title-slug>.json. Exit: 0 ok, 1 problems, 2 usage. Standard library only; no network.
"""
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # set before the imports below: no __pycache__ inside the plugin

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "aix-packager" / "scripts"))
try:
    import companion_prompt as cp
except ImportError:
    raise SystemExit("companion_prompt.py not found: run this from the full ai-extender plugin (skills/aix-packager/scripts).")
import ascii_check as ac


def norm_all(o):
    if isinstance(o, str):
        return ac.normalize(o)
    if isinstance(o, list):
        return [norm_all(x) for x in o]
    if isinstance(o, dict):
        return {k: norm_all(v) for k, v in o.items()}
    return o


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    spec_path = md = title = desc = out = pid = None
    check_only = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--md" and i + 1 < len(argv):
            md = argv[i + 1]; i += 1
        elif a == "--title" and i + 1 < len(argv):
            title = argv[i + 1]; i += 1
        elif a == "--description" and i + 1 < len(argv):
            desc = argv[i + 1]; i += 1
        elif a == "--out" and i + 1 < len(argv):
            out = Path(argv[i + 1]); i += 1
        elif a == "--id" and i + 1 < len(argv):
            pid = argv[i + 1]; i += 1
        elif a == "--check-only":
            check_only = True
        elif not a.startswith("--") and spec_path is None:
            spec_path = a
        else:
            print(__doc__)
            return 2
        i += 1
    if (spec_path is None) == (md is None) or (out is None and not check_only):
        print(__doc__)
        return 2
    if pid and not re.match(r"^[0-9a-f]{32}$", pid):
        print("--id must be 32 lowercase hex characters")
        return 2
    try:
        if md:
            if not title:
                print("--md needs --title")
                return 2
            spec = {"title": title, "description": desc or "", "content": Path(md).read_text(encoding="utf-8-sig")}
        else:
            spec = json.loads(Path(spec_path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print(f"cannot read input: {e}")
        return 2
    if not isinstance(spec, dict) or not isinstance(spec.get("content"), str) or not spec.get("title"):
        print('spec needs "title" and "content" (text)')
        return 2
    spec = norm_all(spec)
    if not isinstance(spec.get("variables"), dict):
        names = list(dict.fromkeys(cp.VAR.findall(spec["content"])))
        spec["variables"] = {n: cp.var("Textarea", n.replace("_", " ").title(), n, "", False, 3000) for n in names}
    left = ac.find(json.dumps(spec, ensure_ascii=False))
    if left:
        ac.report(left, "spec")
        print("Export stopped: non-ASCII left after normalizing.")
        return 1
    doc = cp.build(spec, spec["title"], {"id": pid} if pid else None)
    E, W = cp.check(doc)
    target = (out or Path(".")) / f"{cp.slugify(spec['title'])}.json"
    cp.report(target.name, E, W)
    if E:
        return 1
    if check_only:
        return 0
    out.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"\nWritten: {target}\nImport: Prompt Builder > Settings > Import, choose the .json file.")
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
