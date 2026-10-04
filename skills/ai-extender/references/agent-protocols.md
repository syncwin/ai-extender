# Agent Protocols (platform-neutral)

The logic of the evaluation agents lives here once. Each platform ships a thin agent that loads this protocol and adds only what the platform needs (tool list, model setting, file format). Claude implementations: `agents/claude-grader.md`, `agents/claude-comparator.md`. A future ChatGPT or Gemini adapter gets its own thin file and reuses this text unchanged.

## Contents

1. Grader · 2. Comparator · 3. Adapter contract

## 1. Grader

**Input:** a run directory (outputs, transcript if present) and the eval's `assertions` list.

1. Read the outputs and transcript. Do not run the extension again.
2. For each assertion decide pass or fail from the evidence only. A claim without a matching artifact or quoted output fails.
3. Write `grading.json` in the run directory: `{"expectations":[{"text":"<assertion>","passed":true|false,"evidence":"<short quote or file fact>"}]}`.
4. Add `notes` for any assertion that is vague, trivially always true, or impossible to check; suggest a sharper one.

**Rules:** no leniency for near-misses; no new assertions in the result; evidence under 200 characters each. **Finish:** one-line scratchpad with counts passed/failed and the path written.

## 2. Comparator

**Input:** the task prompt and two outputs labeled A and B. The agent is not told which is new.

1. Read the task prompt and both outputs.
2. Judge on correctness against the task, completeness, adherence to stated requirements, and clarity. Ignore length and style unless the task asks for them.
3. Return the winner (A, B, or tie), two to four concrete reasons citing specifics from each output, and the single change that would most improve the loser.

**Rules:** no assumptions about origin; no hedged verdicts; a tie only if no requirement-level difference exists. **Finish:** one-line scratchpad with the verdict and confidence (high, medium, low).

## 3. Adapter contract

A platform adapter must: read-only access to the run directory (plus write access to it for the grader); no network; the same input and output shapes as above; the platform's own naming prefix (`claude-`, `chatgpt-`, `gemini-`). Adapters never restate the protocol steps beyond a fallback of the output schema.
