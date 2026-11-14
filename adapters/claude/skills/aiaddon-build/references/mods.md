# Mods (hooks written as JavaScript)

Verified 2026-10-03 (code.claude.com/docs/en/plugins/mods/create and /reference, Claude Code v2.1.287+). Claude Code and Desktop only: not Chat, not Cowork. The authoritative reference is the type declarations Claude Code writes for your version (`claude --plugin-dir <dir>` writes `.claude-plugin/types/claude-code/index.d.ts`); trust them over this page.

## Contents

1. Layout · 2. The hook function · 3. Events · 4. Mods API · 5. Limits · 6. Admin settings · 7. Commands

## 1. Layout

A mod is a plugin with `hooks/hooks.json` containing `"modules": ["./register.js"]` (exactly one path, relative to the file; having the key is what makes the plugin a mod; `hooks` may sit beside it). The module is an ES module (`.js .mjs .cjs .jsx .ts .mts .cts .tsx`) that exports `register(on, options)`; `options` holds the manifest's `userConfig` values with defaults filled in. Optional `types/index.d.ts` (named by `types` in the manifest) when the mod uses `$.state` or adds an API namespace. Tests end in `.test.ts` or `.test.tsx`.

## 2. The hook function

`on(eventName, matcher?, async ($, e, next) => result)`. `$` = mods API (write calls in full: `$.fs.read(...)`); `e` = frozen event input (pass a copy to `next` to change it); `next(e)` runs later hooks then Claude Code's behavior. `on(...)` returns a registration with `.catch(handler)`. Also `next.signal`, `next.origin`, `next.budget`, `next.to(e, tier)` (only `prependPlugins`/`appendPlugins` mods). Tiers: `prepend`, `user`, `append`, `builtin`, `core`.

## 3. Events (by group)

Tools `tool.call` `tool.check` `tool.describe` · Prompts `prompt.submit` `prompt.fill` `prompt.suggest` `prompt.edit` `prompt.compose` `prompt.section` `prompt.context` `prompt.attachment` `skill.prompt` `attribution.text` · Commands/config `command.run` `command.describe` `config.set` `config.describe` · Turns `turn.start` `turn.step` `turn.complete` · Session `session.start` `session.end` `session.compact` `session.receive` `session.send` `session.append` `session.attach` `session.detach` `session.measure` · Subagents `agent.offer` `agent.spawn` · UI `ui.render` `ui.resolve` `ui.press` `ui.input` `ui.select` `ui.focus` `ui.scroll` `ui.close` `ui.message` · Other mods `plugin.register` `engine.create` · Telemetry `telemetry.log` `telemetry.mark` · every settings hook as `classic.<Event>` · every API call as `<namespace>.<method>`.

Return shapes: `next(e)` passes on; `{ deny: reason }` refuses (`tool.call`, `config.set`, `agent.spawn`); `{ decision }` for `tool.check` (`allow|ask|deny`); `{ text }` for `prompt.section`, `skill.prompt`, `command.run`; `{ drop: reason }` for `prompt.submit`.

## 4. Mods API (`$`)

`$.plugin` `$.ui` `$.command` `$.tool` `$.agent` `$.model` (`complete`, `fork`, `classify`) `$.prompt` `$.turn` `$.session` `$.config` `$.settings` `$.env` `$.fs` `$.store` (shared key-value, 4 MiB) `$.state` `$.clock` `$.http` `$.process` `$.mcp` `$.audio` `$.telemetry`. `$.fs.write` is not atomic; keep multi-session data in `$.store`. Render sites (`Pane`, `AbovePrompt`, `Spinner`, `ToolUse`, ...) and elements (`Box`, `Text`, `Button`, `Input`, `Select`, `Markdown`, ...) are listed in the reference; `Svg` is Desktop-only, `Raster` and `Image` are terminal-only.

## 5. Limits

Hook runtime 10 s per event; `.catch` 1 s; all `session.end` hooks 1.5 s; `$.process.run` 30 s default, 10 min max; `$.model.complete` `maxTokens` 1024 default; `$.fs` 4 MiB per file; names (command, tool, agent, pane) letters/digits/`_`/`-`, <=64; `claude plugin test` 5 s per test.

## 6. Admin settings (managed)

`prependPlugins` / `appendPlugins` (ordering), `allowManagedModsOnly`, `allowModsToOverrideDenyRules`, `allowManagedHooksOnly`, `disableAllHooks`, `disableSideloadFlags`, `pluginConfigs`. Built-in guard `sec-default@builtin` loads ahead of user mods on managed machines.

## 7. Commands

`claude plugin validate <dir>` (reports events hooked and API calls made; `--strict`, `--json`), `claude plugin test [dir]`, `claude --plugin-dir <dir>` (reloads on save), `/reload-plugins`, `/plugin` (shows active mods). Mods run with the same machine access as Claude Code: treat a mod as code review material and declare what it does in the README (directory scan). Our validator checks the `modules` key and file (H006, H007).
