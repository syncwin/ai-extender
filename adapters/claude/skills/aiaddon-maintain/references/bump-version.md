# Bump version recipe (replaces bump_version.py)

## Purpose and when
Write one changelog entry and move every version field together from one summary. Used in maintain step 3 for every update that needs a new version, or (with level `keep`) to add lines to the current entry.

## Inputs (former CLI options)
| Input | Default | Meaning |
|---|---|---|
| `<dir>` | required | A plugin folder (has `.claude-plugin/plugin.json`) or a single skill folder (has `SKILL.md`). |
| summary | required | Text from the user or from a notes file (`--summary` / `--summary-file`). |
| `--level auto\|patch\|minor\|major\|keep` | auto | How the version moves. |
| `--title "<text>"` | `Update` | Title of a new changelog entry. |
| `--dry-run` | off | Work out everything and report, but write no file. |

Stop and ask when: no summary, a level outside the list, the summary has no lines (`summary has no lines`), or `<dir>` is neither a plugin nor a skill (`not a plugin or skill directory`).

## Parse the summary
| Rule | Detail |
|---|---|
| Groups | Added, Changed, Fixed, Removed. |
| Group line | A line that starts (case-insensitive) with `Added`, `Changed`, `Fixed`, `Removed` or `Breaking`, optionally preceded by `#` characters or `**`, optionally followed by `**` and a `:`. The group becomes the current group (title case). Any text after the colon, with leading `-`, `*` and spaces removed, is the first item of the group. Treat a line as a group line only when the keyword ends at a word boundary. |
| Breaking | `Breaking:` lines go under Changed and set the breaking flag. |
| Other lines | Blank lines are skipped. Any other line is an item of the current group with a leading `- ` or `* ` removed; before any group line, items go under Changed. |
| Empty | If no group has an item, stop: `summary has no lines`. |

## Decide the level
| Level asked | Result |
|---|---|
| `auto` | `major` if the breaking flag is set or anything is under Removed; else `minor` if anything is under Added; else `patch`. |
| `patch` / `minor` / `major` / `keep` | As given. |

Next version from the current one `a.b.c` (the first three numbers; text after them, like `-beta`, is dropped; a version that is not `number.number.number` stops with `version '<v>' is not semver`):
| Level | New version |
|---|---|
| major | `a+1.0.0` |
| minor | `a.b+1.0` |
| patch | `a.b.c+1` |
| keep | unchanged |

## Find what to update
| Mode | Current version | Files whose version moves (only when new differs from old) |
|---|---|---|
| Plugin (`.claude-plugin/plugin.json` exists) | `version` in plugin.json, default `0.0.1` | plugin.json `version`; `metadata.version` in plugin.json when `metadata` is an object that has a `version` key; in `.claude-plugin/marketplace.json`, every entry of `plugins` whose `name` equals the plugin name and that has a `version` key; every `skills/*/SKILL.md` (sorted); every `agents/*.md` (sorted); the README line `**Version** <old>` (replace every occurrence with `**Version** <new>`). |
| Single skill (`SKILL.md` in the folder) | the first indented line `  version: <value>` (quotes allowed) in SKILL.md, default `0.0.1` | that SKILL.md; the README as above. |

Version field in a markdown file: the first line that is only whitespace, `version:`, optional quote, the OLD version, the same quote, nothing else (an indented line, so it sits under `metadata:`). Replace the old version by the new, keeping the quotes. Do not touch a line that does not match exactly.

JSON files are rewritten with 2-space indentation, non-ASCII characters kept, and one trailing newline (use Edit on just the version values when the file is already formatted that way; otherwise Write the whole file).

## Changelog (`CHANGELOG.md` in `<dir>`)
Group block: `**<Group>**` newline, then one `- <item>` line per item. Groups in the order Added, Changed, Fixed, Removed; empty groups are left out. If the file is missing, start from `# Changelog` blank line `Newest first.` blank line.

| Level | Action |
|---|---|
| not keep | Insert a new entry just before the first `## ` heading (or append at the end if there is none): `## <new version>: <title>` blank line, the group blocks separated by blank lines, blank line. Newest first; never delete history. |
| keep | Find the first `## ` heading (none: stop with `--level keep needs an existing changelog entry`). The entry runs until the next `## ` heading or end of file. For each group with items: if the entry already has a `**<Group>**` block, add the new `- ` lines right after that block's last bullet (continuation lines that start with two spaces belong to the bullet); otherwise add a new `**<Group>**` block at the end of the entry after a blank line. Leave the rest of the file as it was. No version changes. |

## Procedure
1. Read the summary, parse it, decide the level.
2. Read plugin.json (or SKILL.md) to get the old version; compute the new one.
3. Prepare every change in memory: version fields, README, marketplace, changelog.
4. Unless `--dry-run`: apply each change with Edit (small replacements) or Write (new changelog text).
5. Re-read the touched files once to confirm the old version string no longer appears in a version field.
6. Print the scratchpad below.

## Output
```
### Scratchpad: Version and Changelog
**Scope:** `<dir name>` <old> -> <new> (<level>)           (add " (dry run)" with --dry-run)

| File | Result |
|---|---|
| `<relative path, forward slashes>` | updated            (would update with --dry-run)
| Changelog lines | <number of summary items> |
```
One row per file that changes (plugin.json, marketplace.json, each SKILL.md and agent file, README.md, CHANGELOG.md). With `keep` only CHANGELOG.md is listed.
