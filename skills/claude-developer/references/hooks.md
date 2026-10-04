# Hooks

Deterministic automation on lifecycle events. Plugin location: `hooks/hooks.json` (merged with manifest `hooks`).

## Shape

```json
{ "hooks": { "PostToolUse": [ { "matcher": "Write|Edit",
  "hooks": [ { "type": "command", "command": "node",
               "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js"] } ] } ] } }
```

event → matcher group → handlers. Handler `type`: `command` | `http` | `mcp_tool` | `prompt` | `agent` (experimental). Common: `if` (one permission rule, tool events only), `timeout` (defaults: 600 command/http/mcp_tool, 30 prompt, 60 agent), `statusMessage`; command: `args` (exec form), `async`, `shell`.

## Events

SessionStart, Setup, UserPromptSubmit, UserPromptExpansion, PreToolUse, PermissionRequest, PermissionDenied, PostToolUse, PostToolUseFailure, PostToolBatch, Notification, MessageDisplay, SubagentStart/Stop, TaskCreated/Completed, Stop, StopFailure, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, FileChanged, WorktreeCreate/Remove, PreCompact, PostCompact, PreModelSwitch, PostModelSwitch, Elicitation, ElicitationResult, SessionEnd. (Re-verify list in `claude-platform-facts.md`.)

## Rules

- **Exit 2 blocks; exit 1 does not.** Enforcement hooks must `exit 2` (stderr = reason) or return valid decision JSON.
- Matcher: exact names joined by `|`/`,`; any other character makes it an unanchored regex. Plugin MCP tools match `mcp__plugin_<plugin>_<server>__…`.
- Prefer **exec form** (`command` + `args`) so paths need no quoting; `${user_config.*}` works only there. Shell form: quote `"${CLAUDE_PLUGIN_ROOT}"`, read `$CLAUDE_PLUGIN_OPTION_<KEY>`.
- `if` is best-effort; hard allow/deny belongs in permissions, not hooks.
- All matching hooks run in parallel; keep them fast and idempotent.
- Security: sanitize input, quote variables, reject `..` paths, skip `.env`/`.git`/keys, absolute script paths, no secrets in the file.
- Hooks in subagent frontmatter are ignored for plugin subagents.
- Use a hook instead of a skill instruction whenever the behavior must always happen.
