# Contributing

Issues and pull requests are welcome at [github.com/syncwin/ai-extender](https://github.com/syncwin/ai-extender).

1. Read `skills/ai-extender/references/standards.md` (naming, metadata, the lean-build rule) and `platforms.md` (how the `ai-` and `claude-` layers split).
2. Keep scripts on the Python 3 standard library. No dependencies.
3. Before you open a pull request, run these from the repository root. Both must pass:
   `python skills/claude-reviewer/scripts/selftest.py`
   `python skills/claude-reviewer/scripts/validate_extension.py . --strict --target directory --require-meta author,company`
4. Add a `CHANGELOG.md` line for every behavior change. For a release, bump the plugin version and every skill's `metadata.version` together.
5. A platform fact needs the official page it came from and the date you checked it.
6. Keep private data out: no keys, client names, internal URLs, or personal details in any file, example, or test.

Contributions are licensed under the MIT License.
