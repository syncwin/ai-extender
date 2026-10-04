# Platform Facts (verified 2026-10-01)

Distilled from official docs. Load only the section needed. Facts drift: re-verify via `claude-docs-sync.md` before relying on version-specific details, and cite the page when it matters.

## Plugin manifest (code.claude.com/docs/en/plugins-reference; verified 2026-10-01)
- Manifest `.claude-plugin/plugin.json` is optional; only `name` required (kebab-case; no spaces, @, :, path seps). Components namespaced `plugin:component`.
- Fields: $schema, name, displayName (UI name; any casing; marketplace entry displayName overrides), version (string, pins version; manifest overrides entry), description, author{name required,email,url}, homepage (must parse as URL), repository, license (SPDX), keywords[], metadata (free-form, v2.1.222+), defaultEnabled, dependencies[], settings{agent,subagentStatusLine only}, userConfig, channels, skills, commands, agents, hooks, mcpServers, lspServers, outputStyles, workflows, experimental{themes,monitors,evals}.
- Unrecognized top-level key: stripped + warning. Strict objects (userConfig options, channels, lspServers, monitors) reject unknown keys => plugin won't load.
- Validate: `claude plugin validate ./dir` (`--strict` makes warnings fail). Also checks .mcp.json entries (v2.1.281+).
- Paths: relative to plugin root, must start `./` (skills also accepts "." ), must exist and stay inside root (no `..`).
- Combine: commands, agents, outputStyles, workflows, themes, monitors REPLACE default dir; skills ADDS to default skills/; hooks, mcpServers, lspServers MERGE with hooks/hooks.json, .mcp.json, .lsp.json.
- agents: `.md` files only (no directories). skills entries: directories. commands: path|array|object map{source|content, description, argumentHint, model, allowedTools}.
- userConfig: keys letters/digits/_; option fields type(string|number|boolean|directory|file), title, description (all required), required, default, options (v2.1.271+), multiple, sensitive (secure storage), min/max. Reference `${user_config.KEY}` (MCP/LSP config, exec-form hook args, skill/agent content non-sensitive only) or env `CLAUDE_PLUGIN_OPTION_<KEY>` in hooks. Not allowed in shell-form hook commands, monitor commands, MCP headersHelper.
- Env vars: ${CLAUDE_PLUGIN_ROOT} (changes on update; no state), ${CLAUDE_PLUGIN_DATA} (persists), ${CLAUDE_PROJECT_DIR}. Not in Bash tool env; in skill/command/agent body they substitute inline.
- Standard layout: skills/, commands/ (prefer skills), agents/, hooks/hooks.json, .mcp.json, .lsp.json, output-styles/, workflows/, themes/, monitors/monitors.json, bin/ (claude.ai and Cowork DON'T install plugins containing bin/), settings.json. Root CLAUDE.md is NOT loaded (validate warns) -> put instructions in a skill.
- Plugin with SKILL.md at root and no skills/ loads as a single skill.
## Marketplace (plugin-marketplaces)
- `.claude-plugin/marketplace.json`: required name, owner{name}, plugins[]; entry needs name + source. Source: relative path ("./plugins/x"), github{repo}, git-subdir{url,path}, url, archive(zip https), npm, command. Pin with ref/sha.
- Entry name must equal manifest name. Relative paths from marketplace root, no `..`. Reserved marketplace names (e.g. claude-plugins-official) rejected on add.
- Test: `claude plugin marketplace add ./dir`; `claude plugin install name@marketplace`; `claude plugin list`; `claude plugin details name`; `/reload-plugins`; `claude plugin marketplace remove`.
- Sharing w/o marketplace: send dir or zip. Submit to Anthropic's directory for public.
## Skills (code.claude.com/docs/en/skills; verified 2026-10-01)
- All frontmatter optional; `description` recommended. Fields: name (defaults dir name), description + when_to_use (combined truncated 1,536 chars in listing; key use case first), argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort (low|medium|high|xhigh|max), context (fork), agent, background, hooks, paths, shell, metadata (free-form map; don't reuse field names), license, compatibility (<=500 chars). Unknown fields ignored silently in Claude Code.
- **claude.ai uploads, Skills API, package_skill.py accept ONLY: name, description, license, compatibility, metadata, allowed-tools.** Any other key = hard error. Plugin skills in Claude Code accept all.
- Frontmatter read only if opening `---` is first line. Bad YAML => skill loads with no fields.
- Plugin skill command = /plugin:name (frontmatter name replaces dir name; prefix not doubled v2.1.246+). Reserved folder names: `synced`, `anthropic-skills` (outside plugin).
- Substitutions: $ARGUMENTS, $ARGUMENTS[N], $N, $name, ${CLAUDE_SESSION_ID}, ${CLAUDE_EFFORT}, ${CLAUDE_SKILL_DIR}, ${CLAUDE_PROJECT_DIR}, ${CLAUDE_PLUGIN_ROOT}, ${CLAUDE_PLUGIN_DATA} (plugin skills). Same vars work in allowed-tools Bash rules: `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)`.
- SKILL.md < 500 lines; body stays in context after load (recurring token cost); content persists; allowed-tools grant clears next message; post-compaction keeps first 5,000 tokens/skill, 25,000 total.
- Invocation: default both; disable-model-invocation:true = user only (description not in context); user-invocable:false = Claude only.
- Dynamic context: !`cmd` and ```! blocks; context: fork runs in subagent; deny skills via permission rules; skillOverrides.
- Evaluate: baseline comparison with/without skill in fresh sessions; `claude plugin eval` (plugin skills; with vs without plugin; graders; nonzero exit below threshold; evals/ dir, experimental.evals); skill-creator plugin format evals/evals.json; description tuning with should/shouldn't-trigger prompts. Formats not interchangeable.
## Subagents (code.claude.com/docs/en/sub-agents)
- `agents/*.md` frontmatter: name (required; no ':' or leading '-'), description (required), tools, disallowedTools, model (sonnet|opus|haiku|fable|full id|inherit), permissionMode, maxTurns, skills, mcpServers, hooks, memory (user|project|local), background, omitClaudeMd, effort, isolation (worktree), color (red|blue|green|yellow|purple|orange|pink|cyan), initialPrompt, experimental.cacheTtl. camelCase; unknown ignored.
- **Plugin subagents ignore permissionMode, mcpServers, hooks, initialPrompt.** Priority: managed > --agents > project > user > plugin (lowest).
- Files w/o name treated as docs; bad YAML skipped. Validate dir: `claude plugin validate .claude/agents`. Body = system prompt only (no Claude Code prompt).
## Hooks (code.claude.com/docs/en/hooks; verified 2026-10-01)
- 3 nesting levels: event -> matcher group -> handlers. Plugin hooks: `hooks/hooks.json` (merged with manifest `hooks`). Also settings files, skill/subagent frontmatter (plugin subagents ignore hooks).
- Events: SessionStart, Setup, UserPromptSubmit, UserPromptExpansion, PreToolUse, PermissionRequest, PermissionDenied, PostToolUse, PostToolUseFailure, PostToolBatch, Notification, MessageDisplay, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, Stop, StopFailure, TeammateIdle, InstructionsLoaded, ConfigChange, CwdChanged, DirectoryAdded, FileChanged, WorktreeCreate, WorktreeRemove, PreCompact, PostCompact, PreModelSwitch, PostModelSwitch, Elicitation, ElicitationResult, SessionEnd.
- Handler types: command, http, mcp_tool, prompt, agent (experimental). Common: type, if (one permission rule, tool events only), timeout (600 cmd/http/mcp; 30 prompt; 60 agent), statusMessage, once (skill frontmatter only). Command: command, args (exec form, no shell), async, asyncRewake, shell (bash|powershell).
- Matcher: "*"/""/omitted = all; letters/digits/_/-/space/,/| = exact list; otherwise unanchored JS regex. MCP tools: mcp__server__tool; plugin servers: mcp__plugin_<plugin>_<server>__tool.
- Exit 0 = success (JSON stdout parsed if starts { ends }); **exit 2 = block** (stderr is reason); any other exit (incl. 1) = non-blocking error. `if` is best-effort; use permissions to enforce hard allow/deny.
- Security: validate/sanitize input, quote vars, block path traversal, absolute paths (${CLAUDE_PLUGIN_ROOT}), skip .env/.git/keys. All matching hooks run in parallel.
- Exec form preferred for paths: {"type":"command","command":"node","args":["${CLAUDE_PLUGIN_ROOT}/scripts/x.js"]}. ${user_config.*} only in exec form; shell form reads $CLAUDE_PLUGIN_OPTION_<KEY>.
## MCP (code.claude.com/docs/en/mcp)
- Plugin MCP: `.mcp.json` at root or inline `mcpServers`; starts on enable. Transports stdio/http/sse/ws. Substitution in stdio command/args/env; http/sse/ws url/headers/headersHelper.
- Env expansion `${VAR}` and `${VAR:-default}` in command,args,env,url,headers. Unset var w/o default => warning, literal text. Credential vars (ANTHROPIC_API_KEY, AWS_*, NPM_TOKEN, HTTPS_PROXY...) read as EMPTY in remote url/headers; copy to own-named var.
- Tool names: `mcp__plugin_<plugin>_<server>__<tool>` (non [A-Za-z0-9_-] -> _). Use in allowed-tools, agent tools, hook matchers. Server scoped name `plugin:<plugin>:<server>`.
- Scopes (non-plugin): local (default), project (.mcp.json, needs approval), user. Official helper: `mcp-server-dev` plugin (claude-plugins-official). Build guides: MCP server guide; Claude connector building docs (auth, testing, Directory submission). Prompt-injection risk from servers fetching external content.
## Agent Skills spec / API constraints (platform docs; re-verify)
- Upload/API skill `name`: lowercase letters, numbers, hyphens; ≤64 chars; no XML tags; docs bar the words `claude` and `anthropic`. `description`: non-empty, ≤1024 chars on the API.
- Upload allowed keys: name, description, license, compatibility, metadata, allowed-tools. Keep all skills within that set so they work everywhere.
- Claude Code plugin skills accept the wider field set; the `claude`-in-name bar is not documented on the Claude Code skills page. *(Project decision: platform-neutral components use `ai-`, Claude-specific ones `claude-`; the `claude-` skill names are therefore rejected by an individual upload to claude.ai/API and are verified only as plugin components.)*
## Cowork (from the installed Cowork plugin tooling)
- Cowork mounts plugins under `mnt/.local-plugins` / `mnt/.plugins`. A `.plugin` file is a zip of the plugin directory contents (root = plugin root). Plugins containing `bin/` are not installed by claude.ai/Cowork.

## Additions 2026-10-01 (platform.claude.com Agent Skills; github.com/anthropics/mcpb)
- Upload/API skill `name` bars `claude`/`anthropic`; best-practices page names `claude-tools` as an example to avoid. Descriptions ≤1,024. Gerund names recommended, noun/action acceptable. References one level deep; contents list for files >100 lines; SKILL.md <500 lines.
- Surfaces don't sync: claude.ai zip upload (individual), API `/v1/skills` (workspace-wide, code-execution container, no network/pip), Claude Code folders `~/.claude/skills`, `.claude/skills`.
- Skill bodies reference MCP tools as `ServerName:tool_name`.
- MCPB: zip with `manifest.json` (spec 0.3; `uv` server type needs 0.4), types node/python/binary/uv, `user_config`, `privacy_policies` required for external services; CLI `@anthropic-ai/mcpb` (`mcpb init`, `mcpb pack`). Plugins may reference `.mcpb`/`.dxt` in `mcpServers`.
- Plugin runtime components verified: LSP (`.lsp.json`), output styles, monitors (experimental), `bin/` (not installed by claude.ai/Cowork), plugin `settings.json` (only `agent`, `subagentStatusLine`), channels. Theme and workflow schemas: see the 2026-10-02 and 2026-10-03 additions.

## Additions 2026-10-02 (plugins/components, workflows, publish, plugin-evals, plugins/org, platform-support, settings, Agent SDK skills)
- Surface support table, themes/workflows formats, mods: `claude-developer/references/components-extra.md`. Distribution routes, directory, tags/renames, organization policy keys: `claude-packager/references/distribution-routes.md`. Eval format: `claude-developer/references/testing.md`.
- `claude plugin validate --strict`, `claude plugin eval` (needs Claude Code ≥2.1.269, git ≥2.31), `claude plugin tag` (`{name}--v{version}`), `--plugin-dir`, `--plugin-url` (zip), `claude plugin update`.
- Plugin agent files may sit in `agents/` subfolders (scoped `plugin:folder:agent`); supported plugin-agent frontmatter: name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, omitClaudeMd, isolation (worktree), color, experimental.cacheTtl.
- `.mcp.json` servers: `/mcp` shows `plugin:<plugin>:<server>`; validate checks `.mcp.json` from v2.1.281; `.lsp.json` is NOT read by validate (a bad entry skips the whole file at load).
- Settings precedence (highest first): managed, command line, project local, shared project, user. Lists merge. `permissions.defaultMode` auto/bypassPermissions ignored from project files.
- Agent SDK: skills are filesystem artifacts (`.claude/skills/...`), loaded per `settingSources`/`setting_sources` (include `user`/`project`), scoped with the `skills` option (`"all"`, names, `[]`; `plugin:skill` for plugin skills); `plugins` option loads from a path; `/<name>` dispatch works regardless of `skills`.

## Additions 2026-10-03 (mods, themes, directory)
- Mods (Claude Code v2.1.287+): `hooks/hooks.json` `modules` (one path), module exports `register(on, options)`; details in `claude-developer/references/mods.md`. Mods run with Claude Code's machine access.
- Themes (v2.1.118+): `{name, base, overrides}`; selection stored as `custom:<slug>`; plugins ship themes in `themes/`. Official terminal-config page not fetched: secondary sources only.
- Directory: portal at claude.ai/directory/manage, Plugin bundle, Validate then scan; blocking and held rules in `claude-packager/references/directory-checklist.md`.
- Component naming: every component is `<plugin>:<name>`; a skill named like its plugin shows as `/<plugin>`.
