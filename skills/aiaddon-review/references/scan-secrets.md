# Secret scan (recipe)

Replaces the former script `scan_secrets.py`. Claude follows this recipe with Grep, Glob, Read, Write and, for history and packages, standard OS and git commands (`git log`, `git ls-files`, `unzip -p`/`tar`). Nothing here is code to save and run. Rules shared with the engine live in `public-safety-scan.md` (23 rules); this file adds the two key-format rules `X001` and `X003` (25 rule ids in total).

## Contents

- 1. Purpose, when to use
- 2. Inputs (former CLI options)
- 3. Key-format rules (the two rules of the original key scan)
- 4. Which files are read
- 5. Procedure: working tree
- 6. Exit status (verdict)
- 7. Output format
- 8. Example (fake values only)

## 1. Purpose, when to use

Find passwords, API keys and private data stored in plain text in the extension folders, archives, git history and built packages the user names. It reads files only and sends nothing anywhere. Values are always masked in the report (never print a full secret).

Use it: (a) when asked, or when a key may have leaked (step 7 of the review workflow); (b) as the blocking secret and private-data scan in every review, even unasked (step 7a); (c) by the packager before and after building. Any finding fails the review.

After a hit: move the value to `userConfig` with `"sensitive": true` (or an environment variable), then rotate the key, because anyone who received a copy still has the old one. For a value already in history, a package or a release, rotate first, then follow past leak remediation in `public-safety.md` section 6. Never force-push without the owner's explicit OK.

## 2. Inputs (former CLI options)

| Input | Meaning |
|---|---|
| `<dir-or-archive> [...]` | One or more folders, `.zip` or `.plugin` files. Only the paths the user gives are scanned. None given and no artifacts: ask the user for a path (the script printed its usage and exited 2). |
| `--history` | Also scan every line ever added on any ref of each `<dir>` that is a git repo (section 6, step H). |
| `--artifacts PATH ...` | Also scan inside built `.zip`/`.plugin` files: a file, or a folder (a `dist/` folder is included). |
| `--allowlist FILE` | False-positive rules. Default: `.public-safety-allow` in each `<dir>` (format in `public-safety-scan.md` section 6). With `--artifacts` only, the default is `.public-safety-allow` in the first path if it is a folder, else in the current folder. |
| `--json` | Report as JSON instead of the table (section 7). |

## 3. Key-format rules (the two rules of the original key scan)

Applied line by line. Per line: X001 first; if it matches, record it and go to the next line. Otherwise test X003 and stop at the first qualifying value on the line.

| Id | Kind in report | Severity | Exceptions |
|---|---|---|---|
| X001 | `known key format` | blocking (error) | none |
| X003 | `key-like value` | blocking (error) | value matches NOT_A_SECRET; or value lacks a digit; or lacks a letter; or has 8 or fewer distinct characters |

Masks: X001 shows the first 6 characters of the match plus `...`. X003 shows `<key name>=` plus the first 4 characters of the value plus `...`; when only the Basic-authorization branch matched, the key name is `Authorization`.

Regexes (verbatim; Python syntax, case-insensitive where `(?i)` is shown):

```
SECRET (X001):
(Bearer\s+[A-Za-z0-9._\-]{20,}|sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)

GENERIC_SECRET (X003):
(?i)([\w-]*?(?:api[_-]?key|apikey|secret|token|passw(?:or)?d|access[_-]?key|private[_-]?key))["']?\s*[:=]\s*["']?([A-Za-z0-9_\-./+=]{20,})|Authorization["']?\s*:\s*["']Basic\s+([A-Za-z0-9+/=]{16,})

NOT_A_SECRET (exception filter, tested against the VALUE only):
(?i)(env|config|process|getenv|example|your|placeholder|xxxx|changeme|dummy|redacted|sample|user_config|plugin_root)
```

X003 value = group 2 (assignment value) or, if empty, group 3 (the Basic credential). It is reported only when ALL hold: the value is not empty; NOT_A_SECRET does not match it; it contains at least one digit; at least one letter; and more than 8 distinct characters (at least 9).

## 4. Which files are read

