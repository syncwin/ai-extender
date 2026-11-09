# ai-extender agent guide

AI Extender for Claude: plans, builds, checks and packages Claude skills, plugins, connectors and agents.

**Structure:** `skills/aix` (router) and `aix-planner|developer|maintainer|reviewer|packager|prompter|cleaner`, `agents/` (comparator, grader), `hooks/hooks.json`, `evals/`, `.github/` (CI).

## Commands
- Self-test (must pass): `python skills/aix-reviewer/scripts/selftest.py`
- Strict validation (must pass): `python skills/aix-reviewer/scripts/validate_extension.py . --strict --target directory --require-meta author,company`
- Secret scan: `python skills/aix-reviewer/scripts/scan_secrets.py`
- Version bump: `skills/aix-maintainer/scripts/bump_version.py`; package: `skills/aix-packager/scripts/package_extension.py`
- Validate: `claude plugin validate . --strict`
- Evals (real model calls): `claude plugin eval . --trust-plugin --ablation none --scaffold --allow-tools Read Glob Grep Skill -j 4 --no-publish`. Rebuild cases with `python A:\Automation\plugin-evals\regen_evals.py <plugin> <router> <fixture ids>`. Write results outside the repo (`D:\SyncWin\AI Outputs\<plugin>\eval-results`); the packager includes repo files.

## Workflow
1. Read the skill or script you change, plus its neighbours.
2. Make the smallest change; run the closest check, then the full gate.
3. Update `CHANGELOG.md` for behavior changes; log ideas in `IMPROVEMENTS.md`.

## Rules
- Run the closest check and the full gate before committing. Never delete or weaken tests or evals. Report failed, skipped or timed-out runs honestly; NOT RUN is never a pass.
- Follow neighbouring files. Keep each `SKILL.md` under 500 lines; move detail into `references/`.
- On release, bump `version` in `.claude-plugin/plugin.json` and every skill's `metadata.version` together; add a `CHANGELOG.md` entry per behavior change.
- No commits, pushes or PRs unless asked. Work on a branch and open a PR; never push to main.
- No new dependencies without asking (scripts stay on the Python standard library).
- Never commit secrets. Never pick names or slugs without user confirmation.
- Pin any GitHub Action to a full commit SHA with the version in a comment; give each job least permissions.
- A platform fact needs its official page and the date checked. Keep private data (keys, client names, internal URLs) out of every file.
- Plugin versions 1.0.0 and 1.1.0 are both kept (user decision, 4 Nov). The public-review `syncwin` marketplace entry is not changed.

## Model routing
Opus plans, decides, writes self-contained briefs with a report word limit, and reviews every result. Haiku for search, reading and mechanical edits. Sonnet for coding, tests and multi-step work. Do 1-2 tool calls inline.

## Docs
README.md, CONTRIBUTING.md, CHANGELOG.md, SECURITY.md; ideas and feedback in `IMPROVEMENTS.md`.
