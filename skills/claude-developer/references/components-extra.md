# Other Plugin Components

Verified 2026-10-02 against code.claude.com/docs (plugins/manifest-reference, output-styles). Paths in manifests start `./`, exist, stay inside the root; `claude plugin validate` is authoritative. Strict objects (LSP configs, monitors, channels, `userConfig` options) reject unknown keys and then the plugin does not load.

## LSP servers (code intelligence)

Default file `.lsp.json` (or inline `lspServers` map, or a `.json` path). Server name → config.

| Field | Req | Notes |
|---|---|---|
| `command` | yes | binary; no spaces unless it starts with `/`; arguments go in `args` |
| `extensionToLanguage` | yes | `{".go": "go"}` ≥1 entry, keys start with a dot |
| `args`, `env`, `initializationOptions`, `settings`, `workspaceFolder` | no | |
| `transport` | no | `stdio` (default); `socket` accepted but still runs over stdio, so keep stdout protocol-only |
| `startupTimeout`, `shutdownTimeout` | no | ms, positive ints |
| `restartOnCrash` (default true), `maxRestarts`, `diagnostics` (default true) | no | |

The language server binary must be installed by the user; say so in the README. Env refs resolve in `command`, `args`, `env`, `workspaceFolder`.

## Output styles

`output-styles/*.md` (or `outputStyles` path; replaces the default scan). Frontmatter, all optional: `name`, `description`, `keep-coding-instructions` (true keeps Claude Code's engineering instructions; default false), `force-for-plugin` (plugin-only; auto-applies whenever the plugin is enabled and overrides the user's choice; use sparingly, first loaded wins). Body = the instructions. A style is an instruction, not a guarantee: enforceable behavior → hook; task-specific → skill; project facts → skill (plugin root `CLAUDE.md` is not loaded). Applies to the main conversation and forks, not other subagents. Setting/value `outputStyle` is case-sensitive.

## Monitors (experimental)

`monitors/monitors.json` or `experimental.monitors`: array of `{name, command, description, when}`. `command` runs as a persistent background process in the session cwd; `when`: `"always"` (default) or `"on-skill-invoke:<skill>"`. Interactive sessions only; not on Bedrock/Vertex/Foundry. `${user_config.*}` and `CLAUDE_PLUGIN_OPTION_*` unavailable, the script must fetch its own config. Quote `"${CLAUDE_PLUGIN_ROOT}"` in the command.

## Themes (experimental)

`themes/<slug>.json` (manifest key `experimental.themes` replaces the folder scan; Claude Code v2.1.118+). Same format as a user's `~/.claude/themes/<slug>.json`: `{"name": "Dracula", "base": "dark", "overrides": {"claude": "#bd93f9", "error": "#ff5555"}}`. `name` shows in `/theme`; `base` is the preset inherited from (`dark`, `light`, or another built-in such as `dark-ansi`); `overrides` maps semantic tokens to colors, and a key the base does not define or an invalid color is ignored. Selection is stored as `custom:<slug>`. Plugin themes are read-only (edits save as a user copy). Known gaps reported against 2.1.x: diff color overrides and the startup banner title may ignore overrides. Token names come from the built-in theme object; verify a token by testing it. The validator checks `name`, `base`, and `overrides` types (T002-T004).

## Workflows (dynamic, script-orchestrated subagents)

`workflows/<name>.js` (manifest key `workflows`). Runs as `/<plugin>:<meta.name>`. Format:
```js
export const meta = { name: 'audit-routes', description: 'Audit every route handler for missing auth checks' }
const found = await agent('List every .ts file under src/routes/.', { schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } } })
const audits = await pipeline(found.files, f => agent(`Audit ${f} for missing authentication checks.`, { label: f }))
return audits.filter(Boolean)
```
- `meta` first statement, plain object literal with `name` and `description` (anything non-literal drops it from autocomplete).
- Body: plain JavaScript with top-level `await`; globals `agent()`, `pipeline()`, `parallel()`, `phase()`, `log()`, `args`. `agent()` can return `null` (stopped/failed): filter it.
- **No `import()` / module loading** (fails before the run), no direct filesystem or shell from the script (agents do that), no mid-run user input. `Date.now()`, `Math.random()`, and no-arg `new Date()` throw (pass time in via `args`).
- Limits: 16 concurrent agents by default, 4,096 items per `parallel()`/`pipeline()`, 1,000 agents per run.
- Use a workflow only when the task needs many agents or a repeatable orchestration; otherwise a skill or agent is cheaper. Costs scale with agents; test on a small slice first.

## Mods (hooks written as JavaScript)

A `modules` key in `hooks/hooks.json` (one path) makes a plugin a mod: a JavaScript or TypeScript module that Claude Code loads once per session and that can hook events, add commands and tools, and draw in the interface. Claude Code and Desktop only. Full reference: `mods.md`.

## Executables: `bin/`

Files in `bin/` are on the Bash tool's PATH while the plugin is enabled. **claude.ai and Cowork refuse to install a plugin containing `bin/`**; the validator errors for `--target cowork`. Alternative that works everywhere: ship scripts in `scripts/` and call them via `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PLUGIN_ROOT}`.

## Plugin `settings.json`

Plugin-root `settings.json` (or manifest `settings`): only `agent` and `subagentStatusLine` take effect; everything else is dropped. The file wins over the manifest key. Use `agent` to make a plugin agent the default main thread.

## Channels

`channels: [{server, displayName?, userConfig?}]` binds a message channel (chat bridge) to one of the plugin's MCP servers (`server` = key in `mcpServers`). Its `userConfig` values substitute into the server's `env` via `${user_config.KEY}`. Build the MCP server per `mcp-servers.md`.

## Dependencies and defaults

`dependencies`: `"name"`, `"name@marketplace"`, or `{name, marketplace, version}`. `defaultEnabled` (default true; marketplace entry overrides; an existing user's setting persists across updates). `strict` (marketplace entry): default true; with `strict:false` an entry that also declares components conflicts with the manifest and the plugin fails to load.

## Surface support (where each component loads)

| Component | Chat (claude.ai) | Cowork | Claude Code |
|---|---|---|---|
| Skills | yes | yes | yes |
| Commands | as a skill | yes, run as `/plugin:command` | yes |
| Agents, hooks | ignored | yes | yes |
| Remote MCP (`http`/`sse`, fixed URL) | listed on the plugin's Connectors tab | yes | yes |
| Local MCP / `.mcpb` | ignored | only when the Cowork session runs on the user's computer | yes |
| MCP using `${user_config.*}` | ignored if in the URL | ignored when an option has no default (no prompt) | yes, prompts |
| `bin/` | can't be installed | can't be installed | yes |
| LSP, output styles, themes, `settings` | ignored | ignored | yes |

Limits when adding a plugin yourself on claude.ai/Cowork: ≤25 marketplaces per account, ≤5,000 files and 200 MB per plugin, and "Upload plugin" takes a zip of the folder. Choose components for the weakest target the user named.
