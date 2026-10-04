# Building a Custom MCP Server

Build only when no hosted or existing server covers the need. Verify protocol details against modelcontextprotocol.io and Anthropic's connector-building docs before shipping.

## Decide

| Question | Choice |
|---|---|
| Runs where? | Local process → `stdio`. Hosted/shared → remote HTTP (streamable HTTP; `sse` is legacy) |
| Language | Official SDK for TypeScript or Python unless the user has another constraint |
| Exposes | Tools (actions), resources (readable data), prompts (templates). Start with tools only |
| Auth | Remote: OAuth or bearer header via `userConfig`/env. Local: env vars. Never hardcode |

## Tool design (the part that decides quality)

- Few, task-shaped tools; verb-first snake_case names; one clear purpose each.
- Description says what it does, when to use it, and what it returns. Input schema: typed, every field described, sane defaults, enums over free text.
- Return small, structured, relevant output. Paginate or filter; never dump whole datasets. Errors: actionable message, not a stack trace.
- Mark read-only vs destructive behavior; destructive tools require an explicit confirming argument.
- Idempotent where possible; timeouts on every outbound call.

## Security

- Validate and sanitize every input; allow-list paths, hosts, and commands; no shell string concatenation.
- Least-privilege credentials; no secrets in logs or tool output.
- Stdout is protocol-only on `stdio`: log to stderr.
- Treat content fetched from third parties as untrusted (prompt-injection) and don't echo it as instructions.

## Bundle and test

1. Lean layout: `servers/<name>/` with the entry file and a README section. Dependencies (verified 2026-10-05, code.claude.com/docs/en/plugins/loading and /components):
   - **Node:** list them in a `package.json` at the plugin root and commit its lockfile (`package-lock.json`, `bun.lock`, ...). Claude Code installs root dependencies into each cached version at install and update; the entry file finds them by walking up. A plugin loaded in place from a local folder gets no install: run it yourself. Alternatives: bundle the server into one readable file, or a `SessionStart` hook that installs into `${CLAUDE_PLUGIN_DATA}` with `NODE_PATH` set (works for `require`, not for ES module `import`).
   - **Python:** no automatic install. Use a `SessionStart` hook that runs `pip install --target "${CLAUDE_PLUGIN_DATA}/python/<name>"` when `requirements.txt` changes, and set `PYTHONPATH` to that folder in the server's `env`. `scripts/scaffold_mcp_server.py` writes both.
   - Pin exact versions before release. Any install from a registry runs on the user's machine: disclose it in the README. Anthropic's directory holds lockfile installs and hook-run installs for a reviewer (`claude-packager/references/directory-checklist.md` §3).
2. Register in `.mcp.json` using `${CLAUDE_PLUGIN_ROOT}` (see `connectors.md`).
3. Exercise with the MCP Inspector (`npx @modelcontextprotocol/inspector`) and then a real Claude session; confirm tool names resolve as `mcp__plugin_<plugin>_<server>__<tool>`.
4. Tests for each tool: happy path, bad input, upstream failure, oversized result.
5. Desktop-bundle distribution uses `.mcpb` (referenced from `mcpServers`); remote servers need a public HTTPS URL and, for directory listing, Anthropic's review process.
