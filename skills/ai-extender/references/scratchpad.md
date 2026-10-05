# Scratchpad Format

Canonical format. Every skill, connector, and plugin emits one after completing its task.

## Rules

- **Standalone task:** emit one scratchpad at the end.
- **Chained workflow:** each stage adds its rows to one running scratchpad; emit it once, at the end of the chain. Never one per stage.
- State the scope on the first line. Omit sections that don't apply (no "N/A").
- Successes: one count or one line. Detail only for failures, flags, and judgment calls.
- Facts only: what was done, not what was intended. No prose, no restating the request.

## Template

```
### Scratchpad: <Visible Name> v<version>
**Scope:** <what was run>

| Area | Result |
|---|---|
| <thing checked/built/changed> | <done / pass / fail + one clause> |

**Changed:** <files or components created/edited, one line each>
**Flags:** <failures, assumptions, unresolved items (omit if none)>
**Next:** <single next action (omit if none)>
```
