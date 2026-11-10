#!/usr/bin/env python3
"""Check a plugin's router against its router evals. No dependencies.

Usage: route_check.py <plugin-dir> [--cases evals/router/cases.json] [--json]
Reads the routing table in the router skill (skills/<plugin>/SKILL.md, the table under the heading "Routing table":
`| Order | Trigger phrases | Skill | Then |`, phrases separated by `;`, matched as whole words, first matching row wins; a phrase starting with `!` excludes the row when it appears),
routes every case prompt, and compares with the expected slug (`ask` = no row matches: the router asks its one closed
question). Exit 0 when every case routes as expected, 1 on a mismatch or a missing table, 2 on usage.
"""
import json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True

def parse_table(text):
    """[(order, [phrases], slug, [then slugs])] from the Routing table section; None when there is no such section."""
    m = re.search(r"^#{2,4}[^\n]*Routing table[^\n]*\n(.*?)(?=^#{1,4} |\Z)", text, re.M | re.S | re.I)
    if not m: return None
    rows = []
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not line.lstrip().startswith("|") or re.fullmatch(r"[-: ]+", cells[0]) or cells[0].lower() == "order": continue
        slugs = re.findall(r"`([^`]+)`", cells[2])
        if not slugs: continue
        then = re.findall(r"`([^`]+)`", cells[3]) if len(cells) > 3 else []
        rows.append((cells[0], [p.strip().lower().replace("’", "'") for p in cells[1].split(";") if p.strip()], slugs[0].split(":")[-1], [s.split(":")[-1] for s in then]))
    return rows

def route(rows, prompt):
    """Slug the table picks for the prompt, or 'ask' when no row matches."""
    q = prompt.lower().replace("’", "'")
    has = lambda ph: re.search(r"(?<![\w])" + re.escape(ph) + r"(?![\w])", q)
    for _, phrases, slug, _ in rows:
        if any(has(ph[1:]) for ph in phrases if ph.startswith("!")): continue  # an exclusion phrase cancels the row
        if any(has(ph) for ph in phrases if not ph.startswith("!")): return slug
    return "ask"

def check(root, cases_path=None):
    """(problems, n_cases). Problems are strings."""
    root = Path(root)
    name = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"] if (root / ".claude-plugin" / "plugin.json").exists() else root.name
    router = root / "skills" / name / "SKILL.md"
    if not router.exists(): return [f"no router skill skills/{name}/SKILL.md"], 0
    rows = parse_table(router.read_text(encoding="utf-8-sig"))
    if not rows: return ["router has no Routing table (`| Order | Trigger phrases | Skill | Then |`)"], 0
    cp = Path(cases_path) if cases_path else root / "evals" / "router" / "cases.json"
    if not cp.exists(): return [f"no router cases at {cp}"], 0
    cases = json.loads(cp.read_text(encoding="utf-8-sig")).get("cases", [])
    bad = []
    for c in cases:
        got = route(rows, c["prompt"])
        if got != c["expected"]: bad.append(f"'{c['prompt']}' routed to {got}, expected {c['expected']}")
    skills = {d.name for d in (root / "skills").iterdir() if d.is_dir()} - {name}
    for s in sorted(skills):
        n = sum(1 for c in cases if c["expected"] == s)
        if n < 2: bad.append(f"skill {s} has {n} router case(s); at least 2 are required")
    if not any(c["expected"] == "ask" for c in cases): bad.append("no ambiguous case (expected 'ask')")
    return bad, len(cases)

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    cp = argv[argv.index("--cases") + 1] if "--cases" in argv else None
    if cp: args.remove(cp)
    if len(args) != 1: print(__doc__); return 2
    bad, n = check(args[0], cp)
    if "--json" in argv: print(json.dumps({"cases": n, "problems": bad}, indent=2))
    else:
        print(f"### Scratchpad: Router Check\n**Scope:** {args[0]}, {n} cases\n")
        print("| Result | Detail |\n|---|---|")
        if bad:
            for b in bad: print(f"| FAIL | {b} |")
        else: print(f"| PASS | all {n} prompts route to the expected skill |")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
