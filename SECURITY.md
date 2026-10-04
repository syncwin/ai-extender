# Security Policy

## Scope

AI Extender for Claude is Markdown instructions plus local Python scripts. It makes no network requests of its own and collects no data. The scripts write only to folders you point them at, and they call other scripts in this plugin through `subprocess` with fixed argument lists, never a shell. The README lists the few things Claude may do on your behalf (a folder check in Cowork, fetching Anthropic's docs when you ask, GitHub when you ask).

## Reporting a vulnerability

Email support@syncwin.com with what you found and the steps to reproduce it. You can also use GitHub's private vulnerability reporting on this repository if it's enabled. Please don't open a public issue for a vulnerability. We aim to reply within five working days; fixes ship as a patch release with a changelog entry.

## What counts

- A script that runs input as code, writes outside its target folder, follows a symlink out of it, or exposes a secret.
- A skill or agent instruction that could lead Claude into a destructive or external-write action the user didn't ask for.
- Anything in the repository that leaks private data.

## Supported versions

Only the latest release gets fixes.
