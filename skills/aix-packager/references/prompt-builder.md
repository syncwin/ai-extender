# Companion prompt: delivery options

Config (read the value from here; never hard-code the link elsewhere):

```
prompt_builder_url: https://sync.win/promptbuilder
```

## Ask once

Before packaging, ask the user once which companion prompt files they need:

| Choice | Files next to the package |
|---|---|
| `md` | `<Name> v<ver> prompt.md` (raw Markdown, ASCII only, {{variables}}) |
| `json` | `<title-slug>.json` (Prompt Builder import file, format prompt-builder-plain v2.0) |
| `both` (default) | both |

Pass the answer as `--prompts md|json|both`. Both forms are generated from the same source (`prompts/<title-slug>.json`), so they never drift.

## Prompt Builder line (only when relevant)

Mention Prompt Builder only when the user asked for the JSON (or both) and has not used it, or asks what the JSON is for. One neutral line, no promotion:

> Prompt Builder is a browser extension that imports the JSON file and shows the prompt as a fillable form: <prompt_builder_url>

Skip it when the user chose `md` only or already knows the tool.
