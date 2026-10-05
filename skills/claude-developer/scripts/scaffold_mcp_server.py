#!/usr/bin/env python3
"""Scaffold a minimal stdio MCP server inside a plugin and register it in .mcp.json.

Usage: scaffold_mcp_server.py <plugin-dir> --name my-server --lang node|python [--tool echo]
Creates servers/<name>/ and merges a server entry into .mcp.json using ${CLAUDE_PLUGIN_ROOT}.
Node (@modelcontextprotocol/sdk): dependencies go in the plugin-root package.json. Run `npm install` once in the
plugin folder and commit package-lock.json: Claude Code installs root dependencies when it caches the plugin.
Python (official `mcp` package, FastMCP): servers/<name>/requirements.txt, a SessionStart hook that installs it
into ${CLAUDE_PLUGIN_DATA}/python/<name> when it changes, and PYTHONPATH pointing there.
Both install from a package registry on the user's machine: say so in the README (references/mcp-servers.md).
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
        pj = root / "package.json"
        pkg = json.loads(pj.read_text()) if pj.exists() else {"name": root.name, "version": "0.0.1", "private": True}
        pkg.setdefault("dependencies", {}).update({"@modelcontextprotocol/sdk": "^1", "zod": "^3"})
        pj.write_text(json.dumps(pkg, indent=2) + "\n")
        entry = {"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/%s/index.mjs" % a["name"]]}
        nxt = "run `npm install` in the plugin folder and commit package-lock.json (Claude Code installs root dependencies when it caches the plugin)"
    else:
        (d / "server.py").write_text(PY.format(**a))
        (d / "requirements.txt").write_text("mcp>=1,<2\n")
        lib = "${CLAUDE_PLUGIN_DATA}/python/%s" % a["name"]
        req = "${CLAUDE_PLUGIN_ROOT}/servers/%s/requirements.txt" % a["name"]
        seen = "${CLAUDE_PLUGIN_DATA}/%s-requirements.txt" % a["name"]
        entry = {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/servers/%s/server.py" % a["name"]], "env": {"PYTHONPATH": lib}}
        hook = {"type": "command", "command": f'diff -q "{req}" "{seen}" >/dev/null 2>&1 || (python3 -m pip install --quiet --target "{lib}" -r "{req}" && cp "{req}" "{seen}")'}
        hf = root / "hooks" / "hooks.json"
        hcfg = json.loads(hf.read_text()) if hf.exists() else {}
        hcfg.setdefault("hooks", {}).setdefault("SessionStart", []).append({"hooks": [hook]})
        hf.parent.mkdir(exist_ok=True); hf.write_text(json.dumps(hcfg, indent=2) + "\n")
        nxt = "the SessionStart hook installs requirements.txt into the plugin data folder on first run and after it changes; pin exact versions before release"
    mcp = root / ".mcp.json"
    cfg = json.loads(mcp.read_text()) if mcp.exists() else {}
    cfg.setdefault("mcpServers", {})[a["name"]] = entry
    mcp.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"### Scratchpad: MCP Scaffold\n**Scope:** {a['name']} ({a['lang']})\n\n| Item | Result |\n|---|---|\n| Server | `{d}` |\n| Registered | `.mcp.json` → `{a['name']}` |\n| Tool | `{a['tool']}` |\n\n**Next:** {nxt}; disclose the package install in the README; replace the sample tool; test with the MCP Inspector.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
