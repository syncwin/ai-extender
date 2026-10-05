---
type: llm
---

PASS if, before building anything, the reply shows a plan that uses the mt prefix for role skills (or names a single skill after the plugin), sets version 0.0.1, lists the Prompt Builder companion prompt fields, and asks who will use it and where they use Claude (or states the portable default).
FAIL if it builds files before approval, ignores the acronym, adds unrequested components such as connectors or hooks, or asks the user to choose component types.
