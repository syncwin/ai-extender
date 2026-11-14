# Companion prompt recipe

Replaces the former `companion_prompt.py`. Claude follows this recipe with built-in tools only (Read, Glob, Grep, Write, Edit; Bash only for a timestamp, a random id, or file copy). No script is saved or run. Other recipes point here for the Prompt Builder schema ("Build the file") and for the validation rules ("Check rules").

## Contents

- Purpose and when
- Modes (former CLI forms)
- Step 1: read the manifest
- Default spec
- Build the file
- ASCII normalization (used when building and for Markdown)
- Check rules
- Markdown form (for the formats md and both, and for the to-Markdown mode)
- Procedure (default mode)
- Notes

## Purpose and when

Every extension ships one companion prompt: `<extension-dir>/prompts/<title-slug>.json`, in Prompt Builder's JSON import format (format `prompt-builder-plain`, version `2.0`). Users import it into Prompt Builder and start the extension with a short form instead of a blank chat. The JSON in `prompts/` is the single source; the Markdown form is generated from it. `prompts/` is never put inside the packaged extension.

Run this recipe from the packaging steps (see `package-extension.md`), whenever the manifest or description changes, and when the user asks to create, check or convert a companion prompt.

## Modes (former CLI forms)

| Mode | Behaviour |
|---|---|
| Default, no spec, no file yet | Write a default prompt built from the manifest (see "Default spec"): task, stage (only when the plugin has more than one role skill), files, details. |
| With a spec (`--spec FILE`) | Write the prompt from the spec `{"title"?, "description"?, "content", "variables"}`. `content` must be text and `variables` an object, otherwise stop with: `spec needs "content" (text) and "variables" (object)`. |
| File already there | Check it and leave it untouched, unless force (`--force`) or a spec is given. |
| Out (`--out DIR`) | Also copy the checked file into DIR (next to the packaged extension). |
| Formats (`--formats md/json/both`, default `both`) | Which companion files to deliver into DIR: `json`, `md`, or `both`. The Markdown is written only into DIR, never into `prompts/`. |
| Check (`--check FILE`) | Check any Prompt Builder JSON file and stop. Print the report; failed if there is any error. |
| To Markdown (`--to-md FILE`, optional `--out FILE`) | Check the file first (stop on errors, printing the report); then make the Markdown form and write it to the named file (say `wrote <file>`) or show it. |

Inputs for the default mode: the extension dir (must be a folder; otherwise say `not a directory: <dir>` and stop). A wrong call is a usage error: say so and stop.

## Step 1: read the manifest

Plugin (a `.claude-plugin/plugin.json` exists):

| Value | Source |
|---|---|
| name (the invocation slug) | `name` in plugin.json, or the folder name if missing |
| title | `displayName`, else the name with `-` turned into spaces and each word capitalized |
| description | `description`, or empty |
| role skills | for each `skills/*/SKILL.md` in sorted order, skip the one whose folder name equals the plugin name; the entry is (folder name, first `# ` heading text, or the folder name with `-` to spaces and capitalized) |
| version | `version`, default `0.0.1` |

Skill (a `SKILL.md` in the folder, no plugin.json):

| Value | Source |
|---|---|
| name | front matter `name`, or the folder name |
| title | first `# ` heading in the file, or the name with `-` to spaces and capitalized |
| description | front matter `description` (a folded or literal block is joined into one line with single spaces; surrounding quotes removed) |
| role skills | none |
| version | the front matter line `  version: <value>` (indented; quotes removed), default `0.0.1` |

Neither: stop with `not a plugin or skill directory: <dir>`. Remove a leading byte order mark; treat CRLF as LF when reading the front matter.

The title slug used for filenames: lower-case the title, replace each run of characters outside `a-z0-9` with `-`, strip leading and trailing `-`, and use `prompt` if empty. The target file is `<dir>/prompts/<title-slug>.json`.

## Default spec

Short description: the description text up to the first `. ` (period and space), with trailing periods removed; if the description is empty, `Run <title>`.

Spec title is the title. Spec description is: `<short>. Fill in the task and run <title> in one step.`

