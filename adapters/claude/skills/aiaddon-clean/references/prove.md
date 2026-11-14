# Keep-unique proof recipe (replaces prove.py)

## Purpose and when
Prove that every normalized line of the untouched BEFORE tree still exists in the AFTER tree or in the archive folder. Run in clean-up step 6 after the edits. Read-only.

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `<before-dir>` | required | Untouched copy or `git worktree` of the original. |
| `<after-dir>` | required | The cleaned tree. |
| `--archive <dir>` | none | Archive folder; its lines count as kept (only if the folder exists). |
| `--ext list` | `.md,.json,.py,.yaml,.yml,.txt` | Extensions to compare; a missing dot is added; lowercase. |

Both directories must exist; otherwise stop and ask (the script exited 2).

## Rules
| Rule | Detail |
|---|---|
| Normalizing a line, trivial lines, reading a file | Exactly as in `references/inventory.md` (norm, trivial, UTF-8 without BOM, CRLF as LF). |
| Files in BEFORE | Same walk and skips as the inventory: skip folders `.git`, `__pycache__`, `node_modules`, `.venv`, `archive`; skip links; extension filter. |
| Files in AFTER | Same, except the folder `archive` is NOT skipped (only `.git`, `__pycache__`, `node_modules`, `.venv` are). |
| Files in the archive folder | No folders skipped. |
| BEFORE line set | Every distinct non-trivial normalized line, remembering its first location (file relative to the before dir, 1-based line number). |
| KEPT line set | Union of all distinct non-trivial normalized lines of AFTER and of the archive folder. |
| Lost | A BEFORE line that is not in KEPT. |

## Procedure
1. List the files of both trees with Glob using the rules above; read each with Read.
2. Build the BEFORE line set with first locations. For a large tree, do not read every file into the reply: process file by file and keep only lines not yet found.
3. For each BEFORE line, check by Grep (fixed-string, case-insensitive, whitespace-collapsed) whether it exists in AFTER or the archive; a line is kept when some line there normalizes to the same text. Where a line was only reworded, it is lost: the proof is about exact normalized lines.
4. Print the counts and every lost line, then the verdict.

## Output
```
before: <n> unique lines; after (+archive): <m> unique lines; lost: <k>
LOST <file>:<line>: <normalized line, first 140 characters>      (one per lost line, sorted by file then line)
PASS zero unique lines lost
```
or, when anything is lost, the last line is:
`FAIL unique lines would be lost: add them to a kept file or the plan`

Exit meaning: 0 = PASS, 1 = lost lines. Any lost line: restore it in a kept file (or add it to the plan and get approval), then re-run. Paste the PASS line in the clean-up report.
