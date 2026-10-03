# GitHub (Composio, a GitHub connector, or `gh`)

Tool routes, in order: a connected GitHub connector; Composio (its GitHub toolkit); the `gh` CLI with the user's authentication. Use only tools actually present in the session (check the tool list; in chat, Composio tools are deferred: load them with tool search first). Never claim a push, tag, or release happened without a tool result proving it. SyncWin repos live under the `syncwin` org; ask for the repo name and visibility (private by default) if not given.

## Contents

1. Publish · 2. Keep it maintained · 3. Orphan cleanup · 4. Rules · 5. Prepared repo (no tools)

## 1. Publish a plugin or skill repo

1. Validate and package first (`ai-extender-reviewer`, `package_extension.py`).
2. Repo root = plugin root (`.claude-plugin/`, `skills/`, ...). Keep `.gitignore`; never commit `*.plugin`/`*.zip` (attach them to releases).
3. Set `plugin.json` `repository` and `homepage`. Marketplace entry `source` is `./` when the repo is the marketplace, else `{"source": "github", "repo": "<owner>/<repo>"}` (pin `ref` or `sha` for releases).
4. Commit with the version and one-line what/why from the changelog. Batch files into a few multi-file commits (Composio: commit-multiple-files); an empty repo needs one single-file commit first.
5. Tag `v<version>`, create a release with the changelog entry as notes, attach the versioned download file.
6. Verify the install path: `claude plugin marketplace add <owner>/<repo>` then `claude plugin install <name>@<marketplace>`.

## 2. Keep it maintained (every change)

After any edit to a repo-backed extension: update `CHANGELOG.md` and versions, revalidate, push the changed files, tag on a version bump, then run the orphan check. Verify each push by comparing blob SHAs from the tool result with `git hash-object` of the local file.

## 3. Orphan cleanup

Orphans are remote files or paths that no longer exist locally (renamed or removed skills, superseded scripts, stale build output), plus repos, branches, tags, and releases left behind by a rename.
1. List the remote tree and diff it against the local file list. Delete remote-only files in the same commit as the change that orphaned them.
2. Rename means move: delete the old paths, add the new ones, record old to new in the changelog.
3. Deleting a whole repo, branch, tag, or release is irreversible: name exactly what will go, get the user's confirmation, then delete. Archive instead when unsure.
4. Report what was removed in the scratchpad.

## 4. Rules

- Same-session iterations: commit to a branch, tag only on a real version bump.
- Secrets scan before every push (validator code `X001` must be clean).
- Public repo is not a public marketplace release; that stays dormant (`release.md`).
- Updates to a published extension: `ai-extender-maintainer` first, then re-tag.

## 5. Prepared repo (no tools needed)

The release directory ships ready for `git`: `git init`, one commit per version, annotated tag `v<version>`. With credentials the user runs:
`git remote add origin https://github.com/syncwin/<repo>.git && git push -u origin main --tags`
