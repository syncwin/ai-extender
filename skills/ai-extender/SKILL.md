---
name: ai-extender
description: >
  Entry point and router for AI Extender for Claude. Use whenever the user wants to build, update,
  audit, version, package, or extend a Claude extension: plugin, skill, connector, agent, hook, MCP server, or add-on.
  Triggers: "build me a plugin", "make me a skill", "add a connector", "create an agent", "turn this workflow into a
  plugin or skill", "update my plugin", "audit my extension", "bump the version", "package this for Cowork", and
  mentions of /skill-creator, /skill-creator-plus, /create-cowork-plugin, /cowork-plugin-customizer. Load first; routes only.
license: MIT
metadata:
  version: 0.5.0
  author: "@wasimness"
  company: SyncWin
---

# AI Extender for Claude

Router only. Standards for every extension built or changed: `references/standards.md`.

## 1. Environment (detect, never ask)

Cowork if `find mnt/.local-plugins mnt/.plugins -maxdepth 1 -type d 2>/dev/null` returns anything or a Cowork session is active. Otherwise standard (Claude Code, claude.ai, API).

## 2. Mode (ask one question only if unclear)

New extension (plugin / skill / connector / agent / MCP / add-on) · Update existing · Audit · Convert a workflow.

## 3. Route

| Mode | Skills, in order |
|---|---|
| New | `ai-extender-planner` → `ai-extender-developer` → `ai-extender-reviewer` → `ai-extender-packager` |
| Update existing | `ai-extender-maintainer` → `ai-extender-reviewer` → `ai-extender-packager` |
| Audit | `ai-extender-reviewer` → owning skill for each fix |
| Convert | `ai-extender-planner` (extract intent) → as New |

- Skip stages the request doesn't need; never chain by default.
- User explicitly says the extension may be **publicly released on the marketplaces** → `ai-extender-packager/references/release.md`. Never raise it yourself.
- Corrections stay in the active skill. Re-route only for an unrelated new build.
- Cowork `.plugin` output and customizing: `ai-extender-packager/references/cowork.md`.

## 4. Efficiency ladder

1. In context already? Reuse; don't re-ask, re-read, or re-derive.
2. One skill enough? Don't chain.
3. File unchanged since last validation? Reuse the result.
4. Only then the full workflow. No speculative re-checks or polish loops.

## 5. Finish

One scratchpad per `references/scratchpad.md`.

## Absorbed skills

`/skill-creator` → developer + reviewer · `/skill-creator-plus` → maintainer + standards · `/create-cowork-plugin` and `/cowork-plugin-customizer` → packager (`cowork.md`) + maintainer.
