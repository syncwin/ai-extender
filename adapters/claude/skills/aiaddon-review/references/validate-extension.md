# Recipe: validate extension

This recipe replaces the old `validate_extension.py`. Claude follows it with built-in tools only: Read, Glob, Grep, Write, Edit, and Bash for plain OS or git commands (`git log`, `git diff`, `git ls-files`). Do not write or run a script for it.

Rule count: this recipe holds 194 findings, one per `add(...)` call in the old script (numbered 1 to 194 below). Several rows share a rule ID because the old script raised the same ID in more than one place.

## Contents

1. Purpose and inputs
2. Output format and verdict
3. Shared helpers (frontmatter, secrets, safe reading)
4. Procedure
5. Rule tables (1 to 194)
6. Dependencies on other recipes

## 1. Purpose and inputs

Use it to check a Claude extension folder (a plugin or a single skill) before release. It complements `claude plugin validate`, it does not replace it.

Inputs (these were CLI options):

| Input | Values | Meaning |
|---|---|---|
| `<dir>` | folder path | Required. The plugin or skill folder. |
| target | `all` (default), `claude-code`, `upload`, `cowork`, `directory` | Changes some severities (see rows). Any other value: stop and ask. |
| require-meta | comma list, for example `author,company` | Each key must exist in plugin metadata or skill metadata. |
| must-contain | prefix | Every skill name must start with this prefix. |
| known-connectors | comma list, file, or pasted `claude mcp list` text | Connectors the account already has. Used for `M008`. Entries: a name, a URL, `name=URL`, a `name: URL` line, or a JSON file with `mcpServers`. |
| rules | one or more project instruction files (CLAUDE.md, AGENTS.md, pasted text) | Used for `S018`. |
| no-history | flag | Skip the git history secret scan (`X012`). The tree and built packages are always scanned. |
| strict | flag | Warnings also fail the verdict. |
| json | flag | Output a JSON array instead of Markdown (section 2). |
| cache | flag | Optional. If no file changed since the last passing report, say so and reuse it (compare `git status` and file times). Not required. |

Kind detection: if `<dir>/.claude-plugin/plugin.json` exists, or `<dir>/skills/` exists and `<dir>/SKILL.md` does not, the kind is `plugin`. Else if `<dir>/SKILL.md` exists, the kind is `skill`. Else stop: "not a plugin or skill directory". If `<dir>` is not a folder, stop: "not a directory".

## 2. Output format and verdict

Write the report in this shape:

```
### Scratchpad: Extension Validation
**Scope:** <kind> `<folder name>`, target=<target>

| Errors | Warnings | Info |
|---|---|---|
| <n> | <n> | <n> |

**Errors**
- `<ID>` <path relative to the folder, or . for the folder itself>: <message>
**Warnings**
- ...
**Info**
- ...
```

Rules for the report:

- Print a severity section only when it has items. Order: Errors, Warnings, Info.
- If there are no findings at all, write `All checks passed.`
- Drop exact duplicate findings (same severity, ID, path, message).
- JSON form: an array of `{"severity": ..., "code": ..., "where": ..., "message": ...}`.
- Verdict: fail when there is at least one Error, or any Warning in strict mode. Otherwise pass. (Old exit codes: 0 pass, 1 fail, 2 usage error.)
- Severity words are exactly `error`, `warn`, `info`.

## 3. Shared helpers

Safe reading. Skip symlinks and any file over 2,000,000 bytes. Ignore a leading BOM. Treat CRLF as LF. A file that cannot be read counts as missing.

Text suffixes scanned for secrets and placeholders: `.md .py .json .sh .js .mjs .cjs .ts .txt .yaml .yml .toml .ini .cfg .env .ps1 .bat`

Skipped folders for tree scans: `.git node_modules __pycache__ dist .venv results`

Frontmatter reading (a small YAML subset). The text must start with `---` on line 1 and have a closing `---` line. Read: plain scalars, quotes stripped, folded (`>`, `>-`) and literal (`|`, `|-`) blocks, one-level maps (a key with an empty value followed by indented `key: value` lines), and inline lists `[a, b]`. If the opening `---` is missing or never closed, frontmatter is "missing". The body is everything after the closing `---`.

Secret check (rows 1 and 2, and the tree scans). Two steps per line:

1. Known token formats (rule `X001`):

```
(Bearer\s+[A-Za-z0-9._\-]{20,}|sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)
```

A hit stops checking that line. Mask it as the first 6 characters plus `...`.

2. Key-like assignment (rule `X003`), case-insensitive:

```
([\w-]*?(?:api[_-]?key|apikey|secret|token|passw(?:or)?d|access[_-]?key|private[_-]?key))["']?\s*[:=]\s*["']?([A-Za-z0-9_\-./+=]{20,})|Authorization["']?\s*:\s*["']Basic\s+([A-Za-z0-9+/=]{16,})
```

