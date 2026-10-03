# Add-ons for existing extensions

Extend someone else's plugin/skill/connector without forking or editing it.

## Approach

1. **Read the base** (its manifest, skills, hooks, connectors, documented extension points) and record the version you target.
2. **Ship a separate plugin.** Declare `"dependencies": ["base-plugin"]` (or `"base@marketplace"`, optionally with `version`) so the base must be enabled.
3. **Add, don't override.** New skills/agents/commands with your own prefix; hooks on the same events; your own connectors. Components are namespaced `your-plugin:name`, so nothing collides.
4. **Integrate through documented surfaces only:** the base's hook events, tool names (`mcp__plugin_<base>_<server>__…`), config values, file formats. Never edit or copy base files.
5. **Compatibility:** state supported base versions in README and `compatibility`; the reviewer checks them on each base update.
6. **Licensing:** confirm the base license permits add-ons/redistribution of your own code; credit, don't bundle.
7. Name: `<acronym>-<base>-addon` style role slug per standards; own version starting `0.0.1`.

## When a fork is the only way

Stop and ask. Forking needs license verification and a maintenance commitment (see `maintainer/references/versioning.md`).
