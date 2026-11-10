# No-loss gate: details

Run before any merge is accepted (SKILL.md lists the rules).

## Script
`no_loss_check.py --old FILE --new FILE [--threshold 0.15] [--map-yaml FILE] [--sxs OUT] [--pairs OUT]`; exit 1 on any problem.
- Clauses: sentences, `;` parts and each `Why:` part. Significant words drop stopwords and words of 2 chars or fewer.
- Mapping: old items are headings and `name:`/`id:` values. The map file lists `was: [item, item]` per new item; each old item must appear exactly once.
- Downgrades: strong words (must, never, always, only, hook, ...) fewer than before, weaker words (should, may, guidance, ...) more than before, dropped capitalised MUST/NEVER/ALWAYS, fewer examples, missing numbers, tools, paths or URLs.
- `--sxs`: two-column old/new markdown, aligned by line. `--pairs`: each old clause beside its closest new clause with a verdict line, for the reviewer.

## Reviewer brief (fresh context, read-only)
"Read each OLD/NEW pair. Verdict per item: identical meaning / weaker / lost nuance / changed scope. For anything else quote the exact old phrase at risk. Do not edit." Report counts per verdict. A flagged item stays blocked until restored or the user approves it.

## Report table
| check | result | evidence |
|---|---|---|
| clause coverage | pass/fail | flags found, each resolved by quote or restore |
| mapping | | unmapped count |
| no downgrade | | script output |
| collateral diff | | files outside the merge touched, justified |
| old text preserved | | commit or archive path, side-by-side path |
| semantic review | | items reviewed, verdict counts |
| flagged items | | each item and the user's decision |

Limit: word coverage cannot prove emphasis or tone; the side-by-side file is for human review.
