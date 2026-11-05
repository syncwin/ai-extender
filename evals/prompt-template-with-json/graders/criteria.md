---
type: llm
---

PASS if the reply produces a prompt with {{variables}} (for example the transcript and optionally a word limit or audience), lists each variable with a field type among Text, Textarea, Radio, Checkbox, or Predefined, preserves the decisions, action items with owners, open questions, and under-200-words requirements, and either shows JSON with top-level prompts and metadata (format prompt-builder-plain, version 2.0) or runs the bundled export script, and tells the user to import it in Prompt Builder. Text is ASCII only with no HTML entities such as &#x27;.
FAIL if a requirement is lost, a variable is used but not defined, the JSON contains HTML entities or non-ASCII characters, or the reply summarizes a transcript instead of building the prompt.
