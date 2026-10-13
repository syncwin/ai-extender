---
type: llm
---

PASS if, before building anything, the reply shows a plan that uses the mt prefix for role skills (or names a single skill after the plugin), sets version 0.0.1, lists the Prompt Builder companion prompt fields, and asks who will use it and where they use Claude (or states the portable default).
Listing Composio as the default connector, or saying it is left out, is expected and is not an unrequested component; the same holds for the injection guardrail hook that comes with a connector.
FAIL if it builds files before approval, ignores the acronym, adds other unrequested components such as hooks, agents, or connectors beyond Composio, or asks the user to choose component types.
