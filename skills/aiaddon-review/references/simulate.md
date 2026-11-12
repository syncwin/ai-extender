# Offline simulator (recipe)

Replaces the former script `simulate.py`. No network and no model calls in the original; here Claude does the work by reading and by following the other recipes. Nothing here is code to save and run. Two modes: `triggers` (a lexical proxy for skill selection) and `install` (package, extract, validate, inventory).

## Contents

- 1. Purpose, when to use, inputs
- 2. Mode `triggers`: procedure
- 3. Mode `install`: procedure
- 4. Example (fake plugin)

## 1. Purpose, when to use, inputs

- `triggers`: catch weak or colliding skill descriptions. Scores each should-trigger and should-not-trigger prompt against every skill description (TF-IDF cosine similarity) and reports the hit rate, the false-positive rate, misrouted prompts and skill pairs whose descriptions overlap too much. It cannot predict Claude's real choices: use it to find weak descriptions, then confirm with real runs (`claude plugin eval` or fresh sessions).
- `install`: package the extension, extract it into a clean temporary folder as an installer would, validate the extracted copy, and list the components with the names a user would see.

Inputs (former CLI):

| Input | Meaning |
|---|---|
| `<extension-dir>` | The plugin root. Must contain a `skills/` folder; otherwise stop with `no skills/ in <root>` (the script exited 2). |
| mode | `triggers` or `install`; anything else: show the two usages above (exit 2). |
| `--evals FILE` | `triggers` only. Default `<extension-dir>/evals/evals.json`. If missing, stop with `missing <path>` (exit 2). The file is JSON with `"trigger": {"should": [prompts], "should_not": [prompts]}`. |
| `--min-hit N` | `triggers` only. Minimum acceptable should-trigger hit rate, default 0.8. |
| `--out DIR` | `install` only. Where the package is written. Default: a `dist` folder inside the temporary working folder (removed afterwards). |

Verdict (original exit code): pass = 0, findings = 1, usage error = 2.

## 2. Mode `triggers`: procedure

### 2.1 Read the skills

For each `skills/*/SKILL.md` (sorted by path): read it as UTF-8 (BOM ignored, CRLF treated as LF). The front matter is the text between the first `---` line and the next `---` line; no front matter means the skill is ignored. Within it:

- `name:` gives the name (surrounding quotes removed). A skill without a name is ignored.
- `description:` gives the description. If the value after the colon is not one of `>`, `|`, `>-`, `|-`, it is part of the description. Following lines that are indented by two or more spaces, or blank, are added (trimmed), until a non-indented non-empty line.
- No skills left: print `no skills found` and stop with verdict 1.

### 2.2 Tokens

Tokenizing a text (`toks`) works like this: lowercase it and take every run of `[a-z0-9]+`. A token is discarded when it is in the stop list or has fewer than 2 characters. A token with more than 4 characters loses one trailing `ing`, `ed`, `es` or `s` (the regex `(ing|ed|es|s)$`, applied once).

Stop list (verbatim words): `a an and are as at be by for from has have how i in into is it its me my of on or our that the this to use used using when whenever with you your do does did can could should would will`.

For a skill, the document tokens are `toks(description + " " + name with each - replaced by a space)`.

### 2.3 Weights

Let N be the number of skills and df(w) the number of skills whose token list contains w. idf(w) = ln((N + 1) / (df(w) + 0.5)) + 1; a word that is in no skill has idf 1.0. A text's vector has, for each word w that appears n times, the weight (1 + ln n) x idf(w). Cosine of two vectors = dot product divided by the product of their lengths (0 when either length is 0).

### 2.4 Score the prompts

For each prompt, vector = weights of `toks(prompt)`. Its best match is the skill with the highest cosine (ties: the skill whose name sorts last; no skills: score 0 and no name). Do this for all `should` prompts (positives) and `should_not` prompts (negatives).

### 2.5 Calibrate the threshold

Rates for a threshold th: hit rate = share of positives with score > th (denominator at least 1); false-positive rate = share of negatives with score > th (denominator at least 1). Candidates = every distinct score of every prompt, plus 0. Choose the candidate with the greatest (hit rate minus false-positive rate); on a tie choose the larger candidate. A prompt "matches" a skill only if its score is strictly above the threshold; otherwise its matched skill is none.

Score separation = (lowest positive score, or 0 if none) minus (highest negative score, or 0 if none).

