# Self-test: checks 1 to 86

Part of the self-test recipe `selftest.md`; read its sections 1, 2 and 9 first (purpose, output, conventions and the notes on checks marked (N)).

## Contents

- 3. Checks 1 to 22: fixture, validator basics, robustness, simulator
- 4. Checks 23 to 52: shell paths, cleaner, workflows, modes, directory target
- 5. Checks 53 to 86: companion prompt, manifest names, scaffold, packaging

## 3. Checks 1 to 22: fixture, validator basics, robustness, simulator

| # | Check name | Setup and mutation | PASS when |
|---|---|---|---|
| 1 | scaffold ok | Scaffold `F` (convention above) | scaffold succeeds |
| 2 | mcp scaffold ok | Add MCP server `ab-srv`, language python, into `F` | succeeds |
| 3 | validator passes clean fixture | `V(F, --require-meta author,company)` | verdict pass |
| 4 | catches name mismatch | broken, code `S002`: in `sk` replace `name: ab-demo-build` with `name: other` | broken rule |
| 5 | catches missing description | broken, `S005`: in `sk` replace `description:` with `desc:` | broken rule |
| 6 | catches literal secret | broken, `X001`: create `skills/ab-demo-build/references/x.md` containing `key ` + `FAKESK` | broken rule |
| 7 | catches placeholder text | broken, `S010`: append a line made of the marker word T-O-D-O (written without dashes) and ` finish` to `sk` | broken rule |
| 8 | catches bad hook event | broken, `H002`: `hooks/hooks.json` = `{"hooks":{"Nope":[]}}` | broken rule |
| 9 | catches secret in mcp | broken, `M003`: `.mcp.json` = `{"mcpServers":{"x":{"url":"https://a.b/c","headers":{"Authorization":"<FAKEBEARER>"}}}}` | broken rule |
| 10 | catches upload-incompatible keys | broken, `S006`: in `sk` replace `license:` with `model: sonnet` newline `license:`; option `--target upload` | broken rule |
| 11 | catches bad manifest path | broken, `P007`: set `"agents": ["./nope.md"]` in `.claude-plugin/plugin.json` (keep other keys) | broken rule |
| 12 | accepts BOM + CRLF skill files | Rewrite `sk` with CRLF line endings and a UTF-8 BOM; `V(copy, --require-meta author,company)` | verdict pass |
| 13 | rejects non-object plugin.json | `plugin.json` content `[]`; `V` | verdict fail and `P001` |
| 14 | rejects invalid JSON | `plugin.json` content `{nope`; `V` | verdict fail and `P001` |
| 15 | rejects non-object hook handler without crashing | `hooks/hooks.json` = `{"hooks":{"Stop":[{"hooks":["x"]}]}}`; `V` | verdict fail, `H003` present, no crash or stack trace |
| 16 | missing dir exits 2 | `V` on a path that does not exist | usage error (2) |
| 17 | empty dir exits 2 | `V` on a new empty folder | usage error (2) |
| 18 | packager skips symlinks | Copy `F`, add a symlink `leak.md` pointing to `/etc/hostname`; package as zip | success and no archive member ends in `leak.md`; if symlinks are unsupported here, count as PASS (name it `packager skips symlinks (symlinks unsupported here, skipped)`) |
| 19 | packager defaults missing version | Remove `version` from `plugin.json`; package as zip with `--skip-validate` | success and an output file name contains `v0.0.1` |
| 20 | simulator: install | Run `simulate` install on `F` (see `simulate.md`) | success and the output has the row `Router skill = plugin name` answered `yes` |
| 21 | simulator: builder triggers | Run `simulate` triggers on this plugin's root (the folder holding `skills/`) | success |
| 22 | simulator: builder install | Run `simulate` install on this plugin's root | success |

## 4. Checks 23 to 52: shell paths, cleaner, workflows, modes, directory target

