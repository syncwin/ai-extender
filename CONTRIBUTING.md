# Contributing

Issues and pull requests are welcome at [github.com/syncwin/aiaddon](https://github.com/syncwin/aiaddon).

1. Read `skills/aiaddon/references/standards.md` (naming, metadata, the lean-build rule) and `platforms.md` (how the layers split).
2. Keep scripts on the Python 3 standard library. No dependencies.
3. Before you open a pull request, run these from the repository root. Both must pass:
   `python skills/aiaddon-review/scripts/selftest.py`
   `python skills/aiaddon-review/scripts/validate_extension.py . --strict --target directory --require-meta author,company`
4. Pull requests need passing CI (self-tests, strict validation, secret scan, injection screen, CodeQL) and review from the code owner. Pin any GitHub Action you add to a full commit SHA with the version in a comment, and give each job only the permissions it needs.
5. Add a `CHANGELOG.md` line for every behavior change. For a release, bump the plugin version and every skill's `metadata.version` together.
6. A platform fact needs the official page it came from and the date you checked it.
7. New skills, agents and commands follow the naming standard (router = plugin name, everything else prefixed `aiaddon-`, action-style slugs) and are added to the router's routing table with router evals in `evals/router/cases.json` (`python skills/aiaddon-review/scripts/route_check.py .`).
8. Keep private data out: no keys, client names, internal URLs, or personal details in any file, example, or test. The scan checks the tree and full history: `python skills/aiaddon-review/scripts/scan_secrets.py . --history`. Fake keys in tests are assembled at run time, never written out.

Contributions are licensed under the MIT License.
