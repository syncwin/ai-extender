# Architecture

## Layout (only confirmed components)

```
<plugin-slug>/
├── .claude-plugin/plugin.json     # manifest (marketplace.json here too if private marketplace)
├── skills/<role-slug>/SKILL.md    # router = <plugin-slug>; + references/ scripts/ assets/
├── agents/*.md   hooks/hooks.json   .mcp.json   commands/ (legacy only)
├── prompts/<title-slug>.json      # Prompt Builder companion prompt (always)
├── README.md  CHANGELOG.md  LICENSE
```

Everything except `plugin.json`/`marketplace.json` sits at plugin root, never inside `.claude-plugin/`. A manifest is optional but always written here. Kebab-case names. No empty folders. No `bin/` if Cowork/claude.ai is a target. A root `CLAUDE.md` is not loaded: instructions belong in skills.

## plugin.json

`name` (kebab-case, = router slug; never starting `claude-`/`anthropic-`, and keep `claude` out of it entirely: brand words go in `displayName`), `displayName`, `version` (`0.0.1`), `description`, `author` {`name`, `email`, `url`}, `license` (SPDX), `keywords`, `homepage`/`repository` only when real, directory listing fields when the plugin will be listed (`documentationUrl`, `supportUrl`, optional `privacyPolicyUrl`, `termsOfServiceUrl`, `icon`; all `https://` or a `./` image path), `metadata` (free-form: `company`, catalog data), `dependencies`, `userConfig` for user-supplied values (use `sensitive: true` for secrets). Unknown top-level keys are stripped; unknown keys inside `userConfig`/`channels`/`lspServers`/`monitors` entries break loading. Component paths start `./`, exist, stay inside the root. `commands`, `agents`, `outputStyles`, `workflows` replace their default folder; `skills` adds; `hooks`/`mcpServers`/`lspServers` merge.

Prefer `userConfig` over text placeholders for values users must supply.

## Router rule

Every plugin has one entry skill named exactly like the plugin. With one skill, that skill is the entry point and does the work: no separate router. With two or more, the entry skill is a router: it detects context, picks a mode, hands off, and holds no task logic, and role skills use the user's acronym prefix if one was chosen (`mt-extractor`), else bare roles (`extractor`). Capability skills stay usable on their own when named directly.

## How many skills

- **Split** when triggers, outputs, or lifecycle differ, or the body would pass ~500 lines even with references.
- **Merge** when they always fire together, share triggers, or one is meaningless alone.
- **Foundation** material used by several skills (naming, standards, scratchpad) lives once as a shared reference, not as a skill.
- Skills are roles (`developer`, `reviewer`), not activities. Progressive disclosure: frontmatter always loaded, body on trigger, references/scripts on demand.

## Choosing the component

| Need | Component |
|---|---|
| Knowledge or a procedure Claude applies | skill |
| Must always happen / block / format automatically | hook |
| External service or data | connector (MCP) |
| Isolated context, restricted tools, parallel or cheaper model | agent |
| Extend another publisher's extension | add-on (own plugin + `dependencies`) |
| User-supplied settings | `userConfig` |

Component support differs by surface (agents, hooks, local MCP, LSP, `bin/` do not load everywhere): check `claude-developer/references/components-extra.md` §Surface support and pick components for the weakest target the user named.

## Shared patterns

- **Knowledge vs execution:** reference material that only informs goes in `references/` (one canonical home per fact, separately labeled by source); execution logic stays in skills.
- **Step controller:** only when users run stages individually; a thin table (option → skill), no task logic, never auto-chains.
- **Stable contract:** state the bare-invocation behavior and skill names others depend on; changing them needs a changelog mapping.
- **Scratchpad** in every skill, agent, and connector task (copy `ai-extender/references/scratchpad.md`).
- **Shared foundation** (efficiency ladder, lean build, security) copied into generated routers/developers per `standards.md` §5.

## Output

Confirmed tree, skill list with one-line roles, draft `plugin.json`, and the companion prompt's fields (3 to 6, per `ai-extender/references/companion-prompt.md` §4). Loop back only if authoring shows a boundary was wrong.
