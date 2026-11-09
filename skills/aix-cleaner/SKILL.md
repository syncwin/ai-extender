---
name: aix-cleaner
description: >
  Use for "clean up my plugin", "find duplicate content across my skills", "merge overlapping skills", "shrink my plugin without losing anything", "de-duplicate my skills", "deep clean this extension", or "what overlaps in my plugin". Deep clean-up and de-duplication of Claude plugins and skills without losing anything unique: script-only inventory, overlap map, a merge plan with a keep-unique proof, a hard stop for approval, then the smallest diffs and a before/after proof. Dry-run by default; never deletes (moves to an archive folder).
license: MIT
metadata:
  displayName: "AI Extender Cleaner"
  version: 1.5.0
  author: "@wasimness"
  company: SyncWin
  plugin: ai-extender
---

# AI Extender Cleaner

Goal: a smaller, clearer extension where **no unique line is lost**. Scripts do the counting; a cheap model only reads what the scripts flag. Dry-run unless the operator approves a plan.

**Script paths (E9):** copy the scripts once per session into the working folder, then run them from there. Never put a `/root/.claude` or `~/.claude` path in a shell command.

```bash
mkdir -p ./tools && cp -r "${CLAUDE_SKILL_DIR}/scripts" ./tools/aix-cleaner
```

Always run with `python -B` (no bytecode). Python 3.9+, standard library only.

## Workflow

1. **Inventory (script only, no LLM).** Work on a copy or a git worktree of the target as `<before>`.
   `python -B ./tools/aix-cleaner/scripts/inventory.py <before> --out before.json`
   Lists files, headings, normalized line hashes, exact duplicate paragraphs and near-duplicate paragraphs (5-word shingles, Jaccard 0.6).
2. **Overlap map.** From `before.json` only: group findings by file pair (exact, near, shared headings). Read just the flagged paragraphs (line ranges), never whole folders. Classify each as: identical, near (differences listed), same topic in two places, or intentional repeat (keep, say why).
3. **Plan with keep-unique proof.** `references/plan-template.md`. Every merge or removal lists, per affected paragraph, where each unique line lands (`file:line` in the surviving text). A line that exists nowhere else is unique and must survive.
4. **HARD STOP.** Show the plan and wait for the operator's explicit yes. No file changes before it, none for anything not in the approved plan. Dry-run output is the default end of a run.
5. **Smallest diffs.** Edit in place; replace a duplicate with a one-line pointer only when the plan says so. Files to remove go to the archive, never deleted:
   `python -B ./tools/aix-cleaner/scripts/archive.py <root> <relative-file> --archive <archive-dir> [--apply]` (dry-run without `--apply`).
6. **Prove.** Re-run the inventory on the result and the proof against the untouched `<before>`:
   `python -B ./tools/aix-cleaner/scripts/prove.py <before> <after> --archive <archive-dir>`
   It must print `PASS zero unique lines lost` (exit 0). Also run the plugin's evals and `ai-extender:aix-reviewer` before and after, and report both. Any lost line: restore it and re-run; do not argue with the script.

## Rules

- Dry-run by default. Approved runs change only what the plan lists.
- Never delete. Moves go to the archive folder named in the plan; the operator empties it.
- Token-lean: scripts first, read line ranges only, smallest model for reading; report counts, not file dumps.
- Deliberate repeats (a rule restated where it is enforced, a reference loaded on its own) are not duplicates: keep them and note why in the plan.
- Never rename or restructure beyond the plan. Version and changelog follow `ai-extender:aix-maintainer`.
- Details: `references/workflow.md` (report fields, thresholds, edge cases).

Finish with the scratchpad (`aix/references/scratchpad.md`).
