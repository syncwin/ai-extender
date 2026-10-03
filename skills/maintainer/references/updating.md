# Updating Existing Extensions

Common first steps: read all files; run the validator for a baseline (`ai-extender:reviewer`); snapshot the current version as the eval baseline; note the stable contract (skill names, invocation, `plugin.json` name).

## By target

| Target | Do | Watch |
|---|---|---|
| **Skill** | edit `SKILL.md`/references; re-tune description; run trigger + output tests vs snapshot (`developer/references/testing.md`) | don't rename `name` (breaks `/plugin:name` and references); keep portable frontmatter |
| **Connector** | edit `.mcp.json`; update assignment table and README data-handling; re-check tool names in `allowed-tools`/agent `tools`/hook matchers | literal secrets; credential env vars in remote URLs; renamed server key changes every tool name |
| **Agent** | edit frontmatter/body | plugin agents ignore `permissionMode`, `mcpServers`, `hooks`; `name` has no `:` |
| **Hook** | edit `hooks/hooks.json`/scripts | enforcement needs exit 2; exec form; parallel execution |
| **Plugin** | add/remove components, keep router = plugin slug, update manifest, README, changelog | `commands`/`agents` keys replace defaults; `version` pins users until bumped; `bin/` blocks Cowork |
| **Add-on** | re-verify against the new base version; adjust `dependencies` range | never edit the base |
| **Cowork plugin with `~~placeholders`** | replace each `~~name` with the user's real value, grouped by theme, from the user's answers and connected sources | never expose `~~` to the user; never rename the plugin/skills; treat `commands/*.md` like skills; for our own plugins use `userConfig` instead |

## Customizing (Cowork, placeholders)

1. Find: `find mnt/.local-plugins mnt/.plugins -type d -name "*<name>*"`; read it fully.
2. Mode: placeholders present → replace them all; user named one area → touch only that area; else ask what to change.
3. Gather org context (chat/doc/email connectors if available; otherwise ask).
4. Work from a plain-language todo ("Learn how standup prep works"), not file paths.
5. Validate, repackage with the next version in the filename.

## Migration safety

Breaking change (renamed slug, removed skill, changed invocation) → MAJOR-equivalent note in the changelog with old→new mapping; keep the old name as an alias skill only if users depend on it and the user agrees.
