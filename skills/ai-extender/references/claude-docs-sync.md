# Docs Sync

Refresh `claude-platform-facts.md` when a fact is older than the user's tolerance, a validator result disagrees with it, or the user asks. Tell the user before fetching; if no web tool is available, say which facts may be stale and continue.

## Sources (code.claude.com/docs/en/…)

`overview` · `plugins` · `plugins/components` · `plugins/publish` · `plugins/org` · `plugins/manifest-reference` · `plugin-evals` · `plugin-marketplaces` · `skills` · `sub-agents` · `hooks` · `mcp` · `settings` · `workflows` · `agent-sdk/skills` · `llms.txt` (full index) · claude.com/docs/plugins/platform-support · plus the Agent Skills spec and Claude connector/MCP build docs. Confirm slugs from `https://code.claude.com/docs/llms.txt`; they move (e.g. plugin pages now live under `/plugins/…`). Also `plugins/mods/create`, `plugins/mods/reference`, claude.com/docs/plugins/submit and /pre-submission-checklist. The terminal-config page (custom themes) could not be fetched directly: theme facts come from the v2.1.118 changelog and secondary sources, so re-verify a theme token before relying on it.

## Procedure

1. Fetch with whatever web fetch tool the session has, on a URL a search returned (append `.md` to code.claude.com pages for markdown), 2 pages per call. Only official Anthropic pages; no other site is needed. Large results are stored to a file: parse the JSON, write each page's `text` to disk, `grep -n "^#"` for headings, and read only the needed sections.
2. Compare against `claude-platform-facts.md`; edit only lines that changed; stamp the date.
3. Propagate changes to affected `references/*.md` and to `scripts/validate_extension.py` constants (field lists, events, colors).
4. Record in `CHANGELOG.md` under the current version if same-session, else bump per versioning rules.
5. A browser tool is only for pages a plain fetch can't render; never the default.
