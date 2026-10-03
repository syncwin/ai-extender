# Testing Extensions

Verified 2026-10-02 (code.claude.com/docs/en/plugin-evals). Triggering and output quality are different questions; measure both against a baseline, in fresh sessions.

## Contents

1. Choose the tool · 2. Official `claude plugin eval` · 3. Manual loop (any surface) · 4. Trigger tuning · 5. Improve · 6. Gate

## 1. Choose the tool

| Situation | Use |
|---|---|
| Claude Code ≥ 2.1.269 available, plugin under test | `claude plugin eval` (graded, with/without baseline, CI exit codes) |
| claude.ai / Cowork / API, or no CLI | manual loop (§3) with the grader and comparator agents |
| Quick description sanity check, offline | `ai-extender-reviewer/scripts/simulate.py <dir> triggers` (lexical proxy only) |

Build evals **before** writing extensive instructions: run the tasks without the extension, note the failures, write the minimum that fixes them, re-measure. At least 3 cases; test on every model that will use it.

## 2. Official `claude plugin eval`

Layout (cases live in `evals/`; `claude plugin eval init` writes them, `init --bare <name>` writes a blank case):

```
evals/<case>/prompt.md        # frontmatter: max_turns (10), timeout_seconds (300), allowed_tools, runs (3), tags, env (EVAL_* only); body = the user's request
evals/<case>/graders/<name>.md # frontmatter: type + options (+ weight, arm); body = rubric
evals/<case>/case.yaml         # optional: context.scaffold_script / history_file / add_dirs
evals/mocks/<server>/<tool>.md # optional MCP mocks ({{input.x}}, expect:, error:, type: agent)
```

- **Grader types** (no custom code): `regex` (JS regex over `target`), `tool_used` (`tool`, `input_match`, `min`, `max`; `min:0 max:0` = never called), `tool_order`, `file_exists`, `llm` (rubric of concrete PASS/FAIL, 2 of 3 votes), `baseline` (at least as good as a reference transcript).
- Each case runs 3× with the plugin and 3× without; `Δ` = with − without. `tool_used: Skill` graders are indicators only (excluded from scoring) unless `arm: both`.
- Runs are isolated: only the plugin loads; read-only tools by default; grant `Write`, `Edit`, `Bash(...)` with `--allow-tools` (Bash runs sandboxed; Windows needs WSL2). MCP tools are mocked unless `--allow-real-servers` / `--mocks off`. `--scaffold` is required to run `scaffold_script`.
- Run: `claude plugin eval .` · one case cheaply: `--case <name> --runs 1 --ablation none` · CI: `--trust-plugin --json results.json --threshold 0.8 --model <pin> --judge-model <pin> --no-publish --max-cost-usd N`. Exit 0 pass, 1 below threshold/invalid, 2 partial (cost ceiling or auth).
- Stable graders: `regex` over file contents for long output; one result grader + one process grader (`tool_used`/`tool_order`) per case; tighten rubrics so formatting doesn't decide the verdict; re-check with `--judge-model sonnet` when `Δ` is negative but the skill fired.
- Every run and judge is a real model call on the user's account: say so before running; add `evals/results/` to `.gitignore`.
- Reading results: `evals/results/<timestamp>/report.html` and `aggregate-result.json` (`aggregates.overallScore`, `casesPassed`, `meanDelta`, `cases[].arms.with[].error`). A usage-limit error mid-suite looks like a regression: check `NOTES` first.
- This format is not interchangeable with the skill-creator `evals.json` format.

## 3. Manual loop (any surface)

1. Test set: 2–4 realistic prompts (one vague/casual) + a trigger set (~8 should / ~8 should-not, negatives as near-misses). Keep the trigger sets in `evals/evals.json` (`trigger`, `trigger_heldout`).
2. Per prompt, in parallel, in fresh contexts: **with** the extension and **baseline** (none for new; previous version for edits). Save to `<name>-workspace/iteration-N/<eval-id>/{with,baseline}/` and write `timing.json` (`total_tokens`, `duration_ms`) when each run finishes.
3. Grade with the `ai-extender-grader` agent (writes `grading.json`: `{"expectations":[{"text","passed","evidence"}]}`); compare outputs blind with `ai-extender-comparator`.
4. `python ${CLAUDE_SKILL_DIR}/scripts/aggregate_results.py <iteration-dir>` → pass rate, tokens, seconds, delta, flags (non-discriminating or failing assertions, high variance). `eval_report.py <iteration-dir>` → `report.html`.

## 4. Trigger tuning

Under-triggering is the common failure. Run the should/should-not set in fresh sessions with only the extension's descriptions visible; add the phrasings users actually type, narrow words that over-match; re-run. Keep a held-out set you never tune against. A near-zero `Δ` with the `Skill` indicator failing means the description doesn't match natural phrasing.

## 5. Improve

Read transcripts, not just outputs; cut instructions that cause wasted work; generalize from failures instead of patching the example; move repeated helper code into `scripts/`; explain why behind rules that matter; re-run everything into `iteration-N+1`; stop when the user is satisfied or gains stall. Two-instance loop: one Claude drafts, a fresh one uses it on real tasks; carry observed behavior back.

## 6. Gate

Before release: `ai-extender-reviewer` (`validate_extension.py`, `selftest.py` if scripts changed), `claude plugin validate --strict`, evals at the agreed threshold.
