# Commands (legacy) and invocation control

`commands/*.md` still work and accept the skill frontmatter (minus `name`/`paths`), but **new extensions use `skills/`** (supporting files, progressive disclosure, same `/plugin:name` invocation).

Use `commands` only when the user wants flat single-file commands or a manifest object map:

```json
{ "commands": { "status": { "source": "./commands/status.md", "argumentHint": "[env]" },
                "about":  { "content": "Explain what this plugin provides." } } }
```

Each entry sets exactly one of `source` or `content`; optional `description`, `argumentHint`, `model`, `allowedTools`. Setting `commands` replaces the default `commands/` scan; list it explicitly to keep it. Paths start with `./` and exist inside the plugin.

Arguments: `$ARGUMENTS`, `$0`/`$1`, named via `arguments:`. Claude Code only.
