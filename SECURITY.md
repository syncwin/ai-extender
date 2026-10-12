# Security Policy

## Scope

AI Extender for Claude is Markdown instructions plus local Python scripts. Its scripts make no network requests and it collects no data. It declares one connector, Composio, at the shared address `https://connect.composio.dev/mcp`, with no account or key inside the plugin: each user connects it and signs in with their own Composio account, and Claude uses it only for GitHub or another app the user asked for. One hook runs in Claude Code and Cowork: after a web fetch, web search, or Composio call, it screens that output locally for prompt injection and warns Claude. It reads nothing else, sends nothing, and exits quietly on any error. The scripts write only to folders you point them at, and they call other scripts in this plugin through `subprocess` with fixed argument lists. No shell is involved. The README lists the few things Claude may do on your behalf (a folder check in Cowork, fetching Anthropic's docs when you ask, GitHub or another app through Composio when you ask).

## Reporting a vulnerability

Email support@syncwin.com with what you found and the steps to reproduce it. GitHub's private reporting also works when enabled. Please don't open a public issue for a vulnerability: we aim to reply within five working days, and fixes ship as a patch release with a changelog entry.

## What counts

- A script that runs input as code, writes outside its target folder, follows a symlink out of it, or exposes a secret.
- A skill or agent instruction that could lead Claude into a destructive or external-write action the user didn't ask for.
- Anything in the repository that leaks private data.

## Supported versions

Only the latest release gets fixes.
