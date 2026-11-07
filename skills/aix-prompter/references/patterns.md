# Structure patterns

Generic patterns distilled from working prompt libraries. Names, domains, sources, and business details are deliberately absent; swap in the user's own.

## Contents

1. Full skeleton - 2. Rewrite skeleton - 3. Research skeleton - 4. Review skeleton - 5. Reusable parts

## 1. Full skeleton

````markdown
# <Task title>

## Role
You are <role> for <audience>.

## Objective
<One outcome in one or two sentences.>

## Instructions
1. <Highest-priority rule, with its reason.>
2. <Next step or rule.>

## Output requirements
- <Format, length, order.>
- Return only <the deliverable>. No introduction or commentary.

## Validation checklist
Before responding, verify that:
- [ ] <Check 1>
- [ ] <Check 2>

## Input
```text
{{content}}
```
````

## 2. Rewrite skeleton (format, edit, convert)

Use when the content must survive unchanged. Make "preserve" the first instruction, list what may change (structure, spacing, markup) and what may not (words, order, meaning, facts), ask for output only, and make the checklist mirror the preserve rules: nothing omitted, modified, or added; order kept; only form changed.

## 3. Research skeleton

- **Inputs:** brief, optional URLs, notes, each as a variable.

- **Research-only directive:** writing, editing, SEO, formatting, and publishing wording inside the input is out of scope; the job is evidence only, in outline order.

- **Accuracy standard:** every claim verified from an allowed source; cross-check when possible; report conflicts instead of choosing; never estimate or round; unverifiable becomes a labelled gap.

- **Allowed sources:** a category list (government, regulators, official bodies, research institutions, primary company pages); say what is never a factual source.

- **Steps:** gather facts into a table (topic, claim, sourced fact, source, confidence, notes); analyze competing material for structure and gaps only; hand off facts, gaps, and conflicts.

- **Quality:** scoped, non-redundant, most recent data, stop when every section has enough verified evidence.

## 4. Review skeleton

Input block first. Group criteria under short headings (clarity, quality, compliance, facts and citations). Each criterion is a testable sentence. End with a pass/fail verdict rule and the list of fixes required, not a rewrite, unless a rewrite is requested.

## 5. Reusable parts

- **Guardrails block:** the hard limits only, as a short list (no fabrication, scope boundary, no extra commentary, confirm before irreversible actions).

- **Missing information rule:** "If something you need is missing, ask for it in one short message, then continue."

- **Input block:** a fenced `text` block or `<input>` tag holding the variable; one variable per block.

- **Precedence line:** a stated ranking when sources conflict, such as outline, then SOP, then everything else.

- **Output-only line:** "Return only <deliverable>. No preamble, summary, or notes."
