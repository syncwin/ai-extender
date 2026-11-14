# No-loss check recipe (replaces no_loss_check.py)

## Purpose and when
Prove that a merge, shortening or de-duplication lost no nuance. Run on every merged or shortened text before the merge is accepted (SKILL.md, no-loss gate). Word coverage cannot prove emphasis or tone, so the independent semantic reviewer pass stays mandatory (`references/no-loss-gate.md`).

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `--old FILE` | required | The text before the change. |
| `--new FILE` | required | The text after the change. |
| `--threshold X` | 0.15 | Share of an old clause's content words that may be missing from the new text. |
| `--map-yaml FILE` | none | Old-item -> new-place map (needed when the old text has named items). |
| `--sxs OUT.md` | none | Write the two-column side-by-side review file. |
| `--pairs OUT.md` | none | Write each old clause beside its closest new clause, for the semantic reviewer. |

## Definitions
| Term | Rule |
|---|---|
| Clause | Take each line of the text; strip one leading list or heading marker (`-`, `*`, `+`, a number with `.` or `)`, or a run of `#`) and trim; skip empty lines. Split the rest at: a sentence end (`.`, `!` or `?` followed by whitespace, but not right after `e.g` or `i.e`), at each `;` (with following spaces), and before the word `Why:`. Trim each piece; drop empties. |
| Content words | Lowercase the clause, turn the curly apostrophe into `'`, take the tokens made of letters, digits, `_`, `'`, `/`, `.`, `:`, `-`; strip `. : , ; - ' _` from both ends of each token; keep tokens longer than 2 characters that are not stop words. |
| Stop words | the a an and or but if of to in on at by for with from as is are was were be been being it its this that these those then than so not no you your we our they them their he she his her can will would could do does did has have had into onto over per via also any all each |
| Closest new clause | The new clause whose content-word set has the highest Jaccard score (shared words / all distinct words) with the old clause; empty if the new text has no clauses. |
| New-word set | All distinct content words of the whole new text. |

## Checks
Run all three, collect every problem, never stop at the first. Each problem is one printed block (message text below).

### Check 1: clause coverage
| Rule | Detail |
|---|---|
| For each old clause with at least one content word | `missing` = distinct content words of the clause that are not in the new-word set. If `len(missing) / (content words of the clause, counted with repeats)` is greater than the threshold, it is a problem. |
| Problem text | `CLAUSE FLAG (<m>/<n> words missing: <sorted missing words, comma separated>)` then indented lines `old: <clause>`, `closest new: <closest new clause>`, `-> quote the new sentence that carries it, or restore the wording`. |
| Title prefix | When the old clause starts with a bold span (`**x**` or `__x__`), put `TITLE (merged heading) ` before `CLAUSE FLAG`. |

### Check 2: mapping completeness
| Rule | Detail |
|---|---|
| Old items | Every markdown heading text (`#`..., trimmed) plus every line of the form `name: X` or `id: X` (optional leading `-`); strip backticks, quotes and spaces from each item. |
| No items | Skip this check. |
| Items but no `--map-yaml` | Problem: `MAPPING: <n> old items found but no --map-yaml given`. |
| With a map | Collect every name inside every `was: [a, b, ...]` list in the map file (strip quotes, backticks, spaces). Each old item must appear exactly once: otherwise `MAPPING: old item '<item>' is mapped <n> times (must be exactly once)`. A name in the map that is not an old item: `MAPPING: map names unknown old item '<name>'`. |

### Check 3: no downgrade
Counting uses whole-word, case-insensitive matches unless noted.
| Rule | Problem text |
|---|---|
| Strong words: must, never, always, shall, required, mandatory, only, hook, block, fail, forbidden, prohibited. If the new text has fewer of a word than the old text | `DOWNGRADE: '<word>' <old count> -> <new count>` then, for each old clause that contains the word while its closest new clause does not, `    lost in old clause: <clause>`; if no clause is isolated: `    (no single clause isolated: word dropped inside a merged clause, check manually)` |
| Weak words: should, may, might, prefer, consider, guidance, recommended, try. If the new text has MORE of a word than the old | `DOWNGRADE?: weaker word '<word>' <old> -> <new> (must->should, hook->guidance?)` |
| Capitalised MUST, NEVER, ALWAYS (case-sensitive, whole word). If the new count is lower | `DOWNGRADE: capitalised <WORD> dropped or lowered` |
| Examples: count of `e.g.`, `for example`, `example`. If the new count is lower | `DOWNGRADE: fewer examples` |
| Numbers and thresholds: first remove cross-reference noise from each text (line-leading list numbers like `3.` or `3)`, and phrases like `rule 3`, `steps 2 and 3`, `section 4`, `item 2`, `check 1`, `#5`, including lists joined by `,`, `and`, `&`, `-`, `to`). Then take numbers (digits with optional `.`, `,` or `:` groups, optional `%`). Every old number missing from the new text | `DOWNGRADE: number/threshold '<x>' no longer present` (sorted) |
| Named things: after the same noise removal, take URLs (`http...`), backtick spans, path-like strings (words ending in `/` or backslash segments), and file names ending in .py .md .json .js .sh .yml .yaml .txt; strip backticks and `. , ) ;` at the ends. Every old one missing from the new text | `DOWNGRADE: named tool/path/URL '<x>' no longer present` (sorted) |

## Optional files
| File | Format |
|---|---|
| `--sxs` | Markdown table, header `\| OLD \| NEW \|` and `\|---\|---\|`. Compare the two texts line by line (optionally run `git diff --no-index --unified=0 <old> <new>` to see the changed blocks; unchanged lines between them are "equal" blocks). One row per block: old lines joined with `<br>`, new lines joined with `<br>`; escape `\|` inside text as `&#124;`; an empty side is a single space; unchanged blocks get a plain row, changed blocks get one extra trailing space after the closing pipe. |
| `--pairs` | For each old clause numbered from 1: `## <n>` newline `OLD: <clause>` newline `NEW (closest): <closest new clause>` newline `Verdict (identical meaning / weaker / lost nuance / changed scope):` newline, blocks separated by a blank line. |

## Procedure
1. Read both files with Read. Split into clauses (definitions above).
2. Run check 1, 2 and 3. For counts, use Grep with `-c`/`-o` and word boundaries on each file, or count while reading; do not skip a word in the lists.
3. Write the optional files with Write.
4. Print every problem block, then the last line: `PASS no-loss gate: <n> old clauses, 0 problems` or `FAIL no-loss gate: <n> old clauses, <m> problems`.
5. Result: any problem is a FAIL (the script exited 1). Fix by restoring the wording or quoting the carrying sentence, then run the whole check again. Do not argue with a FAIL.
6. Then the mandatory semantic review of the pairs file (see `references/no-loss-gate.md`).

## Limit
Done by reading, the word counts are only as exact as your counting. Count each listed word explicitly and show the numbers in the evidence column of the report.
