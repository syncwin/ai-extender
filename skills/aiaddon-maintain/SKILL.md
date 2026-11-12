---
name: aiaddon-maintain
description: >
  Use for "update my agent so it only reads files", "update my skill", "split or merge my skills", "fix this plugin", "clean up", "this failed in production", "bump the version", "add a changelog entry", "migrate", or "customize this Cowork plugin". Updates existing Claude extensions and governs their versions: fix, extend, or refactor a plugin, skill, connector, agent, hook, or MCP server you already have; de-duplicate and shrink token use; bump semver; keep the changelog.
license: MIT
---

# AI Add-on Builder Maintainer

1. **Read everything** in the target first (all files). Identify type, current version, stable contract.
2. **Flow** by target: `references/updating.md`.
3. **Scope:** change only what was asked; confirm larger restructures.
4. **De-duplicate, version, log:** `references/versioning.md`. Same-session iterations stay under the current changelog entry.
   - One summary → changelog entry and every version field: follow `references/bump-version.md` with `<dir>` and the summary from `<notes.md>` (`--level keep` adds to the current entry without a bump).
   - What a release keeps, changes, adds, and drops: follow `references/release-diff.md` with `<old> <new>` (folders or packages).
   - Shared files (scratchpad and others) live once and are copied into each skill: follow `references/sync-shared.md` with `<dir>` and `.claude-plugin/shared-files.json`.
4a. **Public safety before and after every change:** follow `aiaddon-review/references/scan-secrets.md` (with history) on `<dir>` first and again on the result; keep the `.gitignore` preset, `PUBLIC-SAFETY.md` and `.env.example` intact (`aiaddon-review/references/public-safety.md`). Names stay inside the naming standard (`aiaddon/references/standards.md` section 1); a renamed slug is confirmed with the user and gets a migration note in the README and changelog.
4b. **Past leak remediation** (a secret or private value already in git, a package or a release; full steps in `aiaddon-review/references/public-safety.md` section 6), in this order: detect with the scan; tell the user; rotate or revoke the credential FIRST; rewrite history with `git filter-repo` (or BFG) on a backed-up mirror; force-push ONLY after the user's explicit OK for that exact push, never automatically; delete and re-create affected releases and tags and note forks; ask GitHub Support to purge cached views and PR refs; re-scan to prove zero traces.
5. Not authored here (downloaded/third-party)? Disclose the fork consequences first (versioning.md).
6. Re-validate with `aiaddon:aiaddon-review`, repackage with `aiaddon:aiaddon-package`.

Finish with the scratchpad (`aiaddon/references/scratchpad.md`).
