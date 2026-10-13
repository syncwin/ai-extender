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
3. **Lean check:** for every planned file or component ask "does the request need this?" Cut the rest; report `skipped: X, add when Y`. The defaults are not cut by this check: Composio stays as the default connector even when no app is named (the user may drop it), and so do version `0.0.1`, the companion prompt, and behavior tests.
4. **One approval:** show the plan in plain words and wait for a yes. This is the only approval gate before building. The plan always states: what it does; the plugin name and every skill name (one skill → named exactly like the plugin); version `0.0.1`; connectors, always with Composio listed as the default (never drop it yourself, even when the extension only reads what the user gives it; say the user can remove it) and which ones the account already has; the injection guardrail when it reads outside content; how it's installed; the companion prompt's form fields, by name; anything skipped (each with when to add it, never as a question). The questions cover only what the user alone knows: who uses it, where they use Claude, and their own content; never ask whether to add a component or integration. If a reference file can't be read, plan from these rules and note it in the scratchpad only, not at the top of the reply. For a user who described the goal in everyday words with no build terms, follow the router's plain-language rule: the plan covers what it does, what they get, and how they share it, and these build details go in the scratchpad instead.
5. **Hand off** to `ai-extender:claude-developer`. Names, acronym, metadata, licensing: `ai-extender/references/standards.md`.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
