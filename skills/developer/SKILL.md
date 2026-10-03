---
name: developer
description: >
  Builds the components of a Claude extension: skills, connectors (MCP config), agents, hooks, commands, MCP servers,
  LSP servers, output styles, and add-ons. Use for "make me a skill that formats commit messages", "write a skill",
  "add a connector for Notion", "make an agent", "write a hook that blocks edits to .env", "build an MCP server",
  "hook this up to X", "extend this plugin", or "test this skill". Drafts SKILL.md, .mcp.json, agent files, and evals.
license: MIT
metadata:
  version: 0.6.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Developer

Build only what the plan confirmed. Load the one reference for the component:

| Component | Reference |
|---|---|
| Skill | `references/skills.md` |
| Connector / `.mcp.json` | `references/connectors.md` |
| Custom MCP server | `references/mcp-servers.md` |
| Agent | `references/agents.md` |
| Hook | `references/hooks.md` |
| Command (legacy) | `references/commands.md` |
| Add-on for another extension | `references/addons.md` |
| LSP, output styles, monitors, themes, workflows, `bin/`, plugin settings, channels | `references/components-extra.md` |
| Mods (JavaScript hooks module) | `references/mods.md` |
| Local MCP bundle (`.mcpb`) | `references/mcpb-bundles.md` |
| Skills outside plugins (`.claude/skills`, claude.ai, API) and their limits | `references/upload-and-api.md` |
| Testing and description tuning | `references/testing.md` (`scripts/aggregate_results.py`; agents `ai-extender:grader`, `ai-extender:comparator`) |
| New project skeleton | `scripts/scaffold_extension.py --help` |
| MCP server skeleton (Node/Python) | `scripts/scaffold_mcp_server.py --help` |
| Eval review page | `scripts/eval_report.py --help` |

## Rules

- **Lean first:** least code and text that meets the request; reuse existing tools, connectors, skills. Report `skipped: X, add when Y`.
- Verify field names and limits against `ai-extender/references/platform-facts.md` (refresh via `docs-sync.md` when stale or doubtful).
- Names, acronym, metadata: `ai-extender/references/standards.md`.
- Copy the shared foundation (scratchpad, efficiency ladder, lean build, security; standards §5) into generated extensions when relevant.
- Every skill, agent, and connector you write ends with a scratchpad step.
- Run the de-duplication pass (`maintainer/references/versioning.md` Part 1) on each skill written.

Next: `ai-extender:reviewer`. Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
