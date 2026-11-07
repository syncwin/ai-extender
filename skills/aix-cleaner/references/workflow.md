# Cleaner workflow details

Contents: what the scripts measure, thresholds, reading flagged text, applying, proof, limits.

## What the scripts measure

- **Normalized line:** lowercase, list and heading markers removed, whitespace collapsed; blank and punctuation-only lines ignored. Two lines are the same line when their normalized text is equal.
- **Exact duplicate paragraph:** equal normalized paragraph text (Markdown files, at least 12 words).
- **Near duplicate paragraph:** Jaccard similarity of 5-word shingles at or above 0.6 (`--threshold`). Cheap candidate search through a shingle index; no LLM.
- **Shared heading:** the same heading text in more than one file; a hint for merged or split skills.
- **Unique line:** a normalized line present in exactly one place. These are what the proof protects.

Tune with `--min-words` and `--threshold`. Lower the threshold to find looser overlaps; expect more false hits.

## Reading flagged text

Open only the line ranges the report names. Decide per finding: identical, near, same topic, or intentional repeat. A rule stated in the router and again where it is enforced is usually intentional. Mention it in the plan and keep it.

## Applying an approved plan

- One action at a time, smallest diff, in the order of the plan.
- Prefer a pointer ("see `references/x.md`") over deleting the only explanation; keep the surviving copy where it is loaded.
- Moves use `archive.py` (dry-run first, then `--apply`). It keeps the relative path, refuses paths outside the root and never overwrites.
- Do not touch version fields or the changelog here; hand off to `aix-maintainer`.

## Proof

`prove.py <before> <after> --archive <dir>` compares every normalized line of the untouched before tree with the after tree plus the archive. Any missing line is printed as `LOST file:line: text` and the run fails. A reworded line counts as lost: if rewording is wanted, keep the original line in the plan's proof table as `reworded to ...` and apply it by hand after review, or keep both.

Also report the inventory totals before and after (files, bytes, unique lines, duplicate paragraphs) and the evals and reviewer results before and after.

## Limits

Line equality is textual. It does not catch two lines that say the same thing in different words (that is the near-duplicate report plus human judgement), and it does not read images or binary files. Archive and `.git` folders are skipped in the inventory.
