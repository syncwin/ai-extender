# Aggregate results recipe (replaces aggregate_results.py)

## Purpose and when
Turn one eval iteration into pass rate, tokens, seconds, delta and quality flags. Used in testing step 4 (`references/testing.md`) after grading is done.

## Inputs (former CLI options)
| Input | Meaning |
|---|---|
| `<iteration-dir>` | Folder `<name>-workspace/iteration-N/`. Must exist; otherwise print `not a directory: <path>` and stop. |
| `--json` | Give the result as JSON instead of the table. |

## Data read
Layout: `<iteration-dir>/<eval-id>/{with,baseline}/{grading.json,timing.json}`.
| File | Fields used |
|---|---|
| `grading.json` | `expectations`: list of `{"text", "passed", "evidence"}` |
| `timing.json` | `total_tokens` (missing counts as 0), `duration_ms` (missing counts as 0; seconds = duration_ms / 1000) |

A file that is missing or is not valid JSON counts as absent. Eval folders are the sub-folders of the iteration folder, in name order. For each eval, the two configs are `with` and `baseline`.

## Rules
| Rule | Detail |
|---|---|
| Skip | A config whose `grading.json` is absent is skipped entirely (its timing too). |
| Pass rate of one run | passed expectations / number of expectations. A run with no expectations has no rate (not counted). `passed` counts as true when it is truthy. |
| Per config lists | pass rates (one per run with a rate), tokens and seconds (one per run that has a `timing.json`). |
| Aggregate | For each list: mean and population standard deviation (divide by n, not n-1). An empty list has no mean and no deviation (show `n/a`). A single value has deviation 0. |
| No data | If no run at all had a `grading.json`: print `no grading.json found` and stop (script exit 1). |
| Assertion table | For every (eval id, expectation text) remember whether it passed under `with` and under `baseline`. |

## Flags (in this order)
| Flag | Condition | Text |
|---|---|---|
| Non-discriminating assertion | passed under both `with` and `baseline` | `non-discriminating: <eval id>: <text>` |
| Failing assertion | it exists under `with` and did not pass | `FAILS with extension: <eval id>: <text>` |
| High variance | for a config, the pass-rate deviation is greater than 0.25 | `high variance in pass rate (<config>): sd=<value with 2 decimals>` |

The first two flags are produced while walking the assertions (in eval order, then expectation order); the variance flags come after them, `with` then `baseline` in the order the configs were found.

## Procedure
1. List the eval folders with Glob; Read each `grading.json` and `timing.json` that exists.
2. Compute the per-run values, lists, mean and deviation by counting carefully (write the numbers down before the table).
3. Build the flags.
4. Output as below.

## Output
Table (default):
```
| Config | Pass rate | Tokens | Seconds |
|---|---|---|---|
| with | <mean as whole percent> +/- <sd as whole percent> | <mean, 0 decimals> +/- <sd, 0 decimals> | <mean, 1 decimal> +/- <sd, 1 decimal> |
| baseline | ... |
```
Print `with` first, then `baseline`, only the configs that have data; a value with no mean prints `n/a`. (The original used a plus-minus sign; this recipe writes `+/-`.)

When both configs have a pass-rate mean, add a blank line and `Pass-rate delta: <with minus baseline, signed, whole percent>` (for example `+25%`).

When there are flags: a blank line, `Flags:`, then one `- <flag>` line each.

With `--json`: print
```
{ "stats": { "<config>": { "pass_rate": [mean, sd], "tokens": [mean, sd], "seconds": [mean, sd] } },
  "flags": [ "...", "..." ] }
```
where an absent mean or deviation is `null`. In JSON mode print no table and no delta.
