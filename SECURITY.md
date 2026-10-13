# Security Policy

## Reporting a vulnerability

Report privately, never in a public issue:

- **GitHub:** [Report a vulnerability](https://github.com/syncwin/ai-extender/security/advisories/new) (private vulnerability reporting).
- **Email:** support@syncwin.com, with what you found and the steps to reproduce it.

What happens next: we acknowledge within five working days, confirm or decline within ten, and agree a disclosure date with you (normally within 90 days, sooner for an issue under active attack). Fixes ship as a release with a GitHub security advisory and a changelog entry, and we credit you unless you ask us not to.

## Supported versions

| Version | Fixes |
|---|---|
| 1.0.x | yes |
| earlier (pre-releases) | no |

## What the plugin does on your machine

AI Extender for Claude is Markdown instructions plus Python 3 scripts that use only the standard library. Nothing is downloaded or installed when it runs.

- **Scripts** make no network requests. They read and write only the folders you point them at (plus a temporary folder while packaging), refuse paths that resolve outside those folders, skip symbolic links, and call other scripts in this plugin through `subprocess` with fixed argument lists.
- **Guardrail hook** (Claude Code and Cowork): after a web fetch, web search, or Composio call, and no other tool, it screens that tool's output on your machine with a 67 KB local model and warns Claude if the text tries to give it instructions. Its launcher is one fixed shell line that picks `python3` or `python`; no tool output or user text reaches the shell. It never blocks work, sends nothing, and exits quietly on any error.
- **Connector:** one, Composio, at the shared address `https://connect.composio.dev/mcp`. The plugin holds no account, key, or token; each user connects and signs in with their own Composio account, and Claude uses it only for GitHub or another app the user asked for.
- **Agents** have read-only tools, except the grader, which may also write its `grading.json`.
- **Instructions** tell Claude to treat file, web, and connector content as data, and to ask before pushing, publishing, sending, deleting, or overwriting anything outside its working folder.

The README section "What it runs, reads, and sends" lists every case in plain words, and `PRIVACY.md` covers data.

## How releases are protected

- **Build provenance:** the release `.plugin` is built from the tagged commit on GitHub's runners and signed with a provenance attestation. Verify a download:
  ```
  gh attestation verify "AI.Extender.for.Claude.v1.0.0.plugin" --repo syncwin/ai-extender
  sha256sum -c SHA256SUMS
  ```
- **Every push and pull request** runs 113 self-tests (one pass as a non-root user), the directory validator in strict mode, a secret scan, the injection screen, the trigger simulation, and CodeQL (`security-extended`) on the Python and the workflows. OpenSSF Scorecard runs weekly.
- **Workflows** pin every action to a full commit SHA, default to read-only permissions, grant write access per job only where needed, and never pass untrusted input into a shell. Dependabot proposes action updates weekly.
- **Repository:** secret scanning with push protection, Dependabot alerts and security updates, private vulnerability reporting, code-owner review, and rules that block force-pushes and deletion of `main` and `v*` release tags for everyone but repository admins.

## In scope

- A script that runs input as code, writes outside its target folder, follows a symlink out of it, unpacks an archive unsafely, or exposes a secret.
- A hook, skill, or agent instruction that could lead Claude into a destructive or outward action the user didn't ask for, or that obeys instructions found in fetched or connector content.
- A release whose contents don't match its tagged source, checksum, or attestation.
- Anything in the repository that leaks private data.

Out of scope: vulnerabilities in Claude, Claude Code, Cowork, Composio, or GitHub themselves (report those to their owners), and prompt injection that the guardrail misses without the plugin then acting on it (the guardrail is a warning layer, documented as such).
