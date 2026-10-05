# Changelog

Newest first.

## 1.0.0: First public release

Released after the final self-audit, run from an installed copy, and the first live `claude plugin eval` run.

**Fixed**
- One-skill plugins: the planner now names the single skill after the plugin and skips the router, instead of either adding an empty router or leaving no entry skill. Two or more skills still get a router, and role skills carry the user's acronym when one is set.
- Intake: the router shows a short plan with its defaults first and asks at most three questions, only ones the user alone can answer. The live eval caught it opening with a five-question list.
- Eval suite: the audit and packaging cases had nothing to work on. Each now ships a sample in `fixture/notes-helper`: a deliberately flawed plugin for the audit, a clean skill for packaging. Neither has its own manifest. The packaging case is now `package-skill-upload` and may run the bundled scripts, and the scaffold case's grader follows the one-skill rule.
- Companion prompts: `Text` (single-line) fields are confirmed against a real Prompt Builder export and no longer warned about; `maxLength` may be `""` for no limit on `Text` and `Textarea`.
- Script reports and the scratchpad template no longer use dashes in headings; number ranges in references read "2 to 4".

**Changed**
- Credits: removed the `skill-creator-plus` entry.
- Docs: shorter plugin description that names claude.ai too; the README status now says exactly what CI runs.
- The audit test's sample skill no longer tells Claude to email anything, so a security scan has nothing to misread. It still has plenty to fail on: vague descriptions, no manifest or license, and an agent with no tool limits.
- Final self-audit from the installed 1.0.0 build:
  - Scoping now matches the router: defaults go in the plan, with at most three questions asked alongside it. Author, company, license, and acronym appear as plan defaults instead of separate questions, and packaging uses the target the plan settled instead of asking again.
  - The developer skill hands any build without an approved plan to the planner, and the planner no longer claims to run before the router.
  - Acronym prefixes are optional everywhere (architecture, add-on naming, this changelog), matching the standards.
  - Fixed contradictions: the contents-list threshold is 100 lines in every file, the manifest reference points to its current docs address, the platform-facts header shows its full date range, and the README describes CI exactly.
  - The companion prompt guide lists all five validator codes (`C000` to `C004`), the GitHub asset example uses the full display name, and the Ponytail credit links to its repository.
- Two self-tests (67 in total): a `Text` field with no length limit passes, and a zero `maxLength` is rejected.

## 0.11.0: Self-audit fixes

Pre-release. Findings from AI Extender's audit of itself, run from an installed copy.

**Fixed**
- The router named the skill-folder variables literally, so Claude Code replaced them with real paths and the sentence stopped making sense. It now describes the fallback without the variable names.
- Cowork detection looked only for `mnt/.plugins`, which cloud Cowork sessions don't have. It now also checks `/mnt/user-data/outputs`, and the script-finding fallback searches the plugin folders instead of the whole disk.
- MCP server scaffold: Node dependencies sat in `servers/<name>/package.json`, where Claude Code never installs them, and the guidance to install into the data folder didn't work for ES modules. Node dependencies now go in the plugin-root `package.json` (installed by Claude Code when a lockfile is committed). Python servers get a `SessionStart` hook that installs `requirements.txt` into the plugin data folder and a `PYTHONPATH` pointing there.
- `.gitignore` now ignores `dist/`, where the packager writes by default.
- Audits no longer end with "hand over the file" when nothing was built.

**Added**
- Work-on-a-copy rule: attached `.plugin`/`.zip` files and installed plugins are unpacked or copied to a working folder; installed copies are read-only.
- Validator: reserved plugin names (`P016`, matching `claude plugin validate`: `claude-`/`anthropic-` prefixes are errors, `claude` as a word is a warning), directory listing fields (`P017`), and a companion prompt that never names its slash command (`C004`). The listing fields no longer trigger unknown-key warnings.
- The scaffolder refuses reserved plugin slugs.
- `plugin.json`: `documentationUrl` and `supportUrl` for the directory listing.
- Platform facts verified 2026-10-05: listing fields, plugin-name rules, data folder lifecycle, automatic Node installs, rejected outbound symlinks.
- Seven self-tests (65 in total).

**Changed**
- Packaging reference lists the real exclusions and the companion prompt step; public-release steps name the listing fields.

## 0.10.0: Companion prompts, metadata, pre-release hardening

Pre-release. 1.0 waits for the final self-audit from a real install.

