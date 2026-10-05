#!/usr/bin/env python3
"""Create, check, and deliver the Prompt Builder companion prompt for an extension.

Usage: companion_prompt.py <extension-dir> [--spec FILE] [--out DIR] [--force]
       companion_prompt.py --check FILE

Every extension ships one companion prompt: <extension-dir>/prompts/<title-slug>.json, in Prompt Builder's
JSON import format (format "prompt-builder-plain", version 2.0). Users import it into Prompt Builder and use
it to start the extension with a short form instead of a blank chat.

  (no spec, no file yet)  writes a default prompt built from the manifest: task, stage (when the plugin has
                          more than one role skill), files, details.
  --spec FILE             writes the prompt from a spec: {"title"?, "description"?, "content", "variables"}.
  (file already there)    checks it and leaves it untouched unless --force or --spec is given.
  --out DIR               also copies the checked file into DIR (next to the packaged extension).
  --check FILE            checks any Prompt Builder JSON file and exits.
Exit: 0 ok, 1 problems found, 2 usage. Standard library only; no network.
Format notes and field rules: ai-extender/references/companion-prompt.md.
"""
import html, json, re, secrets, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

FORMAT, FORMAT_VERSION = "prompt-builder-plain", "2.0"
# Copied from Prompt Builder 2.0 exports; every export inspected carries this value regardless of content.
CHECKSUM = "-9vapbe"
TYPES = {"Text", "Textarea", "Radio", "Checkbox"}
VAR = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
FILE_OPTIONS = "Attached in This Message\nIn the Claude Project Files\nCreated Earlier in This Chat\nNone, Start from Scratch"

def now():
    t = datetime.now(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "prompt"

def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text.replace("\r\n", "\n").lstrip("\ufeff"), re.S)
    out, key, buf = {}, None, []
    for line in (m.group(1).split("\n") if m else []):
        if re.match(r"^[A-Za-z_-]+:", line):
            if key: out[key] = " ".join(buf).strip()
            key, v = line.split(":", 1); v = v.strip(); buf = [] if v in (">", "|", ">-", "|-") else [v.strip("\"'")]
        elif key and line.startswith(" "): buf.append(line.strip())
    if key: out[key] = " ".join(buf).strip()
    return out

def info(root):
    """Return (title, slug_for_invocation, description, role_skills[(name, title)])."""
    pj = root / ".claude-plugin" / "plugin.json"
    if pj.exists():
        m = json.loads(pj.read_text(encoding="utf-8-sig"))
        name = m.get("name") or root.name
        roles = []
        for sm in sorted((root / "skills").glob("*/SKILL.md")) if (root / "skills").is_dir() else []:
            n = sm.parent.name
            if n == name: continue
            h1 = re.search(r"^#\s+(.+)$", sm.read_text(encoding="utf-8-sig"), re.M)
            roles.append((n, h1.group(1).strip() if h1 else n.replace("-", " ").title()))
        return (m.get("displayName") or name.replace("-", " ").title(), name, m.get("description", ""), roles)
    sm = root / "SKILL.md"
    if sm.exists():
        t = sm.read_text(encoding="utf-8-sig"); fm = frontmatter(t)
        h1 = re.search(r"^#\s+(.+)$", t, re.M)
        name = fm.get("name") or root.name
        return (h1.group(1).strip() if h1 else name.replace("-", " ").title(), name, fm.get("description", ""), [])
    raise SystemExit(f"not a plugin or skill directory: {root}")

def var(type_, label, placeholder, context, required=False, max_length="", options=""):
    return {"type": type_, "label": label, "placeholder": placeholder, "context": context,
            "maxLength": max_length, "required": required, "options": options}

