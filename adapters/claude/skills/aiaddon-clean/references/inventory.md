# Inventory recipe (replaces inventory.py)

## Purpose and when
Read-only inventory and overlap map for a plugin or skill tree, with fixed counting rules instead of judgement. Used in clean-up step 1 on the `<before>` copy. Produces the same JSON report shape as before, so later steps (overlap map, plan) read it unchanged.

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `<dir>` | required | Folder to inventory (must exist; otherwise ask the user). |
| `--out report.json` | none | Where to write the JSON. Without it, show the JSON in the reply. |
| `--min-words N` | 12 | A paragraph needs at least N words to count for duplicate checks. |
| `--threshold X` | 0.6 | Minimum Jaccard score for a near-duplicate pair. |
| `--ext list` | `.md,.json,.py,.yaml,.yml,.txt` | Comma-separated extensions; a missing leading dot is added; compared in lowercase. |

## Rules

### Which files
| Rule | Detail |
|---|---|
| Walk | Every file under `<dir>` (Glob `**/*`), sorted by path. |
| Skip folders | Any file with a path part (relative to `<dir>`) equal to `.git`, `__pycache__`, `node_modules`, `.venv` or `archive`. |
| Skip links | Symbolic links are skipped. |
| Extension | Keep a file only when its lowercase suffix is in the `--ext` list. |
| Reading | Read as UTF-8; drop a leading byte-order mark; treat CRLF as LF. A file that cannot be read as text is skipped. |

### Normalizing one line ("norm")
1. Trim the line and lowercase it.
2. Remove one leading marker: any run of `#`, `>`, `*`, `+`, `-` characters, or a number followed by `.` or `)`, only when followed by whitespace.
3. Collapse every whitespace run to one space and trim.

A normalized line is **trivial** when it is shorter than 3 characters or has no letter a-z and no digit 0-9. Trivial lines are ignored everywhere below.

### Per file
| Field | Rule |
|---|---|
| `path` | Path relative to `<dir>`, forward slashes. |
| `bytes` | Size of the text in UTF-8 bytes (after CRLF -> LF). |
| `lines` | Number of line breaks plus 1. |
| `headings` | Every line that starts with 1 to 6 `#` followed by whitespace, trimmed, original text. |
| line list | The set of distinct non-trivial normalized lines of the file, sorted. The script stored a 12-character SHA-1 of each line (`line_hashes`). Claude cannot compute hashes by reading, so the recipe stores the normalized line text itself in a field named `lines_normalized`. Comparison is by text equality, which is all the hash was used for. |

### Duplicate rules (across all kept files)
| Finding | Rule |
|---|---|
| Paragraph | Only in `.md` files. Consecutive non-blank lines form one paragraph; its text is the normalized lines joined by single spaces; its start is the 1-based line number of its first line. Keep it only when it has at least `--min-words` words (split on whitespace). |
| Exact duplicate paragraphs | Two or more paragraphs (even in the same file) with identical text. Record each location as `{file, line, text}`, text = first 160 characters. |
| Near-duplicate paragraphs | For paragraphs with different text: split each into 5-word shingles (every run of 5 consecutive words; a paragraph under 5 words has one shingle of all its words). Jaccard = shared shingles / all distinct shingles of both. A pair at or above `--threshold` is reported once (earlier paragraph = a, later = b), score rounded to 3 decimals. Sort by Jaccard, highest first. The script ignored any shingle that occurs in more than 50 paragraphs when looking for candidate pairs. |
| Shared headings | Normalize each heading; list those that appear in more than one distinct file, with the sorted list of files; sort by heading. |
| Lines in several files | A distinct non-trivial normalized line that occurs in 2 or more distinct files. |

## Procedure
1. Glob the files, apply the skip rules, read each one with Read.
2. For each file compute the per-file fields. Keep a running map of normalized line -> set of files, and a list of paragraphs (file, line, text).
3. Exact duplicates: group paragraphs by identical text and keep groups of 2 or more. On a large tree, use Grep with a fixed-string search of a distinctive 8-word phrase of each paragraph across `<dir>` and count matching files.
4. Near duplicates: for each paragraph, find candidate partners with Grep on a few of its 5-word shingles. For each candidate pair only, list the two shingle sets and count shared versus total to get the Jaccard score. When a tree is too large to score every pair, say in the report which pairs were checked. A by-hand run cannot score every pair the way the script did, so this is the one place the recipe is weaker. Never invent a score.
5. Shared headings and lines-in-several-files come from the maps built in step 2.
6. Build the report (shape below) and write it with Write to `--out`, or show it in the reply.
7. Print the summary line.

## Output
JSON written to `--out`:
```
{ "root": "<absolute dir>", "tool": "aiaddon-clean inventory",
  "files": [ {"path","bytes","lines","headings":[...],"lines_normalized":[...]} ],
  "exact_duplicate_paragraphs": [ {"hash": "<short id>", "locations": [ {"file","line","text"} ] } ],
  "near_duplicate_paragraphs": [ {"jaccard", "a": {"file","line","text"}, "b": {"file","line","text"}} ],
  "shared_headings": [ {"heading", "files": [...]} ],
  "totals": {"files","bytes","unique_lines","lines_in_several_files","exact_duplicate_paragraphs","near_duplicate_paragraphs"} }
```
`hash` in an exact-duplicate group is any short unique id (for example `d1`, `d2`). `totals.unique_lines` = distinct non-trivial normalized lines over all files; `totals.bytes` = sum of the file bytes.

Summary line (always printed):
`inventory: <files> files, <unique_lines> unique lines, <exact> exact and <near> near duplicate paragraphs; report <out>`
The `; report <out>` part appears only with `--out`; without `--out` the JSON follows the line.

Read-only: the only file this recipe writes is the report.
