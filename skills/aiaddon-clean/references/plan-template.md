# Clean-up plan template

Contents: header, overlap map, actions, keep-unique proof, approval.

## Header

Target, `before.json` totals (files, unique lines, exact and near duplicate paragraphs), archive folder, mode (dry-run).

## Overlap map

| # | Where (file:line) | Where else (file:line) | Kind | Differences |
|---|---|---|---|---|
| 1 | skills/a/SKILL.md:12 | skills/b/SKILL.md:9 | exact | none |
| 2 | ... | ... | near (0.78) | b adds one sentence |

Kind: exact, near, same topic, intentional repeat (keep; give the reason).

## Actions

One row per change. The smallest edit that removes the repeat.

| # | Action | Files touched | Result |
|---|---|---|---|
| 1 | Keep in a, replace in b with a pointer | skills/b/SKILL.md | b links to a |
| 2 | Merge b-only sentence into a | skills/a/SKILL.md | a holds both |
| 3 | Move file to archive | references/old.md | moved, not deleted |

## Keep-unique proof

For every paragraph that changes or leaves, every line that exists only there is listed with its new home.

| Original (file:line) | Unique line (short) | Lands at (file:line after the change) |
|---|---|---|
| skills/b/SKILL.md:11 | "Always ask for the invoice number first." | skills/a/SKILL.md:13 |

If a row has no landing place, the action is not allowed until it has one. Lines that are duplicated elsewhere verbatim are listed as `duplicate of file:line`.

## Approval

Ask once: "Apply this plan?" Nothing changes before a clear yes. After applying, run `prove.py`; paste its PASS line.
