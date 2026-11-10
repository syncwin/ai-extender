# Public Safety

Every extension this plugin creates, changes, reviews, packages or cleans is treated as a public repository, even when the user never says so. Nothing private may reach git, a package, a release or a listing. This is enforced by scripts, not by memory: `scan_secrets.py`, `validate_extension.py` (`X008` to `X013`) and the CI job.

## Contents

1. Public and private classification · 2. Plan line: split and threat model · 3. Required `.gitignore` preset · 4. `PUBLIC-SAFETY.md` template · 5. The scan · 6. Past leak remediation · 7. GitHub switches

## 1. Public and private classification

| Public (may be committed, packaged, released) | Private (never published; keep out of the repo, packages and releases) |
|---|---|
| Source code, skills, agents, hooks, scripts | Secrets: API keys, tokens, passwords, private keys, certificates, `.env` files, credentials files |
| Docs, README, CHANGELOG, LICENSE | Personal data: personal e-mail addresses, phone numbers, home addresses, IDs |
| Generic examples with placeholder values (`<your-key>`, `example.com`, `noreply` addresses) | Client names and client data, customer records, internal business details |
| Manifests, `.env.example` (names only, no values), `PUBLIC-SAFETY.md` | Internal URLs and hosts (intranet, private IPs, staging behind a login) |
| Tests and fixtures built from fake data (fake keys assembled at run time, never a literal) | Local absolute user paths (a Windows `Users` folder, `/home/<name>/`, `/Users/<name>/`) |
| The author's chosen public contact (allowlisted on purpose) | Private notes, scratch files, logs, memory and progress files, local settings |

Rules: classify every file and every value the extension will hold, in the plan. When unsure, treat it as private and ask. A value only the owner has (key, address, client name) is a user setting (`userConfig` with `"sensitive": true`, or an environment variable documented in `.env.example`), never a literal in a file.

## 2. Plan line: split and threat model

Every plan carries two lines, next to its component list:

- **Public/private split:** what ships public (source, docs, generic examples) and what stays private (every secret, personal or client value the extension will touch, and where each lives instead: `userConfig`, environment variable, the user's own folder).
- **Threat model:** one line naming what could leak and how it is stopped, for example: "a pasted key or client name ends up in a skill, a log, a fixture or git history; stopped by the `.gitignore` preset, the scan in CI and before every release, and `userConfig` for values."

## 3. Required `.gitignore` preset

Every extension has these lines in `.gitignore` from the first commit (the validator checks them, `X009`; `scaffold_extension.py` writes them):

```
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

Add the extension's own build output and caches below the preset. Never remove a preset line. Ignoring is not a cure: a file committed once stays in history (section 6).

## 4. `PUBLIC-SAFETY.md` template

Every extension has a `PUBLIC-SAFETY.md` at its root (`X010`). Copy this and fill the brackets:

```
# Public Safety

This repository is public. Only what is listed under "May be public" is published.

## May be public
- Source code, skills, agents, hooks and scripts
- Documentation, README, CHANGELOG, LICENSE
- Generic examples with placeholder values, `.env.example` (variable names only)
- Author contact chosen for publication: [address or "none"]

## Never published
- Secrets: API keys, tokens, passwords, private keys, `.env` files, credentials
- Personal data: personal e-mails, phone numbers, addresses
- Client names and data; internal URLs and hosts
- Local absolute user paths; private notes, logs, memory or progress files

## Where private values live instead
- [setting name]: `userConfig` (sensitive) or environment variable [NAME], documented in `.env.example`

## Checks
- `python <skills>/aiaddon-review/scripts/scan_secrets.py . --history` before every release
- CI runs the same scan on every push and pull request
- Allowed false positives: `.public-safety-allow`, each with a reason in a comment

## If something leaks
Rotate the credential first, then remove it from history (past leak remediation in the review skill's public-safety reference).
```

`.env.example` lists every variable the extension reads, names only (`NAME=`), never a value (`X011`: required when the extension's connectors, hooks, servers or scripts read environment variables; the scaffolder always writes one; when present it must hold no values).

## 5. The scan

`python ${CLAUDE_SKILL_DIR}/scripts/scan_secrets.py <folder> [--history] [--artifacts <dir-or-zip> ...] [--allowlist FILE] [--json]` (pure Python standard library, no installs). It reads files only, masks every value, and exits 1 on any finding. Every finding is blocking: there is no warning level.

- **Working tree:** files git would publish (tracked plus untracked and not ignored); a plain folder or a package when not a git repo.
- **Full history (`--history`):** every line ever added on any ref, from `git log --all -p`, and any private file ever committed. A key deleted last week is still found.
- **Built artifacts (`--artifacts`, and inside every `.zip` or `.plugin` found):** the contents of produced packages, including nested archives.
- **Looks for:** GitHub, OpenAI, Anthropic, AWS, Slack and Google keys and tokens, private key blocks, `Bearer` tokens, `password=` and key-like assignments, high-entropy strings, e-mail addresses other than `noreply` or placeholders, Windows, macOS and Linux absolute user paths, internal hosts, and private file names (`.env`, key files, logs, memory or progress notes).
- **Allowlist:** `.public-safety-allow` at the folder root, one `<rule>:<path-glob>[:<value-substring>]` per line, `#` comments. Only exact public false positives belong there; a real credential is rotated, never allowlisted.
- The validator runs the same engine (`X008` tree, `X012` history, `X013` packages); `aiaddon-package` runs it before building and again on the produced files and refuses to continue on any finding.

## 6. Past leak remediation

Use when a scan finds a secret or private value already committed, pushed, packaged or released. Do the steps in this order; never skip ahead to rewriting history.

1. **Detect:** run `scan_secrets.py <repo> --history --artifacts dist`; list each finding (rule, file, commit, masked value) and where copies may exist (remote branches, tags, releases, packages, forks, PR refs).
2. **Tell the user** plainly, in one short message: what leaked, since when, where it is visible. Do not repeat the value.
3. **Rotate or revoke the credential first,** at the provider (the user does this; give the link or steps). Treat it as compromised from the moment it was public. For personal data (a private e-mail, a client name) there is nothing to rotate: note the exposure and continue.
4. **Rewrite history** to remove it from every commit: `git filter-repo --replace-text` (values file kept outside the repo) or `--path <file> --invert-paths`; or BFG Repo-Cleaner. Work on a fresh mirror clone, never the only copy. Back up the repository first.
5. **Force-push only after the user explicitly says yes** to that exact push (naming the repository and the branches and tags it rewrites). Never force-push automatically, and never to a protected branch without the owner's say-so. Prefer `--force-with-lease`.
6. **Delete and re-create affected releases and tags** that carried the value or a package built from it; rebuild packages from the cleaned tree. Forks and clones keep the old history and cannot be cleaned from here: tell the user.
7. **Ask GitHub Support** to purge cached views and pull-request refs (`refs/pull/*`) that still hold the old commits, and to remove sensitive data from forks if needed.
8. **Re-scan** the cleaned repository (`--history`), every rebuilt package and a fresh clone; the result must show zero findings. Report the proof and anything that cannot be fixed from here.

## 7. GitHub switches

For every public repository the extension lives in, tell the user to enable, in Settings > Code security: secret scanning, push protection, and private vulnerability reporting. Push protection stops a push containing a recognised secret before it lands. These complement, and never replace, the scan above.
