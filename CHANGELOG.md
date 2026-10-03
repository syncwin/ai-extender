# Changelog

Newest first.

## 0.5.0 — Renamed to AI Extender

**Changed (breaking: slugs)**
- Renamed to **AI Extender for Claude**. Plugin and router slug `ai-extender` (was `ai-extension-architect`); skills `ai-extender-planner|developer|maintainer|reviewer|packager` (were `ai-extension-<role>`); agents `ai-extender-grader|comparator`. Download file: `AI Extender for Claude v0.5.0.plugin`. Reinstall as `ai-extender@syncwin`; the old plugin name is not kept as an alias.
- GitHub is now a standing rule: `syncwin/ai-extender`, with push, tag, and orphan-cleanup steps in `github.md` and `versioning.md`. `repository` and `homepage` are set.
- All skill `metadata.version` values now match the plugin version.

**Fixed**
- Eval grader patterns followed the rename (the router is now `ai-extender`, not `ai-extender-architect`).

## 0.4.0 — Remaining docs, official evals, organization rollout

**Added**
- Docs-verified references (2026-10-02): themes and workflow formats, mods pointer, surface-support table (Chat / Cowork / Claude Code), `distribution-routes.md` (routes, release prep, directory process, tags/renames, organization managed-settings keys, seed dirs), Agent SDK skills.
- Evals in the official `claude plugin eval` layout (`evals/<case>/prompt.md` + `graders/`): scaffold, audit, Cowork packaging, unrelated-request. `testing.md` documents the format, grader types, flags, CI usage, and exit codes. Trigger sets stay in `evals/evals.json` for `simulate.py`.
- Validator checks for workflows, themes, monitors, LSP, output styles, plugin `settings.json`, and eval suites (60+ checks); findings de-duplicated.
- `selftest.py` grew to 39 checks.

**Changed**
- `docs-sync.md` source list now comes from `llms.txt` and the `/plugins/…` page layout.
- Originality check run: 8-word overlap scan against the Anthropic and SyncWin source skills found only a shell path, example-URL boilerplate, and one line from the author's own skill-creator-plus.

**Fixed**
- A stale slug in a new reference was caught by the validator before release.

**Known**
- GitHub push pending tools; official evals and the claude.com directory checklist still to be run or fetched.

## 0.3.0 — Platform-neutral rename, simulator, hardening

**Changed (breaking: slugs)**
- Renamed to **AI Extension Architect for Claude**. Plugin and router slug `ai-extension-architect`; every skill and agent slug uses `ai-extension-<role>` (was `claude-extension-<role>`). "Claude" now appears only in the display name, so other platforms can be added later without renaming slugs. Download file: `AI Extension Architect for Claude v0.3.0.plugin`.
- Slug prefix rule is now `ai-` (reserved-word conflict with claude.ai/API uploads is gone). Validator option `--must-contain` now takes a prefix.
- Skill descriptions rewritten with real trigger phrasings after simulation found weak spots.

**Added**
- `simulate.py`: offline trigger simulator (calibrated lexical proxy: hit rate, false positives, overlapping descriptions) and install simulator (package, extract to a clean dir, validate the copy, list the components a user would see).
- Held-out trigger prompts in `evals/evals.json`.
- 29-check `selftest.py`: BOM/CRLF, malformed JSON, non-object hooks, missing/empty directories, symlinks, missing version, simulator.
- Composio/GitHub procedure in the packager skill's github reference; local git repo prepared with commit and tag.

**Fixed**
- Validator and packager: tolerate BOM/CRLF, skip symlinks and oversized files, reject non-object manifests/hooks/MCP config without crashing, validate the output directory; packager defaults a missing version.


## 0.2.0 — Gap closure

**Added**
- References: `components-extra.md` (LSP, output styles, monitors, `bin/`, plugin settings, channels), `mcpb-bundles.md`, `upload-and-api.md` (skills outside plugins, claude.ai/API limits), `github.md` (publish procedure).
- Scripts: `scaffold_mcp_server.py` (Node/Python), `eval_report.py` (HTML review page), `selftest.py` (18 checks).
- Agents: `ai-extension-grader`, `ai-extension-comparator`; `evals/evals.json` for the builder itself.
- Authoring rules from Anthropic's skill best-practices (degrees of freedom, plan-validate-execute, one-level references, `ServerName:tool_name`, test across models, evals first).

**Changed**
- Validator: contents-list threshold 100 lines (official), backslash-path warning.
- Tests run: 18/18 self-tests pass; the builder validates itself with 0 errors.

**Known**
- Platform docs bar `claude` in uploaded skill names; this plugin's skills keep it by owner rule (works in the installed plugin flow).

## 0.1.0 — Full in-house coverage

**Added**
- Self-contained lifecycle coverage built from the official Claude Code docs: manifest and `userConfig`, layout rules, private marketplaces, portable vs Claude-Code-only skill frontmatter, connectors, custom MCP servers, agents, hooks, commands, add-ons, updates per extension type, Cowork packaging and customization, baseline testing and trigger tuning. No dependency on other skills or plugins.
- Scripts (Python 3 only): `validate_extension.py`, `package_extension.py` (`.plugin`/`.zip`, versioned names), `scaffold_extension.py`, `aggregate_results.py`.
- `platform-facts.md` (docs verified 2026-10-01) and `docs-sync.md`.
- Efficiency, lean-build, and security standards; coverage table in README.

**Changed**
- Every skill name now contains `claude`: `claude-extension-<role>` (owner rule). Upload-target risk documented in standards; validator warns, errors under `--target upload`.
- Author `@wasimness` and company SyncWin on every skill and the plugin; SyncWin never used in names.
- Third-party license files removed; credits only (`CREDITS.md`).
- Router `ai-extension-architect`; plugin slug fixed as `ai-extension-architect`.
- Skills default to portable frontmatter (works in claude.ai/API upload); Claude-Code-only fields only when the user confirms a Claude-Code-only target.

## 0.0.1 — Initial structure

**Added**
- Router plus five role skills (planner, developer, maintainer, reviewer, packager); shared `standards.md` and `scratchpad.md`; `marketplace.json` (owner SyncWin); dormant public-release mode; changelog and README.
