# Improvements

Log feedback and ideas here; move to Accepted when approved.

## Inbox
- 2026-11-05 | Versioning: every new app/plugin starts at 0.0.1 with a semantic CHANGELOG (Keep a Changelog); bump slowly (patch/minor) through beta; 1.0.0 only when the owner says so. | User
- 2026-11-11 | Directory policy (non-Verified orgs) refuses: any hook (all types, LOCAL_CODE_HOOK_COMMAND); any file not md/txt/json/yaml/png/jpeg/gif/webp/ico, or starting with #!, or a package-manager config, or non-UTF-8/NUL (LOCAL_CODE_FILE_TYPE; .py/.svg/.tmpl/CODEOWNERS/.public-safety-allow hit it); frontmatter keys outside the allowed list (LOCAL_CODE_FRONTMATTER_KEY; evals/*.md and agent model/color/tools/metadata suspected). Add a "directory edition" build (no hooks, scripts or evals; scripts become instructions) and make validate_extension.py fail on these three for community submissions. | Directory review of v0.1.0 fa89fba | Claude
- 2026-11-11 | Policy hold MCP_FORWARDS_CREDENTIAL_ENV is a false positive from validate_extension.py's own env-read regexes (lines 428, 663); keep regex text out of shipped files or build it from parts. RUNTIME_FETCH_EXEC (10 files) is docs plus the validator pattern: no action. UNREAD_ASSET_REFERENCED: CHANGELOG, distribution-routes.md, plugin.json mention icon files. | Directory review | Claude
Format: date · idea · source

- 2026-11-04 · AGENTS.md model routing (Opus plans, Haiku/Sonnet execute) as a shipped default · all plugins (Claude plugins note)

## Accepted

## Done
- 2026-11-05 | Security first (enterprise level): never break existing behaviour (tests + review before merge); secure-by-default foundation for every project: secret scanning, least-privilege tokens, dependency pinning/audit (supply chain), input validation, signed releases, threat model in each brief, Critical/Important security findings block release. | User | Done in 1.0.1
- 2026-11-05 | Packager crashes printing its scratchpad on Windows cp1252 consoles (UnicodeEncodeError on the arrow); reconfigure stdout to UTF-8. Package itself was written. | Claude | Done in 1.0.1
