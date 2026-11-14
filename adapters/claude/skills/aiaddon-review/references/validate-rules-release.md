# Validate extension: rule tables, part 2 (rows 90 to 194)

Rule tables 5.9 to 5.19 of `validate-extension.md` (read that file first for inputs, output format, helpers and procedure). Severity "E/W" means: error or warn as stated in the row. `<x>` is a placeholder filled with the real value.

## Contents

- 5.9 Directory target (rows 90 to 112)
- 5.10 Companion prompts (rows 113 to 117)
- 5.11 Secrets outside skills (row 118)
- 5.12 Overlap and routing (rows 119 to 122)
- 5.13 Shared files (rows 123 to 125)
- 5.14 Supply chain (rows 126 to 133)
- 5.15 Script paths (rows 134 to 136)
- 5.16 Router standard (rows 137 to 142)
- 5.17 Naming standard (rows 143 to 148)
- 5.18 Public safety (rows 149 to 159)
- 5.19 Plugin manifest and root files (rows 160 to 194)

### 5.9 Directory target (rows 90 to 112)

Run only when target is `directory`. Collect all files under the plugin root except `.git` and `__pycache__` folders.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 90 | `D001` | error | plugin name shape | `^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$` | `name '<name>' must be ASCII lowercase letters/digits/hyphens, <=64, starting and ending alphanumeric` |
| 91 | `D001` | error | plugin name reserved | name in `claude anthropic official plugin mcp test` | `name '<name>' is a reserved word` |
| 92 | `D002` | error | no README in the root | a file whose lowercase name starts with `readme` | `README missing` |
| 93 | `D002` | error | README too short | fewer than 40 words after removing fenced code blocks | `README has <n> words outside code blocks (>=40 required)` |
| 94 | `D003` | error | no license | no `LICENSE` file and no `license` key in plugin.json | `no LICENSE file and no license in plugin.json` |
| 95 | `D004` | error | system file | name `.DS_Store`, `Thumbs.db`, `desktop.ini`, or path part `__MACOSX` | `system file: remove` |
| 96 | `D005` | error | a symlink | any symlink | `symbolic link: commit a regular file` |
| 97 | `D011` | error | invalid file name | any path part matching `[:<>"\|?*]\|[. ]$` or the Windows device pattern | `name invalid on Windows/macOS` |
| 98 | `D011` | error | two paths differ only by case | compare lowercase relative paths | `differs only by case from <other path>` |
| 99 | `D006` | warn | too many files | regular files > 512 | `<n> files (>512: held for a reviewer)` |
| 100 | `D006` | warn | binary file that is not an image or font | file whose first 4096 bytes are not valid UTF-8, suffix not in the image and font lists | `binary file other than PNG/JPEG/GIF/WebP/font: held for a reviewer` |
| 101 | `D006` | warn | large non-image file | size > 256 KiB (262144 bytes), non-image, non-font | `<size in KiB, whole number> KiB (>256 KiB non-image file: held for a reviewer)` |
| 102 | `D007` | error | an MCP launcher with no exact version pin | see launcher rules below | `server '<name>': <reason>` |
| 103 | `D009` | error | server url not secure | url, when present, must match `^(https\|wss)://`, or start with `${user_config.`, or be empty | `server '<name>': url must be https://, wss://, a ${user_config.*} reference, or empty` |
| 104 | `D010` | warn | bundled server file | server JSON matches `\.(mcpb\|dxt)\b` | `server '<name>': .mcpb/.dxt bundles are held for a reviewer; declare command/args or url` |
| 105 | `D008` | error | package-source config beside a launcher (only if some server hit row 102) | any of `.npmrc`, `bunfig.toml`, `uv.toml` in the root | `package-source config next to a launcher` (path: that file) |
| 106 | `D015` | info | the plugin sets `icon` | `icon` key present in plugin.json | `the icon field draws an image policy hold; keep the listing icon at its default location and drop the field` |
| 107 | `D014` | warn | a server reads the user's environment | in the JSON of the server's `env`, `headers`, `args`, `url`: any match of the environment reference pattern (section 3), one finding per distinct match | `server '<name>': <match> reads the user's environment (policy hold); ask with userConfig (sensitive: true) and use ${user_config.KEY}` |
| 108 | `D014` | warn | a code file reads the environment or home folder | code means suffix `.py .js .mjs .cjs .ts .sh .bash .ps1` or first path part `hooks`; pattern `os\.environ\|os\.getenv\|process\.env\|Path\.home\(\)\|expanduser\(` | `reads the user's environment or home folder (policy hold: 'uses a credential from the user's machine'); take values as arguments or ${user_config.KEY}` |
| 109 | `D014` | info | a Markdown or JSON file has an environment reference example (a `$` followed by a name in braces) beside a URL (only when row 108 did not fire for the file) | environment reference pattern plus `https?://` in the same file | `an environment reference example sits beside a URL (policy hold); write examples as ${user_config.KEY}` |
| 110 | `D015` | info | a file names a bundled image or font | file text contains the name of an image or font file in the plugin; applies when the file is code, `.json` (not `.claude-plugin/plugin.json`), or a Markdown code span `` `[^`\n]*<name>`` | `names the image file '<name>' (policy hold: a reviewer checks it); describe it in words instead` |
| 111 | `D016` | warn | a hook file (first path part `hooks`, suffix `.json`) installs or downloads code | fetch-and-run pattern (section 3) | `a hook installs packages or downloads code at run time (policy hold); ship the code inside the plugin` |
| 112 | `D016` | info | any other file has a fetch-and-run command | fetch-and-run pattern (section 3) | `download-and-run command (portal warning); fine in docs, but ship the script inside the plugin if the plugin runs it` |

