# Agents (subagents)

Location: `agents/<name>.md`. In `plugin.json`, `agents` takes `.md` file paths only (not directories) and replaces the default scan.

## Frontmatter (camelCase; unknown keys ignored silently)

| Field | Notes |
|---|---|
| `name` (req) | unique, role slug; no `:` and no leading `-` or the file is skipped |
| `description` (req) | when Claude should delegate; add 1 or 2 concrete trigger examples |
| `tools` / `disallowedTools` | least privilege; omit = inherits everything |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, full id, or `inherit` |
| `maxTurns`, `effort`, `color`, `background`, `isolation: worktree`, `memory`, `skills` (preload), `omitClaudeMd` | optional |
| `color` | red, blue, green, yellow, purple, orange, pink, cyan |

**Plugin agents ignore `permissionMode`, `mcpServers`, `hooks`, `initialPrompt`.** Need those → tell the user to copy the agent to `.claude/agents/`, or put the behavior in a skill/hook instead.

## Body = the whole system prompt

The subagent sees only this plus environment basics (not Claude Code's prompt). Write: role (one line), responsibilities, process, output format, stop condition.

## When to add one

Isolated/noisy context, hard tool restriction, parallel work, or a cheaper model for a narrow job. Otherwise a skill is cheaper. One responsibility per agent; end with a scratchpad (`ai-extender/references/scratchpad.md`).

Validate a folder: `claude plugin validate <dir>`.
