---
name: claude-packager
description: >
  Packages and delivers a validated Claude extension: Cowork .plugin files, single-skill .zip uploads, plugin folders,
  and private git marketplaces, with correctly named, versioned download files. Use when an extension is ready to ship,
  install, share, or hand over: "package my extension as a zip for upload", "make a .plugin for Cowork", "push this to
  GitHub", "prepare a private marketplace".
license: MIT
metadata:
  version: 0.9.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Packager

1. Run `ai-extender:claude-reviewer` on the exact files first (the script below re-runs it and blocks on errors).
2. Confirm target(s); never produce all by default. Formats, marketplace entries, checks: `references/targets.md`; routes, release prep, organization rollout: `references/distribution-routes.md`; Anthropic directory: `references/directory-checklist.md`.
3. Cowork session: `references/cowork.md`. User asked for GitHub, or the extension already lives in a repo they keep in sync: `references/github.md` (push, tag, orphan cleanup; confirm before the first push).
4. Build: `python ${CLAUDE_SKILL_DIR}/scripts/package_extension.py <dir> --format plugin|zip --out <dir>`. Filename = visible Title Case name + ` v<version>` in the officially required format.
5. Present the file with two or three lines on how to install it and one example prompt to try. Never claim delivery without the file existing.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`).
