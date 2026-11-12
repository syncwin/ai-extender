---
name: aiaddon-clean
description: >
  Use for "clean up my plugin", "find duplicate content across my skills", "merge overlapping skills", "shrink my plugin without losing anything", "de-duplicate my skills", "deep clean this extension", or "what overlaps in my plugin". Deep clean-up and de-duplication of Claude plugins and skills without losing anything unique: script-only inventory, overlap map, a merge plan with a keep-unique proof, a hard stop for approval, then the smallest diffs and a before/after proof. Dry-run by default; never deletes (moves to an archive folder).
license: MIT
---

# AI Add-on Builder Cleaner

Goal: a smaller, clearer extension where **no unique line is lost**. Scripts do the counting; a cheap model only reads what the scripts flag. Dry-run unless the operator approves a plan.

**Recipes, not scripts:** every step below is a Markdown recipe in `references/` that you follow with the built-in tools (Read, Glob, Grep, Write, Edit) and standard OS or git commands only. Nothing here runs Python. Never put a `/root/.claude` or `~/.claude` path in a shell command.

| Step | Recipe |
|---|---|
| Inventory and overlap map | `references/inventory.md` |
| No-loss check | `references/no-loss-check.md` |
| Archive a file (move, never delete) | `references/archive.md` |
| Keep-unique proof | `references/prove.md` |

## No-loss gate (non-negotiable)

No merge, shortening or de-duplication of rules, instructions or skills is accepted until every check passes. **Preserve over compress:** when unsure whether wording carries nuance, keep the original verbatim. Merging may only remove exact or near-exact repetition; never paraphrase a unique clause. Hedges, qualifiers, examples, exceptions, ordering cues ("first", "before", "only after") and tone words are nuance.

1. **Clause coverage.** Split OLD into clauses (sentences, `;` parts, each "Why:" separately). Flag a clause when more than 15% of its significant words are missing from NEW. Resolve every flag by quoting the exact new sentence with the same meaning, or restore the wording. Zero unresolved flags.
2. **Mapping.** Every old item (rule, section, skill) maps to exactly one new item (`was: [..]` field or a map table). Unmapped fails.
3. **No downgrade.** must/should levels, hook vs guidance, MUST/NEVER/ALWAYS, numbers, examples, named tools, paths and URLs never weaken.
4. **Collateral diff.** Outside the merged files only references (numbers, names, versions) may change; anything else is listed and justified.
5. **Old text recoverable** (git history or archive) and an old-to-new map is written.
6. **Side-by-side file, always** (not optional): follow `references/no-loss-check.md` with `--sxs <out>.md`; point the user to it.
7. **Semantic review.** After the check passes, an independent reviewer in a fresh context (`aiaddon:aiaddon-review` skill of this plugin or a read-only subagent, never the one that merged) reads each old item beside its new text (`--pairs <out>.md`) and gives a verdict per item: identical meaning / weaker / lost nuance / changed scope, quoting the old phrase at risk. Anything but "identical meaning" blocks the merge until restored or the user approves that item.
8. **Report** a table `check | result | evidence` (include semantic review: items reviewed, verdict counts; every flagged item with the user's decision). State the limit: word coverage cannot prove emphasis or tone.

Run the check by following `references/no-loss-check.md` with `--old OLD.md --new NEW.md [--map-yaml MAP] --sxs sxs.md --pairs pairs.md`; any problem means FAIL. Details of the gate: `references/no-loss-gate.md`.

## Workflow

1. **Inventory (script only, no LLM).** Work on a copy or a git worktree of the target as `<before>`.
   Follow `references/inventory.md` with `<before> --out before.json`.
   Lists files, headings, normalized line hashes, exact duplicate paragraphs and near-duplicate paragraphs (5-word shingles, Jaccard 0.6).
2. **Overlap map.** From `before.json` only: group findings by file pair (exact, near, shared headings). Read just the flagged paragraphs (line ranges), never whole folders. Classify each as: identical, near (differences listed), same topic in two places, or intentional repeat (keep, say why).
3. **Plan with keep-unique proof.** `references/plan-template.md`. Every merge or removal lists, per affected paragraph, where each unique line lands (`file:line` in the surviving text). A line that exists nowhere else is unique and must survive.
4. **HARD STOP.** Show the plan and wait for the operator's explicit yes. No file changes before it, none for anything not in the approved plan. Dry-run output is the default end of a run.
5. **Smallest diffs.** Edit in place; replace a duplicate with a one-line pointer only when the plan says so. Files to remove go to the archive, never deleted:
   ```
   references/archive.md <root> <relative-file> --archive <archive-dir> [--apply]
   ```
   (dry-run without `--apply`).
6. **Prove.** Re-run the inventory on the result and the proof against the untouched `<before>`:
   ```
   references/prove.md <before> <after> --archive <archive-dir>
   ```
   Expected output: `PASS zero unique lines lost` (exit 0). The no-loss gate above runs on every merged text and must pass before the merge is accepted. The plugin's evals and `aiaddon:aiaddon-review` run before and after, and both are reported. Any lost line: restore it and re-run; the script's verdict is final.

## Public safety (every clean-up)

- Follow `aiaddon-review/references/scan-secrets.md` (with history) on `<before>` first and again on the result: a clean-up never moves, merges or archives a secret into a new place, and the `.gitignore` preset, `PUBLIC-SAFETY.md` and `.env.example` stay.
- A secret or private value found in git history, a package or a release starts past leak remediation, not a merge: detect, tell the user, rotate or revoke FIRST, rewrite history with `git filter-repo` (or BFG), force-push ONLY after the user's explicit OK, delete and re-create affected releases and tags (note forks), ask GitHub Support to purge cached views and PR refs, then re-scan to prove zero traces (`aiaddon-review/references/public-safety.md` section 6). Never auto force-push.

## Rules

- Dry-run by default. Approved runs change only what the plan lists.
- Never delete. Moves go to the archive folder named in the plan; the operator empties it.
- Token-lean: scripts first, read line ranges only, smallest model for reading; report counts, not file dumps.
- Deliberate repeats (a rule restated where it is enforced, a reference loaded on its own) are not duplicates: keep them and note why in the plan.
- Never rename or restructure beyond the plan. Version and changelog follow `aiaddon:aiaddon-maintain`.
- Details: `references/workflow.md` (report fields, thresholds, edge cases).

Finish with the scratchpad (`aiaddon/references/scratchpad.md`).
