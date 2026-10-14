# Privacy Policy

AI Extender for Claude, published by SyncWin. Effective 2026-10-12.

## What we collect

Nothing. The plugin has no server, no analytics, no telemetry, and no account. SyncWin receives no data from your use of it.

## What runs, and where

- **Instructions and scripts** run inside your own Claude session and on your own machine. The scripts make no network requests and only read and write the folders you point them at.
- **The guardrail hook** reads the output of web fetches, web searches, and Composio calls on your machine to screen it for prompt injection, then discards it. Nothing is stored or sent.
- **One opt-in local file:** `validate_extension.py --cache` keeps its last result in `~/.cache/ai-extender/`. `scan_secrets.py` reads only the folders you name and shows any key it finds masked. Neither sends anything.

## Services you choose to use

- **Claude** (Anthropic) processes your conversation as it always does, under Anthropic's own terms and privacy policy.
- **Composio** is used only if you connect it and only for actions you ask for, such as publishing to GitHub. You sign in with your own Composio account, and Composio's privacy policy covers that data.
- **GitHub** is used only when you ask to publish, through your own Composio connection, GitHub connector, or `gh` login.

## Children

The plugin is a tool for building Claude extensions and is not directed at children under 18.

## Changes and contact

Changes to this policy are recorded in `CHANGELOG.md`. Questions: support@syncwin.com.