Launcher rules for row 102 (take the last path part of `command`, for example `npx`):

- `npx`, `bunx`, `uvx`; or `pnpm`/`yarn` with `dlx` in args; or `pipx` with `run` in args: take the first argument that does not start with `-` and is not `dlx` or `run`. If it does not match the pin pattern `.+(@|==)v?\d+\.\d+\.\d+`, reason is `package launcher without an exact version pin`.
- `uv` with `run` in args and neither `--locked` nor `--frozen` in args: reason is `uv run without --locked or --frozen`.

Rows 106 to 112 run as part of the directory target, after rows 102 to 105. Skip image and font files and the self-quoting files for rows 108 to 112. Servers for rows 102 to 107 come from `.mcp.json` and the manifest `mcpServers`.

### 5.10 Companion prompts (rows 113 to 117)

Glob `prompts/*.json`.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 113 | `C000` | info | no `prompts/*.json` file | none found | `no companion prompt in prompts/: the packager creates one (companion_prompt.py)` |
| 114 | `C000` | info | the companion prompt rules cannot be found | the `aiaddon-package` recipe for companion prompts is missing | `companion prompt checker not found; skipped` |
| 115 | `C002` | error | each error the companion prompt check returns | see section 6 | the error text itself |
| 116 | `C003` | warn | each warning the companion prompt check returns | see section 6 | the warning text itself |
| 117 | `C004` | warn | prompt never starts the extension (only when a plugin or skill name is known) | join the `content` of every item in `prompts`; slash-command names found with `(?<![\w/])/([a-z0-9][a-z0-9-]*)(?::[a-z0-9-]+)?` must include the extension name | `prompt never starts the extension: add `/<name>` (or `/<name>:<skill>`) to its content` |

### 5.11 Secrets outside skills (row 118)

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 118 | `X004` | error | a committed env file | outside `skills/` and skipped folders: name is `.env`, or starts with `.env.` and does not end with `.example` or `.sample` | `committed .env file: remove it and list the variables in the README` |

Also run the secret check (rows 1 and 2) on every text file outside `skills/` (and `.env*` files).

### 5.12 Overlap and routing (rows 119 to 122)

