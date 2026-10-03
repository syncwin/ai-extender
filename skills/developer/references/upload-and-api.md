# Skills Outside Plugins: Surfaces and Constraints

Verified against platform.claude.com Agent Skills docs and code.claude.com Agent SDK skills docs, 2026-10-02. **Skills do not sync across surfaces**: install separately on each.

| Surface | How | Scope | Constraints |
|---|---|---|---|
| Claude Code | folder in `~/.claude/skills/` (personal) or `.claude/skills/` (project, commit it); or via a plugin | personal / project / plugin | full network, any frontmatter |
| claude.ai | zip upload, Settings → Features (Pro, Max, Team, Enterprise; code execution on) | individual user only; no org-wide admin distribution | network varies by user/admin settings; portable frontmatter only |
| Claude API | `/v1/skills` endpoints; use via `container` with the code execution tool and a `skill_id` | workspace-wide | **no network, no runtime package install**; portable frontmatter only |
| Agent SDK | filesystem skills at `.claude/skills/`; set `settingSources` to include `user`/`project`; scope with the `skills` option; `plugins` option loads a plugin path | per application | no programmatic skill registration |
| Cowork | plugin `.plugin` | per `packager/references/cowork.md` | no `bin/` |

## Hard limits (all upload surfaces)

- `name`: ≤64, lowercase letters/numbers/hyphens, no XML tags, **no `claude` or `anthropic`** (the best-practices page lists `claude-tools` as a name to avoid).
- `description`: non-empty, ≤1,024 chars, no XML tags.
- SKILL.md body <500 lines; reference files linked **one level deep from SKILL.md** (nested links get partial reads); contents list on references >100 lines.
- Forward-slash paths only. List needed packages in the skill; on the API they must already be installed.
- Use skills only from trusted sources; audit bundled scripts. Enterprise content scanning covers claude.ai/Cowork uploads, not API/Console.

## Zip for upload

`python ${CLAUDE_SKILL_DIR}/../packager/scripts/package_extension.py <skill-dir> --format zip --target upload`. The skill folder is the zip's top-level entry.

## This builder's naming

This plugin's slugs contain no reserved word (`claude` appears only in the display name). Its role skills are bare (`planner`, `developer`, ...) because the plugin namespace supplies the context; a skill uploaded on its own loses that namespace, so give it a descriptive or prefixed name first. Extensions built for users follow the user's acronym (or none) and must pass `--target upload` before individual skill upload.
