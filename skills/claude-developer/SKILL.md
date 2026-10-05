---
name: claude-developer
description: >
  Builds the components of a Claude extension: skills, connectors (MCP config), agents, hooks, commands, MCP servers,
  LSP servers, output styles, and add-ons. Use for "make me a skill that formats commit messages", "build the planned skill",
  "add a connector for Notion to this plugin", "make an agent", "write a hook that blocks edits to .env", "build an MCP server",
  "hook this up to X", "extend this plugin", or "test this skill". Drafts SKILL.md, .mcp.json, agent files, and evals.
license: MIT
metadata:
  displayName: "AI Extender Developer"
  version: 1.0.0
  author: "@wasimness"
  company: SyncWin
  plugin: ai-extender
---

# AI Extender Developer

Build only what the plan confirmed. No approved plan in context: hand to `ai-extender:claude-planner` first. Load the one reference for the component:

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
| Testing and description tuning | `references/testing.md` (`scripts/aggregate_results.py`; agents `ai-extender:claude-grader`, `ai-extender:claude-comparator`) |
| Companion prompt (Prompt Builder JSON) | `ai-extender/references/companion-prompt.md`; `../claude-packager/scripts/companion_prompt.py --help` |
| New project skeleton | `scripts/scaffold_extension.py --help` (also writes a default companion prompt) |
| MCP server skeleton (Node/Python) | `scripts/scaffold_mcp_server.py --help` |
| Eval review page | `scripts/eval_report.py --help` |

## Rules

- **Lean first:** least code and text that meets the request; reuse existing tools, connectors, skills. Report `skipped: X, add when Y`.
- Verify field names and limits against `ai-extender/references/claude-platform-facts.md` (refresh via `claude-docs-sync.md` when stale or doubtful).
- Names, acronym, metadata: `ai-extender/references/standards.md`.
- Copy the shared foundation (scratchpad, efficiency ladder, lean build, security; standards §5) into generated extensions when relevant.
- Every skill, agent, and connector you write ends with a scratchpad step.
- Every extension gets its companion prompt: write the fields agreed in the plan as a spec and run `companion_prompt.py <dir> --spec <spec.json>` (the scaffold's default is a starting point, not the finish).
- Run the de-duplication pass (`claude-maintainer/references/versioning.md` Part 1) on each skill written.

Next: `ai-extender:claude-reviewer`. Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
