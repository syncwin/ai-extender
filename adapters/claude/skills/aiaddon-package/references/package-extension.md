# Package an extension recipe

Replaces the former `package_extension.py`. Claude follows this recipe with built-in tools (Read, Glob, Grep, Write, Edit) and Bash/PowerShell only for standard OS commands (`Compress-Archive`, `robocopy`, `zip`, `cp`, `find`, a SHA-256 tool, `git`). No script is saved or run.

## Contents

- Purpose and when
- Inputs (former CLI options)
- Exclusion rules (what never goes into the package)
- Step 1: read the manifest
- Step 2: names
- Step 3: stage the source
- Step 4: companion prompt (always)
- Step 5: behavior tests (evals) status
- Step 6: R001 and the public-safety scan (never skipped)
- Step 7: reuse check (unless force)
- Step 8: validation (when not reused)
- Step 9: build the zip (when not reused)
- Step 10: after build or reuse
- Step 11: report (print exactly this shape)
- Notes

## Purpose and when

Validate, name and zip a Claude extension (a plugin folder or a single skill folder) into a package, and deliver the companion prompt and the install guide beside it. Use it for every release build, for Cowork uploads, and when the user asks for a `.plugin` or `.zip`.

## Inputs (former CLI options)

| Input | Values | Default | Meaning |
|---|---|---|---|
| dir | folder | required | The plugin or skill folder |
| format (`--format`) | `plugin` or `zip` | required | `plugin`: zip with the plugin root as the archive root, extension `.plugin` (Cowork). `zip`: zip with one top-level folder named after the skill or plugin `name` (not the source folder's name), extension `.zip`. |
| out (`--out`) | folder | `./dist` | Where the package and its companions go |
| skip validation (`--skip-validate`) | flag | off | Skip the validation run only. Never skips the R001 refusal or the secret scan. |
| target (`--target`) | name | `all` | Validation target. For format `plugin` with target `all`, validate for target `cowork`; otherwise use the target given. |
| previous (`--previous`) | file or folder | newest other version of the same package in out | Package to diff against |
| repo (`--repo`) | `owner/repo` | none | Passed to the install guide |
| force (`--force`) | flag | off | Rebuild even if an identical package exists |
| require evals (`--require-evals`) | flag | off | Stop if behavior tests are missing, never run, or stale |
| prompts (`--prompts`) | `md`, `json`, `both` | `both` | Which companion prompt files to deliver |

Wrong input (no dir, bad format, a missing value, an unknown option) is a usage error: say what is wrong and stop. Format `plugin` with a skill folder (no `.claude-plugin/plugin.json`): say `.plugin format requires a plugin directory` and stop.

## Exclusion rules (what never goes into the package)

| Kind | Excluded |
|---|---|
| Folders, at any depth | `.git`, `.github`, `__pycache__`, `node_modules`, `.venv`, `dist`, `prompts`, `evals`, `.claude`, `dev` (`prompts/` because the Prompt Builder file ships beside the package, never inside it) |
| File extensions | `.plugin`, `.zip`, `.pyc` |
| File names | `.DS_Store`, `IMPROVEMENTS.md` |
| Links | every symbolic link or junction (files and folders) |
| Directory entries | not stored as entries; only files |

Equivalent `zip -x` patterns, if zipping straight from a folder instead of a staged copy: `-x ".git/*" "*/.git/*" ".github/*" "*/.github/*" "__pycache__/*" "*/__pycache__/*" "node_modules/*" "*/node_modules/*" "dev/*" "*/dev/*" ".venv/*" "*/.venv/*" "dist/*" "*/dist/*" "prompts/*" "*/prompts/*" "evals/*" "*/evals/*" ".claude/*" "*/.claude/*" "*.plugin" "*.zip" "*.pyc" "*.DS_Store" "*IMPROVEMENTS.md"` (stage a copy when links exist, because `zip` follows links).

## Step 1: read the manifest

- Plugin (`.claude-plugin/plugin.json` exists; ignore a leading byte order mark): it must be a JSON object with a `name`, otherwise stop (`plugin.json is not valid JSON: <reason>` or `plugin.json needs a name`). kind = plugin; visible name = `displayName` or else `name`; version = `version` as text or `0.0.1`; slug = `name`.
- Skill (otherwise a `SKILL.md` exists; read it with CRLF treated as LF): needs a `name:` line, else stop with `SKILL.md has no name`. kind = skill; slug = the name (quotes removed); visible name = the first `# ` heading, else the name with `-` turned into spaces and each word capitalized; version = the first indented `  version: <value>` line (quotes removed), else `0.0.1`.
- Neither: stop with `not a plugin or skill directory: <dir>`.

## Step 2: names

- File name = `<visible name> v<version><ext>` with the characters `\ / : * ? " < > |` removed from the whole name; ext is `.plugin` or `.zip`.
- Package path = `<out>/<file name>`. The install guide is `<out>/<file name without ext> install.md`.

## Step 3: stage the source

Always make a staged copy for zipping: a fresh temp folder `<tmp>/<slug>/` with the exclusions applied (so `prompts/` stays out). Besides that, when the source folder (or its `prompts/` folder) is read-only, the companion step also works on this staged copy so the source is never written to; when it is writable, the companion prompt is written into `<dir>/prompts/`.

- Windows: `robocopy "<dir>" "<tmp>\<slug>" /E /XJ /XD .git .github __pycache__ node_modules .venv dist prompts evals .claude dev /XF .DS_Store IMPROVEMENTS.md *.plugin *.zip *.pyc` (exit codes 0 to 7 are success), then delete reparse points: `Get-ChildItem "<tmp>\<slug>" -Recurse -Force | Where-Object { $_.LinkType } | Remove-Item -Force`.- macOS/Linux: `cp -R "<dir>" "<tmp>/<slug>"`, then `find "<tmp>/<slug>" -type l -delete`, then remove excluded folders with `find "<tmp>/<slug>" -type d \( -name .git -o -name .github -o -name __pycache__ -o -name node_modules -o -name .venv -o -name dist -o -name prompts -o -name evals -o -name .claude -o -name dev \) -prune -exec rm -rf {} +` and excluded files with `find "<tmp>/<slug>" -type f \( -name .DS_Store -o -name IMPROVEMENTS.md -o -name '*.plugin' -o -name '*.zip' -o -name '*.pyc' \) -delete`.

When the source is read-only, make the staged copy files writable.

Note the evals read in Step 5 come from the real source folder, not from the staged copy, because `evals/` is excluded from the staged copy.

## Step 4: companion prompt (always)

Follow `companion-prompt.md` in default mode on the working folder (the source, or the staged copy when staged) with out = `<out>` and the chosen prompts format. If it reports errors, show them and stop with: `Companion prompt failed: fix it, then package again.` This creates or checks `prompts/<title-slug>.json` and delivers it next to the package as Prompt Builder JSON, raw Markdown `<Visible Name> v<version> prompt.md`, or both (both come from the same source).

## Step 5: behavior tests (evals) status

Read from the real source folder. Result is (ok, note):

| Situation | ok | note |
|---|---|---|
| No `evals/` folder | no | `no evals/: behavior untested` |
| `evals/results/` missing or has no `*/aggregate-result.json` | no | ``evals/ never run here (`claude plugin eval .`, or the manual loop in testing.md)`` |
| Newest result file (by modified time) is older than the newest file under `skills/`, `agents/`, `hooks/` (files only; if none exist, treat as never newer) | no | `last eval run (<result folder name>) is older than the last skill change` |
| Otherwise | yes | `last run <result folder name>, score <aggregates.overallScore from that JSON, or None if unreadable>` |

If require-evals is set and ok is no: stop with `Behavior tests: <note>. Run them, or package without --require-evals.`

## Step 6: R001 and the public-safety scan (never skipped)

1. R001: run the aiaddon-review validation recipe on the working folder and look for rule `R001` (a shell command names `/root/.claude`). If the validation recipe is not available, Grep the working folder for `/root/.claude` in hook, command and MCP JSON/shell text. Found: stop with `Refusing to package: R001 (a shell command names /root/.claude). Fix it; --skip-validate does not bypass this.`
2. Secret and private-data scan: run the aiaddon-review public-safety scan recipe on the real source folder including its git history. If the recipe is not available, stop with `Refusing to package: the public-safety scan cannot run (the aiaddon-review secret scan is not available).` Any finding: show it and stop with `Refusing to package: the secret and private-data scan found something (blocking). Fix it, rotate any real credential first, then package again; --skip-validate does not bypass this.`

## Step 7: reuse check (unless force)

Content fingerprint: build the list of lines `<relative path with forward slashes>` + a tab + the SHA-256 of that file's bytes, over every non-excluded file of the working folder, sorted by relative path (byte order). Prefix the list with the first line `format:<plugin or zip>`. The fingerprint is the SHA-256 of that whole text (LF line endings). Tools: Windows `Get-FileHash -Algorithm SHA256`; macOS/Linux `shasum -a 256` (or `sha256sum`).

If the package file already exists and force is not set, compare the fingerprint with the sidecar file `<package path>.fingerprint` (a text file that holds only the fingerprint). Reuse only if they match AND the package's real contents match the source: list the package entries (Windows `[IO.Compression.ZipFile]::OpenRead`; macOS/Linux `unzip -Z1`), compare the names with the expected names (for format `plugin` the relative paths; for `zip` the relative paths prefixed `<slug>/`), and compare each entry's SHA-256 with the source file's (extract to a temp folder to hash). Any difference, or a missing sidecar, means rebuild. Reuse means: no re-check of validation and no rebuild, but the public-safety scan still runs on the existing package (Step 10).

## Step 8: validation (when not reused)

Unless skip-validate: run the aiaddon-review validation recipe on the working folder with the target (`cowork` for format `plugin` with target `all`, else the target given). Failure: show the findings and stop with `Validation failed: fix errors or pass --skip-validate.` On success the validation note is `passed, target <t> (<errors> errors, <warnings> warnings)` followed, for each warning, by `<br>warning `<code>` <message>`. If skipped: `skipped (--skip-validate)`. If the validation recipe is not available: `not run (validator not found)`.

## Step 9: build the zip (when not reused)

1. Make a fresh temp folder `<tmp2>`. The package is first built there, then scanned, then copied to `<out>`.
2. Format `plugin`: the archive root is the plugin root. Zip the staged folder's contents (including hidden files and folders such as `.claude-plugin`).
   - Windows: `Get-ChildItem -LiteralPath "<stage>" -Force | Compress-Archive -DestinationPath "<tmp2>\pkg.zip"` then `Move-Item "<tmp2>\pkg.zip" "<tmp2>\<file name>"` (this gives the `.plugin` extension).
   - macOS/Linux: `cd "<stage>" && zip -r -X "<tmp2>/<file name>" .`
3. Format `zip`: one top-level folder named `<slug>` (the manifest name). The staged copy is already `<tmp>/<slug>/`.
   - Windows: `Compress-Archive -Path "<tmp>\<slug>" -DestinationPath "<tmp2>\<file name>"`.
   - macOS/Linux: `cd "<tmp>" && zip -r -X "<tmp2>/<file name>" "<slug>"`.
4. `<stage>` is the staged copy made in Step 3. If the companion step wrote into a staged read-only copy, delete its `prompts/` folder from the stage before zipping.
5. Write the sidecar `<package path>.fingerprint` (Step 7) when validation was not skipped; with skip-validate, write none.
6. Create `<out>` if needed. Run the public-safety scan on the produced package (extract it to a fresh temp folder and scan the files; nested archives included). Any finding: stop as in Step 6.2. Then copy the package from `<tmp2>` to `<out>/<file name>` (and the sidecar). Windows: `Copy-Item`; macOS/Linux: `cp`.

Windows PowerShell 5.1 can store backslashes in entry names; list the entries and, if they do, build with PowerShell 7.

## Step 10: after build or reuse

- If reused, run the public-safety scan on the existing package now (same method); a finding stops the run.
- Count the entries (files only).
- Install guide: follow `install-guide.md` for the working folder with file = `<file name>`, out = `<out>/<file name without ext> install.md`, prompts = the chosen format, and repo if given. If that fails, report the guide as `not written`.
- Release diff: previous = the `previous` input, else the newest other version of the same package in `<out>`: files named `<visible name> v<number><ext>` (version `digits.digits.digits` plus any suffix, no spaces) whose version differs from this one, newest modified time first. If a previous package exists, follow the aiaddon-maintain skill's release-diff recipe to compare it with the new package, and put its one-line summary in the table row `Since <previous file name>`.

## Step 11: report (print exactly this shape)

```
### Scratchpad: Extension Packager
**Scope:** <kind> `<working folder name>` -> <format>

| Item | Result |
|---|---|
| File | `<package path>` [ (unchanged since the last build: reused, not re-checked)] |
| Entries | <n> |
| Version | <version> |
| Validation | <passed when this package was built (if reused) | the note from Step 8> |
| Companion prompt | checked (<prompts>) and delivered separately in `<out>` (not inside the package) |
| Install guide | `<guide path>` or not written |
| Behavior tests | <ok: or flag: ><note from Step 5> |
| Source | read-only, so a temp copy was packaged; the source folder was not changed and has no `prompts/` folder |
| Since <previous file name> | <release diff summary> |
```

The `Source` row appears only when a temp copy was used because the source was read-only; the `Since` row only when a previous package exists and the diff recipe is available. Remove the temp folders at the end.

## Notes

- Never put `prompts/`, `evals/`, `dist/`, packages or the companion files inside the package.
- The old zip comment holding the hash is replaced by the `.fingerprint` sidecar file, because the built-in zip commands cannot set a zip comment.