Spec content is these lines joined with newlines (`<slug>` is the invocation name, `<title>` the title). The Stage line appears only when the plugin has more than one role skill:

```
# <title>

Run /<slug> and help me with the task below. Talk to me in plain words and ask only what you need from me.

* **Task:** `{{task}}`
* **Stage:** `{{stage}}`
* **Files:** `{{files}}`
* **Details:** `{{details}}`

If something you need is missing, ask for it in one short message, then continue.

Before you create, change, send, publish, or delete anything, show a short plan and wait for my yes. Read-only checks run without it.
```

Variables, in this order (stage only when present). Fields are type, label, placeholder, context, maxLength, required, options:

| Name | Type | Label | Placeholder | Context | maxLength | required | options |
|---|---|---|---|---|---|---|---|
| task | Textarea | Task | Describe what you need in your own words. | What goes in, what should come out, and any rules it must follow. | 3000 | true | empty |
| stage | Radio | Stage | stage | `Pick the step to run. Not sure: leave it on the first option and the entry skill decides. Skills: ` then each role as `<Title> = /<slug>:<folder name>` joined by `; `, then a period | "" (none) | false | `Let It Decide` then each role's title, one per line |
| files | Checkbox | Files | files | Where the files for this task are, if there are any. | "" | false | the four lines below |
| details | Textarea | Details | Anything else: deadlines, names, examples, things to avoid. | Everything the task needs that isn't a file. | 2000 | false | empty |

Options for `files`, one per line, exactly:

```
Attached in This Message
In the Claude Project Files
Created Earlier in This Chat
None, Start from Scratch
```

## Build the file

Input: a spec (title optional, description optional, content, variables), the fallback title, and the older file's prompt if one exists.

1. Timestamp: the current UTC time as `YYYY-MM-DDTHH:MM:SS.mmmZ` (milliseconds, three digits). Windows: `(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")`. macOS/Linux: `date -u +%Y-%m-%dT%H:%M:%S.000Z`. Use the same value for exportDate, lastModified, and created (when new).
2. Prompt id: keep the older prompt's `id` if there is one, otherwise make 32 random lower-case hex characters. Windows: `-join ((1..16) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })`. macOS/Linux: `openssl rand -hex 16`. Keep the older `created` value if there is one, otherwise the timestamp.
3. Plain text: for the description, the content, and every variable context, decode HTML entities twice (for example `&amp;#x27;` and `&#x27;` both become `'`; `&amp;`, `&lt;`, `&gt;`, `&quot;`, `&apos;` and numeric `&#...;` or `&#x...;` become the characters). Prompt Builder escapes on its own when it imports, so a pre-escaped value would be escaped twice.
4. Variables: for each variable, keep only these fields in this order, with these defaults when missing:

   | Field | Default |
   |---|---|
   | type | Textarea |
   | label | the variable name with `_` turned into spaces, each word capitalized |
   | placeholder | the variable name |
   | context | empty text |
   | maxLength | empty text `""` |
   | required | false |
   | options | empty text |

   If the type is `Predefined`, add a seventh field `predefinedContent` (default empty text).
5. The prompt object, field order: `id`, `title` (spec title, else the fallback title), `description`, `content`, `variables`, `lastModified` (timestamp), `created`.
6. ASCII pass over the whole prompt object (every string at any depth, except the value of any key named `id`): see "ASCII normalization" below.
7. The document, field order: `prompts` (an array with the one prompt), then `metadata` with fields in this order: `exportDate` (timestamp), `version` (`2.0`), `format` (`prompt-builder-plain`), `count` (1), `checksum` (`-9vapbe`, the fixed value every Prompt Builder 2.0 export carries).

```
File format: JSON, 2-space indent, all non-ASCII as escapes (there should be none), a single trailing newline.
Directory: `prompts/` is created first if it does not exist.
Order: the check rules run before writing; with errors, the report is printed and nothing is written.
```

## ASCII normalization (used when building and for Markdown)

Apply to each string: first delete these characters: U+200B, U+200C, U+200D, U+2060, U+FEFF, U+00AD. Then replace these spaces with one plain space: U+00A0, U+2002, U+2003, U+2009, U+202F. Then replace, per the table:

