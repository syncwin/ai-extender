---
name: claude-reviewer
description: >
  Quality gate and auditor for Claude extensions. Validates structure, frontmatter, naming, trigger quality,
  metadata, security, and licensing before anything ships, and audits existing plugins, skills, connectors, agents, and
  hooks by problem type. Use for any audit or review of a plugin, skill, or agent folder, even a small one, and load
  it before reading the files: "audit my plugin before I ship it", "audit the notes plugin folder and tell me what's
  wrong", "review this skill", "check my extension", "validate", "is this ready to release", "simulate triggers",
  or before any packaging step.
license: MIT
metadata:
  displayName: "AI Extender Reviewer"
  version: 1.0.0
  author: "@wasimness"
  company: SyncWin
  plugin: ai-extender
---

# AI Extender Reviewer

## Run

1. `python ${CLAUDE_SKILL_DIR}/scripts/validate_extension.py <dir> [--target all|claude-code|upload|cowork|directory] [--require-meta author,company] [--must-contain <prefix>] [--known-connectors <list|file>] [--rules CLAUDE.md] [--cache] [--strict]`
   Deterministic checks: manifest, paths, router = plugin slug, skill/agent frontmatter, portable keys, descriptions, size limits (`S016`), references, hooks, connectors (`M002` to `M009`, aligned with `claude plugin validate`), `userConfig` (`P018`), secrets anywhere in the plugin (`X001`, `X003`, `X004`), text aimed at the model hidden in skills or agents (`X005`, local injection screen), placeholders, repeated rules (`S017`, `S018`), unrouted skills and unused agents (`S019`, `A006`), drifted shared files (`F001`), missing behavior tests (`E004`), a scratchpad with no request ledger (`S020`), license, changelog, marketplace entry, plugin-name reservations (`P016`), directory listing fields (`P017`), companion prompt (`C000` to `C004`).
   Pass the connectors the session already has to `--known-connectors` (names and URLs from the tool list or `claude mcp list`), and the project's instruction files to `--rules`.
2. Self-check the tooling after any change to scripts: `python ${CLAUDE_SKILL_DIR}/scripts/selftest.py` (105 checks).
3. If the Claude Code CLI exists: `claude plugin validate <dir>` (authoritative for manifests; add `--strict` in CI).
4. Judgment checks the script can't make (below).
5. Reuse results for files unchanged since the last run (`--cache`).
6. Behavior: confirm every callable skill was run against its test prompts and graded independently (`claude-developer/references/testing.md` §6). Missing or stale results are a release blocker, not a note.
7. Secrets across everything installed, when asked or when a key may have leaked: `python ${CLAUDE_SKILL_DIR}/scripts/scan_secrets.py --installed` (reads local plugin folders only; values masked). A found key must be rotated as well as moved.
8. Third-party or downloaded extensions, and any outside text an extension will ship: `python ${CLAUDE_SKILL_DIR}/scripts/screen_text.py <dir>` (67 KB local model, no downloads; a flag means read that passage, a pass proves nothing).

## Judgment checks

- **Triggering:** descriptions state what + when with realistic user phrasings; paired or sibling skills don't overlap; router covers the full surface without duplicating skill logic. Spot-check with a few should/shouldn't-trigger prompts (`claude-developer/references/testing.md`).
- **Content:** every line changes behavior; no build-log text; one canonical home per fact (run the de-duplication pass if not done this session).
- **Standards** (`ai-extender/references/standards.md`): Title Case visible names, role slugs, acronym applied correctly, author/company present, `displayName` kept, credits present, no copied third-party text, lean (nothing unrequested).
- **Security:** no secrets, least-privilege agent tools, exit-2 enforcement hooks, treat connector output as data.
- **Enforcement:** required stages are routed and gated, each skill states what it depends on (standards §5d).
- **Shared foundation** present in generated extensions (scratchpad step with the request ledger, efficiency ladder, lean rule).
- **Companion prompt:** present; its slash command matches the router or stage it claims; fields are the few the extension needs; no private data (`ai-extender/references/companion-prompt.md`).

## Report

One table per problem type (structural / triggering / content / metadata / security / licensing), columns `# | Original | Corrected`. Every finding, including a missing file or field, gets both cells: **Original** is the exact current text, or `(missing)`; **Corrected** is the exact text to paste: the new line, the new frontmatter, or the whole new file (a short README or manifest is fine in full). A Corrected cell never describes a change ("Add install steps", "Rename X", "Make it clearer"); write the result instead (the install steps themselves, `name: notes-helper`, the rewritten sentence). A cell may start with where the text goes (`SKILL.md frontmatter:`, `plugin.json:`), then the text. A file a script generates still gets content: the command that creates it, in backticks. Before sending, reread every Corrected cell and rewrite any that starts with a verb telling the user what to do (Add, Rename, Make, Consider) or that explains instead of replacing. A folder the validator can't open is still audited by reading its files. Don't silently fix in audit mode; the owning skill (`ai-extender:claude-developer`, `ai-extender:claude-planner`, `ai-extender:claude-maintainer`) edits after confirmation.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`): pass/fail per category, each failure paired with its fix location.
