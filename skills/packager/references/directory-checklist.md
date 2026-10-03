# Directory Pre-submission Checklist

Verified 2026-10-03 (claude.com/docs/plugins/pre-submission-checklist and /submit). Only on the user's explicit public-release instruction (`release.md`). Automate with `python ${CLAUDE_SKILL_DIR}/../reviewer/scripts/validate_extension.py <dir> --target directory --strict`; the portal's Validate button runs the authoritative version, then a security scan runs on every new commit.

## Contents

1. Results · 2. Blocks · 3. Held for a reviewer · 4. Security scan · 5. Submission steps

## 1. Results

**Blocks** (cannot submit) · **Policy hold** (a reviewer reads the version) · **Warning** · **Note**. Everything must also follow the Anthropic Software Directory Policy and Terms.

## 2. Blocks

- Plugin folder contains `.claude-plugin/plugin.json`; one plugin per submission; every file a hook, script, or component path uses lives inside the plugin folder.
- Regular files only: no symlinks, submodules, or LFS pointers; no `.DS_Store`, `Thumbs.db`, `desktop.ini`, `__MACOSX`; file names valid on Windows and macOS (no colon, trailing dot or space, device names, case-only differences); no `export-ignore`, `export-subst`, or content-rewriting `filter` in `.gitattributes`.
- Name: lowercase ASCII letters/digits/hyphens, <=64, not a reserved word alone (`claude`, `anthropic`, `official`, `plugin`, `mcp`, `test`), not taken, not presenting itself as official. `displayName` and `author.name` in one writing system, no look-alike or invisible characters. Component keys spelled exactly and not under `experimental`.
- README >=40 words outside code blocks; LICENSE file or `license` in `plugin.json`.
- Package launchers (`npx`, `bunx`, `pnpm dlx`, `yarn dlx`, `uvx`, `pipx run`, `uv run`) pinned to an exact version (`pkg@1.2.3`, `pkg==1.2.3`); `uv run` with `--locked` or `--frozen`; no `.npmrc`, `bunfig.toml`, `uv.toml` beside a launcher.
- No real credentials anywhere; ask through `userConfig` with `sensitive: true` and refer to `${user_config.KEY}`. No HTTP hook sending a credential read from the environment.
- `.mcp.json` valid; remote servers `type` http/sse/ws with an absolute `https://` or `wss://` URL (or a `${user_config.KEY}` reference, or `""`); no `.mcpb`/`.dxt` fetched from a URL.
- `hooks/hooks.json` valid with a top-level `hooks` object, known events and types, `https://` on HTTP hooks; valid YAML front matter with `description` as one text value; exact folder and file spelling (`hooks/`, `skills/`, `SKILL.md`).
- Repository size: <50 MiB archived, <256 MiB unpacked, <10,000 entries, every plugin file <5 MiB (otherwise validation stops).

## 3. Held for a reviewer

Non-image, non-font file >256 KiB; >512 files; binary files other than PNG/JPEG/GIF/WebP/fonts; bundled `.mcpb`/`.dxt`; local MCP servers started through a shell, `-c`, or `npm run`; any pinned launcher package; `package.json` with a lockfile; scripts the validator cannot follow (when the plugin sits in a subfolder, keep hook and server logic in shell scripts that name each path as `${CLAUDE_PLUGIN_ROOT}/<file>`); credential read from the user's environment; names resembling a known brand or another listing; forks reusing the upstream name; minified or packed code.

## 4. Security scan

Flags undisclosed behavior (data sent elsewhere, hidden code, permission changes). Describe in the README everything the plugin runs, sends, or fetches; commit readable source.

## 5. Submission steps

Needs a paid plan and a role that can submit, a GitHub repository on github.com with the account connected on claude.ai (public at publish time), then claude.ai/directory/manage: Submit new, Plugin bundle, Source (repo, optional plugin path, tracked branch or tag), Validate, fix Blocks, Re-validate, submit. Raise `version` on every release. A first submission that fails the scan is rejected; later failing versions cannot go live. Submit an MCP server you run separately as a connector too.
