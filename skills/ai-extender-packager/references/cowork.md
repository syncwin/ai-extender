# Cowork

## Is Cowork available? (infer, never read billing state)

Run once, when packaging starts: `find mnt/.local-plugins mnt/.plugins -maxdepth 1 -type d 2>/dev/null`.
- Output present, or the outputs directory for delivery is reachable → Cowork path available.
- Otherwise → say plainly that Cowork packaging isn't available in this session and use `targets.md` formats. Don't guess why.

## Cowork-specific rules (verified in `platform-facts.md`)

- Plugin = directory of skills, agents, hooks, MCP config. Delivered as a `.plugin` file: a zip whose root is the plugin root (not wrapped in a folder).
- Loads in Cowork: skills, commands, agents, hooks, remote MCP, local MCP only when the session runs on the user's computer. Ignored: LSP, output styles, themes, plugin `settings`. Full table: `ai-extender-developer/references/components-extra.md`.
- A plugin containing `bin/` is not installed by claude.ai or Cowork; validator flags it as an error for `--target cowork`.
- Values users must supply → `userConfig`, not text placeholders.
- Keep user-facing conversation in plain language: say what the plugin will do, not file paths or schema names, unless asked.

## Build and deliver

1. `ai-extender-reviewer` passes with `--target cowork`.
2. `python ${CLAUDE_SKILL_DIR}/scripts/package_extension.py <plugin-dir> --format plugin --out /mnt/user-data/outputs`
   (builds in a temp dir first, because writing straight into outputs can fail on permissions; names the file `<Display Name> v<version>.plugin`).
3. Present the file. If the user wants it editable later: `ai-extender-maintainer/references/updating.md` (customizing).

## Free vs paid

Free or non-Cowork sessions still get every other target. Never claim `.plugin` delivery happened unless the file exists in outputs.
