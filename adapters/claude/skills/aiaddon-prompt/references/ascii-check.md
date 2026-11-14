# ASCII check recipe

Replaces the former `ascii_check.py`. Claude follows this recipe with built-in tools only (Read, Grep, Edit, Write). No script is saved or run.

## Purpose and when

Every prompt, Prompt Builder file, spec and companion prompt must be plain ASCII (code points 0 to 127). Run this check on any prompt text or file before delivering it, and run it again after any edit. The check fails on every non-ASCII character. The optional fix step swaps the common look-alikes for plain ASCII and removes invisible characters; anything it does not know stays in place and is reported.

## Inputs (former CLI options)

| Input | Meaning |
|---|---|
| FILE | A file to check (read it with Read; a UTF-8 byte order mark at the start is ignored). |
| `-` (stdin) | Text given directly in the chat or in a spec. Check only; there is no file to fix, so with this input the fix step is not allowed. Tell the user to give a file, or fix the text by hand and show it. |
| fix flag (`--fix`) | Apply the replacement table below to the file and save it, then check again. Only on a real file. |

## Outputs

- One report line per non-ASCII character found, in this exact form: `FILE:LINE:COLUMN: non-ASCII U+XXXX` (hex code point, at least four digits, upper case; line and column count from 1; a column counts characters, not bytes).
- At most the first 50 hits are listed. If there are more, add the line `... N more` where N is the number beyond 50.
- Last line: `ASCII only.` when nothing is left, otherwise `N non-ASCII character(s) left.`
- Verdict: clean (exit 0 equivalent) or non-ASCII left (exit 1 equivalent; tell the user the file failed). A wrong call (no file, or fix on stdin) is a usage error: say what was wrong and stop.

## How to find non-ASCII characters

Use the Grep tool on the file with this pattern (ripgrep syntax): `[^\x00-\x7F]` with line numbers on, output mode content. Every matching line holds at least one hit. For the column, count characters from the start of the line (the first character is column 1). Report one line per character, not one per line. If Grep returns nothing, the file is clean.

If Grep is not available, Read the file and scan it line by line.

## Replacement table (the fix step)

For each character: first delete the "remove" characters, then replace the others.

### Characters to remove (zero-width and soft hyphen)

| Code point | Name |
|---|---|
| U+200B | zero width space |
| U+200C | zero width non-joiner |
| U+200D | zero width joiner |
| U+2060 | word joiner |
| U+FEFF | byte order mark / zero width no-break space |
| U+00AD | soft hyphen |

### Characters to replace

| Code point(s) | Replace with | What it is |
|---|---|---|
| U+2014, U+2013, U+2012, U+2212, U+2010, U+2011 | `-` | em dash, en dash, figure dash, minus sign, hyphen, non-breaking hyphen |
| U+2018, U+2019, U+201A, U+201B | `'` | single curly quotes and low/high single quotes |
| U+201C, U+201D, U+201E | `"` | double curly quotes and low double quote |
| U+00AB, U+00BB | `"` | guillemets |
| U+2026 | `...` | ellipsis |
| U+2192 | `->` | right arrow |
| U+2190 | `<-` | left arrow |
| U+21D2 | `=>` | double right arrow |
| U+2194 | `<->` | left-right arrow |
| U+2713, U+2714, U+2705 | `[x]` | check marks |
| U+2717, U+2718, U+274C | `[ ]` | crosses |
| U+2022, U+25CF, U+25E6, U+00B7, U+2023 | `-` | bullets and middle dot |
| U+00A0, U+2009, U+202F, U+2002, U+2003 | a single space | non-breaking, thin, narrow no-break, en and em space |
| U+00D7 | `x` | multiplication sign |
| U+2265 | `>=` | greater or equal |
| U+2264 | `<=` | less or equal |
| U+2260 | `!=` | not equal |

Any other non-ASCII character is not touched by the fix step. It stays in the file and is reported; the verdict stays "non-ASCII left".

## Procedure

```
1. Get the text: Read the file (or take the pasted text for the `-` case).
2. Fix step only if the user asked for the fix and the input is a real file:
   1. Make the replacements above. Use Edit with `replace_all` once per distinct character that Grep found; or, for many characters, Read the whole file, apply the table, and Write it back as UTF-8 (no byte order mark).
   2. Do not change anything else in the file (line endings and all other text stay as they were).
3. Run the Grep pattern again on the (possibly fixed) file and build the report lines.
4. Print the report as described under Outputs, then the final line and the verdict.
```
5. If characters are left after the fix step, show them with their code points and propose a plain ASCII wording for each; apply only what the user confirms.

## Notes

- This recipe creates no helper files; the only file it may change is the fixed file itself.
- Prompt Builder files and companion prompts are checked field by field by their own recipes, which use the same table (see `export-prompt.md` here and `companion-prompt.md` in the aiaddon-package skill).
