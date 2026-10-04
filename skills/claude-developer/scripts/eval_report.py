#!/usr/bin/env python3
"""Render a static HTML review page for an eval iteration.

Usage: eval_report.py <iteration-dir> [--out report.html]
Reads <iteration>/<eval-id>/{with,baseline}/{grading.json,timing.json} and any text/markdown output files
in each run dir. Writes a single self-contained HTML file (no network, no dependencies).
"""
import html, json, sys
from pathlib import Path

def load(p):
    try: return json.loads(p.read_text())
    except (OSError, ValueError): return None

def block(run):
    g, t = load(run / "grading.json"), load(run / "timing.json")
    out = []
    if g:
        ex = g.get("expectations", [])
        ok = sum(bool(e.get("passed")) for e in ex)
        out.append(f"<p><b>{ok}/{len(ex)}</b> assertions passed</p><ul>")
        for e in ex:
            out.append(f"<li class='{'p' if e.get('passed') else 'f'}'>{html.escape(str(e.get('text')))}<br><small>{html.escape(str(e.get('evidence','')))}</small></li>")
        out.append("</ul>")
    if t: out.append(f"<p><small>{t.get('total_tokens','?')} tokens · {t.get('duration_ms',0)/1000:.1f}s</small></p>")
    for f in sorted(run.iterdir()):
        if f.is_file() and f.suffix in {".md", ".txt", ".json", ".py", ".html"} and f.name not in {"grading.json", "timing.json"}:
            body = f.read_text(errors="replace")[:6000]
            out.append(f"<details><summary>{html.escape(f.name)}</summary><pre>{html.escape(body)}</pre></details>")
    return "".join(out) or "<p><i>no data</i></p>"

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root = Path(argv[0]); out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else root / "report.html"
    if not root.is_dir(): print(f"not a directory: {root}"); return 2
    rows = []
    for ev in sorted(p for p in root.iterdir() if p.is_dir()):
        cols = "".join(f"<td><h4>{c}</h4>{block(ev / c)}</td>" for c in ("with", "baseline") if (ev / c).is_dir())
        if cols: rows.append(f"<section><h3>{html.escape(ev.name)}</h3><table><tr>{cols}</tr></table></section>")
    doc = ("<!doctype html><meta charset=utf-8><title>Eval report</title><style>body{font:14px system-ui;margin:2rem;max-width:1200px}"
           "table{width:100%;border-collapse:collapse}td{vertical-align:top;width:50%;padding:.5rem;border:1px solid #8884}"
           "li.p{color:#0a7a2f}li.f{color:#b00020}pre{white-space:pre-wrap;background:#8881;padding:.5rem}</style>"
           f"<h1>Eval report: {html.escape(root.name)}</h1>" + ("".join(rows) or "<p>No eval runs found.</p>"))
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out} ({len(rows)} evals)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
