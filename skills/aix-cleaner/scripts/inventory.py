#!/usr/bin/env python3
"""Script-only inventory and overlap map for plugins and skills. No LLM, stdlib only, Python 3.9+.

Usage: inventory.py <dir> [--out report.json] [--min-words 12] [--threshold 0.6] [--ext .md,.json,.py,.yaml,.yml,.txt]
Writes JSON: files (path, bytes, lines, headings, unique normalized line hashes), exact duplicate
paragraphs, near-duplicate paragraphs (5-word shingles, Jaccard), shared headings, totals.
Read-only. Exit 0 ok, 2 usage. Run with: python -B inventory.py ...
"""
import hashlib, json, re, sys
sys.dont_write_bytecode = True
from pathlib import Path

SKIP = {".git", "__pycache__", "node_modules", ".venv", "archive"}
DEFAULT_EXT = (".md", ".json", ".py", ".yaml", ".yml", ".txt")


def norm(line):
    """Normalize one line: lowercase, no list or heading markers, collapsed whitespace."""
    t = re.sub(r"^\s*(?:[#>*+-]+|\d+[.)])\s+", "", line.strip().lower())
    return re.sub(r"\s+", " ", t).strip()


def trivial(t):
    return len(t) < 3 or not re.search(r"[a-z0-9]", t)


def h(t):
    return hashlib.sha1(t.encode("utf-8")).hexdigest()[:12]


def text_files(root, exts, skip=SKIP):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in exts and not (set(p.relative_to(root).parts) & skip):
            yield p


def read(p):
    try:
        return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    except (OSError, UnicodeDecodeError):
        return None


def paragraphs(text):
    out, cur, start = [], [], 1
    for no, ln in enumerate(text.split("\n"), 1):
        if ln.strip():
            if not cur:
                start = no
            cur.append(ln)
        elif cur:
            out.append((start, " ".join(norm(x) for x in cur)))
            cur = []
    if cur:
        out.append((start, " ".join(norm(x) for x in cur)))
    return out


def shingles(words, k=5):
    return {" ".join(words[i:i + k]) for i in range(max(1, len(words) - k + 1))}


def build(root, exts, min_words, threshold):
    files, paras, headings, line_owner = [], [], {}, {}
    for p in text_files(root, exts):
        t = read(p)
        if t is None:
            continue
        rel = p.relative_to(root).as_posix()
        hs = [ln.strip() for ln in t.split("\n") if re.match(r"^#{1,6}\s", ln)]
        for x in hs:
            headings.setdefault(norm(x), []).append(rel)
        hashes = []
        for ln in t.split("\n"):
            n = norm(ln)
            if not trivial(n):
                k = h(n)
                hashes.append(k)
                line_owner.setdefault(k, set()).add(rel)
        files.append({"path": rel, "bytes": len(t.encode("utf-8")), "lines": t.count("\n") + 1, "headings": hs, "line_hashes": sorted(set(hashes))})
        if p.suffix.lower() == ".md":
            for start, txt in paragraphs(t):
                if len(txt.split()) >= min_words:
                    paras.append((rel, start, txt))
    exact = {}
    for rel, start, txt in paras:
        exact.setdefault(h(txt), []).append({"file": rel, "line": start, "text": txt[:160]})
    exact_dups = [{"hash": k, "locations": v} for k, v in exact.items() if len(v) > 1]
    sets = [shingles(txt.split()) for _, _, txt in paras]
    index = {}
    for i, s in enumerate(sets):
        for sh in s:
            index.setdefault(sh, []).append(i)
    near = []
    for i, s in enumerate(sets):
        cand = set()
        for sh in s:
            ids = index[sh]
            if len(ids) <= 50:
                cand.update(j for j in ids if j > i)
        for j in cand:
            if h(paras[i][2]) == h(paras[j][2]):
                continue
            jac = len(s & sets[j]) / float(len(s | sets[j]))
            if jac >= threshold:
                near.append({"jaccard": round(jac, 3),
                             "a": {"file": paras[i][0], "line": paras[i][1], "text": paras[i][2][:160]},
                             "b": {"file": paras[j][0], "line": paras[j][1], "text": paras[j][2][:160]}})
    near.sort(key=lambda d: -d["jaccard"])
    shared = [{"heading": k, "files": sorted(set(v))} for k, v in sorted(headings.items()) if len(set(v)) > 1]
    dup_lines = sum(1 for v in line_owner.values() if len(v) > 1)
    return {"root": str(root), "tool": "aix-cleaner inventory", "files": files,
            "exact_duplicate_paragraphs": exact_dups, "near_duplicate_paragraphs": near, "shared_headings": shared,
            "totals": {"files": len(files), "bytes": sum(f["bytes"] for f in files), "unique_lines": len(line_owner),
                       "lines_in_several_files": dup_lines, "exact_duplicate_paragraphs": len(exact_dups),
                       "near_duplicate_paragraphs": len(near)}}


def main(argv):
    opts = {"--out": None, "--min-words": "12", "--threshold": "0.6", "--ext": ",".join(DEFAULT_EXT)}
    args, i = [], 0
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        elif argv[i].startswith("-"):
            print(__doc__)
            return 2
        else:
            args.append(argv[i])
            i += 1
    if len(args) != 1 or not Path(args[0]).is_dir():
        print(__doc__)
        return 2
    exts = tuple(e if e.startswith(".") else "." + e for e in opts["--ext"].lower().split(",") if e)
    rep = build(Path(args[0]).resolve(), exts, int(opts["--min-words"]), float(opts["--threshold"]))
    out = json.dumps(rep, indent=1)
    if opts["--out"]:
        Path(opts["--out"]).write_text(out, encoding="utf-8")
    t = rep["totals"]
    print(f"inventory: {t['files']} files, {t['unique_lines']} unique lines, {t['exact_duplicate_paragraphs']} exact and "
          f"{t['near_duplicate_paragraphs']} near duplicate paragraphs" + (f"; report {opts['--out']}" if opts["--out"] else ""))
    if not opts["--out"]:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
