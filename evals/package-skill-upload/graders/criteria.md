---
type: llm
---

PASS if it validates the skill first, produces '<Display Name> v<version>.zip' with the skill folder as the top-level entry (for example 'Notes Helper v0.1.0.zip'), and hands over the Prompt Builder companion prompt JSON with the package.
FAIL if it skips validation, uses a different file name or extension, or changes what the skill does.
