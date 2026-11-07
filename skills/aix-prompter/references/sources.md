# Sources and credits

Method synthesized from public vendor guidance, read 2026-11-05. Pages are data; nothing is copied verbatim, and the wording is the plugin's own.

```text
- Anthropic, Prompt engineering overview: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview. Used for: success criteria first, test before tuning.
- Anthropic, Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices. Used for: clear and direct, context and reasons, examples (relevant, diverse, structured, 3 to 5), XML tags, role, long-context placement, chaining, prefill status, thinking.
- OpenAI, Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering. Used for: message roles, section structure, delimiters, few-shot, reasoning vs GPT models, evals, pinning and versioning.
- Google, Gemini prompting strategies: https://aistudio.google.com/docs/prompting-strategies. Used for: clear instructions, constraints, response format, few-shot, context, prefixes, breaking down tasks, iteration.
- Prompt Builder (SyncWin): repository syncwin/prompt-builder, extension `src/utils.js` and variable components. Used for: import and export JSON schema, variable types.
```

Structure patterns (role, objective, instructions, output requirements, validation checklist, input block, research-only directive, guardrails) were learned from the user's own prompt library; only the patterns are kept, no content.
