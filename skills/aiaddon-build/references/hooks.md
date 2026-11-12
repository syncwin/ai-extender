# Hooks

Deterministic automation on lifecycle events. Plugin location: `hooks/hooks.json` (merged with manifest `hooks`).

**Compliance first.** The Anthropic directory refuses hooks of any type from non-Verified organizations. Plugins built here ship no hooks by default. If the user asks for a hook, say so plainly: it still works for private and GitHub-marketplace installs, but not in the directory. Offer the compliant method first: put the rule in the skill or command instructions as a recipe step, use `userConfig` with `sensitive: true` for settings and secrets, or a remote MCP over HTTP. Only if the user then chooses a private or GitHub-only release, write the hook, and label it "not directory-compliant" in the plan and README. The technical notes below stay valid for those cases.

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
- **No required runtime (`H008`).** A hook works with plain shell. Python or Node only for optional extras, wrapped so a missing runtime skips silently: `for c in python3 python py; do "$c" -c "" >/dev/null 2>&1 && exec "$c" "${CLAUDE_PLUGIN_ROOT}/<script>.py"; done; exit 0`. Never test with `command -v python3` (the Windows Store stub passes it and then fails). A guard hook (blocks on doubt) is the exception: it needs its runtime, so say so in the README.
- Prefer **exec form** (`command` + `args`) so paths need no quoting; `${user_config.*}` works only there. Shell form: quote `"${CLAUDE_PLUGIN_ROOT}"`, read `$CLAUDE_PLUGIN_OPTION_<KEY>`.
- Exec form (`"command": "python3", "args": [...]`) suits a plugin submitted to Anthropic's directory, but fails loudly where python3 is missing (`H008`); the fallback loop above is the default for everything else. Anthropic's directory reads exactly what runs; a shell launcher with its own variables (`$py`, `$p`) is treated as code assembled at run time and held for a reviewer, and blocks when the plugin sits in a subfolder. Where `python3` is missing (some Windows setups) the hook fails without blocking; say so in the README.
- Scope `matcher` to the tools the hook guards (`WebFetch|WebSearch|mcp__.*<server>.*`), never every tool; warn with exit 2 rather than block unless blocking is the point.
- `if` is best-effort; hard allow/deny belongs in permissions, not hooks.
- All matching hooks run in parallel; keep them fast and idempotent.
- Security: sanitize input, quote variables, reject `..` paths, skip `.env`/`.git`/keys, absolute script paths, no secrets in the file. A guard (blocks or protects) fails closed: on an error or doubt, exit 2. A nag or advisory hook fails open: on its own error, exit 0 (standards §5c).
- Hooks in subagent frontmatter are ignored for plugin subagents.
- Use a hook instead of a skill instruction whenever the behavior must always happen.
