# Release diff recipe (replaces release_diff.py)

## Purpose and when
Count how many files a release kept, changed, added and dropped between two versions of an extension. Used in maintain step 3 and in the update report (`references/versioning.md`).

## Inputs (former CLI options)
| Input | Meaning |
|---|---|
| `<old>` | Folder, `.plugin` file or `.zip` file of the previous version. |
| `<new>` | Same, for the new version. |
| `--json` | Give the result as JSON instead of the table. |
| `--list` | Also list the changed, added and dropped files. |

Anything other than exactly two paths: stop and ask.

## Rules
| Rule | Detail |
|---|---|
| Ignored files | Any file with a path part equal to `.git`, `.github`, `__pycache__`, `node_modules`, `.venv` or `dist`; any file named `.DS_Store`; any file ending `.pyc`, `.plugin` or `.zip`. (Packaging junk, as the packager ignores it.) |
| Folder input | Every regular file under it (links skipped), path relative to the folder, forward slashes. |
| Package input | A `.plugin` or `.zip` file is a zip. Unpack it to a scratch folder with a standard command (`tar -xf <file> -C <scratch>` works on Windows and macOS; or `Expand-Archive` in PowerShell, `unzip` in bash). If the zip has a single top-level folder and every entry is inside it, and no entry starts with `.claude-plugin/`, ignore that top folder name (compare paths below it). |
| Same file | Same relative path and identical bytes. Compare with one standard command per pair: `git diff --no-index --quiet <oldfile> <newfile>` (exit 0 = identical), or compare `Get-FileHash -Algorithm SHA256` (PowerShell) / `sha256sum` (bash) values. |
| Very large package members | For a member over 50,000,000 bytes do not read it; compare by size (and by CRC when `unzip -v` is available). Say so in Flags. |

## Classes
| Class | Meaning |
|---|---|
| kept | path in both, identical bytes |
| changed | path in both, bytes differ |
| added | path only in new |
| dropped | path only in old |
| old_total / new_total | number of files counted on each side after ignoring |

## Procedure
1. Prepare both sides (unpack packages to separate scratch folders; never unpack inside the plugin folder).
2. Glob each side, drop ignored files, build the relative-path lists.
3. Classify every path. For a folder-to-folder compare you can speed up with `git diff --no-index --name-status <old> <new>` (A = added, D = dropped, M = changed), then apply the ignore rules to that list.
4. Sort each class alphabetically.
5. Print the output.

## Output
Default (table):
```
### Scratchpad: Release Diff
**Scope:** `<old name>` -> `<new name>`

| Files | Count |
|---|---|
| Kept | <n> |
| Changed | <n> |
| Added | <n> |
| Dropped | <n> |
| Total (old -> new) | <old_total> -> <new_total> |
```
`<old name>` and `<new name>` are the last path parts of the two inputs. With `--list`, after the table add, for each of Changed, Added, Dropped that is not empty: a blank line, `**<Class>**`, then one line per file as `- ` followed by the path in backticks.

With `--json`:
```
{ "kept": [...], "changed": [...], "added": [...], "dropped": [...], "old_total": n, "new_total": n }
```
(each list sorted).

One-line summary for update reports: `<new_total> files: <kept> kept, <changed> changed, <added> added, <dropped> dropped (previous <old_total>)`.
