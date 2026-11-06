---
type: llm
---

<!-- screen:allow-sample -->
PASS if the reply returns one tightened Markdown prompt that keeps every requirement (fix spelling and grammar, do not change meaning, do not rewrite sentences unless there is a mistake, return only the corrected text with no explanation, keep the original tone) exactly once, keeps the {{text}} variable inside an input block, removes the greetings, politeness, and repeated meaning rule, adds no new requirement, and uses ASCII characters only.
FAIL if any requirement is dropped or weakened, the meaning rule appears twice, a new rule or example is invented, the {{text}} variable is lost, or the reply performs the editing task instead of returning the prompt.
<!-- /screen:allow-sample -->
