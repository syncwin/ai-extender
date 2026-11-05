# Improvements

Log feedback and ideas here; move to Accepted when approved.

## Inbox
- 2026-11-05 | Versioning: every new app/plugin starts at 0.0.1 with a semantic CHANGELOG (Keep a Changelog); bump slowly (patch/minor) through beta; 1.0.0 only when the owner says so. | User
Format: date · idea · source

- 2026-11-04 · AGENTS.md model routing (Opus plans, Haiku/Sonnet execute) as a shipped default · all plugins (Claude plugins note)

## Accepted

## Done
- 2026-11-05 | Security first (enterprise level): never break existing behaviour (tests + review before merge); secure-by-default foundation for every project: secret scanning, least-privilege tokens, dependency pinning/audit (supply chain), input validation, signed releases, threat model in each brief, Critical/Important security findings block release. | User | Done in 1.0.1
- 2026-11-05 | Packager crashes printing its scratchpad on Windows cp1252 consoles (UnicodeEncodeError on the arrow); reconfigure stdout to UTF-8. Package itself was written. | Claude | Done in 1.0.1
