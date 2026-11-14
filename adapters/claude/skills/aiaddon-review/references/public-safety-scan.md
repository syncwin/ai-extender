# Public-safety scan engine (recipe)

Replaces the former script `public_safety.py` (the engine behind `scan_secrets.py` and the validator checks `X008` to `X013`). Claude follows this recipe with Grep, Glob, Read and standard git and OS commands. Nothing here is code to save and run. Policy and remediation are in `public-safety.md`; the command-level wrapper (inputs, report, key-format rules X001 and X003) is `scan-secrets.md`.

## Contents

- 1. Purpose, when to use, inputs
- 2. Line rules (applied in this exact order; stop at the first finding on the line)
- 3. Regexes (verbatim, Python syntax)
- 4. High-entropy rule (rule 22) step by step
- 5. File-name rule (rule 23), tree scan, packages and history
- 6. Allowlist
- 7. Masking (what may appear in a report)
- 8. Gitignore preset and `.env.example` check (used by validator `X009` and `X011`)
- 9. Procedure for Claude
- 10. Example (fake values only)

## 1. Purpose, when to use, inputs

Find, in text, file names, git history and built packages: provider keys and tokens (GitHub, OpenAI, Anthropic, AWS, Slack, Google and more), private keys, Bearer tokens, password and secret assignments, high-entropy strings, personal e-mail addresses, absolute user paths (Windows, macOS, Linux), internal hosts, and files that must never be published (`.env`, keys, logs, memory or progress notes). Every finding is blocking. Values are always masked in reports.

Inputs: a folder (the root of the extension or repo), optional `--history`, optional package files or folders, optional allowlist file (default `.public-safety-allow` at the scanned root).

Total: 23 rule ids = 13 key-format rules + 9 other line rules + 1 file-name rule (`private-file`). Each finding records: file, line (0 for a whole-file finding), rule id, label (kind), masked value, where (empty, a package name, or `commit <hash>`). One finding per line at most; the first matching rule on a line wins.

## 2. Line rules (applied in this exact order; stop at the first finding on the line)

Lines longer than 4000 characters are cut to their first 4000 before testing. All regexes are Python `re` syntax and are listed verbatim in section 3.

| # | Rule id | Label (kind) | What | Severity | Exceptions |
|---|---|---|---|---|---|
| 1 | github-token | GitHub token | `ghp_ gho_ ghu_ ghs_ ghr_` then 20+ alphanumerics, or `github_pat_` then 20+ | blocking | allowlist only |
| 2 | anthropic-key | Anthropic key | `sk-ant-` then 20+ | blocking | allowlist only |
| 3 | openai-key | OpenAI-style key | `sk-`, optional `proj-` or `svcacct-`, then 20+ | blocking | allowlist only |
| 4 | aws-key | AWS access key id | `AKIA ASIA AGPA AIDA AROA` + 16 upper or digits | blocking | allowlist only |
| 5 | slack-token | Slack token | `xox` + one of `abposr` + `-` + 10+ | blocking | allowlist only |
| 6 | google-key | Google API key | `AIza` + 35 | blocking | allowlist only |
| 7 | google-oauth | Google OAuth token | `ya29.` + 20+ | blocking | allowlist only |
| 8 | private-key | private key block | `-----BEGIN ... PRIVATE KEY-----` header | blocking | allowlist only |
| 9 | huggingface-token | Hugging Face token | `hf_` + 30+ | blocking | allowlist only |
| 10 | stripe-key | Stripe secret key | `sk_` or `rk_` + `live` or `test` + 16+ | blocking | allowlist only |
| 11 | jwt | JSON Web Token | three dot-separated parts, first two start `eyJ` | blocking | allowlist only |
| 12 | slack-webhook | Slack webhook URL | `hooks.slack.com/services/T../B../token` | blocking | allowlist only |
| 13 | bearer | Bearer token | `Bearer` + 20+ token characters | blocking | allowlist only |
| 14 | basic-auth | Basic authorization | `Authorization: "Basic <16+ base64>"` | blocking | allowlist only |
| 15 | password | password assignment | name containing `pass` or `pwd` (`password`, `passwd`, `pwd`...) assigned a value of 6+ characters | blocking | value matches PLACEHOLDER; or value starts with `$` or `%`; or shorter than 6 |
| 16 | key-assignment | key-like value | name containing api key, apikey, secret, token, access key or private key assigned a value | blocking | value matches PLACEHOLDER; or no digit; or no letter; or 8 or fewer distinct characters |
| 17 | url-credentials | credentials inside a URL | `scheme://user:password@host` | blocking | user or password matches URL_CRED_OK; or password matches PLACEHOLDER |
| 18 | email | personal e-mail address | any e-mail address | blocking | local part in EMAIL_LOCAL_OK; domain matches EMAIL_DOMAIN_OK; local part matches EMAIL_NOREPLY; domain ends in `.md .json .py .yml .yaml .txt .js` |
| 19 | user-path | absolute local user path | `C:\Users\<name>`, `/Users/<name>`, `/home/<name>` | blocking | `<name>` matches USER_OK |
| 20 | drive-path | absolute local drive path | `X:\<folder>\` or `X:/<folder>/` | blocking | `<folder>` (trimmed) matches DRIVE_OK |
| 21 | internal-host | internal URL or host | `http(s)://` to 10.x, 127.0.0.x, 192.168.x, 172.16-31.x, or a host ending `.internal .corp .lan .intranet .local` | blocking | allowlist only |
| 22 | high-entropy | high-entropy string | a run of 32+ token characters that looks random | blocking | see section 4 |
| 23 | private-file | (label by file name, section 5) | file name or folder says the file must never be published | blocking | PRIVATE_OK names; allowlist |

