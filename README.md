# AI Add-on Builder

Tell Claude what you want. Use your own words, and AI Add-on Builder turns that into a working Claude skill or plugin. It plans the build, writes the files, checks them, and hands you something you can install, plus a companion prompt you can import into Prompt Builder to start it from a short form. You don't need to know what a manifest or an MCP server is.

**Download:** [aiaddon.plugin](https://github.com/syncwin/aiaddon/releases/latest/download/aiaddon.plugin) (asset of the latest GitHub release) or the [rolling next build](https://github.com/syncwin/aiaddon/releases/download/next/aiaddon.plugin)

**Version** 0.2.1 · **Author** @wasimness · **Company** SyncWin · **Contact** support@syncwin.com · **License** MIT

## What you can build

- **Skills** that teach Claude a task the same way every time: a checklist, a house style, a report format.
- **Plugins** that bundle several skills with agents, hooks, or connectors.
- **Connectors** to the services your work already lives in (Notion, Slack, a CRM, your own API).
- **Agents and hooks** for narrower jobs, such as a reviewer that can only read files or a rule that blocks edits to `.env`.
- **Internal business tools**: your team's onboarding steps, proposal checks, or client reporting, packaged so everyone gets the same result.

Every plugin it builds comes with Composio already declared, so its skills can reach Gmail, Notion, Slack, a CRM, and 1,000+ other apps. Each person signs in with their own Composio account, so nothing personal is stored in the plugin. Plugins that read outside content also get a small injection guardrail. Say so in the plan if you don't want either.

It also updates, audits, versions, and packages extensions you already have. One summary of what changed becomes the changelog entry and every version number. Each package comes with install and removal steps for the desktop app, the web, the Code tab, and the terminal. A release report shows how many files were kept, changed, added, or dropped.

## Quick start

1. Install the plugin (below).
2. Type `/aiaddon`, or just describe what you want: "make a skill that turns my meeting notes into action items."
3. Answer the few questions only you can answer, usually who will use it and where.
4. Approve the short plan. AI Add-on Builder builds it, checks it, and gives you the file, install steps, and its companion prompt.

More things to try:

- "My team forgets steps when we onboard a client. Can Claude help with that?"
- "Add a Notion connector to my plugin."
- "Audit my plugin before I share it."
- "Bump the version and package it for Cowork."

## Install

**Claude Code**

```
claude plugin marketplace add syncwin/aiaddon
claude plugin install aiaddon@syncwin
```

**Cowork or claude.ai**: download the `.plugin` file from the [latest release](https://github.com/syncwin/aiaddon/releases/latest) and upload it as a custom plugin. Once the plugin is listed in Anthropic's directory, you can add it from there instead.

**One skill only**: every skill is self-contained and attached to each release as `<skill>.zip` (for example `aiaddon-review.zip`). On claude.ai, Cowork or desktop, upload it under Customize > Skills. In Claude Code, run `npx skills add syncwin/aiaddon --skill aiaddon-review`. Whole plugin on claude.ai, Cowork or desktop: Customize > Plugins > add the GitHub repo as a marketplace.

## Companion prompt

Every extension AI Add-on Builder builds comes with a companion prompt: a JSON file for [Prompt Builder](https://promptbuilder.syncwin.com/), a Chrome extension that keeps prompts as fill-in forms and inserts them into Claude. Import it under Settings > Import ([help](https://promptbuilder.eniston.com/)). Fill in the form, and the prompt starts the right skill with everything it needs. The source file lives in the extension's `prompts/` folder; packaging delivers it as a separate file next to the package and never puts it inside the package, because it belongs to Prompt Builder, not to Claude.

AI Add-on Builder has one too: `ai-add-on-builder.json`, attached to each release as its own file. Pick a goal, describe what you want, and send.

## Requirements

Use Claude Code, Cowork, or claude.ai. Skills must be turned on. The plugin is Markdown only: nothing to install and no Python needed. Claude follows the recipes in each skill's `references/` folder with its own read, search and write tools and standard OS or git commands.

## What it runs, reads, and sends

AI Add-on Builder is Markdown instructions and recipes only, all readable in this repository. It ships no scripts and no hooks.

- **Recipes** run on your machine through Claude's own tools. They make no network requests and read or write only the folders you point them at (plus a temporary folder while packaging). Packaging also writes the companion prompt into the extension's `prompts/` folder and delivers it, with an install guide, next to the package (never inside it).
- **Injection screen**: a manual step (`aiaddon-review/references/screen-text.md`) with a checklist of injection patterns. Claude runs it after every WebFetch, WebSearch or connector output and on third-party files it audits. It reads only the text in question and sends nothing. No hook ships.
- **If something looks like an injection:** Claude treats the content as data, quotes the passage to you, and asks before acting on it.
- **Secret scan:** the scan-secrets recipe reads only the folders you name to look for passwords and keys saved in plain text. It masks what it finds and sends nothing.
- **Folder checks**: the router may run `ls -d /mnt/user-data/outputs mnt/.plugins mnt/.local-plugins` to tell whether it's inside Cowork. It reads folder and file names only.
- **Web pages**: if you ask it to refresh its platform facts, Claude fetches Anthropic's official documentation pages with the web tool your session already has. It tells you before fetching.
- **Composio connector**: the plugin declares one connector, Composio, at its shared address `https://connect.composio.dev/mcp`. It ships no account and no key: you connect it yourself under Customize > Plugins > AI Add-on Builder > Connectors and sign in with your own Composio account. AI Add-on Builder uses it to push and release to GitHub when you ask, and to reach another app when a build needs one. Every skill still works without it; GitHub then falls back to your own GitHub connector or `gh` login. If you already have Composio connected at the same address, Claude uses that one and doesn't load a second copy.
- **GitHub**: only when you ask it to publish or keep a repo in sync, and only through Composio, your own GitHub connector, or `gh` login. It asks for the owner and repo, and confirms before the first push.

Nothing else leaves your machine. Apart from the Composio connector, the plugin has no MCP servers, hooks or executables of its own, and it collects no data. Claude asks before any step that deletes, sends, or publishes, and you can report a vulnerability privately by following the steps in `SECURITY.md`.

## Skills and agents

Start with `/aiaddon:aiaddon`. The router has an explicit routing table (phrases to exact skill, tie-break rules, one closed question when unclear) and loads the chosen skill itself; it never answers the task. It reads your request and calls the right skill, so you rarely need to call the others yourself.

| Skill | What it does |
|---|---|
| `aiaddon:aiaddon` | Router. Asks what you want, picks the steps |
| `aiaddon:aiaddon-plan` | Scopes the request and designs the structure |
| `aiaddon:aiaddon-build` | Writes skills, connectors, agents, remote MCP servers, and tests (hooks and local servers only for private installs, with a directory warning) |
| `aiaddon:aiaddon-maintain` | Updates existing extensions, versions, changelogs |
| `aiaddon:aiaddon-review` | Validates and audits before anything ships |
| `aiaddon:aiaddon-package` | Builds `.plugin` and `.zip` files, companion prompts, and marketplace entries |
| `aiaddon:aiaddon-clean` | Deep clean-up and de-duplication with a keep-unique proof; dry-run, plan approval, never deletes |
| `aiaddon:aiaddon-prompt` | Writes, tightens, and templates prompts for any AI model; exports Prompt Builder JSON |

Agents: `aiaddon:aiaddon-grade` grades test runs against their assertions, and `aiaddon:aiaddon-compare` compares two outputs blind.

| Connector | Used by | For | Without it |
|---|---|---|---|
| Composio (`https://connect.composio.dev/mcp`) | `aiaddon:aiaddon-package`, and any role when a build needs an outside app | Pushing, tagging, and releasing on GitHub; reaching other apps a build depends on | Skills work as usual; GitHub goes through your own GitHub connector or `gh` |

**Naming.** Router skill = plugin name (`aiaddon`); every other skill and agent is prefixed `aiaddon-` and named for an action (`aiaddon-review`, not a role noun). The validator enforces this for every extension it builds. Other platform layers could sit beside this one later (`skills/aiaddon/references/platforms.md`).

## Public safety

Everything this plugin creates is treated as a public repository, even when you never say so. Each plan states what is public (source, docs, generic examples) and what stays private (keys, tokens, passwords, personal data, client names, internal URLs, local user paths, logs, memory files). Every scaffold includes a `.gitignore` preset, a `.env.example` with names only, and a `PUBLIC-SAFETY.md`.

- **Scan, blocking:** the recipes `aiaddon-review/references/scan-secrets.md` and `public-safety-scan.md` check the working tree, every line of git history (`git log --all -p`) and the contents of built `.zip` and `.plugin` files, with standard git and OS commands. Allowed false positives go in `.public-safety-allow`.
- **Enforced three ways:** the validator (`X008` to `X013`), the packager (refuses to build or release on any finding and scans inside the produced zip), and CI (job `public-safety` on every push and pull request).
- **If something already leaked:** detect, tell the user, rotate or revoke the credential first, rewrite history with `git filter-repo` (or BFG), force-push only after your explicit OK, re-create affected releases and tags, ask GitHub Support to purge cached views and pull-request refs, then re-scan to prove zero traces. Steps: `skills/aiaddon-review/references/public-safety.md`.
- **Turn on GitHub's own protection** for every public repository: Settings > Code security > secret scanning and push protection (and private vulnerability reporting). They complement this scan; they do not replace it.

## Security and verification

Each release `.plugin` is built from its tagged commit on GitHub's runners and signed with a build-provenance attestation, and the release lists its SHA-256 checksums. To check a download before you install it:

```
gh attestation verify "aiaddon.plugin" --repo syncwin/aiaddon
sha256sum -c SHA256SUMS
```

Every change also runs CodeQL, a secret scan, the injection screen, and the full self-test suite, with GitHub Actions pinned to exact commits. Report a vulnerability privately as described in `SECURITY.md`. The plugin collects no data (`PRIVACY.md`).

## Troubleshooting

- **A skill doesn't trigger.** Say what you want in plain words ("audit my plugin") or call `/aiaddon` directly. To check the descriptions offline, follow `aiaddon-review/references/simulate.md`.
- **Validation fails.** Follow `aiaddon-review/references/validate-extension.md` (strict) on the folder and fix the listed codes. Each message names the file and the rule.
- **A skill upload is rejected on claude.ai.** Skill names that contain `claude` can't be uploaded alone. Upload the `.plugin` file instead.
- **A plugin's connector shows "Not added" though you already use that service.** The plugin points at a different address than your own connector, so Claude treats them as two. Run the validator with `--known-connectors "Name=https://your-connector-url"` and use the address it reports. Claude Code skips a plugin connector only when the address matches exactly.
- **A key or password ended up in a plugin.** Follow `aiaddon-review/references/scan-secrets.md` on the plugin folder, move each value it finds into the plugin's settings, and rotate the key, since anyone who received a copy still has it.

## Status

Version 0.2.0. Maintainer CI (dev tools in `dev/`, not shipped): every push to `main` and every pull request runs the 195 self-tests and 43 router cases, the directory validator, the secret scan, the injection screen, and the trigger simulation on Python 3.9 to 3.13, and `claude plugin validate --strict` passed before release. The `evals/` folder holds five live cases for `claude plugin eval`; the last full run (2026-10-12, Sonnet as judge) scored 0.93, 0.73 above the same tasks without the plugin; six-run repeats scored 1.00 on audits, intake, and scaffolding. Run them yourself with `claude plugin eval . --allow-tools Bash Write Edit --judge-model sonnet` (the shell cases need the sandbox tools bubblewrap and socat on Linux; the default small judge misreads long, table-heavy replies). Platform facts were checked against Anthropic's documentation on 2026-10-11. If you find a mismatch, please open an issue.

## Contributing and credits

Issues and pull requests are welcome; see `CONTRIBUTING.md`. Credits are in `CREDITS.md`. AI Add-on Builder is an independent project by SyncWin, and it is not affiliated with or endorsed by Anthropic in any way.
