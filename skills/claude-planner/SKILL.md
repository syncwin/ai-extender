---
name: claude-planner
description: >
  Plans a Claude extension before anything is built: scopes the request (intent, platform target, components,
  install method, naming, acronym) and designs the structure (directory tree, skill boundaries, plugin.json, router
  rule). Use, after the router, for any new plugin, skill, connector, agent, MCP server, or add-on; for internal tools for a team or
  business process; for "turn this workflow into a Claude plugin", "turn this conversation into a plugin or skill"; "what components does my
  extension need"; and any structural decision.
license: MIT
metadata:
  displayName: "AI Extender Planner"
  version: 1.0.0
  author: "@wasimness"
  company: SyncWin
  plugin: ai-extender
---

# AI Extender Planner

1. **Scope:** `references/scoping.md`. Reuse context; ask only real gaps.
2. **Design:** `references/architecture.md`. Include only confirmed components.
3. **Lean check:** for every planned file or component ask "does the request need this?" Cut the rest; report `skipped: X, add when Y`.
4. **One approval:** show the plan in plain words and wait for a yes. This is the only approval gate before building. The plan always states: what it does; the plugin name and every skill name (one skill → named exactly like the plugin); version `0.0.1`; connectors, with Composio listed as the default and which ones the account already has; how it's installed; the companion prompt's form fields; anything skipped.
5. **Hand off** to `ai-extender:claude-developer`. Names, acronym, metadata, licensing: `ai-extender/references/standards.md`.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