Rules 1 to 13 are the "key formats" (KEY_RULES). Rule 23 is file-name based, not line based.

Ordering detail for rules 14 to 22: BASIC is tested once; then every ASSIGN match on the line in order (rules 15 and 16: a match whose key contains `pass` or `pwd` can only produce `password`, and if it fails that test it does NOT fall through to `key-assignment`); then every URL_CRED match; then every EMAIL match; then USER_PATH (Windows pattern first, then the Unix pattern); then DRIVE_PATH; then INTERNAL_HOST (first match); then TOKENISH.

## 3. Regexes (verbatim, Python syntax)

Pipes and backticks appear in these patterns, so they are given in a fenced block, one per line as `NAME: pattern`. Lookbehinds `(?<!...)` are not supported by the Grep tool (Rust regex); run those with Bash `grep -rnP` or `git grep -nP`, or search with the pattern minus its leading lookbehind and check the preceding character by reading.

```
github-token:      \b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})
anthropic-key:     \bsk-ant-[A-Za-z0-9_\-]{20,}
openai-key:        \bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{20,}
aws-key:           \b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b
slack-token:       \bxox[abposr]-[A-Za-z0-9\-]{10,}
google-key:        \bAIza[0-9A-Za-z_\-]{35}\b
google-oauth:      \bya29\.[0-9A-Za-z_\-]{20,}
private-key:       -----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----
huggingface-token: \bhf_[A-Za-z0-9]{30,}
stripe-key:        \b[sr]k_(?:live|test)_[A-Za-z0-9]{16,}
jwt:               \beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}
slack-webhook:     hooks\.slack\.com/services/T[A-Z0-9]{6,}/B[A-Z0-9]{6,}/[A-Za-z0-9]{16,}
bearer:            \bBearer\s+[A-Za-z0-9._~+/\-]{20,}=*

BASIC (basic-auth; credential = group 1):
(?i)Authorization["']?\s*:\s*["']Basic\s+([A-Za-z0-9+/=]{16,})

ASSIGN (password, key-assignment; key = group 1, value = group 2):
(?i)\b([\w-]*?(?:api[_-]?key|apikey|secret|token|passw(?:or)?d|passwd|pwd|access[_-]?key|private[_-]?key))["']?\s*[:=]\s*["']?([^\s"'`<>,;(){}\[\]]{6,})

