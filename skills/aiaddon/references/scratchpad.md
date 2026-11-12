# Scratchpad Format

Canonical format. Every skill, connector, and plugin emits one after completing its task.

## Rules

- **Standalone task:** emit one scratchpad at the end.
- **Chained workflow:** each stage adds its rows to one running scratchpad; emit it once, at the end of the chain. Never one per stage.
- State the scope on the first line. Omit sections that don't apply (no "N/A").
- Successes: one count or one line. Detail only for failures, flags, and judgment calls.
- Facts only: what was done, not what was intended. No prose, no restating the request.
- **Request ledger first.** One row per individual request the user made during the task: split compound asks, include requests added mid-task, questions asked, and anything declined or deferred. Nothing is left out, so the user sees what was done and what is still open.
  - **Request:** what they asked for, in a few of their own words.
  - **Status:** one of `done`, `partly done`, `in progress`, `failed`, `not started`, `needs you`.
  - **Context:** one clause the user needs to understand the outcome: the result, the blocker, or what is left. No filler.

## Template

```
### Scratchpad: <Visible Name> v<version>
**Scope:** <what was run>

| # | Request | Status | Context |
|---|---|---|---|
| 1 | <one request, in the user's words> | <done / partly done / in progress / failed / not started / needs you> | <result, blocker, or what's left> |

| Area | Result |
|---|---|
| <thing checked/built/changed> | <done / pass / fail + one clause> |

**Changed:** <files or components created/edited, one line each>
**Flags:** <failures, assumptions, unresolved items (omit if none)>
**Next:** <single next action (omit if none)>
```
