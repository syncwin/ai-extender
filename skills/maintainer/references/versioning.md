# De-duplication, Versioning, Changelogs

## Part 1: De-duplication pass

Run on every create/edit checkpoint and before a version bump. Test for each line: **would removing it lose an instruction, constraint, edge case, or fact?** No → cut. Yes → keep; compress wording, never content.

1. Read every file of the extension before editing any (redundancy hides file-by-file).
2. Find real redundancy: a rule stated twice (keep one full statement, other becomes `see §X`); a fact in two files (one canonical home); stale cross-references (grep old names after every rename); orphan headings left by edits; build-log or "compiled from" notes; prose that is a bullet with no loss.
3. Consolidate, don't just delete: if a rule appears 3 times, one complete statement + two pointers.
4. Structure for parsing: bullets for discrete rules, bold lead term, grouped by topic, contents list on files >300 lines.
5. Verify zero loss: every rule, threshold, number, example still present somewhere. Check reported line reductions against a real diff.

Token efficiency beyond text: prefer scripts over repeated generated code; load references on demand; avoid re-reading files already in context; keep `SKILL.md` under 500 lines.

## Part 2: Updates

Propose a change when a reusable gap appears (missing, wrong, ambiguous, or contradictory rule), the user reports a real failure, or a structural request arrives. Pure rephrasing is Part 1, not a version reason.

- **Ask before changing:** state the gap in 1–2 sentences and the file it goes in; proceed on an explicit yes. A yes to a broad task does not authorize unrelated edits. If the user pre-authorized a scoped piece of work ("do whatever's best for X"), proceed inside that scope and narrate afterwards.
- **Diagnose failures concretely:** diff before/after. *Execution gap* (rule right, not followed → fix sequencing) vs *specification gap* (rule missing/wrong → fix the rule). Fix it in the file that owns it.
- **Scope:** a request to fix X is not permission to restructure Y. Follow the extension's existing organization. Mirror a new rule where it is already represented, as pointers.

## Part 3: Versioning and changelog

- Semver. New extensions start at **`0.0.1`**. MAJOR = breaking invocation/structure; MINOR = new capability; PATCH = fix or clarification.
- **Same session, same build:** add lines to the current changelog entry; don't bump per edit. New version only for a genuinely new iteration, a confirmed milestone, or an explicit request.
- `CHANGELOG.md`: newest first; per version, Added / Changed / Fixed / Removed; each line says what and why. Never delete history. A deliberate backward or skipped number gets a note.
- Plugin version and each skill's `metadata.version` move together when a skill changes (plugin version pins users, so a changed plugin with an unchanged `version` is never delivered to existing installs).
- Repo-backed extensions: push the update, tag a version bump, and clean orphans (`packager/references/github.md`).
- Every update ships: edited files, changelog, the new version stated, a short what/why, revalidated and repackaged output (filename carries the version), scratchpad.

## Part 4: Third-party extensions

Before updating something this builder didn't author: tell the user once, plainly, that their copy becomes a fork, stops receiving upstream updates, and that reinstalling upstream overwrites local changes with no merge. Get acknowledgement. Check its license permits modification and redistribution first. Prefer an add-on (`developer/references/addons.md`) over a fork.