**Added**
- Companion prompt for every extension. `claude-packager/scripts/companion_prompt.py` writes a Prompt Builder JSON (`prompts/<title-slug>.json`, format `prompt-builder-plain` 2.0) from the manifest or from a spec, checks it, and copies it next to the package. The packager runs it on every build and stops on a broken prompt; the scaffolder writes a default one. Rules in `ai-extender/references/companion-prompt.md`, checked against the Prompt Builder help center and two real exports.
- AI Extender's own companion prompt: `prompts/ai-extender-for-claude.json` (goal, request, audience, surface, files).
- Validator: companion prompt checks (`C000`-`C003`) and version consistency between the manifest, its metadata, and every skill (`P015`, `S015`).
- Router: how to find the bundled scripts when `${CLAUDE_SKILL_DIR}` is not substituted (Cowork, claude.ai), and what to do with no Python or shell.
- Eight self-tests (58 in total): prompt written by the scaffolder, four broken-prompt cases, spec rewrite keeping the prompt `id`, prompt copied beside the package, no bytecode left in a checked plugin.

**Changed**
- Metadata everywhere: `plugin.json` has author `@wasimness` with company `SyncWin`, and a `metadata` block with display name, version, author, company, homepage, repository, license, and the companion prompt path. Every skill and agent carries `displayName`, `version`, `author`, `company`, and `plugin`. Generated extensions get the same keys from the scaffolder.
- Planner shows the companion prompt's fields in the one plan approval; developer writes them; reviewer checks them; maintainer refreshes them when skills change (keeping the prompt `id`).
- Scaffolded plugins get a README that passes the directory's 40-word rule (install, companion prompt, disclosure sections), a plain `## 0.0.1: <date>` changelog heading, and no placeholder author name.
- GitHub procedure: attach the companion prompt to releases and label assets, since GitHub turns spaces in asset names into dots.

**Fixed**
- The validator left `__pycache__` inside the plugin it checked once it began importing the prompt checker; bytecode writing is now off.
- Scaffold usage example suggested a `claude-` slug, which claude.ai and the API reject for uploaded skills.
- The short-README self-test relied on the scaffold's README being short.

## 0.9.0: Public launch

**Added**
- Plain-language start. Run `/ai-extender` with no request, or a vague one, and it asks one question: what should Claude do for you? Technical choices are worked out for you and shown as a short plan with one approval.
- Internal business solutions as their own route. The planner now asks who will use the result (just me, my team, the whole organization) and picks the delivery to match: `.plugin` file, private marketplace, or organization rollout. Company rules and templates become reference files; per-user values become `userConfig`.
- Eval case `plain-language-intake` and two business-use trigger prompts.
- `.github/` for the public repo: CI (self-test, strict directory validation, trigger simulation on Python 3.9 to 3.13), bug and feature issue templates, and a pull request checklist.

**Changed**
- Publisher in `plugin.json` is now SyncWin; @wasimness is listed as maintainer in `metadata`.
- Extensions built for users carry only the author, company, contact, and repo the user supplies. This plugin's own details are never copied into them.
- GitHub steps (push, tag, orphan cleanup) run only when the user asks for GitHub or keeps an existing repo in sync. The owner is always asked, never assumed, and the first push to a repo is confirmed.
- Docs refresh uses whatever web fetch tool the session has and tells the user first; no specific third-party tool is named.
- README rewritten for first-time users, with a full list of what the plugin runs, reads, and sends. SECURITY, CONTRIBUTING, and CREDITS rewritten for a public audience.
- Router description gained business-process phrasings and dropped a reference to a private skill.

**Fixed**
- README promised a CI workflow and issue template that the package didn't contain.
- A duplicated 0.6.0 heading in this changelog.
- Removed personal and internal notes from references and evals.

## 0.8.0: Platform layering and public-release hardening

**Changed**
- Agents are now thin Claude adapters over one platform-neutral protocol (`ai-extender/references/agent-protocols.md`), so another platform needs only its own thin adapter, not new logic. `claude-grader` and `claude-comparator` keep their names and tools and carry an inline fallback.
- Claude-only shared references took the platform prefix: `platform-facts.md` became `claude-platform-facts.md`, `docs-sync.md` became `claude-docs-sync.md`.
- The packager leaves `.github/` out of the `.plugin` file.

**Added**
- `ai-extender/references/platforms.md`: layers (`ai-` neutral core, `claude-` today, `chatgpt-` and `gemini-` planned), naming, and the steps for adding a platform.
- `SECURITY.md`, `CONTRIBUTING.md`, an issue template, and a GitHub Actions workflow (self-test, strict directory validation, and trigger simulation on Python 3.9 to 3.12).
- README sections: requirements, security and data handling, troubleshooting.

