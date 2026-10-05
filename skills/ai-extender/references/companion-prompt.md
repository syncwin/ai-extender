# Companion Prompt (Prompt Builder)

Every extension this plugin builds or updates ships one companion prompt: a JSON file the user imports into Prompt Builder, a Chrome extension that stores prompts with form fields and inserts the filled prompt into Claude, ChatGPT, Gemini, and other chatbots (docs: promptbuilder.eniston.com). It turns "remember the right slash command and what to type" into a short form. Platform-neutral: the same file works wherever the extension runs.

## Contents

1. When · 2. File and format · 3. Field rules · 4. Writing the prompt · 5. Tooling

## 1. When

- **Always.** New build: the planner settles the form fields in the plan; the developer writes the spec; the packager creates or checks the file on every package. Update: refresh the prompt when skills, stages, or inputs change.
- Hand it over with the package: the file sits next to the `.plugin`/`.zip`, plus one line on how to import it (Prompt Builder > Settings > Import, choose the `.json`).

## 2. File and format

`prompts/<title-slug>.json` inside the extension (title "Meeting Tasks" → `meeting-tasks.json`). Shape of a Prompt Builder 2.0 export:

```json
{ "prompts": [ { "id": "<32 lowercase hex>", "title": "...", "description": "...", "content": "... {{task}} ...",
    "variables": { "task": { "type": "Textarea", "label": "Task", "placeholder": "...", "context": "...",
                             "maxLength": 3000, "required": true, "options": "" } },
    "lastModified": "<ISO, ms, Z>", "created": "<ISO, ms, Z>" } ],
  "metadata": { "exportDate": "<ISO, ms, Z>", "version": "2.0", "format": "prompt-builder-plain", "count": 1, "checksum": "-9vapbe" } }
```

- Keep `id` and `created` stable across updates so a re-import replaces the old copy instead of duplicating it (Prompt Builder asks to replace or merge duplicates).
- `checksum` is copied from Prompt Builder's own exports; every export checked so far carries the same value.

## 3. Field rules

| Field | Rule |
|---|---|
| Variable name | letters, digits, underscores; used in `content` as `{{name}}`; every `{{name}}` has a variable and every variable is used |
| `type` | `Text` (one line: a name, a keyword, a URL), `Textarea` (several lines), `Radio` (pick one), `Checkbox` (pick several) |
| `label` | short, Title Case, shown above the field |
| `placeholder` | example input for text fields; for Radio/Checkbox exports repeat the variable name |
| `context` | the tooltip. Stored HTML-escaped (an apostrophe becomes `&#x27;`); the script escapes it for you |
| `maxLength` | `Text`/`Textarea`: a positive whole number, or `""` for no limit; `""` for Radio/Checkbox |
| `required` | `true` only for what the extension cannot run without (usually one field) |
| `options` | Radio/Checkbox only: at least two, one per line, no duplicates; `""` otherwise |

## 4. Writing the prompt

- **Title** = the extension's display name. **Description** = one or two sentences on what it does and how to use the form.
- **Content:** `# <Title>`, then `Run /<slug>` (or `/<plugin>:<skill>` for one stage) and the task in one line, then one bullet per field (`* **Label:** \`{{name}}\``), then the rules the extension already enforces that a user should see: ask once for missing inputs, show a plan and wait for a yes before anything that creates, changes, sends, publishes, or deletes.
- **Fields:** 3 to 6. The free-text request first and required; `Text` for one-line answers; a Radio for the stage when users run stages separately; a Checkbox for where the files are; an optional Textarea for everything else. Options in plain words the user would say, not skill slugs; put the mapping in `context`.
- Keep the form short enough to fill in under a minute. No secrets, client names, or internal URLs in the file: users share it.

## 5. Tooling

`python ${CLAUDE_SKILL_DIR}/../claude-packager/scripts/companion_prompt.py <extension-dir> [--spec spec.json] [--out DIR] [--force]` writes a default prompt (task, stage when there are several role skills, files, details) or one from a spec (`{"title"?, "description"?, "content", "variables"}`), checks it, and copies it to `--out`. `--check <file>` checks any Prompt Builder JSON. `package_extension.py` runs it on every package; the validator reports `C000` (no prompt yet, or the checker is missing; info), `C001` (unreadable JSON), `C002` (error), `C003` (warning), and `C004` when the prompt never names the extension's slash command.
