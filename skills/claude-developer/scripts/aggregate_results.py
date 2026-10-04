#!/usr/bin/env python3
"""Aggregate eval runs: <iteration>/<eval-id>/{with,baseline}/{grading.json,timing.json}.

Usage: aggregate_results.py <iteration-dir> [--json]
Prints per-config pass rate / tokens / seconds, the delta, and quality flags.
"""
import json, statistics, sys
from pathlib import Path

def load(p):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None

def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__); return 2
    root = Path(argv[0])
    if not root.is_dir():
        print(f"not a directory: {root}"); return 2
    stats, assertion_rows = {}, {}
    for ev in sorted(p for p in root.iterdir() if p.is_dir()):
        for cfg in ("with", "baseline"):
            d = ev / cfg
            g, t = load(d / "grading.json"), load(d / "timing.json")
            if g is None:
                continue
            exps = g.get("expectations", [])
            rate = sum(bool(e.get("passed")) for e in exps) / len(exps) if exps else None
            s = stats.setdefault(cfg, {"rates": [], "tokens": [], "secs": []})
            if rate is not None:
                s["rates"].append(rate)
            if t:
                s["tokens"].append(t.get("total_tokens", 0))
                s["secs"].append(t.get("duration_ms", 0) / 1000)
            for e in exps:
                assertion_rows.setdefault((ev.name, e.get("text", "?")), {})[cfg] = bool(e.get("passed"))
    if not stats:
        print("no grading.json found"); return 1
    def agg(xs):
        return (statistics.mean(xs), statistics.pstdev(xs)) if xs else (None, None)
    out = {}
    for cfg, s in stats.items():
        out[cfg] = {k: agg(v) for k, v in (("pass_rate", s["rates"]), ("tokens", s["tokens"]), ("seconds", s["secs"]))}
    flags = []
    for (ev, text), r in assertion_rows.items():
        if r.get("with") and r.get("baseline"):
            flags.append(f"non-discriminating: {ev}: {text}")
        if r.get("with") is False:
            flags.append(f"FAILS with extension: {ev}: {text}")
    for cfg, s in stats.items():
        sd = out[cfg]["pass_rate"][1]
        if sd and sd > 0.25:
            flags.append(f"high variance in pass rate ({cfg}): sd={sd:.2f}")
    if "--json" in argv:
        print(json.dumps({"stats": out, "flags": flags}, indent=2)); return 0
    print("| Config | Pass rate | Tokens | Seconds |\n|---|---|---|---|")
    for cfg in ("with", "baseline"):
        if cfg in out:
            f = lambda k, p: "n/a" if out[cfg][k][0] is None else f"{out[cfg][k][0]:{p}} ± {out[cfg][k][1]:{p}}"
            print(f"| {cfg} | {f('pass_rate', '.0%')} | {f('tokens', '.0f')} | {f('seconds', '.1f')} |")
    if "with" in out and "baseline" in out and out["with"]["pass_rate"][0] is not None and out["baseline"]["pass_rate"][0] is not None:
        print(f"\nPass-rate delta: {out['with']['pass_rate'][0] - out['baseline']['pass_rate'][0]:+.0%}")
    if flags:
        print("\nFlags:"); [print(f"- {x}") for x in flags]
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
