# Targets and Formats

Confirm which target(s); never generate all by default. Run `ai-extender-reviewer` first on the exact files.

| Target | Output | Notes |
|---|---|---|
| Cowork | `<Display Name> v<ver>.plugin` | `cowork.md` |
| Single skill upload (claude.ai, API) | `<Display Name> v<ver>.zip`, folder as top-level entry | Portable frontmatter only (validator `--target upload`); name must pass reserved-word rules |
| Plugin, manual install / share | `<Display Name> v<ver>.zip`, plugin folder as top-level entry (or send the folder) | Anthropic's docs: share a plugin as its directory or a zip |
| Private git marketplace | repo with `.claude-plugin/marketplace.json` + plugin source | below |
| Claude Code local test | `claude plugin marketplace add ./dir` then `claude plugin install <name>@<marketplace>`; `claude --plugin-dir <dir>` | `/reload-plugins` applies edits |

Routes, release prep, directory, organization rollout: `distribution-routes.md`.

claude.ai and Cowork "Upload plugin" takes a zip of the plugin folder (≤200 MB, ≤5,000 files); the `.plugin` file is built the same way (zip, plugin root as archive root).

## Build

`python ${CLAUDE_SKILL_DIR}/scripts/package_extension.py <dir> --format plugin|zip [--out DIR] [--skip-validate]`

It runs the validator (blocks on errors), derives the visible name from `displayName` (plugin) or the skill's title, appends `v<version>`, excludes `.git`, `.DS_Store`, `__pycache__`, `node_modules`, and prior archives, and prints the output path.

## Private marketplace entry

- `marketplace.json`: required `name`, `owner.name`, `plugins[]`; each entry `name` (must equal the plugin's manifest name), `source`, optional `description`, `category`.
- `source`: relative `./path` (no `..`), `github` `{repo}`, `git-subdir`, `url`, `archive`, `npm`, `command`; pin with `ref`/`sha`. Use `./` when the repo is the marketplace; a `github` source when the plugin lives in a separate repo.
- Test: `claude plugin validate <marketplace-dir>`, add, install, `claude plugin list`.
- Reserved marketplace names (e.g. `claude-plugins-official`) are refused.

## Final checks

- [ ] Validator ran on the packaged files, not an earlier draft
- [ ] Version, changelog, manifest, and filename agree
- [ ] README accurate for the targets actually produced
- [ ] `LICENSE` matches declared license; `CREDITS.md` present
- [ ] Scratchpad emitted
