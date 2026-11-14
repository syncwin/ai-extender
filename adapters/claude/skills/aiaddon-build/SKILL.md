---
name: aiaddon-build
description: >
  Use for "make me a skill that formats commit messages", "build the planned skill", "add a connector for Notion to this plugin", "make an agent", "write a hook that blocks edits to .env", "build an MCP server", "hook this up to X", "extend this plugin", or "test this skill". Builds the components of a Claude extension: skills, connectors (MCP config), agents, hooks, commands, MCP servers, LSP servers, output styles, and add-ons. Drafts SKILL.md, .mcp.json, agent files, and evals.
license: MIT
---

# AI Add-on Builder Developer

Build only what the plan confirmed. No approved plan in context: hand to `aiaddon:aiaddon-plan` first. Load the one reference for the component:

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
| Public/private rules, `.gitignore` preset, `PUBLIC-SAFETY.md`, scan | `aiaddon-review/references/public-safety.md` |
| Testing and description tuning | `references/testing.md` (`references/aggregate-results.md`; agents `aiaddon:aiaddon-grade`, `aiaddon:aiaddon-compare`) |
| Companion prompt (Prompt Builder JSON) | `aiaddon/references/companion-prompt.md`; `aiaddon-package/references/companion-prompt.md` (recipe) |
| New project skeleton | `references/scaffold-extension.md` (also writes a default companion prompt) |
| MCP server skeleton (Node/Python) | `references/scaffold-mcp-server.md` |
| Eval review page | `references/eval-report.md` |
| Injection screen (recipe), small local models, Docker | `references/local-models.md`; scaffolder copies the screen-text recipe by default with connectors (`--no-guardrail`) |

## Rules

- **Lean first:** least code and text that meets the request; reuse existing tools, connectors, skills. Report `skipped: X, add when Y`.
- Verify field names and limits against `aiaddon/references/claude-platform-facts.md` (refresh via `claude-docs-sync.md` when stale or doubtful).
- Names, acronym, metadata: `aiaddon/references/standards.md`.
- **Secure by default:** every component follows `aiaddon/references/standards.md` §5c (exec-form commands, quoted `${CLAUDE_PLUGIN_ROOT}`, path containment, fail-closed guards, no secrets); the reference templates already do.
- **Script paths (E9):** every plugin you build tells its skills to copy needed scripts once per session into the working folder (for example `./tools/`) and run them from there; never put a `/root/.claude` or `~/.claude` path in a shell command (`R001` error in the validator).
- Copy the shared foundation (scratchpad, efficiency ladder, lean build, security; standards §5) into generated extensions when relevant.
- **Directory-compliant by default:** no hook files, no shipped scripts, no non-text files, text-only frontmatter; guardrails are recipe steps (copy `aiaddon-review/references/screen-text.md` into the new plugin's `references/` instead of a script). Hooks, scripts and local MCP servers only when the user asks after being told the directory refuses them from non-Verified organizations (they still work for private and GitHub-marketplace installs); offer skill or command instructions, `userConfig` with `sensitive: true`, or a remote MCP over HTTP first (`references/hooks.md`, `references/mcp-servers.md`).
- Every skill, agent, and connector you write ends with a scratchpad step.
- Every extension gets its companion prompt: write the fields agreed in the plan as a spec and follow the recipe `aiaddon-package/references/companion-prompt.md` on the folder (the scaffold's default is a starting point, not the finish).
- Run the de-duplication pass (`aiaddon-maintain/references/versioning.md` Part 1) on each skill written.
- Write the behavior tests with the skills, not after: at least 3 cases per skill a user can call, in `evals/` (`references/testing.md`).
- **Public safety, always:** every scaffold includes the `.gitignore` preset, a `.env.example` with variable names only (no values), a `PUBLIC-SAFETY.md` and, when the author chose a public contact, a `.public-safety-allow` line for it (`references/scaffold-extension.md` writes all of them). Never embed a secret, key, token, personal address, client name, internal URL or local user path in any file, example or test fixture: take values from `userConfig` (`"sensitive": true`) or environment variables, and assemble fake keys in tests at run time. Follow `aiaddon-review/references/scan-secrets.md` and `public-safety-scan.md` on the folder before handing to review; a finding blocks (`aiaddon-review/references/public-safety.md`).
- Apply the naming standard (`aiaddon/references/standards.md` section 1) to every skill, agent and command you write; the scaffolder refuses role-noun names, and the validator fails any slip (`P019` to `P023`).
- Apply the router standard (same file) to any extension with more than one skill: the scaffolder writes the routing table, tie-break rules, default question, loading rule and a starter `evals/router/cases.json`; replace its starter phrases with the real ones from the plan and follow `aiaddon-review/references/route-check.md` until it passes.
- Enforcement and quality bar: `aiaddon/references/standards.md` §5b and §5d.

Next: `aiaddon:aiaddon-review`. Finish with the scratchpad (`aiaddon/references/scratchpad.md`).
