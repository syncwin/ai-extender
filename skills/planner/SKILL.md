---
name: planner
description: >
  Plans a Claude extension before anything is built: scopes the request (intent, platform target, components,
  install method, naming, acronym) and designs the structure (directory tree, skill boundaries, plugin.json, router
  rule). Use first for any new plugin, skill, connector, agent, MCP server, or add-on; for "turn this workflow or
  conversation into a plugin or skill"; "what components does my extension need"; and any structural decision.
license: MIT
metadata:
  version: 0.6.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Planner

1. **Scope:** `references/scoping.md`. Reuse context; ask only real gaps.
2. **Design:** `references/architecture.md`. Include only confirmed components.
3. **Lean check:** for every planned file or component ask "does the request need this?" Cut the rest; report `skipped: X, add when Y`.
4. **Hand off** to `ai-extender:developer`. Names, acronym, metadata, licensing: `ai-extender/references/standards.md`.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