**Known**
- Not run in a real Claude Code or Cowork install; Windows and macOS are not covered by CI.

## 0.7.0: Platform-prefix naming (`ai-` neutral, `claude-` Claude-specific)

**Changed (breaking: slugs)**
- Naming decision: `ai-` marks platform-neutral components and `claude-` marks Claude-specific ones, so ChatGPT and Gemini variants can join later as `chatgpt-*` and `gemini-*`. Router `ai-extender` (unchanged). Role skills `claude-planner|developer|maintainer|reviewer|packager` (0.6.0 bare `planner|...`; 0.5.0 `ai-extender-<role>`). Agents `claude-grader|comparator`. Invoked as `/ai-extender:claude-planner` and so on. Mapping: add the `claude-` prefix to the 0.6.0 name.
- `standards.md` §1 records the rule and its trade-off. Skill names containing `claude` are rejected when uploaded on their own to claude.ai or the API; the validator now reports that as info for plugin targets and an error for `--target upload`.

**Fixed**
- Evals and cross-references follow the new slugs.

## 0.6.0: Bare role slugs, mods, themes, directory checks

**Changed (breaking: slugs)**
- Role skills and agents dropped the repeated plugin name, because Claude Code already namespaces every component as `<plugin>:<name>` (a skill named like its plugin shows as `/<plugin>`): `ai-extender-planner|developer|maintainer|reviewer|packager` became `planner|developer|maintainer|reviewer|packager` (`/ai-extender:planner`, ...), agents `ai-extender-grader|comparator` became `grader|comparator`. The router stays `ai-extender`. Mapping is old to new with the `ai-extender-` prefix removed. The `ai-` prefix rule is gone; generated extensions get bare roles unless the user supplies an acronym (`scaffold_extension.py --prefix`).
- `standards.md` records the rule: never repeat the plugin name inside a component name.

**Added**
- `developer/references/mods.md` (hooks modules, events, mods API, limits, admin settings) and `packager/references/directory-checklist.md` (Anthropic directory blocks, holds, scan, submission steps), both verified 2026-10-03.
- Validator: `modules` checks (H006, H007), theme `base`/`overrides` checks (T003, T004), and `--target directory` (D001-D011: name rules, README of 40+ words, license, system files, symlinks, Windows-safe names, file size and count limits, unpinned launchers, non-https MCP URLs). Self-tests grew to 50.
- Theme format details (`name`, `base`, `overrides`, `custom:<slug>`) in `components-extra.md`.

**Fixed**
- The validator reported a mods-only `hooks.json` as an unknown hook event.
- `docs-sync.md` and `platform-facts.md` no longer list mods, themes, or the directory checklist as unfetched. The terminal-config themes page could not be fetched; theme facts rest on the changelog and secondary sources and say so.

**Known**
- `claude plugin eval` and `claude plugin validate` have not been run in a real Claude Code install.

## 0.5.0: Renamed to AI Extender

**Changed (breaking: slugs)**
- Renamed to **AI Extender for Claude**. Plugin and router slug `ai-extender` (was `ai-extension-architect`); skills `ai-extender-planner|developer|maintainer|reviewer|packager` (were `ai-extension-<role>`); agents `ai-extender-grader|comparator`. Download file: `AI Extender for Claude v0.5.0.plugin`. Reinstall as `ai-extender@syncwin`; the old plugin name is not kept as an alias.
- GitHub is now a standing rule: `syncwin/ai-extender`, with push, tag, and orphan-cleanup steps in `github.md` and `versioning.md`. `repository` and `homepage` are set.
- All skill `metadata.version` values now match the plugin version.

**Fixed**
- Eval grader patterns followed the rename (the router is now `ai-extender`, not `ai-extender-architect`).

## 0.4.0: Remaining docs, official evals, organization rollout

**Added**
- Docs-verified references (2026-10-02): themes and workflow formats, mods pointer, surface-support table (Chat / Cowork / Claude Code), `distribution-routes.md` (routes, release prep, directory process, tags/renames, organization managed-settings keys, seed dirs), Agent SDK skills.
- Evals in the official `claude plugin eval` layout (`evals/<case>/prompt.md` + `graders/`): scaffold, audit, Cowork packaging, unrelated-request. `testing.md` documents the format, grader types, flags, CI usage, and exit codes. Trigger sets stay in `evals/evals.json` for `simulate.py`.
- Validator checks for workflows, themes, monitors, LSP, output styles, plugin `settings.json`, and eval suites (60+ checks); findings de-duplicated.
- `selftest.py` grew to 39 checks.

