# Distribution Routes

Verified 2026-10-02 (code.claude.com/docs/en/plugins/publish, plugin-evals, plugins/org; claude.com/docs/plugins/platform-support).

## Contents

1. Pick a route · 2. Prepare for release · 3. Own marketplace · 4. Anthropic's directory · 5. Versions, tags, renames · 6. Organization rollout

## 1. Pick a route

| Route | Who installs | Needs | Updates |
|---|---|---|---|
| No marketplace | whoever receives the folder or zip | the folder / a `.zip` | none; they load your copy (`--plugin-dir`, `--plugin-url` for a zip on a release, or move the folder under `~/.claude/skills/`) |
| Own marketplace | anyone who can reach the repo (private repo = private marketplace) | git repo with `.claude-plugin/marketplace.json` | `claude plugin update <name>@<marketplace>`; auto-update is a per-marketplace user setting, off by default |
| Anthropic's directory | people on claude.ai/Cowork (also syncs to their Claude Code) | GitHub repo + a paid claude.ai plan | automatic after the pushed version is published |

`claude-plugins-official` takes no portal submissions (partner contact only).

## 2. Prepare for release (every release)

1. **Permanent kebab-case name**: users install by `name@marketplace`; a renamed plugin is a different plugin. Use `displayName` for the label.
2. **Version policy**: with `version` set in `plugin.json`, pushing commits without bumping it leaves users on the old copy (`already at the latest version`). Bump every release, or omit `version` in a git marketplace to use the commit SHA.
3. `claude plugin validate --strict ./plugin` (clean = "Validation passed"; `--strict` fails on warnings; drop it only if you omit `version`). Our `validate_extension.py` runs first.
4. Install from a local marketplace and start a session: `claude plugin marketplace add ./mkt` → `claude plugin install <name>@<mkt>`.
5. Metadata users see: `description`, `author`, `homepage` (must parse as a URL), `repository`, README.
6. Run evals if present: `claude plugin eval` (`ai-extender-developer/references/testing.md`).

## 3. Own marketplace

`.claude-plugin/marketplace.json` beside `plugin.json`: `{"name": "...", "owner": {"name": "..."}, "plugins": [{"name": "<same as manifest>", "source": "./"}]}`. No submission step: once pushed, it is published. Users: `claude plugin marketplace add <owner>/<repo>` then `claude plugin install <name>@<marketplace>` (or `/plugin install <name> --marketplace <owner>/<repo>` in a session).

## 4. Anthropic's directory (public; only on the user's explicit release instruction, see `release.md`)

Submit from the developer portal (claude.ai/directory/manage); needs a paid plan (Pro/Max own account; Team/Enterprise Owner or a custom role with the Directory permission). The portal applies extra directory rules the CLI doesn't check, and derives supported surfaces from the component table (`components-extra.md`). The submission steps, per-version checks, and pre-submission checklist live on claude.com (Publish to the directory, Submit a plugin, Plugin pre-submission checklist): fetch them at that time (`docs-sync.md`).

## 5. Versions, tags, renames

- Tag releases when other plugins depend on a version range: `claude plugin tag` creates `{name}--v{version}` (`--push` sends it).
- Never rename a published plugin. If unavoidable, add a `renames` entry in the marketplace file so existing installs migrate (otherwise: `Plugin "<name>" not found in marketplace`).
- `dependencies` in `plugin.json`: bare name or `{name, version range}`; Claude Code installs and enables them.

## 6. Organization rollout (managed settings, Claude Code)

Delivery: server-managed (claude.ai admin console, Owner), MDM, or `managed-settings.json`; by default only the first source that delivers a key applies (`managedSourcesBehavior: "merge"` changes that).

| Need | Key |
|---|---|
| Register a marketplace on every machine | `extraKnownMarketplaces` `{name: {source: {source: "github", repo: "org/repo"}, autoUpdate: true}}` |
| Force-install / block a plugin | `enabledPlugins` `{"plugin@marketplace": true|false}` (managed value locks it) |
| Allowlist / blocklist marketplace sources | `strictKnownMarketplaces` (`[]` blocks all) / `blockedMarketplaces` (checked first); entries: `github` (`org/*` wildcard), `git`, `url`, `file`, `directory`, `hostPattern`, `pathPattern`, `skills-dir` |
| Block local/URL loading | `disableSideloadFlags` |
| Only plugin-sourced customization | `strictPluginOnlyCustomization` |
| Stop synced claude.ai plugins | `syncClaudeAiPlugins: false` |
| Containers / CI without git | seed dir: build with `CLAUDE_CODE_PLUGIN_CACHE_DIR`, run with `CLAUDE_CODE_PLUGIN_SEED_DIR` |
| Per-repo requirement | `.claude/settings.json` `extraKnownMarketplaces` (needs folder trust) + `enabledPlugins` |

Claude.ai/Cowork availability per plugin (Not available / Available / Installed by default / Required) is set by an Owner in Organization settings > Plugins & skills; it does not set the keys above. Audit via OpenTelemetry (`plugin_installed`, `plugin_loaded`) and, on Enterprise, `GET /v1/organizations/analytics/plugins`. Per-user targeting needs separate endpoint-managed settings.
