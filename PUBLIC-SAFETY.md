# Public Safety

This repository is public. Only what is listed under "May be public" is published.

## May be public
- Source code, skills, agents, hooks and scripts
- Documentation, README, CHANGELOG, LICENSE
- Generic examples with placeholder values, `.env.example` (variable names only)
- Author contact chosen for publication: support@syncwin.com

## Never published
- Secrets: API keys, tokens, passwords, private keys, `.env` files, credentials
- Personal data: personal e-mails, phone numbers, addresses
- Client names and data; internal URLs and hosts
- Local absolute user paths; private notes, logs, memory or progress files

## Where private values live instead
- None: the plugin needs no secrets. Connector sign-ins happen in the user's own account.

## Checks
- `python skills/aiaddon-review/scripts/scan_secrets.py . --history` before every release
- CI runs the same scan on every push and pull request (`.github/workflows/ci.yml`, job `public-safety`)
- Allowed false positives: `.public-safety-allow` (the public contact address above)

## If something leaks
Rotate the credential first, then remove it from history: `skills/aiaddon-review/references/public-safety.md`, section 6. Never force-push without the owner's explicit OK.
