---
name: aix-maintainer
description: >
  Use when updating an existing Claude plugin, skill, connector, agent, hook or MCP server: fix, extend, refactor, split or merge, shrink token use, migrate, "bump the version", "add a changelog entry", "customize this Cowork plugin". Governs semver and the changelog.
license: MIT
metadata:
  displayName: "AI Extender Maintainer"
  version: 1.5.0
  author: "@wasimness"
  company: SyncWin
  plugin: ai-extender
---

# AI Extender Maintainer

1. **Read everything** in the target first (all files). Identify type, current version, stable contract.
2. **Flow** by target: `references/updating.md`.
3. **Scope:** change only what was asked; confirm larger restructures.
4. **De-duplicate, version, log:** `references/versioning.md`. Same-session iterations stay under the current changelog entry.
   - One summary → changelog entry and every version field: `python ${CLAUDE_SKILL_DIR}/scripts/bump_version.py <dir> --summary-file <notes.md>` (`--level keep` adds to the current entry without a bump).
   - What a release keeps, changes, adds, and drops: `scripts/release_diff.py <old> <new>` (folders or packages).
   - Shared files (scratchpad and others) live once and are copied into each skill: `scripts/sync_shared.py <dir>` with `.claude-plugin/shared-files.json`.
5. Not authored here (downloaded/third-party)? Disclose the fork consequences first (versioning.md).
6. Re-validate with `ai-extender:aix-reviewer`, repackage with `ai-extender:aix-packager`.

Finish with the scratchpad (`aix/references/scratchpad.md`).