The captured value counts only when all hold: it does not match the not-a-secret pattern below, it has at least one digit, it has at least one letter, and it has more than 8 distinct characters. Report the first such hit per line. Mask as `<key name>=<first 4 chars>...` (use `Authorization` as the key name for the Basic form).

Not-a-secret pattern (case-insensitive):

```
(env|config|process|getenv|example|your|placeholder|xxxx|changeme|dummy|redacted|sample|user_config|plugin_root)
```

Placeholder pattern (rule `S010`):

```
\b(T[O]DO|F[I]XME|T[B]D)\b|<!--\s*F[I]LL|(?i:l[o]rem ipsum)   (bracket classes match the same words; written so this file passes its own check)
```

Slug pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`. Semver pattern: `^\d+\.\d+\.\d+([-+][0-9A-Za-z.\-]+)?$`.

Plugin manifest known top-level keys (anything else is `P003`):
`$schema name displayName version description author homepage repository license keywords metadata defaultEnabled dependencies settings userConfig channels skills commands agents hooks mcpServers lspServers outputStyles workflows experimental icon documentationUrl supportUrl privacyPolicyUrl termsOfServiceUrl types`

Listing URL keys (`P017`): `documentationUrl supportUrl privacyPolicyUrl termsOfServiceUrl`

Upload-portable skill frontmatter keys: `name description license compatibility metadata allowed-tools`

Hook events: `SessionStart Setup UserPromptSubmit UserPromptExpansion PreToolUse PermissionRequest PermissionDenied PostToolUse PostToolUseFailure PostToolBatch Notification MessageDisplay SubagentStart SubagentStop TaskCreated TaskCompleted Stop StopFailure TeammateIdle InstructionsLoaded ConfigChange CwdChanged DirectoryAdded FileChanged WorktreeCreate WorktreeRemove PreCompact PostCompact PreModelSwitch PostModelSwitch Elicitation ElicitationResult SessionEnd`

Hook handler types: `command http mcp_tool prompt agent`

Agent colors: `red blue green yellow purple orange pink cyan`

Agent keys ignored for plugin agents: `permissionMode mcpServers hooks initialPrompt`

userConfig allowed fields: `type title description required default options multiple sensitive min max`. userConfig types: `string number boolean directory file`.

Eval grader types: `regex tool_used tool_order file_exists llm baseline`.

Reserved plugin names (directory target): `claude anthropic official plugin mcp test`.

Windows device name pattern for file names (case-insensitive): `^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$`

Image suffixes: `.png .jpg .jpeg .gif .webp`. Font suffixes: `.ttf .otf .woff .woff2`.

Launcher pin pattern (a package argument counts as pinned): `.+(@|==)v?\d+\.\d+\.\d+`

Version range pattern for npm dependencies (a match means "not pinned"): `^\s*(\^|~|\*|>|<|latest$|next$|x$|.*\.x|.*\|\||git[+:]|https?:|file:|link:)`

Runner pin markers: `npx` and `bunx` and `pnpx` need `@`; `uvx` and `pipx` need `==`.

Environment reference pattern (`D014`): `\$\{(?!user_config\.|CLAUDE_)[A-Za-z_][A-Za-z0-9_]*(?::-[^}]*)?\}`

Environment read in code (`D014`): `os\.environ|os\.getenv|process\.env|Path\.home\(\)|expanduser\(`

Fetch-and-run pattern (`D016`): `(curl|wget)\b[^\n|]*\|\s*(ba|z)?sh\b|\b(iwr|irm|Invoke-WebRequest)\b[^\n|]*\|\s*iex\b|\bnpx\s+-y\b|\bpip3?\s+install\b|\bnpm\s+(i|install)\s+-g\b`

Environment use test for `.env.example` (`X011`): `os\.environ|os\.getenv|process\.env|\$\{(?!CLAUDE_|user_config)[A-Z][A-Z0-9_]*\}`

Self-quoting files skipped by `D014`, `D015`, `D016`: any file named `validate_extension.py`, `selftest.py`, `scan_secrets.py` (these quote the patterns on purpose). Also skip this recipe file when it sits inside a checked extension.

Role nouns for `P023`. A slug ends in a role noun when its last word is one of:
`planner developer maintainer reviewer packager cleaner prompter builder writer checker auditor validator generator manager helper assistant expert specialist analyst researcher drafter architect designer operator strategist engineer tester fixer scanner runner creator publisher deployer migrator optimizer organizer grader comparator finder handler adviser advisor coach bot`

Or when the last word is 6+ letters, ends with `(er|or|ist|ant|ian)$`, and is not one of these allowed words:
`user order folder server cluster number layer filter other error parser buffer border master letter cover water paper power tensor vector sensor monitor timer inner outer after wrapper`

## 4. Procedure

Work in this order. Collect findings into one list, then dedupe and print (section 2).

1. Read the inputs. Decide the kind (section 1).
2. If kind is `plugin`, run steps 3 to 21 (plugin checks, rows 160 to 194 first for the manifest). If kind is `skill`, run the skill check (step 6) on the folder itself with every `*.md` under it as the "plugin files", then the prompt check (step 15) using the skill name.
3. Manifest. Read `.claude-plugin/plugin.json` (rows 160 to 177, 181, 182). Without a manifest, use the folder name as the plugin name and skip manifest-only checks (the old script skipped rows 169 to 173, 181 to 182 when no manifest existed).
4. Skill folders. Glob `skills/*/` (skip symlinks). Rows 178 to 180.
5. Collect the Markdown set: Glob `**/*.md` excluding `.git`, symlinks, and `CHANGELOG.md`. This is "plugin files" for orphan and broken-reference checks.
6. For each skill folder: read `SKILL.md` and its frontmatter, apply rows 5 to 32 (skill rows). Also Glob all files in the folder: apply the per-file rows (24 to 31).
7. Version sync: rows 181 to 183.
8. Agents: Glob `agents/**/*.md`. Apply rows 33 to 38 and the screen row 32.
9. Hooks: if `hooks/hooks.json` exists, apply rows 39 to 51.
10. MCP: read `.mcp.json` and the manifest `mcpServers` object. Apply rows 52 to 60. Remember each server (name, config, file).
11. userConfig: rows 61 to 67.
12. Supply chain: rows 126 to 133.
13. Secrets outside skills: Glob every file outside `skills/`, outside skipped folders, not symlinks. Apply row 118 and the secret check (rows 1, 2) to text files.
14. Overlap and routing: rows 119 to 122, then naming and router rows 137 to 148 (only when a manifest exists).
15. Shared files and prompts: rows 123 to 125, 113 to 117.
16. Evals: row 184 (only when there are skills), then workflows, themes, monitors, LSP, output styles, settings, eval cases: rows 71 to 89.
17. Directory target only: rows 90 to 112.
18. Root files: rows 185 to 191, marketplace rows 192 to 194 (K001 uses row 3 or 4).
19. Script paths: rows 134 to 136.
20. Public safety: rows 149 to 159 (see section 6).
21. Connectors: rows 68 to 70. With `known-connectors` empty, only the in-plugin duplicate check runs.
22. Print the report (section 2).

Per-check detail follows each table.

## 5. Rule tables

Severity "E/W" means: error or warn as stated in the row. `<x>` is a placeholder filled with the real value.

The tables are split by topic so each file loads on demand. Read the file that holds the rows you need; every row is still checked on every run.

| Rows | Topics | File |
|---|---|---|
| 1 to 89 | 5.1 reading and secrets, 5.2 skills, 5.3 agents, 5.4 hooks, 5.5 MCP connectors, 5.6 userConfig, 5.7 connector duplicates, 5.8 workflows, themes, monitors, LSP, output styles, settings, evals | `references/validate-rules-core.md` |
| 90 to 194 | 5.9 directory target, 5.10 companion prompts, 5.11 secrets outside skills, 5.12 overlap and routing, 5.13 shared files, 5.14 supply chain, 5.15 script paths, 5.16 router standard, 5.17 naming, 5.18 public safety, 5.19 plugin manifest and root files | `references/validate-rules-release.md` |

## 6. Dependencies on other recipes

These rows call work that other recipes own. Follow the named recipe for the detection, then raise the finding exactly as written above.

| Rows | Needs | Where |
|---|---|---|
| 32 (`X005`) | Injection screen of Markdown text | `references/screen-text.md` |
| 115, 116 (`C002`, `C003`) | Companion prompt rules (errors and warnings for `prompts/*.json`) | the `aiaddon-package` recipe for companion prompts |
| 123 to 125 (`F001`) | Shared file comparison (source, copy, state: same, missing, drifted) from `.claude-plugin/shared-files.json` | the `aiaddon-maintain` recipe for shared files |
| 142 (`P027`) | Router eval check | `references/route-check.md` |
| 149 to 159 (`X008` to `X013`) | Secret and private-data detection, allowlist, `.gitignore` preset, history and package scans | `references/public-safety.md` and its recipe |

If a needed recipe file does not exist yet, raise the matching "not found" row (114 for companion prompts, 123 for shared files, 149 for public safety) and continue.

Features that cannot match the old script exactly:

- Fast hashing cache (`--cache`): now an optional "nothing changed" shortcut using `git status`.
- Exact numeric injection score in row 32: replaced by a judgment call.
- Byte-exact distinct-character count in the `X003` test: count by eye; this affects only borderline values.
