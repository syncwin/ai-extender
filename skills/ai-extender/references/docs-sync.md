# Docs Sync

Refresh `platform-facts.md` when a fact is older than the user's tolerance, a validator result disagrees with it, or the user asks.

## Sources (code.claude.com/docs/en/…)

`overview` · `plugins` · `plugins/components` · `plugins/publish` · `plugins/org` · `plugins/manifest-reference` · `plugin-evals` · `plugin-marketplaces` · `skills` · `sub-agents` · `hooks` · `mcp` · `settings` · `workflows` · `agent-sdk/skills` · `llms.txt` (full index) · claude.com/docs/plugins/platform-support · plus the Agent Skills spec and Claude connector/MCP build docs. Confirm slugs from `https://code.claude.com/docs/llms.txt`; they move (e.g. plugin pages now live under `/plugins/…`). Not yet fetched: mods pages, theme file format, claude.com directory checklist.

## Procedure

1. Fetch with TinyFish `fetch_content` (markdown, no links/images), 2 pages per call. Large results are stored to a file: parse the JSON, write each page's `text` to disk, `grep -n "^#"` for headings, and read only the needed sections.
2. Compare against `platform-facts.md`; edit only lines that changed; stamp the date.
3. Propagate changes to affected `references/*.md` and to `scripts/validate_extension.py` constants (field lists, events, colors).
4. Record in `CHANGELOG.md` under the current version if same-session, else bump per versioning rules.
5. Playwright MCP is only for pages TinyFish can't render (login-gated or dynamic); never the default.
