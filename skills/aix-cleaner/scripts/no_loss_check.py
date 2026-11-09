#!/usr/bin/env python3
"""No-loss gate: prove a merge/shorten/de-dup lost no nuance. Exit 1 on any problem. Python 3.9+, stdlib only.

Usage: no_loss_check.py --old FILE --new FILE [--threshold 0.15] [--map-yaml FILE] [--sxs OUT.md] [--pairs OUT.md]
Checks: (1) clause coverage  (2) mapping completeness  (3) strength downgrades.
--sxs: two-column old/new markdown for human review. --pairs: each old clause beside its closest new clause,
for the independent semantic reviewer. Word coverage cannot prove emphasis or tone: the reviewer pass is mandatory.
"""
import argparse, difflib, re, sys
from pathlib import Path

STOP = set("the a an and or but if of to in on at by for with from as is are was were be been being it its this that these those "
           "then than so not no you your we our they them their he she his her can will would could do does did has have had "
           "into onto over per via also any all each".split())
STRONG = ["must", "never", "always", "shall", "required", "mandatory", "only", "hook", "block", "fail", "forbidden", "prohibited"]
WEAK = ["should", "may", "might", "prefer", "consider", "guidance", "recommended", "try"]

def clauses(text):
    out = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)]|#+)\s*", "", line).strip()
        if not line: continue
        parts = re.split(r"(?<!e\.g)(?<![Ii]\.e)(?<=[.!?])\s+|;\s*|\s+(?=Why:)", line)
        out += [p.strip() for p in parts if p and p.strip()]
    return out

def words(s):
    return [w for w in (x.strip(".:,;-'_") for x in re.findall(r"[\w'/.\:-]+", s.lower().replace("’", "'"))) if len(w) > 2 and w not in STOP]

def best_match(cl, new_clauses):
    w = set(words(cl))
    return max(new_clauses, key=lambda n: len(w & set(words(n))) / (len(w | set(words(n))) or 1), default="")

def items(old):
    ids = re.findall(r"^\s*#+\s+(.+?)\s*$", old, re.M) + re.findall(r"^\s*-?\s*(?:name|id):\s*(\S.*?)\s*$", old, re.M)
    return [i.strip("`'\" ") for i in ids]

def tokens(text):
    nums = set(re.findall(r"\b\d+(?:[.,:]\d+)*%?", text))
    named = set(re.findall(r"https?://\S+|`[^`\n]+`|(?:[\w.-]+[/\x5c])+[\w.-]*|\b[\w-]+\.(?:py|md|json|js|sh|yml|yaml|txt)\b", text))
    return nums, {n.strip("`.,);") for n in named}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", required=True); ap.add_argument("--new", required=True)
    ap.add_argument("--threshold", type=float, default=0.15); ap.add_argument("--map-yaml")
    ap.add_argument("--sxs"); ap.add_argument("--pairs")
    a = ap.parse_args()
    old, new = Path(a.old).read_text(encoding="utf-8"), Path(a.new).read_text(encoding="utf-8")
    problems = []
    oc, nc, nwords = clauses(old), clauses(new), set(words(new))

    # 1. clause coverage
    for c in oc:
        w = words(c)
        if not w: continue
        miss = sorted({x for x in w if x not in nwords})
        if len(miss) / len(w) > a.threshold:
            problems.append(f"CLAUSE FLAG ({len(miss)}/{len(w)} words missing: {', '.join(miss)})\n    old: {c}\n    closest new: {best_match(c, nc)}\n    -> quote the new sentence that carries it, or restore the wording")

    # 2. mapping completeness
    its = items(old)
    if its:
        if not a.map_yaml:
            problems.append(f"MAPPING: {len(its)} old items found but no --map-yaml given")
        else:
            was = [n.strip("`'\" ") for m in re.findall(r"was:\s*\[([^\]]*)\]", Path(a.map_yaml).read_text(encoding="utf-8")) for n in m.split(",") if n.strip()]
            for i in its:
                n = was.count(i)
                if n != 1: problems.append(f"MAPPING: old item '{i}' is mapped {n} times (must be exactly once)")
            for n in set(was) - set(its): problems.append(f"MAPPING: map names unknown old item '{n}'")

    # 3. no downgrade
    low_o, low_n = old.lower(), new.lower()
    cnt = lambda t, w: len(re.findall(rf"\b{w}\b", t))
    for w in STRONG:
        if cnt(low_n, w) < cnt(low_o, w): problems.append(f"DOWNGRADE: '{w}' {cnt(low_o, w)} -> {cnt(low_n, w)}")
    for w in WEAK:
        if cnt(low_n, w) > cnt(low_o, w): problems.append(f"DOWNGRADE?: weaker word '{w}' {cnt(low_o, w)} -> {cnt(low_n, w)} (must->should, hook->guidance?)")
    for w in ("MUST", "NEVER", "ALWAYS"):
        if len(re.findall(rf"\b{w}\b", new)) < len(re.findall(rf"\b{w}\b", old)): problems.append(f"DOWNGRADE: capitalised {w} dropped or lowered")
    if cnt(low_n, r"e\.g\.|for example|example") < cnt(low_o, r"e\.g\.|for example|example"): problems.append("DOWNGRADE: fewer examples")
    on, oN = tokens(old); nn, nN = tokens(new)
    for x in sorted(on - nn): problems.append(f"DOWNGRADE: number/threshold '{x}' no longer present")
    for x in sorted(oN - nN): problems.append(f"DOWNGRADE: named tool/path/URL '{x}' no longer present")

    if a.sxs:
        ol, nl, rows = old.splitlines(), new.splitlines(), []
        esc = lambda s: s.replace("|", "&#124;") or " "
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ol, nl, autojunk=False).get_opcodes():
            rows.append(f"| {esc('<br>'.join(ol[i1:i2]))} | {esc('<br>'.join(nl[j1:j2]))} |" + ("" if tag == "equal" else " "))
        Path(a.sxs).write_text("| OLD | NEW |\n|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")
    if a.pairs:
        Path(a.pairs).write_text("\n".join(f"## {n}\nOLD: {c}\nNEW (closest): {best_match(c, nc)}\nVerdict (identical meaning / weaker / lost nuance / changed scope):\n" for n, c in enumerate(oc, 1)), encoding="utf-8")

    for p in problems: print(p)
    print(f"{'FAIL' if problems else 'PASS'} no-loss gate: {len(oc)} old clauses, {len(problems)} problems")
    return 1 if problems else 0

sys.exit(main())
