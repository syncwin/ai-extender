# Scaffold MCP server recipe (replaces scaffold_mcp_server.py)

**Not directory-compliant.** This recipe writes server code, a dependency list and (Python) a SessionStart hook. The Anthropic directory refuses scripts, non-text files and hooks from non-Verified organizations; the result still works for private and GitHub-marketplace installs. Before running it, tell the user this plainly and offer the compliant method (a remote MCP server over HTTP registered in `.mcp.json`, `userConfig` with `sensitive: true`, skill instructions). Run it only on the user's explicit choice, and mark the plugin "not directory-compliant" in the plan and README.

## Contents

- Purpose and when
- Inputs (former CLI options)
- Files written
- Procedure
- Output

## Purpose and when
Add a minimal stdio MCP server to an existing plugin and register it in `.mcp.json`, for Node or Python. Used when the plan calls for a connector (`references/mcp-servers.md`). Everything below is written into the USER's plugin; none of it runs as part of AI Add-on Builder.

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `<plugin-dir>` | required | Existing plugin folder; it must contain `.claude-plugin/plugin.json`, else stop with `not a plugin: <dir>`. |
| `--name my-server` | required | Server name: lowercase letters, digits and single hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`). |
| `--lang node\|python` | required | Language of the server. |
| `--tool echo` | `echo` | Name of the sample tool: starts with a lowercase letter, then lowercase letters, digits or `_`. |

Anything that fails these rules: stop and ask. If `<plugin-dir>/servers/<name>` exists: stop with `exists: <path>` (never overwrite).

## Files written
Replace `{name}` and `{tool}` in the templates.

### Node: `servers/<name>/index.mjs`
```
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "{name}", version: "0.0.1" });

server.tool(
  "{tool}",
  "Echo back the given text. Use to verify the connector is working.",
  { text: z.string().max(2000).describe("Text to echo") },
  async ({ text }) => ({ content: [{ type: "text", text }] })
);

await server.connect(new StdioServerTransport());
console.error("{name} ready");
```
Plugin-root `package.json`: if it exists, read it; otherwise start from `{"name": "<plugin folder name>", "version": "0.0.1", "private": true}`. Under `dependencies` set (add or replace) `"@modelcontextprotocol/sdk": "^1"` and `"zod": "^3"`. Write it with 2-space indentation and a trailing newline.

`.mcp.json` entry: `{"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/<name>/index.mjs"]}`.

Next step text: `run npm install in the plugin folder and commit package-lock.json (Claude Code installs root dependencies when it caches the plugin)`.

### Python: `servers/<name>/server.py`
```
from mcp.server.fastmcp import FastMCP
import sys

mcp = FastMCP("{name}")

@mcp.tool()
def {tool}(text: str) -> str:
    """Echo back the given text. Use to verify the connector is working."""
    if len(text) > 2000:
        raise ValueError("text must be at most 2000 characters")
    return text

if __name__ == "__main__":
    print("{name} ready", file=sys.stderr)
    mcp.run()
```
`servers/<name>/requirements.txt` holds one line: `mcp>=1,<2`.

`.mcp.json` entry (with `LIB` = `${CLAUDE_PLUGIN_DATA}/python/<name>`):
`{"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/<name>/server.py"], "env": {"PYTHONPATH": "LIB"}}`.

`hooks/hooks.json`: read it if it exists (else start with `{}`); under `hooks` -> `SessionStart` append one group `{"hooks": [HOOK]}` where HOOK is:
```
{"type": "command", "command": "diff -q \"REQ\" \"SEEN\" >/dev/null 2>&1 || (python3 -m pip install --quiet --target \"LIB\" -r \"REQ\" && cp \"REQ\" \"SEEN\"); exit 0"}
```
with `REQ` = `${CLAUDE_PLUGIN_ROOT}/servers/<name>/requirements.txt`, `SEEN` = `${CLAUDE_PLUGIN_DATA}/<name>-requirements.txt`, `LIB` as above. Create the `hooks` folder if needed; write with 2-space indentation and a trailing newline.

Next step text: `the SessionStart hook installs requirements.txt into the plugin data folder on first run and after it changes; pin exact versions before release`.

### Both languages: the guardrail matcher
If `hooks/hooks.json` exists: for each group under `hooks.PostToolUse` whose hooks mention the screen-text recipe and that has a `matcher`: if the matcher (as a whole-string regular expression) does NOT already match the sample tool name `mcp__plugin_x_<name>__t`, append `|mcp__.*<name>.*` (each hyphen in the name written with a backslash before it) to the matcher. Save the file (2-space indentation, trailing newline). This keeps the injection guardrail screening the new server's output.

### Both languages: register in `.mcp.json`
Read `<plugin-dir>/.mcp.json` if it exists (else `{}`); under `mcpServers` set the key `<name>` to the entry above (replacing a same-named key); write with 2-space indentation and a trailing newline.

## Procedure
```
1. Inputs are checked and the target must not exist (Glob).
2. `servers/<name>/` is created and the language's files are written with Write.
3. The package.json (Node) or requirements and hook (Python) edits are done with Read plus Write or Edit.
4. The guardrail matcher is widened if it applies.
5. The `.mcp.json` entry is merged.
6. The scratchpad below is printed.
```

## Output
```
### Scratchpad: MCP Scaffold
**Scope:** <name> (<lang>)

| Item | Result |
|---|---|
| Server | `<plugin-dir>/servers/<name>` |
| Registered | `.mcp.json` -> `<name>` |
| Tool | `<tool>` |

**Next:** <next step text for the language>; disclose the package install in the README; replace the sample tool; test with the MCP Inspector.
```
Stdout is protocol-only: servers log to stderr (the templates already do).
