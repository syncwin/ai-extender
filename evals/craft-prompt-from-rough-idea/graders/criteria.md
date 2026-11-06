---
type: llm
---

PASS if the reply loads or follows a prompt-building method: it delivers a Markdown prompt in one block with a clear objective, instructions, output format, and an input block holding a variable or placeholder for the complaint email, with XML tags or headings separating instructions from input. It either asks a short batched set of questions with defaults or states its assumptions. The prompt is ASCII only.
FAIL if it writes the reply to a complaint instead of the prompt, builds a plugin or skill, asks more than one round of questions, pads the prompt with filler or praise lines, or uses smart quotes, em dashes, or arrows.