PLACEHOLDER (value filter, search anywhere in the value):
(?i)(env|config|process|getenv|example|your|placeholder|xxxx|\*\*\*|changeme|dummy|redacted|sample|user_config|plugin_root|none|null|false|true|string|secret_value|<|>|\$\{|\$\(|%\w+%|\{\{)

URL_CRED (url-credentials; user = group 1, password = group 2):
\b[a-z][a-z0-9+.\-]*://([^/\s:@\"'`<>]+):([^/\s@\"'`<>]{3,})@[\w.\-]+

URL_CRED_OK (must match the WHOLE user or password to be allowed):
(?i)^(user|username|name|you|your|pass|password|pwd|secret|token|xxx+|\*+|\$\{.*|%.*|<.*|\{\{.*)$

EMAIL (local = group 1, domain = group 2):
(?<![\w.%+\-])([A-Za-z0-9][A-Za-z0-9._%+\-]*)@((?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,})\b

EMAIL_LOCAL_OK (exact set, compared to the lowercased local part):
git, you, user, name, your, email, someone, me, x, a, foo, bar, test, info@example

EMAIL_DOMAIN_OK (search on the domain):
(?i)(^|\.)(example\.(com|org|net)|example|invalid|localhost|test|users\.noreply\.github\.com|noreply\.github\.com|domain\.com|company\.com|yourdomain\.com|email\.com)$

EMAIL_NOREPLY (search on the local part):
(?i)no-?reply|do-?not-?reply|^your[-_.]|[-_.]your$|placeholder|<|>|\.\.\.

USER_PATH, Windows form (user = group 1):
(?i)\b[A-Z]:[\\/]+Users[\\/]+([^\\/\s\"'`<>*|:?]+)

USER_PATH, Unix form (user = group 1):
(?<![\w.~])/(?:Users|home)/([^/\s\"'`<>*|:?]+)

USER_OK (must match the WHOLE user name to be allowed):
(?i)^(public|default|default user|all users|user|username|you|your|yourname|name|me|example|runner|ubuntu|root|vsts|admin|someone|%\w+%|\$\w+|\{.*\}|<.*>|\.\.\.|x+|ci|node|app|claude|\*)$

DRIVE_PATH (drive = group 1, first folder = group 2):
(?<![\w/\\.])([A-Za-z]):[\\/]{1,2}([A-Za-z0-9_.\- ]+)[\\/]

DRIVE_OK (match against the trimmed folder name):
(?i)^(windows|program files( \(x86\))?|programdata|temp|tmp|path|to|your.*|folder|dir|directory|project|repo|example.*|some.*|my.*|users|<.*|\$.*|%.*|\{.*|\.\.\.)$

INTERNAL_HOST:
(?i)\bhttps?://(?:(?:10|127\.0\.0|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.[\d.]+|[\w\-.]+\.(?:internal|corp|lan|intranet|local))(?:[:/\s\"'`)]|$)

TOKENISH (high-entropy candidates):
[A-Za-z0-9+/=_\-]{32,}
```

Note: in the original, `PLACEHOLDER` is tested with `search`, so the plain word `config`, `env`, `none`, `true`, `string` and so on anywhere inside a value makes it a placeholder. `URL_CRED_OK`, `USER_OK` and `DRIVE_OK` are tested with `match` from the start and carry their own `^...$` anchors (or for DRIVE_OK a `$` end); `EMAIL_DOMAIN_OK`, `EMAIL_NOREPLY` and `PLACEHOLDER` are `search`. In user-path and URL patterns `\"` means a plain double quote.

## 4. High-entropy rule (rule 22) step by step

For each TOKENISH match `t` on the line (after rules 1 to 21 found nothing), skip it when any of these holds:

1. It contains more than one `/` after stripping leading and trailing slashes (a path, not a token).
2. It is entirely hex digits (`[0-9a-fA-F]+`, a hash).
3. It lacks any one of: a lowercase letter, an uppercase letter, a digit.
4. PLACEHOLDER (section 3) matches it.
5. It contains more than two `-` characters (a slug or UUID-like name).
6. Its Shannon entropy is below 4.5.

Shannon entropy (bits per character) = minus the sum over each distinct character c of p(c) x log2 p(c), where p(c) is the count of c divided by the length. A 32-character token with all distinct characters scores 5.0; plain words, repeated groups and low-variety strings score far below 4.5. By hand: a value needs roughly 23 or more distinct characters spread fairly evenly to reach 4.5. When in doubt, count the characters and compute; if still doubtful, report it and let the user decide.

Reported as `high-entropy`, label `high-entropy string`, value masked.

## 5. File-name rule (rule 23), tree scan, packages and history

### Private file names

`private-file` applies when the base name (last path component, case-sensitive, shell-style wildcard match where `*` matches any characters and `?` one) matches one of these. Label in brackets.

| Pattern | Label |
|---|---|
| `.env`, `.env.*` | environment file |
| `*.pem`, `*.key` | key file |
| `*.p12`, `*.pfx` | key store |
| `id_rsa`, `id_rsa.*`, `id_ed25519`, `id_ecdsa` | ssh key |
| `credentials.json`, `service-account*.json` | credentials |
| `*.log` | log file |
| `.npmrc`, `.pypirc` | registry credentials |
| `.netrc` | credentials |
| `memory.md` | memory note |
| `progress.md`, `*.progress.md` | progress note |

Total 19 name patterns (the 19 listed in the table). Folder rule: the path starts with, or contains after a `/`, one of `memory/`, `.claude/memory/`, `.claude/progress/`, `logs/` (label `private notes or logs folder`).

Exception (PRIVATE_OK): a base name equal to, or ending with, `.env.example`, `.env.sample` or `.env.template` is never private. Backslashes in paths are read as `/` first.

Allowlist and file names: a private-file finding is suppressed by an allowlist rule whose rule field is `private-file` or `*` and whose glob matches the path; a rule that has a value substring never suppresses a file-name finding (there is no line text to contain it).

Finding fields: file = relative path, line 0, kind = `<label> (must not be published)`, value = the file's base name.

### Tree scan (the working tree)

1. Files to scan: those git would publish: `git -C <root> ls-files -co --exclude-standard -z` (tracked plus untracked and not ignored), provided `<root>` is the top level of a git work tree (compare `git -C <root> rev-parse --show-toplevel` with the folder). Otherwise (not git, or a sub-folder of a repo): every file under the folder, skipping any path with a component `.git`, `node_modules`, `__pycache__`, `.venv`, `venv` or `dist` (built packages are scanned through `--artifacts`), and symlinks and non-files.
2. In both cases skip a path that has a component `.git`, `node_modules`, `__pycache__`, `.venv` or `venv`, symlinks and non-files.
3. For each file: test the file-name rule first (report as above).
4. Skip content larger than 2,000,000 bytes.
5. A `.zip` or `.plugin` file: scan inside it (the package rule below), then go to the next file.
6. A file with a NUL byte in its first 2048 bytes is binary: skip. Otherwise decode as UTF-8 (BOM ignored, bad bytes replaced) and test every line with the line rules (sections 2 to 4). Rule 23 is the only rule applied to a file's name; all other rules to its text. Any text suffix qualifies (this engine does not limit itself to a suffix list).
7. Drop every finding that an allowlist rule allows (section 6).

### Package scan (`.zip`, `.plugin`, nested)

List members (`unzip -l`). Skip directory entries and members with a path component in `.git node_modules __pycache__ .venv venv`. Location is `<package>!<member>`. For each member: file-name rule (kind `<label> (inside package)`); skip members over 2,000,000 bytes; a member ending `.zip` or `.plugin` is opened and scanned the same way, up to two nested levels deep (the member path continues with `!`); otherwise, if not binary (no NUL in the first 2048 bytes), scan its lines. Text findings carry where = the package name (the label of the enclosing package). A file that is not a valid zip is ignored.

Artifacts: for each path given, the file itself; for a folder, every `.zip` and `.plugin` found anywhere under it (symlinks excluded), each labelled by its file name.

### History scan (`--history`)

Run `git -C <repo> log --all -p --no-color --no-ext-diff --format=%x01%h` and walk the output:

1. A line starting with the control character `\x01` begins a commit; the rest is the short hash. Reset the current file.
2. A line `+++ b/<path>` names the current file; `+++ /dev/null` (a deletion) means no file. When a file is named, test the file-name rule once per (rule, file): kind `<label> (committed in history)`, value = base name, where = `commit <hash>`.
3. A line `@@ -a,b +c,d @@` sets the next new-file line number to `c`.
4. A line starting with `+` (and a current file) is an added line: test it with the line rules (text after the `+`); the finding's line number is the tracked new line number; where = `commit <hash>`; then add 1 to the line number. A line starting with a space (context) adds 1 to the line number. Removed (`-`) lines are not scanned.
5. Report each distinct (rule, file, masked value) once across all of history.
6. Apply the allowlist to each finding.

## 6. Allowlist

File `.public-safety-allow` at the scanned root (or the file the user names). One rule per line, `#` starts a whole-line comment, blank lines ignored:

```
<rule>:<path-glob>[:<value-substring>]       e.g.  email:README.md:support@example.org
```

- `<rule>` is a rule id from section 2 or `*` for any rule. The key-format rules `X001` and `X003` of `scan-secrets.md` do not read this file.
- `<path-glob>` uses `*` and `?` (shell wildcard) against the repo-relative path with forward slashes; a glob also matches if it matches only the base name.
- `<value-substring>` (optional; may itself contain `:`, everything after the second colon): the line must contain it. Surrounding spaces on the three fields are trimmed. Lines with fewer than two fields are ignored.
- Only exact false positives belong there; never a real credential (rotate that instead). A missing or unreadable file means no rules.

## 7. Masking (what may appear in a report)

- Most values: the first 4 characters plus `...` when longer than 8 characters, else the first 2 plus `...`.
- password: `<key name>=` plus that mask of the value. key-assignment: same.
- basic-auth: the mask of the credential.
- url-credentials: `<scheme>://` plus the first 2 characters of the user plus `***:***@`.
- email: first 2 characters of the local part plus `***@` plus the domain.
- user-path: the first 3 characters of the matched path plus `...` plus the first 2 characters of the user name plus `***`.
- drive-path: the drive letter plus `:\...` plus the first 2 characters of the folder plus `***`.
- internal-host and the 13 key formats: the mask of the match.
- private-file: the file's base name (it is not secret).

## 8. Gitignore preset and `.env.example` check (used by validator `X009` and `X011`)

Required preset (block written into `.gitignore`, comments excluded from the check):

```
# --- public-safety preset: private data never reaches git ---
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
id_rsa*
id_ed25519*
credentials*.json
service-account*.json
secrets.*
*.log
logs/
memory/
.claude/memory/
.claude/progress/
progress*.md
*.local.md
.claude/settings.local.json
.npmrc
.pypirc
.netrc
private/
# --- end public-safety preset ---
```

There are 24 required lines (every non-empty line that does not start with `#`); a `.gitignore` missing any of them fails `X009`.

`.env.example` check: a variable carries a value when a line matches
`^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*(\S+)` (multi-line mode) and the captured first token does not match `^(<.*>|\$\{.*\}|\"\"|\'\')$`. Names only (`NAME=` with nothing after it on the line, `NAME=<value>`, `NAME=` followed by a `$` and a variable name in braces, `NAME=""`) are fine. Note that the original pattern lets the whitespace after `=` run into the next line, so keep an empty `NAME=` followed by a blank line, a comment, or write `NAME=<...>`.

## 9. Procedure for Claude

1. Decide scope and the allowlist file; read the allowlist.
2. Build the file list (tree scan rules above); apply the file-name rule to every path and every package member.
3. For each rule 1 to 13, Grep the whole file list with its regex. Run lookbehind patterns (email, user-path Unix form, drive-path) with `grep -rnP`/`git grep -nP`.
4. For rules 14 to 22, Grep the broad patterns (BASIC, ASSIGN, URL_CRED, EMAIL, USER_PATH, DRIVE_PATH, INTERNAL_HOST, TOKENISH), then Read each hit line and apply the value filters and the first-match order. Report at most one finding per line.
5. Scan packages and, if asked, history, as described above.
6. Apply the allowlist, mask values, deduplicate, and report through the format in `scan-secrets.md` section 7.
7. Any finding fails the review.

## 10. Example (fake values only)

A person's address at a real company domain in `README.md` line 4 (local part starting `su`) gives `README.md`, 4, `personal e-mail address`, `su***@<that domain>`. A tracked file `config/prod.env` gives `config/prod.env | - | environment file (must not be published) | prod.env`. A Windows path into the `Users` folder for a real account name starting `jd` gives `user-path` with value `C:\...jd***`. The text `https://example.com/path`, `noreply@example.org` and `sk-` followed by fewer than 20 characters are not findings.