| Characters | Replace with |
|---|---|
| U+2014 U+2013 U+2012 U+2212 U+2010 U+2011 | `-` |
| U+2018 U+2019 U+201A U+201B | `'` |
| U+201C U+201D U+201E U+00AB U+00BB | `"` |
| U+2026 | `...` |
| U+2192 | `->` |
| U+2190 | `<-` |
| U+21D2 | `=>` |
| U+2194 | `<->` |
| U+2713 U+2714 | `[x]` |
| U+2717 | `[ ]` |
| U+2022 U+00B7 | `-` |
| U+00D7 | `x` |
| U+2265 | `>=` |
| U+2264 | `<=` |
| U+2260 | `!=` |

Finally, if any non-ASCII is still present, decompose accented letters to their base letter (for example e with an acute accent becomes `e`; drop the combining marks). Anything still non-ASCII after that is left in place for the check rules to reject. This is the same table as the aiaddon-prompt skill's `ascii-check.md`, with the accent step added and without the extra check/cross/bullet look-alikes listed there.

## Check rules

Run on any Prompt Builder JSON document. Collect errors (E) and warnings (W). Errors block; warnings do not. All messages below are shown verbatim (the placeholders in angle brackets are filled in). `at` means `prompts[i]` with i from 0.

Top level and metadata:

| Rule | Level | Message |
|---|---|---|
| Top level is not an object with a non-empty `prompts` array | E (stop checking) | `top level needs a non-empty "prompts" array` |
| `metadata` missing or not an object | E | `missing "metadata" object` |
| `metadata.format` is not `prompt-builder-plain` | E | `metadata.format must be "prompt-builder-plain"` |
| `metadata.version` (as text) is not `2.0` | W | `metadata.version is <value>; current exports use "2.0"` |
| `metadata.count` differs from the number of prompts | E | `metadata.count <value> != <n> prompts` |
| `metadata.checksum` is not text | E | `metadata.checksum must be a string` |
| `metadata.exportDate` does not match `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$` | E | `metadata.exportDate must be an ISO timestamp ending in Z` |

Each prompt:

| Rule | Level | Message |
|---|---|---|
| Prompt is not an object | E | `<at> must be an object` |
| `id` is not 32 lower-case hex characters (`^[0-9a-f]{32}$`) | E | `<at>.id must be 32 lowercase hex characters` |
| `title` empty after trimming | E | `<at>.title is empty` |
| Title (case-insensitive) already used by an earlier prompt | W | `<at>.title duplicates another prompt; Prompt Builder appends a number` |
| `description` present but not text | E | `<at>.description must be text` |
| `content` missing, not text, or blank | E | `<at>.content is empty` |
| `created` or `lastModified` not matching the ISO pattern above | E | `<at>.<field> must be an ISO timestamp ending in Z` |
| `variables` present but not an object | E (skip the rest for this prompt) | `<at>.variables must be an object` |
| A `{{name}}` in content (pattern `\{\{\s*([A-Za-z0-9_]+)\s*\}\}`) with no variable of that name | E | `<at>: {{<name>}} is used in content but has no variable` |
| A variable never used in content | E | `<at>: variable "<name>" is never used in content` |

Each variable (`vat` = `<at>.variables.<name>`):

| Rule | Level | Message |
|---|---|---|
| Name has characters outside letters, digits, underscore | E | `<vat>: name must be letters, digits, underscores` |
| Variable is not an object | E | `<vat> must be an object` |
| `type` not one of Text, Textarea, Radio, Checkbox, Predefined | E (skip the rest for this variable) | `<vat>.type <value> must be one of ['Checkbox', 'Predefined', 'Radio', 'Text', 'Textarea']` |
| `label` blank | E | `<vat>.label is empty` |
| `placeholder`, `context` or `options` present but not text | E | `<vat>.<field> must be text` |
| `required` present but not true or false | E | `<vat>.required must be true or false` |
| Type is Predefined and `predefinedContent` is blank | E | `<vat>: Predefined needs predefinedContent` |
| Type Radio or Checkbox with fewer than two non-blank options (options are split on newlines) | E | `<vat>: <type> needs at least two options, one per line` |
| Radio or Checkbox with duplicate options (compared trimmed, case-insensitive) | E | `<vat>: duplicate options` |
| Radio or Checkbox with a non-empty `maxLength` | W | `<vat>.maxLength is ignored for <type>` |
| Other types with non-blank options | W | `<vat>.options is ignored for <type>` |
| Other types: `maxLength` is neither `""` nor a positive whole number (true/false do not count as numbers) | E | `<vat>.maxLength must be a positive whole number, or "" for no limit, for <type>` |

