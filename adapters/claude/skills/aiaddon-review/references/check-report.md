# Recipe: check report

This recipe replaces the old `check_report.py`. Claude follows it with built-in tools only (Read, Grep). Do not write or run a script for it.

Rule count: the old script had no `add(...)` calls. It raised 6 messages, listed as rows 1 to 6 below. All 6 are kept.

## Contents

1. Purpose and inputs
2. Output format and verdict
3. Word lists and patterns
4. Rules
5. Procedure

## 1. Purpose and inputs

Run it on an audit report before sending it. Every finding row needs an Original cell and a Corrected cell. A Corrected cell must be the replacement text itself, not advice.

Inputs (these were CLI options):

| Input | Meaning |
|---|---|
| report file path | Read the file with Read. Needed unless the report is pasted in the chat. |
| pasted report (was `--stdin`) | Use the text of the report as Claude wrote it in the chat. |
| no input | Show this usage: "give a report file or the report text". Verdict is usage error. |

It reads Markdown tables whose header row has a column named Original and a column named Corrected (compare lowercase, after removing `*`, backticks and spaces around the name). Other tables are ignored.

A location prefix in the Corrected cell is fine, for example `SKILL.md frontmatter: name: notes-helper`.

## 2. Output format and verdict

Clean report:

```
Report check: <n> finding tables, every Corrected cell is replacement text.
```

Problems found:

```
Report check: <n> cells to rewrite before sending.

| Line | Problem |
|---|---|
| <line number> | <message> |
```

No finding tables at all:

```
No Original/Corrected tables found: every finding needs one (aiaddon-review Report).
```

Verdict (old exit codes): 0 clean, 1 cells to rewrite, 2 usage error or no finding tables found.

Line numbers are 1-based line numbers in the report text.

## 3. Word lists and patterns

Instruction verbs (case-insensitive, compare the first word of the Corrected text):

```
add consider make improve rename update ensure include write create fix change provide should use move expand flesh clarify rewrite define document specify replace restrict remove delete set give try avoid
```

Pointer pattern (case-insensitive, matched at the start of the cleaned Corrected text):

```
^(see|as above|same as|n/?a|tbd|todo|\.\.\.)\b
```

Location prefix pattern (case-insensitive, removed from the start of the Corrected cell before the other tests):

```
^[`*]*[\w./ -]{1,60}?(frontmatter|body|line \d+|section|\.json|\.md|\.py|\.ya?ml|\.txt)[`*]*\s*:\s*
```

Table row rule: a line is a table row only when, after trimming, it starts and ends with `|`. Cells are split on `|` that is not preceded by a backslash. A separator row is one where every non-empty cell matches `:?-{3,}:?`.

## 4. Rules

| # | Severity | What to check | Pattern or threshold | Message |
|---|---|---|---|---|
| 1 | problem (counts as a cell to rewrite) | A data row has fewer cells than the header needs | number of cells <= the larger of the Original and Corrected column index | `row has fewer cells than the header` |
| 2 | problem | The Original cell is empty | cell text is empty | `Original is empty; quote the current text or write (missing)` |
| 3 | problem | The Corrected cell is empty after cleanup | cleanup in section 5 step 5 leaves nothing | `Corrected is empty` |
| 4 | problem | The Corrected text only points elsewhere | cleaned text matches the pointer pattern | `Corrected points elsewhere ('<first 40 chars of cleaned text>'); write the replacement text` |
| 5 | problem | The Corrected text starts with an instruction verb, and the raw cell does not start with a backtick | first word (cleaned text lowercased, split at the first space, colon, comma or open parenthesis) is in the verb list | `Corrected starts with '<first word>': write the result itself, not an instruction` |
| 6 | error (stop) | No table with Original and Corrected columns exists | zero header rows found | `No Original/Corrected tables found: every finding needs one (aiaddon-review Report).` |

Notes:

- Rows 2, 3, 4 may fire together for one line, except that row 4 and row 5 are exclusive (if row 3 fires, skip 4 and 5; if row 4 fires, skip 5).
- Row 1 skips all other checks for that line.

## 5. Procedure

1. Read the report (Read the file, or take the pasted text). Number the lines from 1.
2. Walk the lines in order. For each line decide if it is a table row (section 3). A line that is not a table row resets the current header, so the next table needs its own header.
3. If the row has a column named Original and a column named Corrected, remember their column positions and count one finding table. Move to the next line.
4. Skip the row if no header is remembered, or if it is a separator row.
5. For a data row:
   1. If it has fewer cells than needed, record rule 1 and move on.
   2. Take the Original and Corrected cells.
   3. Clean the Corrected cell: remove the location prefix; replace `<br>`, `<br/>`, `<br />` with a space; trim spaces; trim the characters `` ` * _ `` and spaces from both ends. This is the cleaned text.
   4. First word: lowercase the cleaned text, cut at the first space, colon, comma or open parenthesis, keep the first part. Empty if the cleaned text is empty.
   5. Apply rules 2, 3, 4, 5.
6. After the last line: if no finding table was seen, print the rule 6 message (verdict 2). If there are no problems, print the clean line (verdict 0). Otherwise print the problem table (verdict 1).
7. Fix every flagged cell by writing the replacement text, then run this recipe again.
