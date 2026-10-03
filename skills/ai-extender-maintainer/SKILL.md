---
name: ai-extender-maintainer
description: >
  Updates existing Claude extensions and governs their versions: fix, extend, or refactor a plugin, skill, connector,
  agent, hook, or MCP server you already have; de-duplicate and shrink token use; bump semver; keep the changelog.
  Use for "update my agent so it only reads files", "update my skill", "split or merge my skills", "fix this plugin", "clean up", "this failed in
  production", "bump the version", "add a changelog entry", "migrate", or "customize this Cowork plugin".
license: MIT
metadata:
  version: 0.5.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Maintainer

1. **Read everything** in the target first (all files). Identify type, current version, stable contract.
2. **Flow** by target: `references/updating.md`.
3. **Scope:** change only what was asked; confirm larger restructures.
4. **De-duplicate, version, log:** `references/versioning.md`. Same-session iterations stay under the current changelog entry.
5. Not authored here (downloaded/third-party)? Disclose the fork consequences first (versioning.md).
6. Re-validate with `ai-extender-reviewer`, repackage with `ai-extender-packager`.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
