# Platform tips

The core method works everywhere. Apply these only when the target model is known. Checked 2026-11-05 against the official pages in `sources.md`; re-check before relying on a detail.

## Claude (Anthropic)

- XML tags are the native way to separate instructions, context, examples, and input; keep names consistent.

- Put long documents at the top and the question at the end; the docs report better answers with the query last.

- A role in the system prompt focuses tone; one sentence is enough.

- Prefilling the start of the reply is no longer supported on current models (it returns an error on the newest ones). Use direct instructions ("respond directly, no preamble"), tags, or structured output instead.

- With built-in thinking on, do not ask the model to write out its reasoning in tags; let thinking work. Manual step-by-step prompting is a fallback when thinking is off.

- Explicit prompt chaining is useful for inspectable pipelines (draft, review, refine); otherwise the model handles multi-step work internally.

## OpenAI (GPT and reasoning models)

- Developer-level messages hold rules and user messages hold input; developer-level text takes priority.

- Structure as identity, instructions, examples, context. Markdown headers and lists separate sections; XML tags mark where supporting content begins and ends.

- Reasoning models take high-level goals; GPT models need precise, explicit instructions.

- Put reusable content first and per-request context last to benefit from prompt caching.

- Pin production to a model snapshot, keep prompts in version control, and re-run evals on every change.

## Google (Gemini)

- Few-shot examples are generally recommended over zero-shot; keep their format consistent and avoid so many that the model overfits.

- Completion prefixes (start the output and let the model continue) are supported for shaping format.

- Supply reference material as context so answers come from it; tune temperature and output length; enable grounding or code execution when facts or math matter.

- Split complex work into chained or parallel prompts.

## Local and smaller models

- Be more literal: numbered steps, one task per prompt, the exact output format with an example.

- Keep the prompt short; long context degrades small models first.

## Chat tools with forms (Prompt Builder)

Variables become form fields. Choose the field type by input: `Text` (one line), `Textarea` (long), `Radio` (pick one), `Checkbox` (pick several), `Predefined` (a toggle that inserts fixed text). Rules and export: `SKILL.md` and `aix/references/companion-prompt.md`.
