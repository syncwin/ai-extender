# Per-skill zips recipe

Replaces the former `build_skill_zips.py`. Claude follows this recipe with built-in tools (Read, Glob, Grep, Write) and Bash/PowerShell only for standard OS commands (`Compress-Archive`, `robocopy`, `zip`, `cp`, `find`). No script is saved or run.

## Purpose and when

Build one zip per skill: `skills/<name>` becomes `<out>/<name>.zip`, with the skill folder as the single top-level entry. Each zip holds only that skill's own folder, ready for claude.ai Customize > Skills upload or `npx skills add`. Use it for releases and whenever the user wants separate skill zips beside the `.plugin`.

## Inputs (former CLI options)

| Input | Meaning | Default |
|---|---|---|
| plugin-dir | The plugin root that holds `skills/` | required |
| out (`--out`) | Folder for the zips | `dist` |
| only (`--only a,b`) | Comma-separated skill folder names; build only these | all skills |

No plugin-dir is a usage error: say so and stop.

## Rules

- Skills = every sub-folder of `<plugin-dir>/skills/` (sorted by name; files are ignored), narrowed by `only`. If none: say `no skills under <plugin-dir>/skills` and stop (failed).
- A skill folder without `SKILL.md`: say `SKIP <name>: no SKILL.md`, build nothing for it, and mark the run failed (it continues with the other skills).
- Entries are the skill's own files under `<name>/<relative path>` with forward slashes. Directory entries are not counted.
- Exclusions, the same as the packager (see `package-extension.md`):

  | Kind | Excluded |
  |---|---|
  | Folders, at any depth | `.git`, `.github`, `__pycache__`, `node_modules`, `.venv`, `dist`, `prompts`, `evals`, `.claude`, `dev` |
  | File extensions | `.plugin`, `.zip`, `.pyc` |
  | File names | `.DS_Store`, `IMPROVEMENTS.md` |
  | Symbolic links and junctions | all (files and folders) |

- Each produced zip must pass the secret and private-data scan (the aiaddon-review skill's public-safety scan recipe) before it is kept. This is blocking and cannot be skipped.

## Procedure

For each skill, in sorted order:

1. Check `skills/<name>/SKILL.md` exists (else SKIP as above).
2. Stage a clean copy under a fresh temp folder, `<tmp>/<name>/`, with the exclusions applied.
   - Windows (PowerShell):
     ```
     $tmp = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
     robocopy "<plugin-dir>\skills\<name>" "$tmp\<name>" /E /XJ /XD .git .github __pycache__ node_modules .venv dist prompts evals .claude dev /XF .DS_Store IMPROVEMENTS.md *.plugin *.zip *.pyc
     Get-ChildItem "$tmp\<name>" -Recurse -Force | Where-Object { $_.LinkType } | Remove-Item -Force
     ```
     Robocopy exit codes 0 to 7 mean success; 8 or higher is a failure.
   - macOS/Linux:
     ```
     tmp=$(mktemp -d)
     cp -R "<plugin-dir>/skills/<name>" "$tmp/<name>"
     find "$tmp/<name>" -type l -delete
     find "$tmp/<name>" -type d \( -name .git -o -name .github -o -name __pycache__ -o -name node_modules -o -name .venv -o -name dist -o -name prompts -o -name evals -o -name .claude -o -name dev \) -prune -exec rm -rf {} +
     find "$tmp/<name>" -type f \( -name .DS_Store -o -name IMPROVEMENTS.md -o -name '*.plugin' -o -name '*.zip' -o -name '*.pyc' \) -delete
     ```
   The staged copy is a throwaway under the temp folder; the source is never changed.
3. Create the out folder if needed, then zip the staged folder so that `<name>/` is the top-level entry.
   - Windows: `Compress-Archive -Path "$tmp\<name>" -DestinationPath "<out>\<name>.zip" -Force` (give the folder itself, not `\*`). If the entry names in the result use backslashes (older Windows PowerShell 5.1), build with PowerShell 7 instead.
   - macOS/Linux: `cd "$tmp" && zip -r -X "<abs out>/<name>.zip" "<name>"` (use an absolute out path).
4. Scan the produced zip. If the aiaddon-review scan recipe is not available, delete the zip and say `REFUSED <name>: the aiaddon-review secret scan is not available, so the zip cannot be scanned (removed)`, and mark the run failed. Otherwise extract the zip to a fresh temp folder and run the scan recipe over the extracted files, including any nested archives. On any finding, show the findings, delete the zip, say `REFUSED <name>: secret or private data inside the zip (removed)`, and mark the run failed.
5. Count the files in the zip (entries that do not end in `/`): Windows `[IO.Compression.ZipFile]::OpenRead("<zip>")` then count its `Entries` that have a non-empty `Name`; macOS/Linux `unzip -Z1 "<zip>" | grep -vc '/$'`. Say `built <out>/<name>.zip (<n> files)`.
6. Remove the temp folders.

## Result

After all skills: failed if any skill was skipped or refused, otherwise success. Report one line per skill and the final verdict.

## Notes

- To upload to claude.ai, the user chooses `<name>.zip` in Customize > Skills > Create skill > Upload a skill.
- A skill that fails rule `S023` (reads outside its folder) cannot ship alone; fix it before release (see `targets.md`).
