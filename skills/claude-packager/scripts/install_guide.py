#!/usr/bin/env python3
"""Write install and removal steps for an extension, for every place people use Claude.

Usage: install_guide.py <dir> [--repo owner/repo] [--marketplace name] [--file "<package file name>"] [--out FILE]
Covers the Claude desktop app, claude.ai on the web, the desktop app's Code tab, and the terminal, plus how to undo each.
Without --repo the Code tab and terminal steps load the folder or add a local marketplace instead.
Steps verified 2026-10-11 against support.claude.com articles 13837440 (plugins) and 12512180 (skills), and
code.claude.com/docs/en/plugins/install.
"""
import json, re, sys
from pathlib import Path

def info(root):
    pj = root / ".claude-plugin" / "plugin.json"
    if pj.exists():
        m = json.loads(pj.read_text(encoding="utf-8-sig"))
        return "plugin", m["name"], m.get("displayName") or m["name"], str(m.get("version", "0.0.1")), m
    t = (root / "SKILL.md").read_text(encoding="utf-8-sig")
    name = re.search(r"^name:\s*(.+)$", t, re.M).group(1).strip().strip("\"'")
    ver = re.search(r"^\s+version:\s*[\"']?([^\s\"']+)", t, re.M)
    h1 = re.search(r"^#\s+(.+)$", t, re.M)
    return "skill", name, h1.group(1).strip() if h1 else name, ver.group(1) if ver else "0.0.1", {}

def guide(root, repo="", market="", fname=""):
    kind, slug, title, ver, m = info(root)
    if kind == "skill":
        f = fname or f"{title} v{ver}.zip"
        return (f"# Install {title}\n\n"
                f"## Claude desktop app and claude.ai on the web\n\n1. Open **Customize** in the left sidebar, then **Skills**.\n2. Click **+**, then **Create skill > Upload a skill**, and choose `{f}`.\n3. Turn the skill on. Start it by typing `/{slug}` or by describing the task.\n\n"
                f"**Undo:** in **Customize > Skills**, turn the skill off, or delete it from its menu.\n\n"
                f"## Claude Code (terminal or the desktop app's Code tab)\n\nUnzip `{f}` into `~/.claude/skills/` (every project) or `.claude/skills/` (this project only). Start a new session.\n\n"
                f"**Undo:** delete the `{slug}` folder you added.\n")
    f = fname or f"{title} v{ver}.plugin"
    mk = market or (json.loads((root / ".claude-plugin" / "marketplace.json").read_text()).get("name") if (root / ".claude-plugin" / "marketplace.json").exists() else "")
    src = repo or "./path/to/marketplace-folder"
    ident = f"{slug}@{mk}" if mk else f"{slug}@<marketplace>"
    opts = m.get("userConfig") or {}
    servers = {}
    if (root / ".mcp.json").exists():
        d = json.loads((root / ".mcp.json").read_text(encoding="utf-8-sig")); servers = d.get("mcpServers", d) if isinstance(d, dict) else {}
    if isinstance(m.get("mcpServers"), dict): servers.update(m["mcpServers"])
    out = [f"# Install {title}\n",
        "## Claude desktop app (Chat or Cowork) and claude.ai on the web\n",
        "1. Open **Customize** in the left sidebar, then the **Plugins** tab. In Cowork, open the Cowork tab first.",
        f"2. Upload `{f}` as a custom plugin." + (f" Or add the marketplace `{repo}` with **Add > Add marketplace**, then add {title} from **Discover**." if repo else ""),
        "3. Plugins you add here are saved to your account, so they also reach Claude Code when you sign in there with the same account.\n",
        f"**Undo:** in **Customize > Plugins**, turn {title} off, or delete it from its **...** menu. A marketplace you added comes off with its menu's **Remove**.\n",
        "## Code tab in the desktop app (local or SSH sessions)\n",
        f"1. Add the marketplace once from a terminal: `claude plugin marketplace add {src}`." if not repo else f"1. Add the marketplace once: `claude plugin marketplace add {repo}` (or `/plugin marketplace add {repo}` in a session).",
        f"2. Click **+** next to the prompt box, then **Plugins > Add plugin**, select {title}, and choose a scope (you, this project, or this project only for you).\n",
        "**Undo:** **+ > Plugins > Manage plugins**, then disable or uninstall it.\n",
        "## Terminal (Claude Code)\n", "```",
        f"claude plugin install {slug} --marketplace {src}" if repo else f"claude plugin marketplace add {src}\nclaude plugin install {ident}",
        "```", "Already running? Use `/reload-plugins`. To try a folder for one session without installing: `claude --plugin-dir <folder>`.\n",
        f"**Undo:** `claude plugin disable {ident}` to pause it, `claude plugin uninstall {ident}` to remove it" + (f", and `claude plugin marketplace remove {mk}` to drop the marketplace (this also uninstalls everything installed from it)." if mk else ".") + "\n"]
    if opts or servers:
        out.append("## Settings and connectors\n")
        for k, v in opts.items():
            out.append(f"- **{v.get('title', k)}**: {v.get('description', '')}" + (" Stored in secure storage." if v.get("sensitive") else ""))
        for n, s in servers.items():
            u = s.get("url", "") if isinstance(s, dict) else ""
            out.append(f"- Connector **{n}**" + (f" (`{u}`)" if u and "${" not in u else "") + ": in Chat or Cowork, open the plugin's **Connectors** tab and select **Connect**; you sign in with your own account, so nothing personal is stored in the plugin.")
        out.append("- In Claude Code, set options and connector settings under `/plugin` > **Installed** > the plugin > **Configure options** or **Configure**.")
        out.append("- A connector you already have at the same address is reused: Claude Code skips the plugin's copy.\n")
    return "\n".join(out)

def main(argv):
    if not argv or argv[0].startswith("-"): print(__doc__); return 2
    root, a, i = Path(argv[0]).resolve(), {"repo": "", "marketplace": "", "file": "", "out": ""}, 1
    while i < len(argv):
        k = argv[i][2:]
        if argv[i].startswith("--") and k in a and i + 1 < len(argv): a[k] = argv[i+1]; i += 2
        else: print(__doc__); return 2
    text = guide(root, a["repo"], a["marketplace"], a["file"])
    if a["out"]: Path(a["out"]).write_text(text, encoding="utf-8"); print(f"wrote {a['out']}")
    else: print(text)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
