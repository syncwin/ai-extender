#!/usr/bin/env python3
"""Scaffold a lean Claude plugin: only the components you ask for.

Usage: scaffold_extension.py <out-dir> --slug claude-my-thing --display "My Thing"
         [--description "..."] [--author "@name"] [--company "Co"] [--email a@b.c] [--url https://..]
         [--license MIT] [--roles planner,developer] [--prefix claude] [--agents] [--hooks] [--connectors]
Creates <out-dir>/<slug>/ with: plugin.json (version 0.0.1), router skill named <slug>, one stub skill per
--roles entry (<prefix>-<role>), scratchpad reference, README, CHANGELOG, LICENSE (MIT), .gitignore.
Optional empty-but-valid: agents/ (--agents), hooks/hooks.json (--hooks), .mcp.json (--connectors).
Stubs contain real structure and a scratchpad step: fill the bodies, then run the validator.
"""
import json, re, sys
from datetime import date
from pathlib import Path

SCRATCH = """# Scratchpad Format

Every skill, connector, and agent ends its task with one. Standalone: emit at the end. Chained: each stage adds rows to one running scratchpad, emitted once at the end.

```
### Scratchpad — <Visible Name> v<version>
**Scope:** <what was run>

| Area | Result |
|---|---|
| <thing built/checked/changed> | <done / pass / fail + one clause> |

**Changed:** <files or components, one line each>
**Flags:** <failures, assumptions, open items; omit if none>
**Next:** <single next action; omit if none>
```

Facts only. Omit inapplicable sections. Successes in one line; detail only for failures.
"""
MIT = """MIT License

Copyright (c) {year} {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

def frontmatter(name, desc, a):
    meta = ["  version: 0.0.1"] + ([f'  author: "{a["author"]}"'] if a["author"] else []) + ([f'  company: {a["company"]}'] if a["company"] else [])
    return f"---\nname: {name}\ndescription: >\n  {desc}\nlicense: {a['license']}\nmetadata:\n" + "\n".join(meta) + "\n---\n\n"

def main(argv):
    a = {"slug": None, "display": None, "description": "", "author": "", "company": "", "email": "", "url": "", "license": "MIT",
         "roles": [], "prefix": "", "agents": False, "hooks": False, "connectors": False}
    out, i = None, 0
    while i < len(argv):
        x = argv[i]
        if x in ("--agents", "--hooks", "--connectors"): a[x[2:]] = True
        elif x.startswith("--") and x[2:] in a: a[x[2:]] = argv[i+1]; i += 1
        elif not x.startswith("-") and out is None: out = Path(x)
        else: print(__doc__); return 2
        i += 1
    if not (out and a["slug"] and a["display"]) or not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", a["slug"]): print(__doc__); return 2
    roles = [r for r in (a["roles"].split(",") if a["roles"] else []) if r]
    prefix = a["prefix"] or a["slug"].split("-")[0]
    root = out / a["slug"]
    if root.exists(): print(f"exists: {root}"); return 1
    desc = a["description"] or f"{a['display']}."
    (root / ".claude-plugin").mkdir(parents=True)
    author = {k: v for k, v in (("name", a["author"]), ("email", a["email"]), ("url", a["url"])) if v}
    manifest = {"name": a["slug"], "displayName": a["display"], "version": "0.0.1", "description": desc, "author": author or {"name": "unknown"}, "license": a["license"]}
    if a["company"]: manifest["metadata"] = {"company": a["company"]}
    if a["company"]: manifest["author"]["company"] = a["company"]
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    rtable = "\n".join(f"| `{prefix}-{r}` | {r.title()} |" for r in roles) or "| (none yet) | |"
    skills = {a["slug"]: (f"{desc} Entry point and router: use whenever the user asks for anything this plugin covers. Routes to the skill that owns the task.",
              f"# {a['display']}\n\nRouter only. Detect context, pick the skill, hand off.\n\n| Task | Skill |\n|---|---|\n" + "\n".join(f"| {r} | `{prefix}-{r}` |" for r in roles) + "\n\nFinish with the scratchpad (`references/scratchpad.md`).\n")}
    for r in roles:
        skills[f"{prefix}-{r}"] = (f"{r.title()} role for {a['display']}. Use when the task needs the {r} stage.",
              f"# {a['display']} {r.title()}\n\nSteps for the {r} role go here as numbered rules.\n\nFinish with the scratchpad (`{a['slug']}/references/scratchpad.md`).\n")
    for n, (d, body) in skills.items():
        p = root / "skills" / n; p.mkdir(parents=True)
        (p / "SKILL.md").write_text(frontmatter(n, d, a) + body)
    (root / "skills" / a["slug"] / "references").mkdir(exist_ok=True)
    (root / "skills" / a["slug"] / "references" / "scratchpad.md").write_text(SCRATCH)
    if a["agents"]: (root / "agents").mkdir(); (root / "agents" / ".gitkeep").write_text("")
    if a["hooks"]: (root / "hooks").mkdir(); (root / "hooks" / "hooks.json").write_text('{\n  "hooks": {}\n}\n')
    if a["connectors"]: (root / ".mcp.json").write_text('{\n  "mcpServers": {}\n}\n')
    contact = f" · **Contact** {a['email']}" if a["email"] else ""
    who = " · ".join(x for x in (f"**Author** {a['author']}" if a["author"] else "", f"**Company** {a['company']}" if a["company"] else "") if x)
    (root / "README.md").write_text(f"# {a['display']}\n\n{desc}\n\n**Version** 0.0.1 · {who}{contact} · **License** {a['license']}\n\n## Skills\n\n| Skill | Role |\n|---|---|\n| `{a['slug']}` | Router |\n{rtable}\n")
    (root / "CHANGELOG.md").write_text(f"# Changelog\n\nNewest first.\n\n## 0.0.1 — {date.today().isoformat()}\n\n**Added**\n- Initial structure.\n")
    (root / "LICENSE").write_text(MIT.format(year=date.today().year, holder=a["author"] or a["company"] or a["display"]) if a["license"] == "MIT" else f"License: {a['license']}\n")
    (root / ".gitignore").write_text(".DS_Store\n*.plugin\n*.zip\n.env\ndist/\n")
    print(f"### Scratchpad — Scaffold\n**Scope:** {a['slug']}\n\n| Item | Result |\n|---|---|\n| Path | `{root}` |\n| Skills | {', '.join(skills)} |\n| Extras | {', '.join(k for k in ('agents','hooks','connectors') if a[k]) or 'none'} |\n\n**Next:** fill skill bodies, then run the validator.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
