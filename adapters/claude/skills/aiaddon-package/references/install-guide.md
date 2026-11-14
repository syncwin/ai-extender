# Install guide recipe

Replaces the former `install_guide.py`. Claude follows this recipe with built-in tools only (Read, Glob, Write). No script is saved or run.

## Contents

- Purpose and when
- Inputs (former CLI options)
- Step 1: read the folder
- Companion prompt note
- Skill guide (exact text; `<f>` = file name, `<slug>`, `<title>`)
- Plugin guide
- Settings and connectors section
- Procedure
- Notes

## Purpose and when

Write install and removal steps for an extension, for every place people use Claude: the Claude desktop app, claude.ai on the web, the desktop app's Code tab, and the terminal, plus how to undo each. The packaging recipe (`package-extension.md`) writes it next to every package as `<Visible Name> v<version> install.md`. Run it alone when the user asks for install steps.

The steps below were verified 2026-10-11 against support.claude.com articles 13837440 (plugins) and 12512180 (skills), and code.claude.com/docs/en/plugins/install. Re-check them if the user reports a mismatch.

## Inputs (former CLI options)

| Input | Meaning | Default |
|---|---|---|
| dir | The plugin or skill folder | required |
| repo (`--repo owner/repo`) | GitHub repo that serves as the marketplace. Without it the Code tab and terminal steps load the folder or add a local marketplace instead. | none |
| marketplace (`--marketplace name`) | Marketplace name used in `<plugin>@<marketplace>` | the `name` in `<dir>/.claude-plugin/marketplace.json` if that file exists, otherwise unknown |
| file (`--file "<package file name>"`) | The package file name to mention | `<title> v<version>.plugin` for a plugin, `<title> v<version>.zip` for a skill |
| out (`--out FILE`) | Where to write the guide | if absent, show the text in the chat instead of writing |
| prompts (`--prompts md/json/both`, default `both`) | Which companion prompt files the "Companion prompt" section lists; `none` leaves the section out | both |

A wrong call is a usage error: say so and stop.

## Step 1: read the folder

Plugin (a `.claude-plugin/plugin.json` exists; remove a leading byte order mark):

- slug = `name`; title = `displayName` or else `name`; version = `version` as text or `0.0.1`; manifest = the whole plugin.json.

Skill (otherwise read `SKILL.md`; it must exist):

- slug = the front matter line `name: ...` (quotes removed); title = first `# ` heading, else the slug; version = the first indented front matter line `  version: <value>` (quotes removed), else `0.0.1`; no manifest.

## Companion prompt note

Used in both guides unless prompts is `none`. Names: the Markdown file is `<title> v<version> prompt.md`; the JSON file is the title lower-cased, each run of characters outside `a-z0-9` replaced by `-`, leading and trailing `-` stripped, plus `.json`.

```
## Companion prompt

Ships next to the package, never inside it.

- `<title> v<version> prompt.md` is the same prompt as plain Markdown: copy it into any chat, or into a project's instructions, and fill in the {{variables}} by hand.
- `<json file name>` is the same prompt as a Prompt Builder import file (a fillable form).
```

The first bullet appears for prompts `md` or `both`; the second for `json` or `both`. The note ends with a newline. When the note is wanted it is added at the end of the guide after one blank line.

## Skill guide (exact text; `<f>` = file name, `<slug>`, `<title>`)

```
# Install <title>

## Claude desktop app and claude.ai on the web

1. Open **Customize** in the left sidebar, then **Skills**.
2. Click **+**, then **Create skill > Upload a skill**, and choose `<f>`.
3. Turn the skill on. Start it by typing `/<slug>` or by describing the task.

**Undo:** in **Customize > Skills**, turn the skill off, or delete it from its menu.

## Claude Code (terminal or the desktop app's Code tab)

Unzip `<f>` into `~/.claude/skills/` (every project) or `.claude/skills/` (this project only). Start a new session.

**Undo:** delete the `<slug>` folder you added.

<Companion prompt note, if wanted>
```

## Plugin guide

