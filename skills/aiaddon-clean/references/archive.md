# Archive recipe (replaces archive.py)

## Purpose and when
Move one file into an archive folder instead of deleting it. Used in clean-up step 5 for every file the approved plan removes. Dry-run first, then apply. Nothing is ever deleted and nothing is ever overwritten.

## Inputs (former CLI options)
| Input | Meaning |
|---|---|
| `<root>` | The tree being cleaned. Every file to archive must be inside it. |
| `<relative-file>` | Path of the file, relative to `<root>`. |
| `--archive <dir>` | Archive folder (resolve it to an absolute path). |
| `--apply` | Do the move. Without it, only print what would happen (dry-run, the default). |

A missing `<root>`, `<relative-file>` or archive folder, or any unknown option: stop and ask the user for the missing input (the script printed its usage and exited 2).

## Checks (in this order; the first failure stops with exit 1)
| # | Check | Refusal text |
|---|---|---|
| 1 | The resolved source path (root joined with the relative file, `..` and links resolved) lies strictly inside the resolved root AND is an existing regular file (Glob or Read confirms it) | `refused: <relative-file> is not a file inside <root>` |
| 2 | The archive folder is not the source file itself and does not contain the source file (the file must not be archived into its own parent chain) | `refused: bad archive folder` |
| 3 | The destination `<archive>/<relative-file>` does not already exist (Glob it) | `refused: <dest> exists (never overwrites)` |

The destination keeps the file's relative path under the archive, so `docs/a.md` goes to `<archive>/docs/a.md`.

## Procedure
1. Resolve `<root>` and `<archive>` to absolute paths with no `..`. Build source = root + relative file; destination = archive + relative file.
2. Run checks 1 to 3 with Glob and Read. On a failure, print the refusal text and stop.
3. Dry-run (no `--apply`): print `DRY-RUN would move <source> -> <destination>` and stop.
4. With `--apply`: print `MOVE <source> -> <destination>`, create the destination's parent folders (`New-Item -ItemType Directory -Force` or `mkdir -p`), then move the file with one standard command: `Move-Item -LiteralPath <source> -Destination <destination>` (PowerShell) or `mv -n <source> <destination>` (bash). Use `git mv` only when both paths are inside the same git repository. Never use a delete command and never use a force-overwrite flag.
5. Confirm with Glob that the source is gone and the destination exists. Report both paths in the clean-up report.

## Output
One line per file: `DRY-RUN would move <source> -> <destination>`, `MOVE <source> -> <destination>`, or a `refused: ...` line.
