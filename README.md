# AI Extender for Claude

Builds and maintains Claude extensions end to end: plugins, skills, connectors, agents, hooks, MCP servers, and add-ons. Self-contained: scoping, building, testing, validation, packaging, and updates, with no dependency on other skills or plugins.

**Version** 0.6.0 · **Author** @wasimness · **Company** SyncWin · **Contact** support@syncwin.com · **License** MIT

## Install

```
claude plugin marketplace add syncwin/ai-extender
claude plugin install ai-extender@syncwin
```

Cowork or claude.ai: upload `AI Extender for Claude v0.6.0.plugin` (zip of this repo). Then say what you want, for example: "build me a plugin that turns meeting notes into action items", "add a Notion connector to my plugin", "audit my plugin before I ship it", "bump the version and package it for Cowork".

## Skills

Entry: `/ai-extender` (router; slug = plugin slug). Role skills are bare roles because Claude Code already namespaces them (`/ai-extender:planner`); "Claude" appears only in the display name. Renamed from `ai-extension-architect` in 0.5.0; role skills became bare roles in 0.6.0 (was `ai-extender-<role>`).

| Skill | Role | Scripts |
|---|---|---|
| `ai-extender:planner` | Scope and design | none |
| `ai-extender:developer` | Build skills, connectors, MCP servers/bundles, agents, hooks, LSP, output styles, add-ons; test | `scaffold_extension.py`, `scaffold_mcp_server.py`, `aggregate_results.py`, `eval_report.py` |
| `ai-extender:maintainer` | Update existing extensions; versioning, changelogs | none |
| `ai-extender:reviewer` | Validate and audit | `validate_extension.py`, `simulate.py`, `selftest.py` |
| `ai-extender:packager` | Package and deliver (`.plugin`, `.zip`, private marketplace) | `package_extension.py` |

Agents: `ai-extender:grader`, `ai-extender:comparator` (eval grading and blind comparison).

Shared (in the router): `references/standards.md`, `scratchpad.md`, `platform-facts.md` (verified against the official docs, last refresh 2026-10-03), `docs-sync.md`. Scripts need only Python 3.

## Coverage (0.6.0)

| Area | Status |
|---|---|
| Plugins: manifest, `userConfig`, layout, path rules, dependencies, private marketplaces, versioning, renames, tags | Covered, docs-verified 2026-10-02 |
| Skills (portable and Claude-Code-only), agents, hooks, connectors, commands, add-ons, updates | Covered, docs-verified |
| LSP, output styles, themes, workflows, monitors, channels, `bin/`, plugin `settings`, mods | Covered, docs-verified 2026-10-02/03 (`developer/references/components-extra.md`, `mods.md`) |
| Surface support (Chat / Cowork / Claude Code) | Covered, with limits |
| Custom MCP servers, `.mcpb` bundles | Guidance + Node/Python scaffold |
| Skills outside plugins: `.claude/skills`, claude.ai upload, API, Agent SDK | Covered |
| Distribution: no marketplace, own marketplace, Anthropic directory (checklist and submission steps), organization policy keys | Covered, docs-verified 2026-10-03 |
| Testing: official `claude plugin eval` layout, manual loop, aggregator, HTML report, grader/comparator agents, trigger simulator | Covered; official evals not yet run by a human |
| Validator: manifest, skills, agents, hooks, mods, MCP, workflows, themes, monitors, LSP, evals, and `--target directory` pre-submission checks; 50-check `selftest.py` | Passing |
| GitHub | Live: `syncwin/ai-extender`; push, tag, and orphan-cleanup procedure in `packager/references/github.md` |
| Live behavior in Claude Code / Cowork | Install confirmed by the user; run `claude plugin eval .` to measure |

## Connectors

None required. Generated extensions document theirs.

See `CREDITS.md`.
