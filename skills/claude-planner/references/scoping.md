# Scoping

Extract answers from the conversation and attached files first; ask only genuine gaps, in one message, in plain words. Treat attached learnings/checklists as raw material to generalize: flag project-specific details and ask whether they belong.

## Ask (skip anything already known)

1. **Who uses it and where** (first, before any design): just me · my team · my whole organization · anyone. Then the surface: Claude Code · Cowork · claude.ai chat · not sure. "Not sure" → portable skill frontmatter and a `.plugin` that loads everywhere. Cowork, chat, or "not sure" → portable frontmatter only (works in claude.ai/API upload); Claude Code only → extended fields allowed, still portable by default unless a feature needs them.
2. **Purpose:** the one or two things a user opens it for; who triggers it, when, with which phrases; expected output.
3. **Type and components** (decide yourself, then confirm; only scaffold confirmed ones): skills · connectors · agents · hooks · commands (legacy) · custom MCP server · add-on for an existing extension · update to an existing one.
4. **Connectors:** service, existing vs custom, auth, which skills use it.
5. **Install method:** derived from answer 1 (table below). Never offer public release.
6. **Naming:** exact required style, else Title Case visible name + kebab-case role slugs. **Acronym:** user's choice or none (standards).
7. **Metadata** (all optional): author, company, contact, license.
8. **Tests:** suggest evals for objectively checkable outputs, skip for subjective ones; user overrides.

## Business use

For a team, company, or client process, also settle (ask only what isn't known):

| Who uses it | Default delivery |
|---|---|
| Just me | `.plugin` upload (Cowork / claude.ai) or a local folder (Claude Code) |
| My team | `.plugin` file to share, or a private git marketplace if they use Claude Code |
| Whole organization | Owner adds it in Organization settings > Plugins & skills; Claude Code fleets via managed settings (`claude-packager/references/distribution-routes.md` §6) |

- **Company knowledge:** rules, templates, tone, and checklists the business already has become `references/` files, not hard-coded prose. Ask for the source documents; never invent policy.
- **Variable values** (team names, URLs, account IDs): `userConfig`, so one build serves every user.
- **Data:** name every system it reads from or writes to; anything private stays out of the files and goes through a connector or `userConfig` with `sensitive: true`.
- **Approvals:** any step that sends, deletes, or publishes asks first.

## Calibrate language

Match the user's fluency. Explain "frontmatter", "manifest", "MCP" in one clause until they use the terms themselves. With a non-technical user, describe the plan by what it does ("a skill that reads your notes and writes a task list"), not by files.

## Confirm

Restate scope in one short block. Ask for confirmation only for real guesses, then continue to `architecture.md`.
