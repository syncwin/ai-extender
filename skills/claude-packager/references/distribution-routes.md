# Distribution Routes

Verified 2026-10-02 (code.claude.com/docs/en/plugins/publish, plugin-evals, plugins/org; claude.com/docs/plugins/platform-support); §3 and §5 rechecked 2026-11-02 against code.claude.com/docs/en/plugins/host-marketplace and claude.com/docs/cowork/guide/plugins, plus four live marketplace installs.

## Contents

1. Pick a route · 2. Prepare for release · 3. Own marketplace · 4. Anthropic's directory · 5. Versions, tags, renames · 6. Organization rollout

## 1. Pick a route

| Route | Who installs | Needs | Updates |
|---|---|---|---|
| No marketplace | whoever receives the folder or zip | the folder / a `.zip` | none; they load your copy (`--plugin-dir`, `--plugin-url` for a zip on a release, or move the folder under `~/.claude/skills/`) |
| Own marketplace | anyone who can reach the repo (private repo = private marketplace) | git repo with `.claude-plugin/marketplace.json` | `claude plugin update <name>@<marketplace>`; auto-update is a per-marketplace user setting, off by default |
| Anthropic's directory | people on claude.ai/Cowork (also syncs to their Claude Code) | GitHub repo + a paid claude.ai plan | automatic after the pushed version is published |

`claude-plugins-official` is Anthropic-managed; partners use the plugin directory submission form linked from its README, not the portal.

## 2. Prepare for release (every release)

1. **Permanent kebab-case name**: users install by `name@marketplace`; a renamed plugin is a different plugin. Use `displayName` for the label.
2. **Version policy**: with `version` set in `plugin.json`, pushing commits without bumping it leaves users on the old copy (`already at the latest version`). Bump every release, or omit `version` in a git marketplace to use the commit SHA. Set `version` in `plugin.json` only, never also in the marketplace entry: Claude uses `plugin.json` and `validate` reports the mismatch.
3. `claude plugin validate --strict ./plugin` (clean = "Validation passed"; `--strict` fails on warnings; drop it only if you omit `version`). Our `validate_extension.py` runs first.
4. Install from a local marketplace and start a session: `claude plugin marketplace add ./mkt` → `claude plugin install <name>@<mkt>`.
5. Metadata users see: `description`, `author`, `homepage` (must parse as a URL), `repository`, `displayName` (in `plugin.json` and the marketplace entry), `icon` (`./assets/icon.png`, square, 512 px; keep the SVG beside it; with no image library, render the SVG with a headless browser screenshot), README. The README lists every command as `/<plugin>:<skill>`, because the plugin page shows the README and users look there for how to start it.
6. Run evals if present: `claude plugin eval` (`claude-developer/references/testing.md`).

## 3. Own marketplace

`.claude-plugin/marketplace.json` beside `plugin.json`: `{"name": "...", "owner": {"name": "..."}, "plugins": [{"name": "<same as manifest>", "source": "./"}]}`. No submission step: once pushed, it is published. Users: `claude plugin marketplace add <owner>/<repo>` then `claude plugin install <name>@<marketplace>` (or `/plugin install <name> --marketplace <owner>/<repo>` in a session).

- **One repo, one marketplace per product.** Don't list a new plugin in another plugin's marketplace, especially one under directory review. Repo slug = plugin slug unless the user names another.
- **Pick the marketplace `name` once.** Claude identifies a marketplace by `name`, not by repo, and a user can't hold two with the same name. Make it distinctive (`<company>-<plugin>`; plain words like `humanize-ai` collide). Renaming it strands existing installs: the app keeps showing "from <old name>" with the install-time version and a disabled Update, until the user removes the plugin and the old marketplace and adds the repo again. Tell users so whenever a rename is unavoidable.
- **Where users add it.** claude.ai, desktop and mobile: Customize → Plugins → Add marketplace → `<owner>/<repo>`; that install lives on the account and reaches the Code tab too. Adding the same repo again with `claude plugin marketplace add` on that computer creates a second, clashing copy, so give one route, not both. An uploaded `.plugin` never updates: when switching to the marketplace, uninstall the uploaded copy first.
- **How updates arrive.** A user gets a new copy only when `version` changes and their copy of the marketplace refreshes (Claude Code: per-marketplace auto-update, off by default, or `claude plugin marketplace update <name>`; Cowork: Check for updates or Sync automatically where offered). Apps can keep the install-time snapshot; if a plugin stays old, remove and reinstall it. To prove the repo itself is right, install into an isolated config: `CLAUDE_CONFIG_DIR=<temp dir> claude plugin marketplace add <owner>/<repo>`, then `claude plugin install`, then `claude plugin list` shows the version users will get.

## 4. Anthropic's directory (public; only on the user's explicit release instruction, see `release.md`)

While a submission is in review, push nothing to the default branch: keep changes on a separate branch (for example `next`) and merge after the review, so reviewers see a stable repo. Submit from the developer portal (claude.ai/directory/manage); needs a paid plan (Pro/Max own account; Team/Enterprise Owner or a custom role with the Directory permission). The portal applies extra directory rules the CLI doesn't check, and derives supported surfaces from the component table (`components-extra.md`). Checklist, results, and submission steps: `directory-checklist.md` (verified 2026-10-03); run `validate_extension.py --target directory` first. Re-fetch claude.com/docs/plugins/submit and /pre-submission-checklist at submission time, since limits change.

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