**Changed**
- `docs-sync.md` source list now comes from `llms.txt` and the `/plugins/…` page layout.
- Originality check: an 8-word overlap scan against the studied skills found only a shell path, example-URL boilerplate, and one line from an earlier skill by the same author.

**Fixed**
- A stale slug in a new reference was caught by the validator before release.

**Known**
- GitHub push pending tools; official evals and the claude.com directory checklist still to be run or fetched.

## 0.3.0: Platform-neutral rename, simulator, hardening

**Changed (breaking: slugs)**
- Renamed to **AI Extension Architect for Claude**. Plugin and router slug `ai-extension-architect`; every skill and agent slug uses `ai-extension-<role>` (was `claude-extension-<role>`). "Claude" now appears only in the display name, so other platforms can be added later without renaming slugs. Download file: `AI Extension Architect for Claude v0.3.0.plugin`.
- Slug prefix rule is now `ai-` (reserved-word conflict with claude.ai/API uploads is gone). Validator option `--must-contain` now takes a prefix.
- Skill descriptions rewritten with real trigger phrasings after simulation found weak spots.

**Added**
- `simulate.py`: offline trigger simulator (calibrated lexical proxy: hit rate, false positives, overlapping descriptions) and install simulator (package, extract to a clean dir, validate the copy, list the components a user would see).
- Held-out trigger prompts in `evals/evals.json`.
- 29-check `selftest.py`: BOM/CRLF, malformed JSON, non-object hooks, missing/empty directories, symlinks, missing version, simulator.
- GitHub publishing procedure in the packager skill's `github.md`.

**Fixed**
- Validator and packager: tolerate BOM/CRLF, skip symlinks and oversized files, reject non-object manifests/hooks/MCP config without crashing, validate the output directory; packager defaults a missing version.


## 0.2.0: Gap closure

**Added**
- References: `components-extra.md` (LSP, output styles, monitors, `bin/`, plugin settings, channels), `mcpb-bundles.md`, `upload-and-api.md` (skills outside plugins, claude.ai/API limits), `github.md` (publish procedure).
- Scripts: `scaffold_mcp_server.py` (Node/Python), `eval_report.py` (HTML review page), `selftest.py` (18 checks).
- Agents: `ai-extension-grader`, `ai-extension-comparator`; `evals/evals.json` for the builder itself.
- Authoring rules from Anthropic's skill best-practices (degrees of freedom, plan-validate-execute, one-level references, `ServerName:tool_name`, test across models, evals first).

**Changed**
- Validator: contents-list threshold 100 lines (official), backslash-path warning.
- Tests run: 18/18 self-tests pass; the builder validates itself with 0 errors.

**Known**
- Platform docs bar `claude` in uploaded skill names; this plugin's skills keep it by design (works in the installed plugin flow).

## 0.1.0: Full in-house coverage

**Added**
- Self-contained lifecycle coverage built from the official Claude Code docs: manifest and `userConfig`, layout rules, private marketplaces, portable vs Claude-Code-only skill frontmatter, connectors, custom MCP servers, agents, hooks, commands, add-ons, updates per extension type, Cowork packaging and customization, baseline testing and trigger tuning. No dependency on other skills or plugins.
- Scripts (Python 3 only): `validate_extension.py`, `package_extension.py` (`.plugin`/`.zip`, versioned names), `scaffold_extension.py`, `aggregate_results.py`.
- `platform-facts.md` (docs verified 2026-10-01) and `docs-sync.md`.
- Efficiency, lean-build, and security standards; coverage table in README.

**Changed**
- Every skill name now contains `claude`: `claude-extension-<role>` (by design). Upload-target risk documented in standards; validator warns, errors under `--target upload`.
- Author `@wasimness` and company SyncWin on every skill and the plugin; SyncWin never used in names.
- Third-party license files removed; credits only (`CREDITS.md`).
- Router `ai-extension-architect`; plugin slug fixed as `ai-extension-architect`.
- Skills default to portable frontmatter (works in claude.ai/API upload); Claude-Code-only fields only when the user confirms a Claude-Code-only target.

## 0.0.1: Initial structure

**Added**
- Router plus five role skills (planner, developer, maintainer, reviewer, packager); shared `standards.md` and `scratchpad.md`; `marketplace.json` (owner SyncWin); dormant public-release mode; changelog and README.
