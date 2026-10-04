---
type: llm
---

PASS if it validates first, names the file '<Display Name> v<version>.plugin', uses a zip whose root is the plugin root, and hands over the Prompt Builder companion prompt JSON with the package.
FAIL if it skips validation or uses a different extension.
