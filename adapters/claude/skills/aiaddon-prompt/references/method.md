# Prompt craft method

Platform-neutral. Each rule is a synthesis of the vendor guides credited in `sources.md`; where vendors differ, the platform tip lives in `platform-tips.md`.

## Contents

1. Principles - 2. Section set - 3. Tag set - 4. Variables - 5. Tightening rules - 6. Examples - 7. Reasoning and long inputs - 8. Complex tasks - 9. Test and iterate

## 1. Principles

- **State success first.** Know what a good output is (format, length, accuracy bar) before drafting. If it cannot be tested, it is not specific enough.

- **Clear and direct.** The colleague test: someone with no context should be able to follow the prompt. Say what to do, for whom, in what shape.

- **Give the reason.** A rule with its purpose generalizes ("this is read aloud, so no ellipses") better than a bare rule.

- **Positive over negative.** "Write in plain sentences" beats "do not use jargon"; keep a short prohibition list only for hard limits.

- **Match specificity to the model.** Strong reasoning models take goals; smaller or instruction-tuned models need explicit steps and formats.

- **Separate content kinds.** Instructions, context, examples, and input live in distinct delimited blocks so none is mistaken for another.

- **One prompt, one job.** Split unrelated jobs; chain them (section 8).

## 2. Section set

Use only the sections the task needs. Order: stable material first, per-run material last.

| Section | Holds | Skip when |
|---|---|---|
| Role | one line: who the model acts as, and for what audience | the task needs no persona |
| Objective | the single outcome, in one or two sentences | never skip |
| Context | background, definitions, audience, why it matters | nothing beyond the instruction |
| Instructions | numbered when order matters, bullets otherwise; priorities first | never skip |
| Examples | 3 to 5 input/output pairs | format is trivial |
| Output requirements | format, length, order, language, what to leave out | free-form output is fine |
| Validation checklist | the self-check before answering | low-stakes tasks |
| Input | the variable data, in a delimited block, last | no per-run data |

## 3. Tag set

Default tags (consistent, descriptive, lowercase with underscores): `<context>`, `<instructions>`, `<examples>` with `<example>`, `<input>`, `<output_format>`. Add `<document>` with `<source>` for multiple documents. Tags carry no magic; Markdown headings also work. Use tags where content could be confused (pasted text next to instructions), headings elsewhere. Refer to a block by its tag name in the instructions ("using the text in `<input>`").

## 4. Variables

`{{snake_case}}` for anything that changes per use. Name by meaning (`{{audience}}`, not `{{var1}}`). Put each in the block where it belongs; user-supplied bulk text goes inside `<input>`. Every variable is used and listed. Optional variables get a fallback sentence ("If {{notes}} is empty, ignore it").

## 5. Tightening rules

1. Delete: greetings, "please", "make sure to", "it is important that", self-praise ("expert", "world-class") with no effect on the task, restated instructions, rules that describe default behavior.

2. Merge: two rules saying the same thing become one; keep the stronger wording only if the user's intent needs it.

3. Replace vague words with measures: "short" becomes "at most 120 words"; "recent" becomes "from the last 12 months".

4. Keep every real constraint, number, name, and priority order. Emphasis (bold, caps) only on the one or two rules where a miss is costly.

5. Preserve the user's terms for domain concepts.

6. Do not add: no new rules, examples, tone, or checks the user did not ask for. If a gap matters, flag it in the notes, not in the prompt.

7. Final read: remove anything that, if deleted, changes no output.

Existing prompts in Tighten mode keep their order and meaning; headings, lists, and tables for label-value pairs improve structure, and any change that could alter meaning is reported.

## 6. Examples

3 to 5 examples that mirror real inputs, vary enough to avoid copying one pattern, include one edge case, and show the exact output format. Wrap in `<examples>`. Examples outweigh prose: if they conflict with a rule, the examples tend to win, so check them.

## 7. Reasoning and long inputs

- Ask for reasoning on multi-step or judgment tasks ("work through the steps, then give the final answer in <answer>"), unless the model has built-in reasoning that handles it.

- Long documents sit first and the question last. For extraction from long text, quoting the relevant passages before answering helps.

- Say what to do when information is missing: ask once, or mark "not found". Never leave it to a guess.

## 8. Complex tasks

Stages make sense when intermediate results need inspection or each stage needs different wording: generate, review against criteria, refine. Each stage has its own prompt and a defined hand-off format. A research stage is research only, with writing, editing, and optimizing left to a later stage, and a stated outcome for unverifiable claims.

## 9. Test and iterate

Run the prompt on 3 real inputs including one edge case. Compare to the success definition. Change one thing at a time. Re-test after any model change.
