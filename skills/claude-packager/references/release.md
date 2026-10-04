## Public release mode

**Dormant.** Activates only when the user explicitly states the extension may be publicly released on the marketplaces. Never ask, hint, or offer this. Ignore this section otherwise.

When triggered:

1. Ask only these, in one message (skip any already known):
   1. Which marketplace(s)?
   2. Final license, and confirmation that every third-party component's license permits public redistribution?
   3. Publisher name, homepage, and support contact?
   4. Public source repository URL?
   5. If it has connectors: what data each sends to which service (for the privacy disclosure)?
2. Route and prep: `distribution-routes.md` (§2 prep, §4 directory). Fetch each named marketplace's current submission requirements (web fetch); don't rely on memory.
3. Block release until: every third-party license question is resolved; no secrets or private/project-specific data remain in any file; `LICENSE` matches declared license; validator passes.
4. Prepare: public `marketplace.json` entry, README (install, connectors, data handling, support), changelog, correctly named release files, and any listing fields the marketplace requires.
5. Scratchpad lists what was prepared and what the user must still submit themselves.