### 2.6 Flags

- For each positive with no matched skill: `MISS (no skill matched, score <s to 2 decimals>): <prompt>`.
- For each negative with a matched skill: `FALSE POSITIVE -> <skill> (<s to 2 decimals>): <prompt>` (the original prints a right arrow, U+2192).
- For every pair of skills (each pair once, in name order) whose description-vector cosine is above 0.6: `OVERLAP <c to 2 decimals>: <skill a> ~ <skill b> (descriptions too similar)`.

Verdict: findings (1) when the hit rate is below `--min-hit`, or the false-positive rate is above 0.25, or any `OVERLAP` flag exists; otherwise pass (0).

### 2.7 Output format

```
### Scratchpad: Trigger Simulation (lexical proxy)
**Scope:** <N> skills, <P> should / <Q> should-not prompts

| Metric | Value |
|---|---|
| Calibrated threshold | <th, 2 decimals> |
| Should-trigger hit rate | <percent, no decimals> |
| Should-not false-positive rate | <percent, no decimals> |
| Score separation (min positive - max negative) | <signed, 2 decimals, e.g. +0.12> |

**Flags**
- <each flag>

**Next:** confirm with real runs (`claude plugin eval` or fresh sessions); this is a proxy.
```

The `**Flags**` block appears only if there are flags. In the metric label the original uses the minus sign U+2212 between "positive" and "negative".

### 2.8 How Claude carries it out

Do it step by step and show the numbers. For a small plugin (up to about 12 skills and 30 prompts) compute the vectors and cosines directly and report the figures to two decimals. For larger sets, compute the same quantities but say in the reply that the figures are hand-computed and may differ from the old script in the second decimal; do not skip the overlap pairs or the calibration. The result is a proxy either way. Judge each flagged prompt by reading too: a MISS on a prompt that plainly names the skill's job means the description lacks its words.

## 3. Mode `install`: procedure

1. Package the extension as format `plugin` with the packaging recipe (`aiaddon-package/references/package-extension.md`) into the output folder (the `--out` value, or a new temporary folder). If packaging fails, print its output and stop with verdict 1.
2. Take the first `.plugin` file produced. Extract it (`unzip`) into a second, new, empty temporary folder called `installed`, as an installer would.
3. Run the validator recipe on `installed` with `--strict` (verdict pass or FAIL).
4. Read `installed/.claude-plugin/plugin.json` for `name`; list the skills in `installed/skills` (as in 2.1). The router skill is the skill whose name equals the plugin name; if none, the first skill `n` for which some other skill name starts with `n-`; otherwise none.
5. Agents: the file stems of `installed/agents/*.md`, sorted. Connectors: the keys of `mcpServers` in `installed/.mcp.json` if it exists. Hook events: the keys of `hooks` in `installed/hooks/hooks.json` if it exists.
6. Output:

```
### Scratchpad: Install Simulation
**Scope:** `<package file name>` extracted to a clean directory

| Check | Result |
|---|---|
| Archive root is plugin root | yes, or NO (yes when .claude-plugin/plugin.json exists at the root of installed) |
| Validator on extracted copy (--strict) | passed, or FAIL |
| Router skill = plugin name | yes, or NO (yes when a skill is named exactly like the plugin) |

**Components a user would see**
- skill `/<plugin>:<skill>`            (add " (router)" after the router skill)
- agent `<plugin>:<agent>`
- connector `plugin:<plugin>:<server>` (tools `mcp__plugin_<plugin>_<server>__*`)
- hook event `<event>`
```

   In the connector's tool pattern, replace in both the plugin name and the server name every character outside `A-Z a-z 0-9 _ -` with `_`. If the validator FAILed, add a `**Flags**` block holding the last 800 characters of the validator's output.
7. Verdict: pass (0) only if the validator passed AND a router skill was found; otherwise findings (1).
8. Remove the temporary folders (never delete anything else). With `--out`, the package files stay there.

## 4. Example (fake plugin)

A plugin `notes-helper` with skills `notes-helper` (router) and `notes-helper-build`, one agent `reviewer-lens` and a connector `docs` gives: `skill /notes-helper:notes-helper (router)`, `skill /notes-helper:notes-helper-build`, `agent notes-helper:reviewer-lens`, `connector plugin:notes-helper:docs (tools mcp__plugin_notes-helper_docs__*)`.