Sentence rule: take each skill and agent Markdown file; remove fenced code blocks and frontmatter; split on `.`, `!`, `?` followed by space, and on newlines; strip the characters `` ` * _ > # | [ ] ( ) `` and leading or trailing space, dash, colon; lowercase; collapse spaces; keep sentences with 12 or more words.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 119 | `S017` | warn | the same sentence (12+ words) in two skill or agent files | exact equality after cleanup | `repeats a rule from <folder>/<file> ("<first 60 chars>..."): keep one home and point to it` (path: the second file) |
| 120 | `S018` | warn | a sentence equals one in a rules file (only when rules input is set) | same cleanup | `repeats a project instruction from <rules file name> ("<first 60 chars>..."): keep it in one place` |
| 121 | `S019` | warn | the router never names a skill (only when there are 2 or more skills and the router exists at `skills/<plugin name>/SKILL.md`) | the skill name must appear in the router `SKILL.md` or `references/*.md` as a whole word: `(?<![\w-])<name>(?![\w-])` | `the router never names '<skill>': it runs only when its own description happens to match; add it to the routing table` |
| 122 | `A006` | warn | no skill mentions an agent (same conditions; `agents/` folder exists) | the agent name (frontmatter `name`, else file stem) as a whole word in the combined text of all `.md` files under `skills/` | `no skill names agent '<name>': say which step uses it` |

### 5.13 Shared files (rows 123 to 125)

Config: `.claude-plugin/shared-files.json`. If missing, skip.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 123 | `F001` | info | the sync tool cannot be found | the `aiaddon-maintain` recipe for shared files is missing | `sync_shared.py not found; shared copies not checked` |
| 124 | `F001` | error | a shared source file does not exist | source path in the config | `shared source <src> does not exist` |
| 125 | `F001` | warn | a copy differs from its source | state is anything except same | `<state> copy of <src>: run aiaddon-maintain/scripts/sync_shared.py` |

See section 6 for how to compare copies.

### 5.14 Supply chain (rows 126 to 133)

Warn level `pin`: `warn` when target is `directory`, `cowork` or `upload`; otherwise `info`.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 126 | `X006` | pin level | a `requirements*.txt` line is not pinned (skip blank lines, `#` comments, lines starting with `-`) | line has neither `==` nor `@` | `line <n>: '<line>' is not pinned; pin an exact version (==) before release, ideally with --hash` |
| 127 | `X006` | pin level | an npm dependency is a range (`dependencies` and `optionalDependencies` in each `package.json` outside skipped folders) | the version string matches the range pattern in section 3 | `dependency '<name>': '<version>' is a range; pin an exact version before release` |
| 128 | `X006` | pin level | dependencies exist but no lockfile | none of `package-lock.json npm-shrinkwrap.json pnpm-lock.yaml yarn.lock bun.lockb` beside the package.json | `no lockfile: commit package-lock.json so every install gets the same code` |
| 129 | `X006` | pin level | an MCP server uses an unpinned runner (skip when target is `directory`: row 102 covers it) | command `npx bunx pnpx uvx pipx`; first arg not starting with `-` and not `run`; the pin marker (`@` for npx, bunx, pnpx; `==` for uvx, pipx) must be in the arg after stripping a leading `@` | `server '<name>': '<cmd> <pkg>' runs whatever version is newest; pin it (<pkg><marker><version>)` (path: `.mcp.json`) |
| 130 | `X007` | info | servers exist but no injection guardrail | no group in `hooks.json` `hooks.PostToolUse` whose hook JSON mentions `screen_text.py`, and no required screen step (no `skills/*/SKILL.md` mentions `screen-text` together with a `skills/*/references/screen-text.md` file; this step satisfies the rule, since the directory refuses hooks) | `connectors but no injection guardrail: add the required screen step (a skill step that follows references/screen-text.md, standards 5c); a hook is refused by the directory` |
| 131 | `X007` | error | a guardrail matcher is not a valid regex | matcher text (default `.*`) | `guardrail matcher '<matcher>' is not a valid regex` |
| 132 | `X007` | info | guardrail matcher is too broad | matcher is `.*`, `*`, `mcp__.*`, or fully matches `mcp__other-plugin_tool__x` | `guardrail matcher '<matcher>' screens every MCP tool in the session; scope it to this plugin's connectors` |
| 133 | `X007` | warn | guardrail matcher misses a connector | for each plugin server, the matcher must fully match `mcp__plugin_<plugin name>_<server>__any_tool` | `guardrail matcher '<matcher>' misses connector '<server>': its output is never screened` |

Servers for rows 129 to 133 come from `.mcp.json` and the manifest `mcpServers` (only servers with a command for row 129).

### 5.15 Script paths (rows 134 to 136)

Files: every `SKILL.md` (not under `.git`, not symlinks), all `commands/**/*.md`, all `agents/**/*.md`, and `hooks/hooks.json`. Walk each Markdown file line by line. A line starting a fence (first non-space chars are three backticks) toggles "inside a fence". Inside a fence the code is the whole line; outside, the code is all code spans on the line joined by spaces. Skip the line unless the code matches `(^|[\s;&|(])(python3?|bash|sh|node|find|ls|cat|cp|mv|rm|cd|source|pip3?|npm|npx|chmod)\b`.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 134 | `R001` | error | the shell command names `/root/.claude` | substring in the code | `line <n>: shell command names /root/.claude; copy scripts once per session into the working folder (./tools/) and run them from there` |
| 135 | `R002` | warn | the shell command names `~/.claude` (when row 134 did not fire) | substring in the code | `line <n>: shell command names ~/.claude; copy scripts into the working folder (./tools/) instead` |
| 136 | `R001` | error | `hooks/hooks.json` text contains `/root/.claude` | substring | `hook command names /root/.claude; use ${CLAUDE_PLUGIN_ROOT} or a working-folder copy` |

### 5.16 Router standard (rows 137 to 142)

Only when there are 2 or more skills, a plugin name exists, and `skills/<name>/SKILL.md` exists. Run only when a manifest exists.

Routing table parse: find a heading of level 2 to 4 containing `Routing table` (case-insensitive); the table is everything up to the next heading. Each row is `| Order | Trigger phrases | Skill | Then |`. Skip the header and separator rows. Phrases are separated by `;`, lowercased, with curly apostrophes made straight. The skill slug is the first code span in the Skill cell (text after the last `:` is the slug). The Then cell code spans are extra slugs. Rows without a code span in the Skill cell are ignored.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 137 | `P028` | error | no routing table in the router | table not found (see `references/route-check.md`) | ``router has no routing table: add a 'Routing table' section with `\| Order \| Trigger phrases \| Skill \| Then \|` mapping phrases to exact skill slugs`` |
| 138 | `P024` | error | a routed slug is not a skill folder | each slug in Skill and Then cells must be a folder under `skills/` | `routing table names '<slug>', which is not a skills/ folder` |
| 139 | `P025` | error | a skill cannot be reached | every skill folder except the router must appear in some Skill or Then cell | `'<skill>' is not reachable from the router table: add a row (or a Then entry) for it` (path: that skill's SKILL.md) |
| 140 | `P026` | error | the router lacks a standard phrase (case-insensitive text search of the router SKILL.md) | needed text: `skill tool`, `relative`, `closed question`, `never answer` | `router standard missing: <label>` with labels: for `skill tool` "load the chosen skill with the Skill tool using the full slug <plugin>:<skill>"; for `relative` "fallback: read the skill's SKILL.md by relative path when there is no Skill tool"; for `closed question` "a default: when no row matches, ask one closed question with options"; for `never answer` "never answer the task itself" |
| 141 | `P028` | warn if an `evals/` folder exists, else info | no `evals/router/cases.json` | file must exist | `no router evals: add evals/router/cases.json with at least 2 prompts per skill and some ambiguous ones (expected 'ask')` (then stop the router checks) |
| 142 | `P027` | error | every problem that the route-check recipe returns | follow `references/route-check.md`; one finding per problem | the problem text itself (path: `evals/router/cases.json`) |

### 5.17 Naming standard (rows 143 to 148)

Needs a plugin name. Prefix `pre` is `<name>-`.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 143 | `P019` | error | more than one skill but no router named exactly like the plugin | `skills/<name>/SKILL.md` must exist | `the router skill must be named exactly '<name>' (the plugin name): skills/<name>/SKILL.md` |
| 144 | `P019` | error | exactly one skill, not named like the plugin and not prefixed | name equals `<name>` or starts with `<name>-` | `a single skill must be named '<name>' (its own router) or prefixed '<pre>'` |
| 145 | `P020` | error | with more than one skill, a skill other than the router lacks the prefix | `startswith(pre)` | `skill '<skill>' must be prefixed '<pre>' (every skill except the router)` |
| 146 | `P021` | error | an agent (`agents/**/*.md`, name from frontmatter else file stem) lacks the prefix | `startswith(pre)` | `agent '<name>' must be prefixed '<pre>'` |
| 147 | `P022` | error | a command (`commands/**/*.md`) file stem lacks the prefix and is not the plugin name | `startswith(pre)` or equals `<name>` | `command '<stem>' must be prefixed '<pre>'` |
| 148 | `P023` | error | a skill, agent or command name ends in a role noun (skip the router itself) | strip the prefix, then apply the role noun rules in section 3 | `'<name>' ends in the role noun '<noun>': name it for the action (-review, not -reviewer; -plan, not -planner)` |

### 5.18 Public safety (rows 149 to 159)

The detection engine is described in the public-safety recipe (section 6). The finding shapes are fixed here.

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 149 | `X008` | warn | the secret and private-data scan cannot run | public-safety recipe unavailable | `public_safety.py missing next to the validator: secret and private-data scan skipped` |
| 150 | `X008` | error | a secret or private value in files git would publish (first 25 findings) | public-safety recipe | with a line number: `line <n>: <kind> <value>: remove it, use userConfig or an environment variable, rotate it, or allowlist a true false positive`; without: `<kind>: keep it out of the repo (.gitignore) and rotate anything it held` |
| 151 | `X008` | error | more than 25 findings | count - 25 | `<n> more private-data findings: run scan_secrets.py on the folder` (read: apply the public-safety recipe to the whole folder) |
| 152 | `X012` | error | a secret or private file in git history (first 10; only if `.git` exists and no-history is not set) | public-safety recipe, history mode | `<where>: <kind> <value> is in git history: rotate it first, then follow past leak remediation (aiaddon-review/references/public-safety.md); never force-push without the owner's OK` |
| 153 | `X012` | error | more than 10 history findings | count - 10 | `<n> more findings in history: run scan_secrets.py <folder> --history` (read: repeat the history scan on the whole folder) |
| 154 | `X013` | error | a secret inside a built package (`dist/`, root `*.plugin`, root `*.zip`) | public-safety recipe, artifact mode | `inside a built package: <kind> <value>: rebuild after removing it` |
| 155 | `X009` | error | `.gitignore` missing (plugin kind only) | file must exist | `.gitignore missing: add the public-safety preset (aiaddon-review/references/public-safety.md section 3)` |
| 156 | `X009` | error | `.gitignore` lacks preset lines | each required preset line must be in the file (compare lines after trimming and removing a leading `/`) | `.gitignore lacks the public-safety preset lines: <comma list>` |
| 157 | `X010` | error | `PUBLIC-SAFETY.md` missing (plugin kind only) | root file must exist | `PUBLIC-SAFETY.md missing: list what may be public and what stays private (template in aiaddon-review/references/public-safety.md section 4)` |
| 158 | `X011` | warn | no `.env.example`, but the extension reads environment variables | env-use pattern in section 3 found in `.mcp.json`, `hooks/hooks.json`, `.claude-plugin/plugin.json`, or any text file under `servers/`, `scripts/`, `bin/` | `.env.example missing: the extension reads environment variables; list each one, names only, no values` |
| 159 | `X011` | error | `.env.example` holds values | any line with a non-empty value | `.env.example holds values: keep names only` |

Rows 155 to 159 apply only to the plugin kind. Rows 149 to 154 apply to both kinds. Skip the artifact scan when there is no `dist/`, `*.plugin` or `*.zip`.

### 5.19 Plugin manifest and root files (rows 160 to 194)

| # | ID | Sev | What to check | Pattern or threshold | Message |
|---|---|---|---|---|---|
| 160 | `P001` | error if target is `directory` or `cowork`, else warn | no manifest | `.claude-plugin/plugin.json` must exist | `no .claude-plugin/plugin.json: Claude Code loads the folder under its own name with no version, so updates never reach users; add a manifest` |
| 161 | `P001` | error | manifest valid JSON but not an object | must be an object (then stop plugin checks) | `plugin.json must be a JSON object` |
| 162 | `P002` | error | no name | non-empty | `missing name` |
| 163 | `P002` | warn | name not kebab-case | `^[a-z0-9]+(-[a-z0-9]+)*$` | `name should be kebab-case` |
| 164 | `P016` | error | reserved name | normalize: lowercase, replace runs of `-_. ` and whitespace by `-`; error when it matches `^(claude\|anthropic\|anthropics\|cc-plugin)-`, or equals `claude`, `anthropic`, `anthropics`, `claude-code`, `claude-mods`, or contains `official` as a whole hyphen part together with `claude` or `anthropic` as a whole hyphen part (`(^\|-)official(-\|$)` and `(^\|-)(claude\|anthropic)(-\|$)`) | `plugin name '<name>' is reserved: it passes as one of Anthropic's own (claude plugin validate errors)` |
| 165 | `P016` | warn | name reads as Anthropic's own (only when row 164 did not fire) | `(^\|-)(claude\|anthropic\|anthropics)(-\|$)` on the normalized name | `plugin name '<name>' reads as one of Anthropic's own; put the brand in displayName instead` |
| 166 | `P017` | error | a listing URL is not https | for `documentationUrl supportUrl privacyPolicyUrl termsOfServiceUrl` when present | `<key> must be an https:// URL` |
| 167 | `P017` | error | bad icon | `icon` when present must be a string starting with `./` that points to an existing file | `icon must be a ./path to an image file inside the plugin` |
| 168 | `P003` | warn | unknown top-level key | not in the manifest key list in section 3 | `unrecognized top-level key '<key>' (stripped by Claude Code)` |
| 169 | `P004` | warn | no displayName (manifest exists) | non-empty | `no displayName (human-facing name)` |
| 170 | `P004` | warn | no description (manifest exists) | non-empty | `no description` |
| 171 | `P004` | warn | author missing (manifest exists) | `author` must be an object with a `name` | `author.name missing` |
| 172 | `P005` | warn | version not semver (manifest exists) | semver pattern in section 3 | `version '<version>' is not semver` |
| 173 | `P006` | error | a require-meta key is missing | for each key: in `metadata.<key>`, or `author.<key>`, or (for key `author`) `author.name` | `<key> required in plugin metadata` |
| 174 | `P007` | error | a path in `skills commands agents outputStyles workflows` does not start with `./` | each value may be a string, a list, an object of values, or objects with `source`; `.` and `./` are allowed | `<key>: path '<path>' must start with ./` |
| 175 | `P007` | error | the path contains `..` | substring | `<key>: path '<path>' escapes plugin root` |
| 176 | `P007` | error | the path does not exist | relative to the root | `<key>: path '<path>' not found` |
| 177 | `P007` | error | an `agents` entry is not a Markdown file | must end with `.md` | `agents entries must be .md files` |
| 178 | `P008` | error | `skills` exists but is not a folder | must be a folder | `skills must be a directory` |
| 179 | `P008` | warn | no skill folders | at least one folder under `skills/` | `no skills/ directory` |
| 180 | `P009` | warn | no router skill named like the plugin, and no short prefix router (a skill folder with a `SKILL.md` and at least one other skill folder named `<that folder>-...`) | `skills/<name>/SKILL.md` | `no router skill named '<name>' (router slug must equal plugin slug, or be the short prefix of the role skills)` |
| 181 | `P015` | warn | `metadata.version` differs from `version` | when `metadata.version` is set | `metadata.version <metadata version> != version <version>` |
| 182 | `P015` | warn | `metadata.displayName` differs from `displayName` | when both are set | `metadata.displayName differs from displayName` |
| 183 | `S015` | warn | a skill's `metadata.version` differs from the plugin version | when both exist | `metadata.version <skill version> != plugin version <version> (move them together)` (path: that skill's SKILL.md) |
| 184 | `E004` | info | skills exist but `evals/` has no subfolder and no `evals.json` | `evals/` must contain a folder or `evals.json` | `no behavior tests in evals/: run each skill against test prompts and grade them before release (aiaddon-build/references/testing.md)` |
| 185 | `P010` | warn | a root `CLAUDE.md` exists | file exists | `root CLAUDE.md is not loaded; put instructions in a skill` |
| 186 | `P011` | error if target is `cowork`, else warn | a `bin/` folder exists | folder exists | `claude.ai/Cowork do not install plugins containing bin/` (path: `bin`) |
| 187 | `P012` | warn | no LICENSE file | file `LICENSE` | `no LICENSE file` |
| 188 | `P012` | warn | license says MIT but the file lacks the phrase | `license == "MIT"` and `MIT License` not in the file | `LICENSE text does not match declared MIT` |
| 189 | `P012` | warn | license starts with Apache but the file lacks the phrase | `Apache License` not in the file | `LICENSE text does not match declared Apache` |
| 190 | `P013` | warn | `README.md` or `CHANGELOG.md` missing (one finding each) | files exist | `missing <file name>` |
| 191 | `P014` | warn | the top CHANGELOG entry does not match the version (only if the file has text and a version exists) | first heading matching `^##\s*\[?v?(\d+\.\d+\.\d+)` (multiline) must equal `version` | `top entry <found version or none> != plugin version <version>` |
| 192 | `K002` | error | marketplace file lacks `name`, `owner` or `plugins` (`.claude-plugin/marketplace.json`; one finding per key) | key present | `missing '<key>'` |
| 193 | `K003` | error | a marketplace plugin entry name differs from the manifest name | each item of `plugins` | `entry name '<entry name>' != manifest name '<name>'` |
| 194 | `K004` | error | a marketplace relative source is bad | `source` is a string and (contains `..` or does not exist under the root) | `bad relative source '<source>'` |

Notes for rows 160 to 194:

- Rows 169 to 172 run only when a manifest file exists.
- Row 173 needs the require-meta input.
- Rows 181 to 183, 184, 185 to 191, 192 to 194: run only in plugin kind.
- In plugin kind, rows 143 to 148 and 137 to 142 run only when a manifest exists.
- Row 191: compare to the manifest `version` string.
