#!/usr/bin/env python3
"""Scaffold a minimal stdio MCP server inside a plugin and register it in .mcp.json.

Usage: scaffold_mcp_server.py <plugin-dir> --name my-server --lang node|python [--tool echo]
Creates servers/<name>/ (entry, README section stub) and merges a server entry using ${CLAUDE_PLUGIN_ROOT}.
Node uses @modelcontextprotocol/sdk; Python uses the official `mcp` package (FastMCP). Dependencies are
declared, not installed: install into ${CLAUDE_PLUGIN_DATA} (see references/mcp-servers.md).
Stdout is protocol-only: servers log to stderr.
"""
import json, re, sys
from pathlib import Path

NODE = '''import {{ McpServer }} from "@modelcontextprotocol/sdk/server/mcp.js";
import {{ StdioServerTransport }} from "@modelcontextprotocol/sdk/server/stdio.js";
import {{ z }} from "zod";

const server = new McpServer({{ name: "{name}", version: "0.0.1" }});

server.tool(
  "{tool}",
  "Echo back the given text. Use to verify the connector is working.",
  {{ text: z.string().max(2000).describe("Text to echo") }},
  async ({{ text }}) => ({{ content: [{{ type: "text", text }}] }})
);

await server.connect(new StdioServerTransport());
console.error("{name} ready");
'''
PY = '''from mcp.server.fastmcp import FastMCP
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
'''

def main(argv):
    a = {"name": None, "lang": None, "tool": "echo"}
    root, i = None, 0
    while i < len(argv):
        x = argv[i]
        if x.startswith("--") and x[2:] in a: a[x[2:]] = argv[i+1]; i += 1
        elif not x.startswith("-") and root is None: root = Path(x)
        else: print(__doc__); return 2
        i += 1
    if not (root and a["name"] and a["lang"] in ("node", "python")) or not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", a["name"]) or not re.match(r"^[a-z][a-z0-9_]*$", a["tool"]):
        print(__doc__); return 2
    if not (root / ".claude-plugin" / "plugin.json").exists(): print(f"not a plugin: {root}"); return 2
    d = root / "servers" / a["name"]
    if d.exists(): print(f"exists: {d}"); return 1
    d.mkdir(parents=True)
    if a["lang"] == "node":
        (d / "index.mjs").write_text(NODE.format(**a))
        (d / "package.json").write_text(json.dumps({"name": a["name"], "version": "0.0.1", "type": "module", "private": True,
            "dependencies": {"@modelcontextprotocol/sdk": "^1", "zod": "^3"}}, indent=2) + "\n")
        entry = {"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/%s/index.mjs" % a["name"]]}
    else:
        (d / "server.py").write_text(PY.format(**a))
        (d / "requirements.txt").write_text("mcp>=1\n")
        entry = {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/%s/server.py" % a["name"]]}
    mcp = root / ".mcp.json"
    cfg = json.loads(mcp.read_text()) if mcp.exists() else {}
    cfg.setdefault("mcpServers", {})[a["name"]] = entry
    mcp.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"### Scratchpad — MCP Scaffold\n**Scope:** {a['name']} ({a['lang']})\n\n| Item | Result |\n|---|---|\n| Server | `{d}` |\n| Registered | `.mcp.json` → `{a['name']}` |\n| Tool | `{a['tool']}` |\n\n**Next:** install dependencies into `${{CLAUDE_PLUGIN_DATA}}`, replace the sample tool, test with the MCP Inspector.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