| # | Check name | Setup and mutation | PASS when |
|---|---|---|---|
| 23 | E10 flags /root/.claude in a shell command | Copy `F`; append to its first `SKILL.md` a fenced bash block holding `python /root/.claude/plugins/x/scripts/run.py`; `V` | verdict fail and `R001` |
| 24 | E10 packager refuses while R001 exists | Package that copy as zip with `--skip-validate` | verdict fail (exit 1) and `R001` in the output |
| 25 | E10 passes a working-folder copy | Copy `F`; append to its first `SKILL.md` a fenced bash block holding `cp -r skills/x/scripts ./tools && python ./tools/run.py`; `V` | verdict pass and no `R001` |
| 26 | cleaner inventory finds the duplicated paragraph | Run cleaner `inventory` on `evals/clean-duplicate-plugin/fixture/dupe-helper` (`inventory.md`) | success and the total of exact duplicate paragraphs is 1 |
| 27 | cleaner proof passes when the unique line survives | Copy that fixture to `cl-good`; in `skills/filing/SKILL.md` delete the paragraph line starting `Invoice details captured` and the blank line after it; run cleaner `prove` original vs `cl-good` (`prove.md`) | success and `PASS` |
| 28 | cleaner proof fails when a unique line is lost | Copy `cl-good` to `cl-bad`; remove the line `Always ask for the invoice number before filing.`; `prove` original vs `cl-bad` | verdict fail, output contains `LOST` and `invoice number` |
| 29 | cleaner archive is a dry-run by default | Run cleaner `archive` on `cl-good` for `skills/filing/SKILL.md` with an archive folder that does not exist (`archive.md`) | success, the file still exists, the archive folder was not created |
| 30 | no-loss gate fails dropped clause and must->should | Run `no-loss-check` with old `fixtures/old.md` and new `fixtures/new_lossy.md` from the cleaner skill (`no-loss-check.md`) | verdict fail; output contains `CLAUSE FLAG` and `DOWNGRADE` |
| 31 | no-loss gate passes a clean pair | old `fixtures/old.md`, new `fixtures/new_clean.md` | verdict pass |
| 32 | no-loss gate has no list-number or rule-reference false positives | old `evals/no-loss-rules/rules_old.md`, new `evals/no-loss-rules/rules_new.md` | output has no `number/threshold` and does contain `TITLE (merged heading)` |
| 33 | accepts valid workflow | `mk`: `workflows/a.js` = `export const meta = { name: 'a', description: 'b' }`, then `const r = await agent('x')`, then `return r` (three lines) (this text is `GOOD_WF`); `V` | verdict pass |
| 34 | rejects workflow import | `workflows/a.js` = `GOOD_WF` + line `import x from 'y'` | verdict fail and `W003` |
| 35 | rejects Date.now in workflow | `GOOD_WF` + line `const t = Date.now()` | verdict fail and `W004` |
| 36 | rejects workflow without meta | `workflows/a.js` = `const x = 1` | verdict fail and `W001` |
| 37 | rejects bad LSP config | `.lsp.json` = `{"go":{"command":"gopls serve","extensionToLanguage":{"go":"go"}}}` | verdict fail, `L002` and `L003` both present |
| 38 | rejects user_config in monitor | `monitors/monitors.json` = `[{"name":"x","command":"echo ${user_config.k}","description":"d"}]` | verdict fail and `N003` |
| 39 | rejects nameless theme | `themes/t.json` = `{"base":"dark"}` | verdict fail and `T002` |
| 40 | rejects eval case without graders | `evals/c1/prompt.md` = front matter `max_turns: 5`, blank line, `hi` | verdict fail and `E001` |
| 41 | rejects unknown grader type | `evals/c1/prompt.md` = `hi`; `evals/c1/graders/g.md` = front matter `type: magic` | verdict fail and `E002` |
| 42 | warns on dropped plugin settings keys | `settings.json` = `{"agent":"a","model":"x"}` | `G002` appears in the output (no verdict condition) |
| 43 | accepts a valid mod | `hooks/hooks.json` = `{"modules": ["./register.js"]}`; `hooks/register.js` = `export function register(on) {}` | verdict pass |
| 44 | rejects missing hooks module | only `hooks/hooks.json` = `{"modules": ["./register.js"]}` | verdict fail and `H006` |
| 45 | rejects more than one module path | `hooks/hooks.json` = `{"modules": ["./a.js", "./b.js"]}` | verdict fail and `H006` |
| 46 | rejects non-string theme base | `themes/t.json` = `{"name":"x","base":7}` | verdict fail and `T003` |
| 47 | directory: short README blocks | `README.md` = `# Demo`, blank, `Too short.`; `V(--target directory)` | verdict fail and `D002` |
| 48 | directory: clean fixture passes | `README.md` = `# Demo`, blank, then the word `word` repeated 60 times separated by spaces (`LONG_README`); `--target directory` | verdict pass |
| 49 | directory: unpinned npx blocks | `LONG_README` + `.mcp.json` = `{"mcpServers":{"x":{"command":"npx","args":["-y","some-pkg@latest"]}}}`; `--target directory` | verdict fail and `D007` |
| 50 | directory: pinned npx passes | same with `"some-pkg@1.2.3"` | verdict pass |
| 51 | directory: system file blocks | `LONG_README` + file `.DS_Store` containing `x`; `--target directory` | verdict fail and `D004` |
| 52 | directory: non-https MCP url blocks | `LONG_README` + `.mcp.json` = `{"mcpServers":{"x":{"type":"http","url":"http://example.com/mcp"}}}`; `--target directory` | verdict fail and `D009` |

