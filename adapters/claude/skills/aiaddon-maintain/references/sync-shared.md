# Sync shared files recipe (replaces sync_shared.py)

## Purpose and when
Shared files (scratchpad format and others) live once and are copied into each skill that needs them. This recipe copies the source over every target, or only checks for drift. Used in maintain step 3.

## Inputs (former CLI options)
| Input | Meaning |
|---|---|
| `<plugin-dir>` | The plugin folder. |
| `--check` | Report only; copy nothing. Without it, copy the source over each target that is missing or differs. |

## Config file `<plugin-dir>/.claude-plugin/shared-files.json`
```
{"files": {"shared/scratchpad.md": ["skills/*/references/scratchpad.md"]}}
```
Keys are source files (relative to the plugin). Each value is a list of target paths (a single string counts as a list of one). `*` in a folder part of a target matches every existing folder at that level; the last part is the target file name, taken literally. Folders without `*` need not exist yet. If the config file does not exist, print `no .claude-plugin/shared-files.json: nothing to sync` and stop with success.

## Rules
| Rule | Detail |
|---|---|
| Containment | The source and every target must resolve to a path inside the plugin folder (no `..`, no absolute path, no link that leaves it). A source that is a symlink, or any target that is a symlink, is refused. State `outside-plugin`. |
| Source missing | Source is not an existing file: state `missing-source`. |
| Self | A target that resolves to the source itself is skipped. |
| Target states | `same` (exists, identical bytes), `differs` (exists, different), `missing` (does not exist). |

## Procedure
1. Read the config with Read. For each source, Glob to confirm it exists and is a regular file inside the plugin.
2. Expand each target pattern: for each folder part with `*`, Glob the existing directories at that level; build the full target paths. Skip targets equal to the source.
3. For each target decide the state. Identical bytes: compare with `git diff --no-index --quiet <source> <target>` (exit 0 = same) or file hashes (`Get-FileHash` / `sha256sum`).
4. Without `--check`: for each `differs` or `missing` target, create the parent folders if needed and copy the source over it byte for byte (for a text file, Read the source and Write the target; for any other file use `Copy-Item -LiteralPath <source> -Destination <target>` or `cp`). Never copy for `missing-source` or `outside-plugin`.
5. Print the output.

## Output
```
### Scratchpad: Shared Files
**Scope:** `<plugin folder name>` (check|sync)

| Copy | Result |
|---|---|
| <target, or source for a source-level refusal> | <state> |
| unchanged | <number of targets that were same> |
```
One row per target that is not `same`. The Result is the state itself (`differs`, `missing`, `missing-source`, `outside-plugin`) in check mode; in sync mode it is `updated from <source>` for a copied target, and `missing-source` or `outside-plugin` for a refusal.

## Result (exit code meaning)
| Situation | Result |
|---|---|
| `--check` and any target not same, or any refusal | failure (script exit 1): report the drift and fix with a sync run |
| Any `missing-source` or `outside-plugin`, in either mode | failure |
| Otherwise | success |
