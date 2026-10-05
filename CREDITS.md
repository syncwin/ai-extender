# Credits

AI Extender is an independent implementation. It doesn't fork, copy, or need any third-party skill, plugin, or code at runtime. Every capability was written for this plugin from the official Claude documentation (code.claude.com/docs and claude.com/docs) after studying how other tools approach the same jobs.

Studied, then rewritten:

- Anthropic's `/skill-creator`: the test, baseline, grading, and description-tuning loop informed `claude-developer/references/testing.md` and `scripts/aggregate_results.py`; its packaging and validation steps informed the packager and reviewer scripts.
- Anthropic's `/create-cowork-plugin` and `/cowork-plugin-customizer`: the Cowork build and customization flow in `claude-packager/references/cowork.md` and `claude-maintainer/references/updating.md`.
- Anthropic's `plugin-dev` and `mcp-server-dev` plugins: their scope only (what plugin, hook, and MCP authoring should cover).
- Ponytail: the lean-implementation principle.

Not affiliated with or endorsed by Anthropic.
