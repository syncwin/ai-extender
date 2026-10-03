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

1. Lean layout: `servers/<name>/` with the entry file, lockfile, and README section; dependencies installed to `${CLAUDE_PLUGIN_DATA}` if needed (not the plugin root).
2. Register in `.mcp.json` using `${CLAUDE_PLUGIN_ROOT}` (see `connectors.md`).
3. Exercise with the MCP Inspector (`npx @modelcontextprotocol/inspector`) and then a real Claude session; confirm tool names resolve as `mcp__plugin_<plugin>_<server>__<tool>`.
4. Tests for each tool: happy path, bad input, upstream failure, oversized result.
5. Desktop-bundle distribution uses `.mcpb` (referenced from `mcpServers`); remote servers need a public HTTPS URL and, for directory listing, Anthropic's review process.
