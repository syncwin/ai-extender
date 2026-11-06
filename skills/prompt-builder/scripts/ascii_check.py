#!/usr/bin/env python3
"""Fail on any non-ASCII character in a prompt; optionally normalize the common ones.

Usage: ascii_check.py FILE [--fix]
       ascii_check.py -            (read stdin, check only)
Reports line:column and the character for every non-ASCII character. With --fix, rewrites FILE after replacing
common look-alikes (smart quotes, dashes, arrows, check marks, bullets, ellipsis, non-breaking space) and
removing zero-width characters; anything still non-ASCII is reported and the exit code stays 1.
Exit: 0 clean, 1 non-ASCII left, 2 usage. Standard library only.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ inside the plugin

# Written as escapes so this file itself stays ASCII.
MAP = {
    "\u2014": "-", "\u2013": "-", "\u2012": "-", "\u2212": "-", "\u2010": "-", "\u2011": "-",
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u201c": '"', "\u201d": '"', "\u201e": '"',
    "\u2026": "...", "\u2192": "->", "\u2190": "<-", "\u21d2": "=>", "\u2194": "<->", "\u2713": "[x]", "\u2714": "[x]",
    "\u2705": "[x]", "\u2717": "[ ]", "\u2718": "[ ]", "\u274c": "[ ]", "\u2022": "-", "\u25cf": "-", "\u25e6": "-",
    "\u00b7": "-", "\u2023": "-", "\u00a0": " ", "\u2009": " ", "\u202f": " ", "\u2002": " ", "\u2003": " ",
    "\u00d7": "x", "\u2265": ">=", "\u2264": "<=", "\u2260": "!=", "\u00ab": '"', "\u00bb": '"',
}
DROP = {"\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\u00ad"}


def normalize(text):
    return "".join(MAP.get(ch, ch) for ch in text if ch not in DROP)


def find(text):
    hits = []
    for n, line in enumerate(text.split("\n"), 1):
        for c, ch in enumerate(line, 1):
            if ord(ch) > 127:
                hits.append((n, c, ch))
    return hits


def report(hits, label):
    for n, c, ch in hits[:50]:
        print(f"{label}:{n}:{c}: non-ASCII U+{ord(ch):04X}")
    if len(hits) > 50:
        print(f"... {len(hits) - 50} more")


def main(argv):
    if not argv or argv[0] in ("-h", "--help") or len(argv) > 2 or (len(argv) == 2 and argv[1] != "--fix"):
        print(__doc__)
        return 2
    src = argv[0]
    text = sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8-sig")
    if len(argv) == 2:
        if src == "-":
            print("--fix needs a file")
            return 2
        text = normalize(text)
        Path(src).write_bytes(text.encode("utf-8"))  # write_text(newline=) needs Python 3.10+
    hits = find(text)
    report(hits, src)
    print("ASCII only." if not hits else f"{len(hits)} non-ASCII character(s) left.")
    return 1 if hits else 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
