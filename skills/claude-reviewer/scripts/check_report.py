#!/usr/bin/env python3
"""Check an audit report before it is sent: every finding row needs an Original and a Corrected cell, and a
Corrected cell must be the replacement itself, not advice.

Usage: check_report.py <report.md>   (or --stdin)
Reads Markdown tables whose header has "Original" and "Corrected" columns. Flags a Corrected cell that is empty,
starts with an instruction verb ("Add ...", "Consider ...", "Rename ..."), or only points elsewhere ("see above").
A location prefix is fine: `SKILL.md frontmatter: name: notes-helper`.
Exit: 0 clean, 1 cells to rewrite, 2 usage or no finding tables found.
"""
import re, sys
from pathlib import Path

VERBS = ("add", "consider", "make", "improve", "rename", "update", "ensure", "include", "write", "create", "fix",
         "change", "provide", "should", "use", "move", "expand", "flesh", "clarify", "rewrite", "define", "document",
         "specify", "replace", "restrict", "remove", "delete", "set", "give", "try", "avoid")
POINTER = re.compile(r"^(see|as above|same as|n/?a|tbd|todo|\.\.\.)\b", re.I)
PREFIX = re.compile(r"^[`*]*[\w./ -]{1,60}?(frontmatter|body|line \d+|section|\.json|\.md|\.py|\.ya?ml|\.txt)[`*]*\s*:\s*", re.I)

def cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")): return None
    return [c.strip() for c in re.split(r"(?<!\\)\|", s[1:-1])]

def check(text):
    issues, tables, header = [], 0, None
    for no, line in enumerate(text.splitlines(), 1):
        c = cells(line)
        if c is None: header = None; continue
        low = [x.lower().strip("*` ") for x in c]
        if "original" in low and "corrected" in low: header = (low.index("original"), low.index("corrected")); tables += 1; continue
        if header is None or all(re.fullmatch(r":?-{3,}:?", x) for x in c if x): continue
        oi, ci = header
        if max(oi, ci) >= len(c): issues.append((no, "row has fewer cells than the header")); continue
        orig, corr = c[oi], c[ci]
        body = re.sub(r"<br\s*/?>", " ", PREFIX.sub("", corr)).strip().strip("`*_ ")
        first = re.split(r"[\s:,(]", body.lower(), maxsplit=1)[0] if body else ""
        if not orig: issues.append((no, "Original is empty; quote the current text or write (missing)"))
        if not body: issues.append((no, "Corrected is empty"))
        elif POINTER.match(body): issues.append((no, f"Corrected points elsewhere ('{body[:40]}'); write the replacement text"))
        elif first in VERBS and not corr.lstrip().startswith("`"): issues.append((no, f"Corrected starts with '{first}': write the result itself, not an instruction"))
    return tables, issues

def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 2
    text = sys.stdin.read(5_000_000) if argv[0] == "--stdin" else Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    tables, issues = check(text)
    if not tables: print("No Original/Corrected tables found: every finding needs one (claude-reviewer Report)."); return 2
    if not issues: print(f"Report check: {tables} finding tables, every Corrected cell is replacement text."); return 0
    print(f"Report check: {len(issues)} cells to rewrite before sending.\n\n| Line | Problem |\n|---|---|")
    for no, msg in issues: print(f"| {no} | {msg} |")
    return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