## 5. Checks 53 to 86: companion prompt, manifest names, scaffold, packaging

`bad_prompt(label, mutation)`: copy `F`, load `prompts/ab-demo.json`, apply the mutation to its first prompt (`pr`), save, run `V`. PASS only if verdict fail and `C002` present. `CP` = the companion-prompt recipe (`companion-prompt.md`).

| # | Check name | Setup and mutation | PASS when |
|---|---|---|---|
| 53 | scaffold writes companion prompt | look at `F` | `prompts/ab-demo.json` exists and `CP --check` on it passes |
| 54 | catches prompt unused variable | bad_prompt: add variable `extra` = type `Textarea`, label `X`, placeholder empty, context empty, maxLength 10, required false, options empty | broken rule |
| 55 | catches prompt missing variable | bad_prompt: append ` {{nope}}` to `content` | broken rule |
| 56 | catches prompt unknown field type | bad_prompt: set variable `task` type to `Dropdown` | broken rule |
| 57 | catches prompt radio without options | bad_prompt: set variable `files` type `Radio`, options empty | broken rule |
| 58 | catches prompt zero maxLength | bad_prompt: set `task` maxLength to 0 | broken rule |
| 59 | Text field with no length limit passes | copy `F`; set `task` type `Text`, maxLength empty string; `CP --check` | success and its count row shows 0 and 0 (no errors, no warnings) |
| 60 | companion prompt from spec keeps id and writes plain context | copy `F`; write `spec.json` = content `Run /ab-demo for {{client}}.`, variables `client` = type `Textarea`, label `Client`, maxLength 80, required true, context `Who it's for`; run `CP <copy> --spec spec.json` | success; the new prompt keeps the old prompt's `id`; `client.context` equals `Who it's for`; the file has no `&#x` |
| 61 | catches prompt html entity | bad_prompt: set `task.context` to `isn&#x27;t` | broken rule |
| 62 | catches prompt non-ascii text | bad_prompt: append to `description` a space, an em dash (U+2014) and ` x` | broken rule |
| 63 | ascii_check fails on non-ASCII | file `pb.md` = line `# T` + em dash + left and right curly quotes around `q`, then line `Go {{topic}}` + right arrow (U+2192) + check mark (U+2713) + ` it's`; run `ascii_check` (`ascii-check.md`) | verdict fail and the output contains `U+2014` |
| 64 | export_prompt normalizes to ASCII, writes plain text, valid schema | run `export_prompt` on `pb.md` with title `PB Demo` into a new folder (`export-prompt.md`); read `pb-demo.json` | success; no `&#x`; content starts `# T - `; contains `->` and `[x]`; all content ASCII; `CP --check` on it passes |
| 65 | ascii_check --fix normalizes and passes | `ascii_check pb.md` in fix mode | success and the file now starts with `# T - "q"` |
| 66 | validator leaves no bytecode in the plugin | after all runs | no `__pycache__` folder anywhere under the plugin root (N) |
| 67 | catches reserved plugin name | man_edit: set manifest `name` to `claude-tools`; `V --strict`; code `P016` | verdict fail and code |
| 68 | catches brand word in plugin name | name `tools-for-claude`; code `P016` | verdict fail and code |
| 69 | catches non-https listing URL | `supportUrl` = `http://example.com`; code `P017` | verdict fail and code |
| 70 | warns when companion prompt never starts the extension | copy `F`; in the prompt `content` replace `/ab-demo` with `the plugin`; `V` | `C004` appears |
| 71 | scaffold refuses a reserved plugin slug | scaffold slug `claude-x`, display `X` | usage error (2) and no `claude-x` folder created |
| 72 | python MCP scaffold wires PYTHONPATH and an install hook | copy `F`, delete `servers/` and `.mcp.json`, add MCP server `py-srv` (python) | success; its `.mcp.json` entry has `PYTHONPATH` in `env`; `hooks/hooks.json` contains `SessionStart`; `V` verdict pass (N) |
| 73 | node MCP scaffold puts dependencies in the root package.json | copy `F`, add MCP server `js-srv` (node) | success; root `package.json` contains `@modelcontextprotocol/sdk`; `servers/js-srv/package.json` does not exist |
| 74 | package plugin | package `F` as format `plugin` into `out` (`package-extension.md`) | success and file `AB Demo v0.0.1.plugin` exists |
| 75 | packager copies companion prompt beside the package | after 74 | `out/ab-demo.json` exists |
| 76 | packager writes the Markdown companion prompt from the same source | read `out/AB Demo v0.0.1 prompt.md` | contains `<prompt>`, `{{task}}` and `<fields>`; all ASCII |
| 77 | install guide mentions the prompt files | read `out/AB Demo v0.0.1 install.md` | contains `prompt.md` |
| 78 | --prompts md ships only the Markdown file | package zip with `--prompts md` into `out-md` | success; the `.md` file exists; `ab-demo.json` does not |
| 79 | --prompts json ships only the JSON file | package zip with `--prompts json` into `out-js` | success; `ab-demo.json` exists; the `.md` file does not |
| 80 | curly quotes and accents are normalized to ASCII in JSON and Markdown | copy `F`, delete its prompt JSON; spec with title `Caf` + e-acute (U+00E9) + ` Prompt`; description `It` + U+2019 + `s a ` + U+201C + `test` + U+201D + ` ` + em dash + ` ok` + ellipsis (U+2026); content `# T`, blank, `Run /ab-demo for ` + U+201C + `{{task}}` + U+201D + ` now ` + U+2192 + ` go`; variable `task` = `Textarea`, label `T` + a-circumflex (U+00E2) + `che`, placeholder `x`, context `na` + i-diaeresis (U+00EF) + `ve`, maxLength 100, required true; run `CP <copy> --spec <file> --out out-uni` | success; the JSON has no `\u` escapes and contains `Cafe`; a `.md` file exists in `out-uni` and is all ASCII |
| 81 | --to-md converts Prompt Builder JSON | run `CP --to-md prompts/ab-demo.json` | success and the output contains `<prompt>` |
| 82 | plugin archive root | list members of the `.plugin` | contains `.claude-plugin/plugin.json` |
| 83 | package zip | package `F` as format `zip` into `out` | success and `AB Demo v0.0.1.zip` exists |
| 84 | zip archive root | list members of the zip | contains `ab-demo/.claude-plugin/plugin.json` |
| 85 | aggregate | folder `it` with `e1` and `e2`, each with `with` and `baseline` subfolders; each holds `grading.json` = one expectation (`text` `t`, `evidence` `x`, `passed` true for `with`, false for `baseline`) and `timing.json` = `{"total_tokens": 100, "duration_ms": 1000}`; run `aggregate_results` on `it` (`aggregate-results.md`) | success and the output contains `+100%` |
| 86 | eval report | run `eval_report` on `it` (`eval-report.md`) | success and `it/report.html` exists |
