# Self-test (recipe)

Replaces the former script `selftest.py`. Run this checklist after any change to the builder's tooling or recipes. Claude performs each check with its own tools (Read, Glob, Grep, Write, Edit, and Bash only for standard OS and git commands such as `cp -r`, `unzip -l`, `git ls-files`). Nothing here is code to save and run. There are 180 checks (numbered 1 to 180, same order as the original script).

## Contents

1. Purpose, when to use, output
2. Conventions used in the tables
3. Checks (two files)
9. Notes on checks marked (N)

## 1. Purpose, when to use, output

Purpose: prove the builder's checks still catch what they must and still pass what they must. Build a fixture plugin, check the validator passes it, break it in known ways and confirm each break is caught, package it in both formats, and exercise the helper recipes.

Output: one line per check, `PASS <name>` or `FAIL <name>`; a FAIL also carries up to 300 characters of the actual output as detail; then a blank line and `<passed>/<total> passed`. Verdict: all 180 passed = success (original exit 0); any FAIL = failure (original exit 1). Report every FAIL to the user with its detail; do not hide or retry a failing check.

## 2. Conventions used in the tables

- Each former script `<name>.py` has a recipe `references/<name-with-dashes>.md` in the references folder of the skill that owned it (for example `validate_extension.py` is `validate-extension.md`, `scaffold_extension.py` is `scaffold-extension.md`). "Run X" below means: follow that recipe and read its verdict. "Verdict fail" is the original exit code 1 (errors found), "verdict pass" exit 0, "usage error" exit 2.
- Work only in a new scratch folder outside the plugin being tested (never add files inside the plugin or the user's project). Delete nothing outside it.
- `F` = the fixture plugin `ab-demo`, built by scaffolding with slug `ab-demo`, display name `AB Demo`, author `@t`, company `Co`, email `a@b.co`, roles `build`, with hooks and agents enabled, then adding an MCP server named `ab-srv` (language python). `sk(q)` = `skills/ab-demo-build/SKILL.md` of copy `q`.
- `V(dir, options)` = run the validator recipe on `dir` with those options and read its findings (codes such as `S002`) and verdict.
- `broken(label, code, mutation, options)`: copy `F` to `b-<label>`, apply the mutation, run `V`. PASS only if the verdict is fail AND `code` appears in the output.
- `warns(label, code, mutation, present)`: copy `F`, apply the mutation, run `V`. PASS only if the verdict is pass (no errors) AND (`code` appears in the output) equals `present`. Rows named "quiet on" use present = false.
- `mk(label, files)`: copy `F` to `x-<label>` and write the given files (creating folders).
- `skill_md(n)` = `---`, `name: <n>`, `description: Use when testing.`, `---`, blank line, `scratchpad` (one per line, trailing newline).
- Fake secrets are assembled at run time and never stored as one literal in a file of the plugin or repo: `KEY` = the 8 characters `a8F3kL9q` followed by the 16 characters `Pz2XcV7bN1mR4tY6`; `FAKEGH` = `gh` + `p_` + `Ab1` repeated 12 times; `FAKESK` = `sk-` + the letter `a` repeated 30 times; `FAKEBEARER` = `Bearer ` + `a` repeated 30 times; the fake user path = `C:` followed by `\Users\jdoe42\work`. Write them into scratch fixtures only, and mask them in any report.
- Several checks changed meaning when the hook and scripts were removed (guardrail hook, own-source exemption, scanner presence). They are marked `(N)` and explained in section 9.

## 3. Checks (split into two files)

The checks load on demand from two files; run all of them, in order.

| Checks | Sections | File |
|---|---|---|
| 1 to 86 | fixture, validator basics, robustness, simulator, shell paths, cleaner, workflows, modes, directory target, companion prompt, manifest names, scaffold, packaging | `references/selftest-checks-1.md` |
| 87 to 180 | connectors, rules, caching, shared files, release helper, injection screen, packaging edge cases, guardrail, distribution standard, naming, router, public safety | `references/selftest-checks-2.md` |

## 9. Notes on checks marked (N)

These were tests of scripts or of the hook that are being removed from the plugin. They are kept so no check is lost; apply the replacement below, and still count each as one of the 180:

- 66: replaced by "no generated files in the plugin": no `__pycache__` folder and no stray `.pyc` files exist anywhere under the plugin root after running the checks.
- 72, 123, 128, 135, 140 (guardrail hook and scaffold wiring): the `PostToolUse` guardrail hook and `scripts/guardrail` are removed. Replace with: the scaffold writes no hook that runs a script (check the fixture's `hooks/hooks.json` is absent or has no `command` entries that run `python`, `node` or any `.py`/`.js` file), and the manual screen in `screen-text.md` is the only guardrail. For 72, only the installed-dependency (`PYTHONPATH`) wiring remains if the python MCP scaffold still ships; follow `scaffold-mcp-server.md`. For 128, check instead that `screen-text.md` names the tools it covers: WebFetch, WebSearch and any Composio tool (`mcp__plugin_aiaddon_composio__` and `mcp__claude_ai_Composio__` prefixes) and no others. For 135 use the same texts D and E against the manual screen: D (JSON data) is not flagged, E (attack inside a JSON string) is.
- 116: the three texts A, B, C stay; "hook exits 2 with warning" becomes "the manual screen reports A", "B is not reported", "C is treated as plain data and causes no error".
- 123: replaced by "a scaffold with connectors writes no guardrail hook or `scripts/guardrail` folder, with or without connectors".
- 179 and 180: there is no script to exempt and no scanner script to be missing. Replace 179 with "scanning this plugin's `references/` folder reports only quoted rule text inside fenced blocks of the recipe files (known self-matches, `scan-secrets.md` section 4), never a real finding"; replace 180 with "if `references/scan-secrets.md` or `references/public-safety-scan.md` is missing, the packaging step refuses to build skill zips and writes none".