def default_spec(title, slug, desc, roles):
    short = desc.split(". ")[0].rstrip(".") if desc else f"Run {title}"
    lines = [f"# {title}", "", f"Run /{slug} and help me with the task below. Talk to me in plain words and ask only what you need from me.", "",
             "* **Task:** `{{task}}`"]
    variables = {"task": var("Textarea", "Task", "Describe what you need in your own words.",
                             "What goes in, what should come out, and any rules it must follow.", True, 3000)}
    if len(roles) > 1:
        lines.append("* **Stage:** `{{stage}}`")
        variables["stage"] = var("Radio", "Stage", "stage",
                                 "Pick the step to run. Not sure: leave it on the first option and the entry skill decides. Skills: "
                                 + "; ".join(f"{t} = /{slug}:{n}" for n, t in roles) + ".",
                                 False, "", "\n".join(["Let It Decide"] + [t for _, t in roles]))
    lines += ["* **Files:** `{{files}}`", "* **Details:** `{{details}}`", "",
              "If something you need is missing, ask for it in one short message, then continue.", "",
              "Before you create, change, send, publish, or delete anything, show a short plan and wait for my yes. Read-only checks run without it."]
    variables["files"] = var("Checkbox", "Files", "files", "Where the files for this task are, if there are any.", False, "", FILE_OPTIONS)
    variables["details"] = var("Textarea", "Details", "Anything else: deadlines, names, examples, things to avoid.",
                               "Everything the task needs that isn't a file.", False, 2000)
    return {"title": title, "description": f"{short}. Fill in the task and run {title} in one step.", "content": "\n".join(lines), "variables": variables}

def esc_context(s):
    """Prompt Builder exports store the tooltip context HTML-escaped (an apostrophe becomes &#x27;)."""
    return html.escape(html.unescape(s), quote=True)

def build(spec, title, old=None):
    stamp = now()
    variables = {}
    for k, v in spec["variables"].items():
        v = dict(v); v["context"] = esc_context(v.get("context", ""))
        variables[k] = {f: v.get(f, d) for f, d in (("type", "Textarea"), ("label", k.replace("_", " ").title()), ("placeholder", k),
                        ("context", ""), ("maxLength", ""), ("required", False), ("options", ""))}
    p = {"id": (old or {}).get("id") or secrets.token_hex(16), "title": spec.get("title") or title,
         "description": spec.get("description", ""), "content": spec["content"], "variables": variables,
         "lastModified": stamp, "created": (old or {}).get("created") or stamp}
    return {"prompts": [p], "metadata": {"exportDate": stamp, "version": FORMAT_VERSION, "format": FORMAT, "count": 1, "checksum": CHECKSUM}}

def check(d):
    """Return (errors, warnings) for a Prompt Builder JSON document."""
    E, W = [], []
    if not isinstance(d, dict) or not isinstance(d.get("prompts"), list) or not d["prompts"]:
        return ["top level needs a non-empty \"prompts\" array"], W
    md = d.get("metadata")
    if not isinstance(md, dict): E.append("missing \"metadata\" object")
    else:
        if md.get("format") != FORMAT: E.append(f"metadata.format must be \"{FORMAT}\"")
        if str(md.get("version")) != FORMAT_VERSION: W.append(f"metadata.version is {md.get('version')!r}; current exports use \"{FORMAT_VERSION}\"")
        if md.get("count") != len(d["prompts"]): E.append(f"metadata.count {md.get('count')!r} != {len(d['prompts'])} prompts")
        if not isinstance(md.get("checksum"), str): E.append("metadata.checksum must be a string")
        if not ISO.match(str(md.get("exportDate", ""))): E.append("metadata.exportDate must be an ISO timestamp ending in Z")
    titles = set()
    for i, p in enumerate(d["prompts"]):
        at = f"prompts[{i}]"
        if not isinstance(p, dict): E.append(f"{at} must be an object"); continue
        if not re.match(r"^[0-9a-f]{32}$", str(p.get("id", ""))): E.append(f"{at}.id must be 32 lowercase hex characters")
        t = str(p.get("title", "")).strip()
        if not t: E.append(f"{at}.title is empty")
        if t.lower() in titles: W.append(f"{at}.title duplicates another prompt; Prompt Builder appends a number")
        titles.add(t.lower())
        if not isinstance(p.get("description", ""), str): E.append(f"{at}.description must be text")
        c = p.get("content")
        if not isinstance(c, str) or not c.strip(): E.append(f"{at}.content is empty"); c = ""
        for k in ("created", "lastModified"):
            if not ISO.match(str(p.get(k, ""))): E.append(f"{at}.{k} must be an ISO timestamp ending in Z")
        vs = p.get("variables", {})
        if not isinstance(vs, dict): E.append(f"{at}.variables must be an object"); continue
        used = set(VAR.findall(c))
        for name in sorted(used - set(vs)): E.append(f"{at}: {{{{{name}}}}} is used in content but has no variable")
        for name in sorted(set(vs) - used): E.append(f"{at}: variable \"{name}\" is never used in content")
        for name, v in vs.items():
            vat = f"{at}.variables.{name}"
            if not re.match(r"^[A-Za-z0-9_]+$", name): E.append(f"{vat}: name must be letters, digits, underscores")
            if not isinstance(v, dict): E.append(f"{vat} must be an object"); continue
            ty = v.get("type")
            if ty not in TYPES: E.append(f"{vat}.type {ty!r} must be one of {sorted(TYPES)}"); continue
            if not str(v.get("label", "")).strip(): E.append(f"{vat}.label is empty")
            for f in ("placeholder", "context", "options"):
                if not isinstance(v.get(f, ""), str): E.append(f"{vat}.{f} must be text")
            if not isinstance(v.get("required", False), bool): E.append(f"{vat}.required must be true or false")
            opts = [o for o in re.split(r"\n", str(v.get("options", ""))) if o.strip()]
            ml = v.get("maxLength", "")
            if ty in ("Radio", "Checkbox"):
                if len(opts) < 2: E.append(f"{vat}: {ty} needs at least two options, one per line")
                if len({o.strip().lower() for o in opts}) != len(opts): E.append(f"{vat}: duplicate options")
                if ml not in ("", None): W.append(f"{vat}.maxLength is ignored for {ty}")
            else:
                if opts: W.append(f"{vat}.options is ignored for {ty}")
                if ml not in ("", None) and not (isinstance(ml, int) and not isinstance(ml, bool) and ml > 0): E.append(f"{vat}.maxLength must be a positive whole number, or \"\" for no limit, for {ty}")
        if re.search(r"<script|javascript:", json.dumps(p), re.I): E.append(f"{at}: contains script content")
    return E, W

