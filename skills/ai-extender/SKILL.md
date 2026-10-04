---
name: ai-extender
description: >
  Entry point and router for AI Extender for Claude. Use whenever someone wants to build, update, audit, version,
  or package a Claude plugin, skill, connector, agent, hook, MCP server, or add-on, including internal tools for a
  team or business. Triggers: "build me a plugin", "make me a skill", "add a connector", "create an agent", "turn
  this workflow into a Claude plugin or skill", "automate our process for my team", "make Claude check every
  document against our rules", "update my plugin", "audit my extension", "bump the version", "package this for
  Cowork", and mentions of /skill-creator, /create-cowork-plugin, /cowork-plugin-customizer. Load first; routes only.
license: MIT
metadata:
  version: 0.9.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender for Claude

Router only. Standards for every extension built or changed: `references/standards.md`. Platform layering: `references/platforms.md`; agent logic shared across platforms: `references/agent-protocols.md`.

## 0. Start simple

The user should never need to know what a manifest, frontmatter, or MCP is. Talk about what the result will do, not its files.

- **Invoked with no request, or the request is vague:** ask one short question and stop:
  > What would you like Claude to do for you? Describe it the way you'd explain it to a colleague. For example: "turn my meeting notes into action items", "check every blog draft against our style guide", "pull this week's numbers from our CRM into a summary", or "fix the skill I already have".
- **Request is clear:** don't ask; restate it in one plain sentence and continue.
- Work out the technical choices yourself (component types, names, structure) and show them as a short plan in plain words. Ask the user only what they alone can answer: who will use it, where they use Claude, and any names or rules it must follow.
- Default to the smallest thing that works. A single skill beats a plugin when one skill covers it.

## 1. Environment (detect, never ask)

Cowork if `find mnt/.local-plugins mnt/.plugins -maxdepth 1 -type d 2>/dev/null` returns anything or a Cowork session is active. Otherwise standard (Claude Code, claude.ai, API).

## 2. Mode (infer; ask one question only if unclear)

| Mode | What the user says |
|---|---|
| New | wants Claude to do something new, for themselves or others |
| Internal business solution | a process, checklist, or tool for a team or company ("for my team", "our process", "every client") |
| Update existing | has a skill or plugin already and wants it changed or fixed |
| Audit | wants a check before sharing or shipping |
| Convert | "turn this conversation / workflow / prompt into a skill" |

## 3. Route

| Mode | Skills, in order |
|---|---|
| New | `ai-extender:claude-planner` → `ai-extender:claude-developer` → `ai-extender:claude-reviewer` → `ai-extender:claude-packager` |
| Internal business solution | as New; the planner also settles who installs it and how it reaches them (`claude-planner/references/scoping.md` §Business use) |
| Update existing | `ai-extender:claude-maintainer` → `ai-extender:claude-reviewer` → `ai-extender:claude-packager` |
| Audit | `ai-extender:claude-reviewer` → owning skill for each fix |
| Convert | `ai-extender:claude-planner` (extract intent) → as New |

- Skip stages the request doesn't need; never chain by default.
- One plan approval: show the plan once, then build, check, and package without asking again unless something changes scope.
- User explicitly says the extension may be **publicly released on a marketplace or directory** → `claude-packager/references/release.md`. Never raise it yourself.
- Corrections stay in the active skill. Re-route only for an unrelated new build.
- Cowork `.plugin` output and customizing: `claude-packager/references/cowork.md`.

## 4. Efficiency ladder

1. In context already? Reuse; don't re-ask, re-read, or re-derive.
2. One skill enough? Don't chain.
3. File unchanged since last validation? Reuse the result.
4. Only then the full workflow. No speculative re-checks or polish loops.

## 5. Finish

Hand over the result first (file, install steps in two or three lines, one example prompt to try), then one scratchpad per `references/scratchpad.md`.

## Absorbed skills

`/skill-creator` → developer + reviewer · `/create-cowork-plugin` and `/cowork-plugin-customizer` → packager (`cowork.md`) + maintainer.