Text hygiene, per prompt, applied to these fields: `title`, `description`, `content`, and for every variable its `label`, `placeholder`, `context`, `options`, `predefinedContent` (when they are text):

```
| Rule | Level | Message |
|---|---|---|
| Contains an HTML entity (pattern `&#x?[0-9a-fA-F]+;` or `&(amp|lt|gt|quot|apos);`) | E | `<at>.<field>: contains an HTML entity (such as &#x27; or &amp;); write the plain character, Prompt Builder escapes on import` |
| Contains any character above code point 127 | E | `<at>.<field>: contains a non-ASCII character; use plain ASCII (- " ' -> [x] ...)` |
| The prompt's JSON text contains `<script` or `javascript:` (case-insensitive) | E | `<at>: contains script content` |
```

Report format (print this; the table counts are the numbers of errors and warnings; the lists appear only when non-empty):

```
### Scratchpad: Companion Prompt
**Scope:** `<path shown>`

| Errors | Warnings |
|---|---|
| <n> | <n> |

**Errors**
- <message>

**Warnings**
- <message>
```

Reading a file: ignore a leading byte order mark; if it cannot be read or is not valid JSON, stop with `cannot read <path>: <reason>`.

## Markdown form (for the formats md and both, and for the to-Markdown mode)

Take the first prompt in the file, apply the ASCII normalization to every string in it, then build the text. Lines, joined with newlines and ending with one trailing newline:

```
# <title>

<description>        (this line and the blank after it only when a description exists)

<prompt>
<content, trimmed; if it starts with a "# " heading line plus following blank lines, drop them, because the title is already the heading>
</prompt>

<fields>
- {{<name>}} (<Label>; <type lower-case>, required|optional): <context>
</fields>
```

Each variable gets one `<fields>` line, in order. Line rules: the word is `required` when required is true, else `optional`; trailing colons and spaces are removed from the line (so an empty context leaves no colon); if the variable has options (non-blank lines), ` Options: ` is appended followed by the options joined with ` | ` and a final period. After building, the whole text is scanned: if any non-ASCII character remains, the build stops with `Markdown prompt must be ASCII only; found [<characters>]`.

Markdown file name: `<Visible Name> v<version> prompt.md`, where the visible name is the title from step 1, the version is the manifest version (default `0.0.1`), and these characters are removed from the name: `\ / : * ? " < > |`.

## Procedure (default mode)

````
1. Check the extension dir and read the manifest (Step 1). Compute the title slug and the target path.
2. If a file exists at the target, Read it (stop with the read error if invalid).
3. If a spec was given, or no file exists, or force was given: build the document (spec given, else the default spec), using the old prompt for id and created. Run the check rules; on errors print the report and stop (nothing written). Create `prompts/` if needed and Write the file. Action = `written`. Otherwise use the existing file and set action = `checked`.
4. Run the check rules on the document and print the report with scope `prompts/<title-slug>.json` (relative to the dir). Stop here if there are errors (failed).
5. Print the result table:

   ```
   | Item | Result |
   |---|---|
   | File | `<target path>` (<written or checked>) |
   ```

6. If an out dir is given: create it. For formats `json` or `both`, copy the target file there and add the row `| JSON | `<out>/<file name>` |`. For `md` or `both`, write the Markdown file (name above) there and add the row `| Markdown | `<out>/<md name>` |`.
7. Report success.
````

## Notes

- Standard library only and no network were the old script's rules; this recipe needs neither.
- A read-only extension folder cannot take `prompts/`; the packaging recipe stages a temp copy and runs this recipe on it (see `package-extension.md`).