- Folders: walk all files. Skip any path with a component named `.git`, `node_modules`, `__pycache__`, `.venv` or `dist`; skip symlinks, non-files and files over 2,000,000 bytes.
- Key-scan (X001/X003) reads only files whose suffix is one of: `.md .py .json .sh .js .mjs .cjs .ts .txt .yaml .yml .toml .ini .cfg .env .ps1 .bat`, or whose name starts with `.env`. Read as UTF-8, ignoring a BOM, replacing bad bytes.
- A `.zip` or `.plugin` found inside a folder, or given directly, is opened and each member is read the same way (skip directory entries, members with a skipped path component, non-text suffixes and members over 2,000,000 bytes). Report the location as `<archive>!<member path>`. An unreadable or corrupt archive is skipped silently.
- The public-safety rules (`public-safety-scan.md`) are applied in addition, on all non-binary files (see that file for the file list, private file names, history and nested archives).
- Own-source exemption: the old script skipped this plugin's own scanner sources (`validate_extension.py`, `scan_secrets.py`, `selftest.py`, `public_safety.py`) when byte-identical to the shipped copy. These files no longer exist as scripts. Recipe files in `references/` quote the patterns as text; when a scan of this plugin itself matches only quoted rule text inside a recipe's fenced block, record it as a known self-match and do not report it. Any other plugin's file with these names is never exempt.

## 5. Procedure: working tree

1. List the scope: Glob `**/*` under each folder (or `git ls-files -co --exclude-standard` in a git repo, which is what the public-safety engine uses). Drop skipped components and oversized files.
2. X001: Grep (`-n`, `-r`, with `--glob` for the suffixes above plus `.env*`) with the SECRET regex. Use `-P`-compatible syntax through Bash `grep -rnP` if Grep rejects a construct.
3. X003: Grep with the GENERIC_SECRET regex (case-insensitive). For each hit Read the line, take the value (the group-2 string after `:` or `=`, or the Basic credential), and apply the four exceptions in section 3. Lines already reported as X001 are not reported again as X003.
4. Apply the engine rules of `public-safety-scan.md` to the same files (rule order and first-match-per-line logic are described there).
5. Archives: list members (`unzip -l`), read each text member (`unzip -p <file> <member>`), and repeat steps 2 to 4 on the content. Nested archives are opened up to two levels deep.
6. Merge, deduplicate (same file, line, kind and masked value reported once), and drop an engine finding when the key scan already reported the same line number in the same file (compare the path tail after `!`).
7. Mask every value as defined here and in the engine file, then write the report (section 7).

History (`--history`): see `public-safety-scan.md` section 5, step H. Run `git -C <dir> log --all -p --no-color --no-ext-diff --format=%x01%h` and examine only added lines (`+` prefix); track file from `+++ b/<path>`, line number from `@@ ... +<n>` hunks, commit from the `%x01<hash>` line. Report each distinct (rule, file, masked value) once with `where` = `commit <hash>`. Also report any private file name ever added (once per rule and file).

## 6. Exit status (verdict)

Original: exit 0 when nothing found, 1 when anything found, 2 on missing arguments. As a recipe: any finding means the review FAILS (every finding is blocking; there is no warning level). Say so in the reply.

## 7. Output format

Default (Markdown):

```
### Scratchpad: Secret Scan
**Scope:** <paths, comma separated>

No plain-text secrets found.
```

or, when there are findings:

```
### Scratchpad: Secret Scan
**Scope:** <paths, comma separated>

| File | Line | Kind | Value |
|---|---|---|---|
| `<file or archive!member>` | <line or -> | <kind>[ (<where>)] | `<masked value>` |

**Next:** move each real value to userConfig with `sensitive: true`, then rotate the key: copies already shared keep the old one.
```

- Kind for X001 is `known key format`; for X003 `key-like value`; for engine findings it is the engine label (for example `GitHub token`), followed by ` (<where>)` when `where` is set (`commit <hash>`, or the archive name for members of a package).
- Line is the line number; for whole-file findings (private files) the original printed `-` (line 0).
- When any engine finding is present, also print: `Every finding is blocking. A secret or private value already in git history, a package or a release: rotate first, then follow past leak remediation in aiaddon-review/references/public-safety.md (never force-push without the owner's explicit OK). Exact public false positives go in .public-safety-allow.`

`--json`: a JSON array, one object per finding, with keys `file`, `line`, `code` (rule id), `value` (masked), `kind`, `where`; for X001 and X003 the kind is `known key format` and `key-like value`. Print `[]` when clean.

## 8. Example (fake values only)

A line in `servers/crm.js` (line 12) that assigns a 20-character value of mixed letters and digits, such as one starting `Zz9Q`, to a name ending in `API_TOKEN` gives the row: `servers/crm.js`, 12, `key-like value`, `API_TOKEN=Zz9Q...` (the value has digits, letters and more than 8 distinct characters, and none of the NOT_A_SECRET words). A `token` assignment whose value contains the word `your` is not reported.
