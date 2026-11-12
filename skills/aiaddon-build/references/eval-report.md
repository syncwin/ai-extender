# Eval report recipe (replaces eval_report.py)

## Purpose and when
Write one static, self-contained HTML review page for an eval iteration, so the user can read the with/baseline runs side by side. Used after `references/aggregate-results.md` (testing step 4).

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `<iteration-dir>` | required | `<name>-workspace/iteration-N/`; must exist, otherwise print `not a directory: <path>` and stop. |
| `--out report.html` | `<iteration-dir>/report.html` | Where to write the page. |

## Data read
Layout: `<iteration-dir>/<eval-id>/{with,baseline}/` with `grading.json` (`expectations`: list of `{"text","passed","evidence"}`), `timing.json` (`total_tokens`, `duration_ms`) and any other output files. A missing or invalid JSON file counts as absent.

## Rules
| Rule | Detail |
|---|---|
| Evals | Sub-folders of the iteration folder, in name order. An eval gets a section only when at least one of its `with` or `baseline` folders exists. |
| Columns | One table cell per config that exists, in the order `with`, `baseline`. |
| Run block, grading | When `grading.json` exists: `<p><b>OK/TOTAL</b> assertions passed</p>` then a list; each expectation is `<li class='p'>` (passed) or `<li class='f'>` (not passed) holding the escaped text, `<br>`, and `<small>` with the escaped evidence (empty if none). |
| Run block, timing | When `timing.json` exists: `<p><small>TOKENS tokens &middot; SECONDS s</small></p>`; tokens show `?` when missing; seconds = duration_ms / 1000 with 1 decimal (0.0 when missing). |
| Run block, files | Every other regular file in the run folder (sorted by name) whose extension is `.md`, `.txt`, `.json`, `.py` or `.html`, excluding `grading.json` and `timing.json`: `<details><summary>NAME</summary><pre>FIRST 6000 CHARACTERS, escaped</pre></details>`. A file that cannot be read as text is shown with its bad characters replaced. |
| Empty block | A run block with none of the above is `<p><i>no data</i></p>`. |
| Escaping | Every inserted text (eval id, config text, evidence, file name, file body, folder name) is HTML-escaped: `&` -> `&amp;`, `<` -> `&lt;`, `>` -> `&gt;`, `"` -> `&quot;`, `'` -> `&#x27;`. |
| No network, no scripts | The page uses no script and no outside file. |

## Page template
The text below is the page, written in one piece (line breaks only for reading). The section list replaces `ROWS`; without any section, use `<p>No eval runs found.</p>`.
```
<!doctype html><meta charset=utf-8><title>Eval report</title><style>body{font:14px system-ui;margin:2rem;max-width:1200px}table{width:100%;border-collapse:collapse}td{vertical-align:top;width:50%;padding:.5rem;border:1px solid #8884}li.p{color:#0a7a2f}li.f{color:#b00020}pre{white-space:pre-wrap;background:#8881;padding:.5rem}</style><h1>Eval report: FOLDER-NAME</h1>ROWS
```
One section per eval:
```
<section><h3>EVAL-ID</h3><table><tr><td><h4>with</h4>BLOCK</td><td><h4>baseline</h4>BLOCK</td></tr></table></section>
```
`FOLDER-NAME` is the iteration folder's last path part, escaped.

## Procedure
1. List the eval folders with Glob; Read the JSON files and the output files (first 6000 characters of each).
2. Build each block and section by the rules.
3. Write the page with Write to the output path.
4. Print `wrote <out> (<n> evals)` where n = number of sections.
