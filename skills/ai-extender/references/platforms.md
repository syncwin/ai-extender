# Platform Layers

AI Extender is built as a platform-neutral core plus thin platform layers. Only the Claude layer exists today; the others are a plan, not a promise.

## Contents

1. Layers · 2. Naming · 3. What each layer owns · 4. Adding a platform

## 1. Layers

| Layer | Prefix | Today | Holds |
|---|---|---|---|
| Neutral core | `ai-` | `ai-extender` (router), shared references | routing rules, standards, scratchpad format, agent protocols, platform layering |
| Claude layer | `claude-` | `claude-planner`, `claude-developer`, `claude-maintainer`, `claude-reviewer`, `claude-packager`, agents `claude-grader`, `claude-comparator` | Claude Code and Cowork plugin formats, validators, packaging, Claude docs facts |
| ChatGPT layer | `chatgpt-` | not built | would own ChatGPT's extension formats |
| Gemini layer | `gemini-` | not built | would own Gemini's extension formats |

## 2. Naming

`<prefix>-<role>` for skills and agents, one prefix per layer; the plugin namespace supplies `ai-extender:` so a name never repeats the plugin. Shared files that hold platform facts carry the platform prefix (`claude-platform-facts.md`, `claude-docs-sync.md`); files that hold nothing platform-specific keep no prefix (`standards.md`, `scratchpad.md`, `agent-protocols.md`, this file).

## 3. What each layer owns

- **Neutral core:** which stage runs when (router table), naming and metadata rules that hold everywhere, scratchpad format, agent protocols.
- **Platform layer:** component formats, validators, packagers, surface limits, distribution routes. These are format-bound: the Claude validator checks Claude plugin layout and means nothing for another platform, so it is not reused.
- **Agents:** neutral protocol, one thin adapter per platform (`agent-protocols.md` §3). Separate agents per platform are required only for the adapter, not the logic.

## 4. Adding a platform

1. Verify the platform's extension format from official docs and write `<prefix>-platform-facts.md`.
2. Add `<prefix>-planner|developer|maintainer|reviewer|packager` skills and the thin agents; reuse `standards.md`, `scratchpad.md`, and `agent-protocols.md` as is.
3. Add the platform's rows to the router's route table and extend `evals/` with cases for it.
4. Bump the version (new capability) and record it in the changelog.
