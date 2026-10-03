# MCP Bundles (`.mcpb`) for Local Servers

Verified against github.com/anthropics/mcpb (manifest spec 0.3; `uv` type needs 0.4) on 2026-10-01. `.dxt` is the old name. A bundle is a zip: your local MCP server + `manifest.json`, installable by one click in Claude for macOS/Windows. A plugin can reference one in `mcpServers` (path or https URL ending `.mcpb`/`.dxt`; extracted to `.mcpb-cache/`).

## Layout

`manifest.json` (only required file), `server/` (entry + code), bundled deps (`node_modules/`, `server/lib/`), optional `icon.png`, `.mcpbignore`. Prefer **Node.js**: it ships with Claude Desktop, so no runtime install. Python: `type: "uv"` (deps in `pyproject.toml`, no bundled `lib/` or `venv/`) beats bundling compiled packages.

## manifest.json

| Field | Notes |
|---|---|
| `manifest_version`, `name`, `version`, `description`, `author{name}`, `server` | required |
| `server.type` | `node` · `python` · `binary` · `uv` |
| `server.entry_point`, `server.mcp_config` | `{command, args, env, platform_overrides}`; `${__dirname}` = bundle dir; `${HOME}`, `${DESKTOP}`, `${DOCUMENTS}`, `${DOWNLOADS}`, `${/}` |
| `user_config` | `{KEY:{type string|number|boolean|directory|file, title, description, required, default, multiple, sensitive, min, max}}`; reference as `${user_config.KEY}`; arrays expand to separate args |
| `display_name`, `long_description`, `icon(s)`, `screenshots`, `homepage`, `documentation`, `support`, `repository`, `keywords`, `license` | optional |
| `tools`, `prompts`, `tools_generated`, `prompts_generated` | declare what the server provides |
| `privacy_policies` | **required when the bundle talks to external services that process user data** |
| `compatibility` | `{claude_desktop, platforms[darwin|win32|linux], runtimes{node,python}}` |

Secrets: `sensitive: true` in `user_config`, passed via `env`; never in files.

## Build and test

`npm install -g @anthropic-ai/mcpb` → `mcpb init` → `mcpb pack` → open the `.mcpb` in Claude Desktop. Implement over stdio with the official MCP SDK; stdout is protocol-only. Test on a clean machine without dev tools. Filename per standards: `<Display Name> v<version>.mcpb`.
