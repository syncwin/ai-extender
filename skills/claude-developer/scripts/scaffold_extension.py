#!/usr/bin/env python3
"""Scaffold a lean Claude plugin: only the components you ask for.

Usage: scaffold_extension.py <out-dir> --slug my-thing --display "My Thing"
         [--description "..."] [--author "@name"] [--company "Co"] [--email a@b.c] [--url https://..]
         [--license MIT] [--roles planner,developer] [--prefix acronym|none] [--agents] [--hooks] [--connectors]
Creates <out-dir>/<slug>/ with: plugin.json (version 0.0.1), router skill named <slug>, one stub skill per
--roles entry (<prefix>-<role>, or bare <role> without --prefix), scratchpad reference, README, CHANGELOG, LICENSE (MIT), .gitignore,
and the Prompt Builder companion prompt (prompts/<title-slug>.json, via claude-packager/scripts/companion_prompt.py).
Metadata on the manifest and every skill: displayName, version, and author/company when given.
Optional empty-but-valid: agents/ (--agents), hooks/hooks.json (--hooks), .mcp.json (--connectors).
Stubs contain real structure and a scratchpad step: fill the bodies, then run the validator.
"""
import json, re, subprocess, sys
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

def frontmatter(name, desc, a, display):
    meta = ["  version: 0.0.1", f'  displayName: "{display}"'] + ([f'  author: "{a["author"]}"'] if a["author"] else []) + ([f'  company: {a["company"]}'] if a["company"] else [])
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
    prefix = a["prefix"] if a["prefix"] not in ("", "none") else ""
    nm = lambda r: f"{prefix}-{r}" if prefix else r
    root = out / a["slug"]
    if root.exists(): print(f"exists: {root}"); return 1
    desc = a["description"] or f"{a['display']}."
    (root / ".claude-plugin").mkdir(parents=True)
    author = {k: v for k, v in (("name", a["author"] or a["company"]), ("email", a["email"]), ("url", a["url"])) if v}
    manifest = {"name": a["slug"], "displayName": a["display"], "version": "0.0.1", "description": desc, "license": a["license"]}
    if author: manifest["author"] = author
    if a["company"] and author: manifest["author"]["company"] = a["company"]
    manifest["metadata"] = {k: v for k, v in (("displayName", a["display"]), ("version", "0.0.1"), ("author", a["author"]), ("company", a["company"])) if v}
    (root / ".claude-plugin" / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n")
    rtable = "\n".join(f"| `{nm(r)}` | {r.title()} |" for r in roles) or "| (none yet) | |"
    titles = {a["slug"]: a["display"], **{nm(r): f"{a['display']} {r.title()}" for r in roles}}
    skills = {a["slug"]: (f"{desc} Entry point and router: use whenever the user asks for anything this plugin covers. Routes to the skill that owns the task.",
              f"# {a['display']}\n\nRouter only. Detect context, pick the skill, hand off.\n\n| Task | Skill |\n|---|---|\n" + "\n".join(f"| {r} | `{nm(r)}` |" for r in roles) + "\n\nFinish with the scratchpad (`references/scratchpad.md`).\n")}
    for r in roles:
        skills[nm(r)] = (f"{r.title()} role for {a['display']}. Use when the task needs the {r} stage.",
              f"# {a['display']} {r.title()}\n\nSteps for the {r} role go here as numbered rules.\n\nFinish with the scratchpad (`{a['slug']}/references/scratchpad.md`).\n")
    for n, (d, body) in skills.items():
        p = root / "skills" / n; p.mkdir(parents=True)
        (p / "SKILL.md").write_text(frontmatter(n, d, a, titles[n]) + body)
    (root / "skills" / a["slug"] / "references").mkdir(exist_ok=True)
    (root / "skills" / a["slug"] / "references" / "scratchpad.md").write_text(SCRATCH)
    if a["agents"]: (root / "agents").mkdir(); (root / "agents" / ".gitkeep").write_text("")
    if a["hooks"]: (root / "hooks").mkdir(); (root / "hooks" / "hooks.json").write_text('{\n  "hooks": {}\n}\n')
    if a["connectors"]: (root / ".mcp.json").write_text('{\n  "mcpServers": {}\n}\n')
    contact = f" · **Contact** {a['email']}" if a["email"] else ""
    who = " · ".join(x for x in (f"**Author** {a['author']}" if a["author"] else "", f"**Company** {a['company']}" if a["company"] else "") if x)
    slug_t = re.sub(r"[^a-z0-9]+", "-", a["display"].lower()).strip("-")
    (root / "README.md").write_text(f"# {a['display']}\n\n{desc}\n\n**Version** 0.0.1 · {who}{contact} · **License** {a['license']}\n\n"
        f"## Skills\n\n| Skill | Role |\n|---|---|\n| `{a['slug']}` | Router |\n{rtable}\n\n"
        f"## Install\n\nCowork or claude.ai: upload the `.plugin` file as a custom plugin. Claude Code: add the marketplace or folder that holds this plugin, then install `{a['slug']}`. Start it with `/{a['slug']}` and describe what you need.\n\n"
        f"## Companion prompt\n\n`prompts/{slug_t}.json` is a ready-made form for Prompt Builder. Import it there, fill in the fields, and send it to Claude to start this plugin without typing the request from scratch.\n\n"
        f"## What it runs, reads, and sends\n\nList every script, connector, and outside service here before you share this plugin.\n")
    (root / "CHANGELOG.md").write_text(f"# Changelog\n\nNewest first.\n\n## 0.0.1: {date.today().isoformat()}\n\n**Added**\n- Initial structure.\n")
    (root / "LICENSE").write_text(MIT.format(year=date.today().year, holder=a["author"] or a["company"] or a["display"]) if a["license"] == "MIT" else f"License: {a['license']}\n")
    (root / ".gitignore").write_text(".DS_Store\n*.plugin\n*.zip\n.env\ndist/\n")
    cp = Path(__file__).resolve().parents[2] / "claude-packager" / "scripts" / "companion_prompt.py"
    prompt = "not created (companion_prompt.py not found)"
    if cp.exists():
        r = subprocess.run([sys.executable, str(cp), str(root)], capture_output=True, text=True)
        prompt = "prompts/ (default; edit the form fields to match the skills)" if r.returncode == 0 else "FAILED: " + r.stdout[-300:]
    print(f"### Scratchpad — Scaffold\n**Scope:** {a['slug']}\n\n| Item | Result |\n|---|---|\n| Path | `{root}` |\n| Skills | {', '.join(skills)} |\n| Extras | {', '.join(k for k in ('agents','hooks','connectors') if a[k]) or 'none'} |\n| Companion prompt | {prompt} |\n\n**Next:** fill skill bodies, then run the validator.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
