**What changed and why**

**Checks**
- [ ] `python skills/claude-reviewer/scripts/selftest.py` passes
- [ ] `python skills/claude-reviewer/scripts/validate_extension.py . --strict --target directory --require-meta author,company` passes
- [ ] `CHANGELOG.md` updated
- [ ] `python skills/claude-reviewer/scripts/scan_secrets.py .` and `screen_text.py .` report nothing
- [ ] New GitHub Actions are pinned to a full commit SHA with least-privilege permissions
- [ ] No private data, keys, or client names in any file
