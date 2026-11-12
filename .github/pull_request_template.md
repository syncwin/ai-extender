**What changed and why**

**Checks**
- [ ] `python dev/aiaddon-review/scripts/selftest.py` passes
- [ ] `python dev/aiaddon-review/scripts/validate_extension.py . --strict --target directory --require-meta author,company` passes
- [ ] `CHANGELOG.md` updated
- [ ] `python dev/aiaddon-review/scripts/scan_secrets.py .` and `screen_text.py .` report nothing
- [ ] `python dev/aiaddon-review/scripts/scan_secrets.py . --history` (blocking) and `route_check.py .` report nothing
- [ ] New GitHub Actions are pinned to a full commit SHA with least-privilege permissions
- [ ] No private data, keys, or client names in any file
