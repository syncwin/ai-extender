# Export a prompt as Prompt Builder JSON

Replaces the former `export_prompt.py`. Claude follows this recipe with built-in tools only (Read, Grep, Write, Edit). No script is saved or run.

## Purpose and when

Turn a crafted prompt into a Prompt Builder import file (format `prompt-builder-plain`, version `2.0`). Use it for Template mode, or whenever the user wants the prompt in Prompt Builder. The schema, escaping rules and every check are the ones in the aiaddon-package skill's recipe `references/companion-prompt.md` (sections "Build the file" and "Check rules"). Do not copy them here; follow them from there.

## Inputs (former CLI options)

| Input | Meaning |
|---|---|
| SPEC | A JSON spec `{"title", "description"?, "content", "variables"?}`. `title` and `content` (text) are required. |
| md source (`--md PROMPT.md`) | Instead of a spec: a Markdown file whose whole text becomes `content`. Needs a title. |
| title (`--title`) | Required with the md source; if missing, say `--md needs --title` and stop. |
| description (`--description`) | Optional with the md source; default is an empty string. |
| out (`--out DIR`) | Folder to write into. Required unless this is a check only. |
| id (`--id HEX32`) | Reuse this prompt id. Must be exactly 32 lowercase hex characters (`^[0-9a-f]{32}$`), otherwise stop with: `--id must be 32 lowercase hex characters`. |
| check only (`--check-only`) | Run every step except writing the file. |

Exactly one of SPEC or the md source must be given. Missing out (when not check only) is a usage error: say so and stop. If the input cannot be read or is not valid JSON, say `cannot read input: <reason>` and stop. If the spec lacks `title` or text `content`, say `spec needs "title" and "content" (text)` and stop.

## Output

`DIR/<title-slug>.json`, where the title slug is: lower-case the title, replace every run of characters outside `a-z0-9` with one `-`, strip leading and trailing `-`; if that is empty use `prompt`. The file is UTF-8, indent 2 spaces, any non-ASCII written as escapes (there is none after this recipe), one trailing newline.

Final message when written, in this form:

```
Written: <path>
Import: Prompt Builder > Settings > Import, choose the .json file.
```

## Procedure

```
1. Read the input as above (Read tool; ignore a leading byte order mark). For the md source, build the spec `{"title": <title>, "description": <description or "">, "content": <file text>}`.
2. Normalize every text value in the spec (title, description, content, and every string inside variables, recursively; non-text values stay as they are) to ASCII with the fix table in `ascii-check.md` (remove the zero-width characters, then apply the replacements). This is the plain table only, not the accent-stripping step.
3. If the spec has no `variables` object: find every `{{name}}` in the content using the pattern `\{\{\s*([A-Za-z0-9_]+)\s*\}\}`, keep each name once in order of first appearance, and make one variable per name: type `Textarea`, label = the name with `_` turned into spaces and each word capitalized, placeholder = the name, context empty, required false, maxLength 3000, options empty.
4. Search all text in the spec for non-ASCII (Grep with `[^\x00-\x7F]` on the normalized text, or scan it). If any is left, list each as `spec:LINE:COLUMN: non-ASCII U+XXXX` (first 50) and stop with: `Export stopped: non-ASCII left after normalizing.` Nothing is written.
5. Build the Prompt Builder document following `companion-prompt.md`, section "Build the file", using this spec and title. If an id was given, the document keeps that id (the created time is a fresh timestamp since no older file is supplied).
6. Run every rule in `companion-prompt.md`, section "Check rules", on the document. Print the report in the format given there, with the scope shown as the target file name. If there are any errors, stop (nothing written).
7. If this is a check only, stop here (success if no errors).
8. Create DIR if needed and Write the file. Print the final message.
```

## Notes

- Warnings from the check do not block the export.
- If the aiaddon-package skill's recipe is not available, say so and show the spec; do not improvise the schema.
