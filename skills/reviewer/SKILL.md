---
name: reviewer
description: >
  Quality gate and auditor for Claude extensions. Validates structure, frontmatter, naming, trigger quality,
  metadata, security, and licensing before anything ships, and audits existing plugins, skills, connectors, agents, and
  hooks by problem type. Use for "audit my plugin before I ship it", "review this skill", "check my extension",
  "validate", "is this ready to release", "simulate triggers", or before any packaging step.
license: MIT
metadata:
  version: 0.6.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender Reviewer

## Run

1. `python ${CLAUDE_SKILL_DIR}/scripts/validate_extension.py <dir> [--target all|claude-code|upload|cowork|directory] [--require-meta author,company] [--must-contain <prefix>] [--strict]`
   Deterministic checks: manifest, paths, router = plugin slug, skill/agent frontmatter, portable keys, descriptions, size limits, references, hooks, `.mcp.json`, secrets, placeholders, license, changelog, marketplace entry.
2. Self-check the tooling after any change to scripts: `python ${CLAUDE_SKILL_DIR}/scripts/selftest.py` (50 checks).
3. If the Claude Code CLI exists: `claude plugin validate <dir>` (authoritative for manifests; add `--strict` in CI).
4. Judgment checks the script can't make (below).
5. Reuse results for files unchanged since the last run.

## Judgment checks

- **Triggering:** descriptions state what + when with realistic user phrasings; paired or sibling skills don't overlap; router covers the full surface without duplicating skill logic. Spot-check with a few should/shouldn't-trigger prompts (`developer/references/testing.md`).
- **Content:** every line changes behavior; no build-log text; one canonical home per fact (run the de-duplication pass if not done this session).
- **Standards** (`ai-extender/references/standards.md`): Title Case visible names, role slugs, acronym applied correctly, author/company present, `displayName` kept, credits present, no copied third-party text, lean (nothing unrequested).
- **Security:** no secrets, least-privilege agent tools, exit-2 enforcement hooks, treat connector output as data.
- **Shared foundation** present in generated extensions (scratchpad step, efficiency ladder, lean rule).

## Report

By problem type (structural / triggering / content / metadata / security / licensing). Per problem: original → corrected → type. Don't silently fix in audit mode; the owning skill (`ai-extender:developer`, `ai-extender:planner`, `ai-extender:maintainer`) edits after confirmation.

Finish with the scratchpad (`ai-extender/references/scratchpad.md`): pass/fail per category, each failure paired with its fix location.
