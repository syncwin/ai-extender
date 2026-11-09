# Skills

A skill is a folder with `SKILL.md` (+ optional `references/`, `scripts/`, `assets/`). Location in a plugin: `skills/<name>/`.

## Frontmatter

Keep to the **portable set** so the skill works in Claude Code, claude.ai upload, and the API: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Extra keys (`argument-hint`, `model`, `context`, …) are fine in Claude Code plugin skills but hard-fail on upload. Use them only when the user confirms Claude-Code-only.

| Field | Rule |
|---|---|
| `name` | role slug, kebab-case, ≤64, equals folder; platform prefixes per standards §1 |
| `description` | trigger first ("Use when...", real phrases users type), then what; ≤300 chars recommended (`S021`, `S022`); combined with `when_to_use` it is cut at 1,536 chars; ≤1,024 for API |
| `metadata` | `author`, `company`, `version` (free-form map) |
| `license` | SPDX |

## Body

- Under 500 lines (`S008`). The body stays in context after load: every line is a recurring cost. State what to do, not narration. Put the non-negotiable rules in the first ~30 lines; a rule at line 400 is followed partially. Keep must-rules to 10 or fewer, each checkable.
- **Self-contained:** a skill reads nothing outside its own folder (`S023`; no `../`, no sibling skill's files): it must work shipped alone as `<skill>.zip` or via `npx skills add`. Needed by two skills: copy it into each (`sync_shared.py`).
- Put detail in `references/`, link each from the body with when to read it. Files >100 lines get a contents list.
- Deterministic or repeated work goes in `scripts/` (executed, not loaded). If test runs show the agent re-writing the same helper, bundle it.
- Explain why behind non-obvious rules; reserve MUST for true hard stops.
- Reference bundled files with `${CLAUDE_SKILL_DIR}` (skill folder) or `${CLAUDE_PLUGIN_ROOT}` (plugin root). Claude-Code-only features (`!`cmd`` injection, `$ARGUMENTS`, `context: fork`) don't run in claude.ai/API.

## Control (Claude Code)

- Side-effect workflows: `disable-model-invocation: true` (user-only).
- Background knowledge: `user-invocable: false`.
- Pre-approve exact commands: `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)` (grant clears next message).
- Isolation or cost: `context: fork` with `agent`, or `model`/`effort` overrides.

## Authoring rules from Anthropic's guidance

- **Concise:** add only what Claude doesn't already know; justify every paragraph's tokens.
- **Degrees of freedom:** high (text heuristics) when many approaches work; medium (templates/parameterized scripts) when a preferred pattern exists; low (exact script, no flags) for fragile steps like migrations.
- References one level deep from SKILL.md; contents list on files >100 lines (>300 hard flag in the validator).
- Complex workflows: numbered steps plus a copyable checklist; validate-fix-repeat loops; for batch or destructive work use **plan → validate plan with a script → execute → verify**, with verbose validator errors that name the fix.
- One default per decision, one escape hatch; consistent terminology; no dates ("before August 2025"); forward-slash paths; scripts handle errors themselves and document every constant.
- Say whether Claude should *run* a script or *read* it; name files by content (`form_validation_rules.md`).
- **Scripts are optional helpers.** Every skill that runs a script says what Claude does when it cannot run (no Python/Node, blocked, errors): do the step by hand from the stated rules and say the check was skipped. Never make a required step depend on a runtime.
- Test with every model that will use it (Haiku needs more guidance, Opus less).

## Descriptions that trigger

Under-triggering is the common failure. Include the real phrases users type, adjacent synonyms, and the situations (not just the noun). Test with should/shouldn't-trigger prompts (`testing.md`).

## Workflow → skill

Extract the actual steps, tools, corrections, and output shape from the conversation; generalize names and one-off values (flag each to the user); then build as above.

## Domain variants

One skill covering several frameworks: body routes by variant to `references/<variant>.md`; shared setup stated once.

End every skill with a scratchpad step (`aix/references/scratchpad.md`).