def report(path, E, W):
    print(f"### Scratchpad: Companion Prompt\n**Scope:** `{path}`\n\n| Errors | Warnings |\n|---|---|\n| {len(E)} | {len(W)} |")
    for label, items in (("Errors", E), ("Warnings", W)):
        if items:
            print(f"\n**{label}**"); [print(f"- {x}") for x in items]

def load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e: raise SystemExit(f"cannot read {p}: {e}")

def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 2
    if argv[0] == "--check":
        if len(argv) != 2: print(__doc__); return 2
        E, W = check(load(argv[1])); report(argv[1], E, W); return 1 if E else 0
    root, spec, out, force, i = Path(argv[0]).resolve(), None, None, False, 1
    while i < len(argv):
        a = argv[i]
        if a == "--spec" and i + 1 < len(argv): spec = load(argv[i + 1]); i += 1
        elif a == "--out" and i + 1 < len(argv): out = Path(argv[i + 1]); i += 1
        elif a == "--force": force = True
        else: print(__doc__); return 2
        i += 1
    if not root.is_dir(): print(f"not a directory: {root}"); return 2
    title, slug, desc, roles = info(root)
    target = root / "prompts" / f"{slugify(title)}.json"
    existing = load(target) if target.exists() else None
    if spec is not None or existing is None or force:
        if spec is not None and not (isinstance(spec, dict) and isinstance(spec.get("content"), str) and isinstance(spec.get("variables"), dict)):
            print("spec needs \"content\" (text) and \"variables\" (object)"); return 2
        old = (existing or {}).get("prompts", [{}])[0] if existing else None
        doc = build(spec or default_spec(title, slug, desc, roles), title, old)
        E, W = check(doc)
        if E: report(target, E, W); return 1
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        action = "written"
    else:
        doc, action = existing, "checked"
    E, W = check(doc)
    report(target.relative_to(root), E, W)
    if E: return 1
    if out:
        out.mkdir(parents=True, exist_ok=True); shutil.copyfile(target, out / target.name)
    print(f"\n| Item | Result |\n|---|---|\n| File | `{target}` ({action}) |" + (f"\n| Copied to | `{out / target.name}` |" if out else ""))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
