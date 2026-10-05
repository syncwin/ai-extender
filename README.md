# AI Extender for Claude

Tell Claude what you want. Use your own words, and AI Extender turns that into a working Claude skill or plugin. It plans the build, writes the files, checks them, and hands you something you can install, plus a companion prompt you can import into Prompt Builder to start it from a short form. You don't need to know what a manifest or an MCP server is.

**Version** 1.0.0 · **Author** @wasimness · **Company** SyncWin · **Contact** support@syncwin.com · **License** MIT

## What you can build

- **Skills** that teach Claude a task the same way every time: a checklist, a house style, a report format.
- **Plugins** that bundle several skills with agents, hooks, or connectors.
- **Connectors** to the services your work already lives in (Notion, Slack, a CRM, your own API).
- **Agents and hooks** for narrower jobs, such as a reviewer that can only read files or a rule that blocks edits to `.env`.
- **Internal business tools**: your team's onboarding steps, proposal checks, or client reporting, packaged so everyone gets the same result.

It also updates, audits, versions, and packages extensions you already have.

## Quick start

1. Install the plugin (below).
2. Type `/ai-extender`, or just describe what you want: "make a skill that turns my meeting notes into action items."
3. Answer the few questions only you can answer, usually who will use it and where.
4. Approve the short plan. AI Extender builds it, checks it, and gives you the file, install steps, and its companion prompt.

More things to try:

- "My team forgets steps when we onboard a client. Can Claude help with that?"
- "Add a Notion connector to my plugin."
- "Audit my plugin before I share it."
- "Bump the version and package it for Cowork."

## Install

**Claude Code**

```
claude plugin marketplace add syncwin/ai-extender
claude plugin install ai-extender@syncwin
```

**Cowork or claude.ai**: download the `.plugin` file from the [latest release](https://github.com/syncwin/ai-extender/releases/latest) and upload it as a custom plugin. Once the plugin is listed in Anthropic's directory, you can add it from there instead.

## Companion prompt

Every extension AI Extender builds comes with a companion prompt: a JSON file for [Prompt Builder](https://promptbuilder.eniston.com/), a Chrome extension that keeps prompts as fill-in forms and inserts them into Claude. Import it under Settings > Import. Fill in the form, and the prompt starts the right skill with everything it needs. The file lives in the extension's `prompts/` folder and is copied next to the package each time you package it.

AI Extender has one too: `prompts/ai-extender-for-claude.json`. Pick a goal, describe what you want, and send.

## Requirements

Use Claude Code, Cowork, or claude.ai. Skills must be turned on. The bundled scripts need Python 3.8 or newer and nothing else; CI tests them on Python 3.9 through 3.13 on Linux. On Windows or macOS, run them with `python` or `python3`, whichever your system has.

## What it runs, reads, and sends

AI Extender is Markdown instructions plus a few Python scripts, all readable in this repository.

- **Scripts** run on your machine. They make no network requests and read or write only the folders you point them at (plus a temporary folder while packaging). Packaging also writes the companion prompt into the extension's `prompts/` folder. They call only other scripts in this plugin, with fixed arguments and no shell.
- **Folder checks**: the router may run `ls -d /mnt/user-data/outputs mnt/.plugins mnt/.local-plugins` to tell whether it's inside Cowork. If a script path isn't filled in, it runs one `find` under `~/.claude/plugins`, `/mnt`, `mnt`, and the current folder to locate its own scripts. Both read folder and file names only.
- **Web pages**: if you ask it to refresh its platform facts, Claude fetches Anthropic's official documentation pages with the web tool your session already has. It tells you before fetching.
- **GitHub**: only when you ask it to publish or keep a repo in sync, and only through your own connector or `gh` login. It asks for the owner and repo, and confirms before the first push.

Nothing else leaves your machine. The plugin has no connectors, hooks, MCP servers, or executables of its own, and it collects no data. Claude asks before any step that deletes, sends, or publishes, and you can report a vulnerability privately by following the steps in `SECURITY.md`.

## Skills and agents

Start with `/ai-extender`. It reads your request and calls the right role, so most people never call the others directly.

| Skill | What it does |
|---|---|
| `ai-extender` | Router. Asks what you want, picks the steps |
| `ai-extender:claude-planner` | Scopes the request and designs the structure |
| `ai-extender:claude-developer` | Writes skills, connectors, agents, hooks, MCP servers, and tests |
| `ai-extender:claude-maintainer` | Updates existing extensions, versions, changelogs |
| `ai-extender:claude-reviewer` | Validates and audits before anything ships |
| `ai-extender:claude-packager` | Builds `.plugin` and `.zip` files, companion prompts, and marketplace entries |

Agents: `ai-extender:claude-grader` grades test runs against their assertions, and `ai-extender:claude-comparator` compares two outputs blind.

**Naming.** `ai-` marks parts that aren't tied to one platform; `claude-` marks Claude-specific parts. ChatGPT or Gemini layers could sit beside the Claude one later (`skills/ai-extender/references/platforms.md`). Only the Claude layer exists today. Because the role skills contain the word `claude`, claude.ai and the API reject them as individual skill uploads, so install the whole plugin instead.

## Troubleshooting

- **A skill doesn't trigger.** Say what you want in plain words ("audit my plugin") or call `/ai-extender` directly. To check the descriptions offline: `python skills/claude-reviewer/scripts/simulate.py . triggers`.
- **Validation fails.** Run `python skills/claude-reviewer/scripts/validate_extension.py <dir> --strict` and fix the listed codes. Each message names the file and the rule.
- **A skill upload is rejected on claude.ai.** Skill names that contain `claude` can't be uploaded alone. Upload the `.plugin` file instead.

## Status

Version 1.0.0, released after AI Extender audited itself from a real install. Every push runs the 67 self-tests and the directory validator on Python 3.9 to 3.13, and `claude plugin validate --strict` passed before release. The `evals/` folder holds five live cases for `claude plugin eval`; run them yourself with `claude plugin eval . --allow-tools Bash Write Edit` (the shell cases need the sandbox tools bubblewrap and socat on Linux). Platform facts were checked against Anthropic's documentation on 2026-10-05. Found a mismatch? Please open an issue.

## Contributing and credits

Issues and pull requests are welcome; see `CONTRIBUTING.md`. Credits are in `CREDITS.md`. AI Extender is an independent project by SyncWin, and it is not affiliated with or endorsed by Anthropic in any way.
