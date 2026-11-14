# Privacy Policy

AI Add-on Builder, published by SyncWin. Effective 2026-10-12.

## What we collect

Nothing. The plugin has no server, no analytics, no telemetry, and no account. SyncWin receives no data from your use of it.

## What runs, and where

- **Instructions** run inside your own Claude session. The plugin ships Markdown only: no scripts and no hooks. Claude follows the recipes with its own read, search and write tools and standard OS or git commands, only in the folders you point it at.
- **The injection screen** is a manual step (`skills/aiaddon-review/references/screen-text.md`): after each web fetch, web search or connector call, Claude screens that output for prompt injection and treats flagged text as data. Nothing is stored or sent.
- **Secret scan:** the scan-secrets recipe reads only the folders you name and shows any key it finds masked. It stores and sends nothing.

## Services you choose to use

- **Claude** (Anthropic) processes your conversation as it always does, under Anthropic's own terms and privacy policy.
- **Composio** is used only if you connect it and only for actions you ask for, such as publishing to GitHub. You sign in with your own Composio account, and Composio's privacy policy covers that data.
- **GitHub** is used only when you ask to publish, through your own Composio connection, GitHub connector, or `gh` login.

## Children

The plugin is a tool for building Claude extensions and is not directed at children under 18.

## Changes and contact

Changes to this policy are recorded in `CHANGELOG.md`. Questions: support@syncwin.com.
