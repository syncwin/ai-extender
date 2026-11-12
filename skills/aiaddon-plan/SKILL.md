---
name: aiaddon-plan
description: >
  Use, after the router, for any new plugin, skill, connector, agent, MCP server, or add-on; for internal tools for a team or business process; for "turn this workflow into a Claude plugin", "turn this conversation into a plugin or skill"; "what components does my extension need"; and any structural decision. Plans a Claude extension before anything is built: scopes the request (intent, platform target, components, install method, naming, acronym) and designs the structure (directory tree, skill boundaries, plugin.json, router rule).
license: MIT
---

# AI Add-on Builder Planner

1. **Scope:** `references/scoping.md`. Reuse context; ask only real gaps.
2. **Design:** `references/architecture.md`. Include only confirmed components.
3. **Lean check:** for every planned file or component ask "does the request need this?" Cut the rest; report `skipped: X, add when Y`. The defaults are not cut by this check: Composio stays as the default connector even when no app is named (the user may drop it), and so do version `0.0.1`, the companion prompt, and behavior tests.
4. **Threat model (3 lines, in the plan):** what the extension can touch (files, commands, network, accounts), what untrusted text it reads, and the worst a bad input could do. Design from `aiaddon/references/standards.md` §5c; a hook that guards is fail-closed, one that only nags is fail-open.
4a. **Public/private split + threat model line (in every plan):** state what ships public (source, docs, generic examples) and what stays private (secrets, personal data, client names and data, internal URLs and hosts, local absolute user paths, private notes, logs, memory and progress files) and where each private value lives instead (`userConfig` with `sensitive: true`, or an environment variable listed in `.env.example`); then one threat model line naming what could leak and what stops it (the required `.gitignore` preset, `PUBLIC-SAFETY.md`, the scan in the validator and CI). Plan it even when the user never mentions publishing: `aiaddon-review/references/public-safety.md`.
4b. **Names (naming standard, `aiaddon/references/standards.md` section 1):** in the plan, the router is named exactly like the plugin, every other skill, agent and command is `<plugin>-<action>`, and no slug ends in a role noun; list every slug.
4c. **Router (router standard, same file):** for more than one skill the plan includes the routing table (phrases to exact slugs), the tie-break rules and the one closed default question; for one skill, none.
5. **One approval:** show the plan in plain words and wait for a yes. This is the only approval gate before building. The plan always states: what it does; the plugin name and every skill name (one skill → named exactly like the plugin); version `0.0.1`; connectors, always with Composio listed as the default (never drop it yourself, even when the extension only reads what the user gives it; say the user can remove it) and which ones the account already has; the injection guardrail when it reads outside content; how it's installed; the companion prompt's form fields, by name; anything skipped (each with when to add it, never as a question). The questions cover only what the user alone knows: who uses it, where they use Claude, and their own content; never ask whether to add a component or integration. If a reference file can't be read, plan from these rules and note it in the scratchpad only, not at the top of the reply. For a user who described the goal in everyday words with no build terms, follow the router's plain-language rule: the plan covers what it does, what they get, and how they share it, and these build details go in the scratchpad instead.
6. **Hand off** to `aiaddon:aiaddon-build`. Names, acronym, metadata, licensing: `aiaddon/references/standards.md`.

Finish with the scratchpad (`aiaddon/references/scratchpad.md`).
