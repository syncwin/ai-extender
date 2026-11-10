---
name: aiaddon-package
description: >
  Use when an extension is ready to ship, install, share, or hand over: "package my extension as a zip for upload", "make a .plugin for Cowork", "push this to GitHub", "prepare a private marketplace". Packages and delivers a validated Claude extension: Cowork .plugin files, single-skill .zip uploads, plugin folders, and private git marketplaces, with correctly named, versioned download files.
license: MIT
metadata:
  displayName: "AI Add-on Builder Packager"
  version: 0.1.0
  author: "@wasimness"
  company: SyncWin
  plugin: aiaddon
---

# AI Add-on Builder Packager

1. Run `aiaddon:aiaddon-review` on the exact files first (the script below re-runs it and blocks on errors).
1a. **Public safety gate:** `python <tools>/scan_secrets.py <dir> --history` (copy `aiaddon-review/scripts/` into the working folder once, like the other scripts) must pass before anything is built or released; `package_extension.py` runs the same scan on the folder, refuses to build on any finding, and scans inside the produced zip or `.plugin` (nested archives included) before it keeps it. Never override it; fix the finding, rotate the credential, and see `aiaddon-review/references/public-safety.md` section 6 if it is already in history or a release.
2. Use the target settled in the plan; ask only if none was settled. Never produce all by default. Formats, marketplace entries, checks: `references/targets.md`; routes, release prep, organization rollout: `references/distribution-routes.md`; Anthropic directory: `references/directory-checklist.md`.
3. Cowork session: `references/cowork.md`. User asked for GitHub, or the extension already lives in a repo they keep in sync: `references/github.md` (push, tag, orphan cleanup; confirm before the first push). Uses the Composio connector when connected, else a GitHub connector or `gh`; with none, hand over the prepared repo.
4. Ask once which companion prompt files they need: Markdown (`md`), Prompt Builder JSON (`json`), or `both` (default). Only when it is relevant (they want the JSON and may not know the tool), add the one neutral line about Prompt Builder from `references/prompt-builder.md`, which holds the link (`prompt_builder_url`). Never promote it or invent a link.
5. Build: `python ${CLAUDE_SKILL_DIR}/scripts/package_extension.py <dir> --format plugin|zip --out <dir> [--repo owner/repo] [--previous <old package>] [--require-evals] [--prompts md|json|both]`. Filename = visible Title Case name + ` v<version>` in the officially required format. It always creates or checks the companion prompt first (`scripts/companion_prompt.py`, rules in `aiaddon/references/companion-prompt.md`) and copies it next to the package as `<Name> v<version> prompt.md` (raw Markdown) and/or the Prompt Builder JSON, both generated from the same source; a broken prompt stops the build. It also writes `<Name> v<version> install.md` (desktop app, web, Code tab, terminal, how to undo each, and what the prompt files are; `scripts/install_guide.py`), reports the release diff against the previous package, flags missing or stale behavior tests, and keeps an unchanged package instead of rebuilding it (`--force` rebuilds).
6. Present the validation result (the validator's pass line and target, from step 1), then the package, the install guide, and only the companion prompt files the user chose, with two or three lines on how to use them and one example prompt to try. Add the Prompt Builder line only as step 4 allows (only when relevant, never for `md` only). Never claim delivery without the file existing.

Finish with the scratchpad (`aiaddon/references/scratchpad.md`).
