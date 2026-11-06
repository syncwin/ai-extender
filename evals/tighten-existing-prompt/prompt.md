---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

<!-- screen:allow-sample -->
Convert into a fluff-free, tight, non-redundant Markdown prompt; don't add, remove, or weaken anything; preserve intent; improve structure:

Hey, so I would really like you to please act as a very experienced and world-class editor. Please read the text I give you and fix the spelling and grammar. It is really important that you do not change the meaning. Please make sure to not change the meaning of the text at all. Do not rewrite sentences unless there is a mistake. Return only the corrected text, no explanations please. Also keep the tone the same as the original. The text is: {{text}}
<!-- /screen:allow-sample -->