Variables: `<f>` = file name; `<mk>` = marketplace (given, else from marketplace.json `name`, else empty); `<src>` = repo if given, otherwise `./path/to/marketplace-folder`; `<ident>` = `<slug>@<mk>` if `<mk>` is set, otherwise `<slug>@<marketplace>` (literally, with the angle brackets).

````
# Install <title>

## Claude desktop app (Chat or Cowork) and claude.ai on the web

1. Open **Customize** in the left sidebar, then the **Plugins** tab. In Cowork, open the Cowork tab first.
2. Upload `<f>` as a custom plugin.[ Or add the marketplace `<repo>` with **Add > Add marketplace**, then add <title> from **Discover**.]
3. Plugins you add here are saved to your account, so they also reach Claude Code when you sign in there with the same account.

**Undo:** in **Customize > Plugins**, turn <title> off, or delete it from its **...** menu. A marketplace you added comes off with its menu's **Remove**.

## Code tab in the desktop app (local or SSH sessions)

1. <step 1>
2. Click **+** next to the prompt box, then **Plugins > Add plugin**, select <title>, and choose a scope (you, this project, or this project only for you).

**Undo:** **+ > Plugins > Manage plugins**, then disable or uninstall it.

## Terminal (Claude Code)

```
<terminal commands>
```
Already running? Use `/reload-plugins`. To try a folder for one session without installing: `claude --plugin-dir <folder>`.

**Undo:** `claude plugin disable <ident>` to pause it, `claude plugin uninstall <ident>` to remove it<tail>

<Settings and connectors section, only if there are options or servers>

<Companion prompt note, if wanted>
````

Variable parts:

- The bracketed sentence in step 2 appears only when a repo was given (then use the repo text).
- Code tab step 1: with a repo: ``1. Add the marketplace once: `claude plugin marketplace add <repo>` (or `/plugin marketplace add <repo>` in a session).`` Without a repo: ``1. Add the marketplace once from a terminal: `claude plugin marketplace add <src>`.``
- Terminal commands: with a repo, one line: `claude plugin install <slug> --marketplace <src>`. Without a repo, two lines: `claude plugin marketplace add <src>` then `claude plugin install <ident>`.
- `<tail>`: when `<mk>` is set: `, and `claude plugin marketplace remove <mk>` to drop the marketplace (this also uninstalls everything installed from it).` Otherwise a single period.
- There is a blank line between sections as drawn. The line "Already running? ..." follows the closing code fence directly, with no blank line between them.

## Settings and connectors section

Only when the manifest has `userConfig` entries or connectors (MCP servers) exist. Servers come from `<dir>/.mcp.json` (if present: use its `mcpServers` object when it has one, otherwise the object itself; ignore anything that is not an object), then plugin.json `mcpServers` (when an object) is merged in on top. Text, one blank line before the next section:

```
## Settings and connectors

- **<option title>**: <option description> Stored in secure storage.
- Connector **<server name>** (`<url>`): in Chat or Cowork, open the plugin's **Connectors** tab and select **Connect**; you sign in with your own account, so nothing personal is stored in the plugin.
- In Claude Code, set options and connector settings under `/plugin` > **Installed** > the plugin > **Configure options** or **Configure**.
- A connector you already have at the same address is reused: Claude Code skips the plugin's copy.
```

Rules: one bullet per `userConfig` entry, in order; the title is the entry's `title` or else its key; the description is the entry's `description` or empty; add ` Stored in secure storage.` only when the entry has `sensitive: true`. One connector bullet per server; ` (`<url>`)` is shown only when the server has a `url` that is not empty and does not contain `${`. The last two bullets always appear.

## Procedure

```
1. Read the folder (Step 1) with Read and Glob. For the plugin guide also read `.mcp.json` and `marketplace.json` if they exist.
2. Fill the right template above exactly (keep the wording, bold marks and code marks).
3. If an out file is given, Write it as UTF-8 and say `wrote <file>`; otherwise show the text.
4. Report the guide's location and which companion prompt files it lists.
```

## Notes

- The guide is for people, written in plain words. Keep it ASCII (the templates are).
- A guide for a plugin that has no marketplace and no repo keeps the literal `<marketplace>` placeholder and `./path/to/marketplace-folder`; tell the user to replace them or pass the marketplace name and repo.
