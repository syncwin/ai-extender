# Scoping

Extract answers from the conversation and attached files first; ask only genuine gaps, in one message. Treat attached learnings/checklists as raw material to generalize: flag project-specific details and ask whether they belong.

## Ask (skip anything already known)

1. **Platform target** (first, before any design): Claude Code · Cowork (Paid) · other / not limited. Decides components and packaging. Cowork or "other" → portable skill frontmatter only (works in claude.ai/API upload); Claude Code only → extended fields allowed, still portable by default unless a feature needs them.
2. **Purpose:** the one or two things a user opens it for; who triggers it, when, with which phrases; expected output.
3. **Type and components** (only scaffold confirmed ones): skills · connectors · agents · hooks · commands (legacy) · custom MCP server · add-on for an existing extension · update to an existing one.
4. **Connectors:** service, existing vs custom, auth, which skills use it.
5. **Install method:** manual upload · local/private git marketplace · Cowork `.plugin` (default from the platform answer). Never offer public release.
6. **Naming:** exact required style, else Title Case visible name + kebab-case role slugs. **Acronym:** user's choice or none (standards).
7. **Metadata** (all optional): author, company, contact, license.
8. **Tests:** suggest evals for objectively checkable outputs, skip for subjective ones; user overrides.

## Calibrate language

Match the user's fluency. Explain "frontmatter", "manifest", "MCP" in one clause until they use the terms themselves.

## Confirm

Restate scope in one short block. Ask for confirmation only for real guesses, then continue to `architecture.md`.
