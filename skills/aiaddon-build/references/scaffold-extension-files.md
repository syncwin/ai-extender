# Scaffold extension: root file templates

Part of the scaffold recipe `scaffold-extension.md` (read it first: inputs, checks, naming, procedure). These are the templates for the root files the scaffold writes after the plugin manifest, skills and injection-screen step.

## Contents

- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `.gitignore` (public-safety preset)
- `.env.example`
- `PUBLIC-SAFETY.md`
- `.public-safety-allow` (only when an email is given)
- `evals/router/cases.json` (only with roles)

### `README.md`
Compose with these parts (one blank line between sections):
```
# <display>

<description>

**Version** 0.0.1 <DOT> <who><contact> <DOT> **License** <license>

## Skills

| Skill | Role |
|---|---|
| `<slug>` | Router |
| `<slug>-<role>` | <Role> |        (one row per role; with no roles a single row: `(none yet)` with an empty Role cell)

## Install

Cowork or claude.ai: upload the `.plugin` file as a custom plugin. Claude Code: add the marketplace or folder that holds this plugin, then install `<slug>`. Start it with `/<slug>` and describe what you need. Full steps for every app, and how to undo them, come in the install guide the packager writes next to the package.

<connectors section, when Composio is on>
<guardrail section, when the guardrail is on>
## Companion prompt

`prompts/<display-slug>.json` is a ready-made form for Prompt Builder. It is delivered next to the package, never inside it. Import it there, fill in the fields, and send it to Claude to start this plugin without typing the request from scratch.

## What it runs, reads, and sends

List every script, connector, and outside service here before you share this plugin.

Before a directory submission, add a square listing icon (PNG or JPEG, 512 to 2048 px) named icon in the .claude-plugin folder.
```
`<DOT>` is a space, the middle-dot character (U+00B7), a space. `<who>` = `**Author** <author>` and `**Company** <company>` (those given) joined by the same separator; `<contact>` = separator plus `**Contact** <email>` when an email is given. Drop empty parts so no empty slot is left between separators. `<display-slug>` = display name lowercased, every run of characters other than a-z and 0-9 turned into one hyphen, hyphens trimmed from both ends.

Connectors section (Composio on):
```
## Connectors

| Connector | Used by | Purpose | Auth | Data sent |
|---|---|---|---|---|
| Composio | all skills, when a task needs an outside app | one connection to 1,000+ apps (Gmail, Notion, Slack, CRMs) | each user's own Composio sign-in (OAuth) | only what a task sends to the app it uses |

In Chat or Cowork, open the plugin's Connectors tab and select Connect. Claude Code reuses a Composio connector you already have at this exact address instead of loading a second copy.
```
Injection screen section (guardrail on):
```
## Injection screen

After every web fetch, web search or connector call, Claude screens the returned text for instructions aimed at the model, following `references/screen-text.md` (a checklist, no script, no hook, nothing downloaded). Claude treats flagged content as data and asks you before acting on it. The screen is an instruction in this plugin's skills, so it works in chat, Cowork and Claude Code alike. To turn it off, remove the screen rule from the skill bodies.
```

### `CHANGELOG.md`
```
# Changelog

Newest first.

## 0.0.1: <today>

**Added**
- Initial structure.
```

### `LICENSE`
When the license is `MIT`: the text below with `<year>` = this year and `<holder>` = author, else company, else display. Any other license: the single line `License: <license>`.
```
MIT License

Copyright (c) <year> <holder>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### `.gitignore` (public-safety preset)
First these lines, a blank line, then the preset (the same text as the preset block in `aiaddon-review/references/public-safety.md`; use that file's block when it differs):
```
.DS_Store
*.plugin
*.zip
dist/
__pycache__/
*.pyc

# --- public-safety preset: private data never reaches git ---
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
id_rsa*
id_ed25519*
credentials*.json
service-account*.json
secrets.*
*.log
logs/
memory/
.claude/memory/
.claude/progress/
progress*.md
*.local.md
.claude/settings.local.json
.npmrc
.pypirc
.netrc
private/
# --- end public-safety preset ---
```

### `.env.example`
```
# Variables <display> reads. Names only, never values; real values stay in your environment or userConfig.
# EXAMPLE_VARIABLE=
```

### `PUBLIC-SAFETY.md`
`<contact_line>` is the email, or `none`.
```
# Public Safety

This repository is public. Only what is listed under "May be public" is published.

## May be public
- Source code, skills, agents and Markdown recipes
- Documentation, README, CHANGELOG, LICENSE
- Generic examples with placeholder values, `.env.example` (variable names only)
- Author contact chosen for publication: <contact_line>

## Never published
- Secrets: API keys, tokens, passwords, private keys, `.env` files, credentials
- Personal data: personal e-mails, phone numbers, addresses
- Client names and data; internal URLs and hosts
- Local absolute user paths; private notes, logs, memory or progress files

## Where private values live instead
- List each one here: `userConfig` (sensitive) or an environment variable documented in `.env.example`.

## Checks
- the scan-secrets and public-safety-scan recipes (`aiaddon-review/references/`) with git history before every release (working tree, full history, built packages)
- CI runs the same scan on every push and pull request
- Allowed false positives: `.public-safety-allow`, each with a reason in a comment

## If something leaks
Rotate the credential first, then remove it from history; never force-push without the owner's explicit OK.
```
Keep the Checks line aligned with how the public-safety scan is described in `aiaddon-review/references/public-safety.md`.

### `.public-safety-allow` (only when an email is given)
```
# Author contact the owner chose to publish. Only exact public values belong here.
email:*:<email>
```

### `evals/router/cases.json` (only with roles)
2-space indentation, trailing newline:
```
{ "_note": "Router cases: expected = first skill the router's Routing table must pick, or 'ask'. Checked by the route-check recipe (aiaddon-review/references/route-check.md).",
  "cases": [ ... ] }
```
Cases, in order: for each role, `{"prompt": "please <role> this for me", "expected": "<slug>-<role>"}` and `{"prompt": "I want to <role> it now", "expected": "<slug>-<role>"}`; then `{"prompt": "help me", "expected": "ask"}` and `{"prompt": "what should I do next", "expected": "ask"}`.
