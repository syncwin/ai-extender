---
name: ai-extender-packager
description: >
  Packages and delivers a validated Claude extension: Cowork .plugin files, single-skill .zip uploads, plugin folders,
  and private git marketplaces, with correctly named, versioned download files. Use when an extension is ready to ship,
  install, share, or hand over: "package my extension as a zip for upload", "make a .plugin for Cowork", "push this to
  GitHub", "prepare a private marketplace".
license: MIT
metadata:
  version: 0.5.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Packager

1. Run `ai-extender-reviewer` on the exact files first (the script below re-runs it and blocks on errors).
2. Confirm target(s); never produce all by default. Formats, marketplace entries, checks: `references/targets.md`; routes, release prep, organization rollout: `references/distribution-routes.md`.
3. Cowork session: `references/cowork.md`. GitHub tools present (or a repo exists): `references/github.md`; pushing and orphan cleanup are part of every release.
4. Build: `python ${CLAUDE_SKILL_DIR}/scripts/package_extension.py <dir> --format plugin|zip --out <dir>`. Filename = visible Title Case name + ` v<version>` in the officially required format.
5. Present the file; never claim delivery without it existing.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
