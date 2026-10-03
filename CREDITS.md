# Credits

Independent, in-house implementation. No third-party skill, plugin, or code is forked, copied, or required at runtime; every capability is built into this plugin from the official Claude documentation (code.claude.com/docs) and studied approaches.

Studied, then rewritten:
- Anthropic `/skill-creator`: test, baseline, grading, and description-tuning workflow → `developer/references/testing.md` and `scripts/aggregate_results.py`; packaging and validation → `ai-extender:packager` and `ai-extender:reviewer` scripts.
- Anthropic `/create-cowork-plugin`, `/cowork-plugin-customizer`: Cowork build and customization flow → `packager/references/cowork.md`, `maintainer/references/updating.md`.
- Anthropic `plugin-dev` and `mcp-server-dev` plugins (existence only): scope of plugin, hook, and MCP authoring.
- Ponytail: lean-implementation principle.
- `/skill-creator-plus` (SyncWin): de-duplication and versioning disciplines.

Not affiliated with or endorsed by Anthropic.
