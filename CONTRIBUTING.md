# Contributing

Issues and pull requests are welcome at [github.com/syncwin/aiaddon](https://github.com/syncwin/aiaddon).

1. Read `adapters/claude/skills/aiaddon/references/standards.md` (naming, metadata, the lean-build rule) and `platforms.md` (how the layers split).
2. Keep the shipped plugin Markdown only: no scripts, hooks or other non-text files (Anthropic directory policy). Maintainers: dev tools in `dev/` (not shipped). The shipped plugin is the `adapters/claude/` folder; everything outside it is repository tooling.
3. Before you open a pull request, follow the recipes `adapters/claude/skills/aiaddon-review/references/selftest.md` and `validate-extension.md` on `adapters/claude` (strict, target directory, author and company required). Both must pass. Maintainers: dev tools in `dev/` (not shipped).
4. Pull requests need passing CI (self-tests, strict validation, secret scan, injection screen, CodeQL) and review from the code owner. Pin any GitHub Action you add to a full commit SHA with the version in a comment, and give each job only the permissions it needs.
5. Add a `CHANGELOG.md` line for every behavior change. For a release, bump the plugin version in `adapters/claude/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, and mirror README and CHANGELOG edits into `adapters/claude/` (skill frontmatter holds text-only name, description and license).
6. A platform fact needs the official page it came from and the date you checked it.
7. New skills, agents and commands follow the naming standard (router = plugin name, everything else prefixed `aiaddon-`, action-style slugs) and are added to the router's routing table with router evals in `adapters/claude/evals/router/cases.json` (recipe `adapters/claude/skills/aiaddon-review/references/route-check.md`).
8. Keep private data out: no keys, client names, internal URLs, or personal details in any file, example, or test. The scan checks the tree and full history: the recipes `adapters/claude/skills/aiaddon-review/references/scan-secrets.md` and `public-safety-scan.md` (include the history step). Fake keys in tests are assembled at run time, never written out.

Contributions are licensed under the MIT License.
