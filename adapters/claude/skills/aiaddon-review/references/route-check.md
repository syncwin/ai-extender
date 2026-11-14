# Recipe: route check

This recipe replaces the old `route_check.py`. Claude follows it with built-in tools only (Read, Glob, Grep). Do not write or run a script for it.

Rule count: the old script had no `add(...)` calls. It raised 6 problem messages (rows 1 to 6 below). All are kept. Row 7 is an added guard for a bad cases file (the old script crashed there).

## Contents

1. Purpose and inputs
2. Output format and verdict
3. Routing table format and matching rules
4. Rules
5. Procedure

## 1. Purpose and inputs

Use it to check that a plugin's router sends each test prompt to the expected skill. The router is the skill named like the plugin: `skills/<plugin>/SKILL.md`.

Inputs (these were CLI options):

| Input | Meaning |
|---|---|
| `<plugin-dir>` | Required. The plugin folder. |
| cases file | Optional (was `--cases`). Default `evals/router/cases.json`. |
| json output | Optional (was `--json`). Output the JSON form in section 2. |

If the plugin folder is not given, stop and ask for it (usage error).

Plugin name: read `name` from `<plugin-dir>/.claude-plugin/plugin.json`. If that file does not exist, use the folder name.

## 2. Output format and verdict

Markdown (default):

```
### Scratchpad: Router Check
**Scope:** <plugin-dir as given>, <n> cases

| Result | Detail |
|---|---|
| FAIL | <problem> |
```

One FAIL row per problem. If there are none:

```
| PASS | all <n> prompts route to the expected skill |
```

JSON form:

```json
{
  "cases": 12,
  "problems": ["..."]
}
```

Verdict (old exit codes): 0 when every case routes as expected, 1 on a mismatch or a missing table, 2 on a usage error. Any problem makes the verdict a release blocker.

## 3. Routing table format and matching rules

Finding the table: in the router `SKILL.md`, find a heading of level 2 to 4 (`##` to `####`) whose text contains `Routing table` (case-insensitive). The table is everything under it up to the next heading of level 1 to 4. Match with this pattern (multiline, dot matches newline):

```
^#{2,4}[^\n]*Routing table[^\n]*\n(.*?)(?=^#{1,4} |\Z)
```

Columns: `| Order | Trigger phrases | Skill | Then |`.

Reading rows:

- A row is a line that starts with `|`. Split the cells on `|`, trimming the outer pipes and spaces.
- Skip a row with fewer than 3 cells, a separator row (first cell made only of `-`, `:` and spaces), and the header row (first cell is `order`, any case).
- The skill slug is the first code span (text in backticks) in the Skill cell. If there is none, ignore the row. If the slug has a colon, keep only the text after the last colon (so `<plugin>:<skill>` becomes `<skill>`).
- The Then cell (4th) may hold more code spans; each is an extra slug, with the same colon rule.
- Trigger phrases are in the 2nd cell, separated by `;`. Lowercase each, trim it, replace a curly apostrophe (U+2019) with a straight one `'`, drop empty ones.

Routing one prompt:

1. Lowercase the prompt and replace the curly apostrophe with a straight one.
2. Walk the rows in order (the first matching row wins).
3. A phrase starting with `!` is an exclusion. If any exclusion phrase (without its `!`) appears in the prompt, skip this row.
4. Otherwise, if any normal phrase appears in the prompt, the answer is this row's skill slug.
5. A phrase "appears" when it is found as whole words: the character before it and the character after it are not letters, digits or underscore. Match the phrase text literally (no wildcards).
6. If no row matches, the answer is `ask` (the router asks its one closed question).

## 4. Rules

| # | Severity | What to check | Pattern or threshold | Message |
|---|---|---|---|---|
| 1 | problem | The router skill file is missing | `skills/<plugin name>/SKILL.md` must exist | `no router skill skills/<plugin name>/SKILL.md` (stop; case count 0) |
| 2 | problem | No routing table, or the table has no usable rows | section 3 finds at least one row | ``router has no Routing table (`\| Order \| Trigger phrases \| Skill \| Then \|`)`` (stop; case count 0) |
| 3 | problem | The cases file is missing | the cases path must exist (default `evals/router/cases.json`) | `no router cases at <cases path>` (stop; case count 0) |
| 4 | problem | A prompt routes to the wrong skill | route each case `prompt` (section 3); compare to its `expected` | `'<prompt>' routed to <got>, expected <expected>` |
| 5 | problem | A skill has fewer than 2 cases | for every folder under `skills/` except the router: count cases whose `expected` equals the folder name; at least 2 | `skill <skill> has <n> router case(s); at least 2 are required` |
| 6 | problem | No ambiguous case | at least one case has `expected` equal to `ask` | `no ambiguous case (expected 'ask')` |
| 7 | problem | The cases file cannot be used | the file must be JSON with a `cases` list, each item with `prompt` and `expected` | report the error as a problem line (the old script crashed here); do not skip the check |

Notes:

- Row 7 is the only addition: the old script crashed on a bad file. Here Claude reports it as a FAIL row instead.
- Case count in the output is the number of items in `cases` (0 when rows 1 to 3 stop the run).
- Rows 5 sorted by skill name.

## 5. Procedure

1. Read `.claude-plugin/plugin.json` (Read) for the plugin name. If missing, use the folder name.
2. Check `skills/<name>/SKILL.md` (Glob). If missing, record row 1 and go to step 9.
3. Read it. Find the routing table and read the rows (section 3). If none, record row 2 and go to step 9.
4. Read the cases file (default `evals/router/cases.json`, or the one given). If missing, record row 3 and go to step 9. An installed copy has no `evals/` folder (it is not shipped), so a missing default cases file there means the check is skipped, not failed: say so in the report. The file is JSON: `{"cases": [{"prompt": "...", "expected": "<skill slug or ask>"}]}`. Ignore a leading BOM.
5. For each case, in order, route the prompt by hand using section 3. Record row 4 for each mismatch.
6. Glob `skills/*/` to list skill folders. Remove the router. For each remaining folder, in sorted order, count its cases and record row 5 when under 2.
7. If no case has `expected` equal to `ask`, record row 6.
8. Count cases.
9. Print the report (section 2). Verdict as in section 2.

Tip: to route many prompts, use Grep on the router file for each trigger phrase, but still apply the first-match order and the `!` exclusions by reading the table.
