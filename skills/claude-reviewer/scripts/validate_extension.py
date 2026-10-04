#!/usr/bin/env python3
"""Validate a Claude extension (plugin or single skill). No dependencies.

Usage: validate_extension.py <dir> [--target all|claude-code|upload|cowork|directory]
                             [--require-meta author,company] [--must-contain <prefix>]
                             [--strict] [--json]
Exit: 0 pass, 1 errors (or warnings with --strict), 2 usage.
Complements (does not replace) `claude plugin validate`.
"""
import json, re, sys
from pathlib import Path

PLUGIN_KEYS = {"$schema","name","displayName","version","description","author","homepage","repository","license",
  "keywords","metadata","defaultEnabled","dependencies","settings","userConfig","channels","skills","commands",
  "agents","hooks","mcpServers","lspServers","outputStyles","workflows","experimental",
  "icon","documentationUrl","supportUrl","privacyPolicyUrl","termsOfServiceUrl","types"}
LISTING_URLS = ("documentationUrl","supportUrl","privacyPolicyUrl","termsOfServiceUrl")
UPLOAD_KEYS = {"name","description","license","compatibility","metadata","allowed-tools"}
EVENTS = set("""SessionStart Setup UserPromptSubmit UserPromptExpansion PreToolUse PermissionRequest PermissionDenied
PostToolUse PostToolUseFailure PostToolBatch Notification MessageDisplay SubagentStart SubagentStop TaskCreated
TaskCompleted Stop StopFailure TeammateIdle InstructionsLoaded ConfigChange CwdChanged DirectoryAdded FileChanged
WorktreeCreate WorktreeRemove PreCompact PostCompact PreModelSwitch PostModelSwitch Elicitation ElicitationResult
SessionEnd""".split())
HOOK_TYPES = {"command","http","mcp_tool","prompt","agent"}
COLORS = {"red","blue","green","yellow","purple","orange","pink","cyan"}
PLUGIN_IGNORED_AGENT_KEYS = {"permissionMode","mcpServers","hooks","initialPrompt"}
SECRET = re.compile(r"(Bearer\s+[A-Za-z0-9._\-]{20,}|sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9\-]{10,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
PLACEHOLDER = re.compile(r"\b(TODO|FIXME|TBD)\b|<!--\s*FILL|(?i:lorem ipsum)")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+([-+][0-9A-Za-z.\-]+)?$")

F = []  # findings
def add(sev, code, where, msg): F.append((sev, code, str(where), msg))

def parse_frontmatter(text):
    """Minimal YAML subset: scalars, folded/literal blocks, one-level maps, inline lists."""
    if not text.startswith("---\n"): return None, text
    end = text.find("\n---", 4)
    if end < 0: return None, text
    fm, body = text[4:end], text[end+4:].lstrip("\n")
    data, key, mode, buf = {}, None, None, []
    cur_map = None
    def flush():
        nonlocal key, mode, buf
        if key is not None and mode in ("fold","lit"):
            data[key] = (" " if mode == "fold" else "\n").join(s.strip() for s in buf).strip()
        key, mode, buf = None, None, []
    for raw in fm.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"): continue
        indent = len(raw) - len(raw.lstrip())
        if indent == 0 and ":" in raw:
            flush(); cur_map = None
            k, v = raw.split(":", 1); k, v = k.strip(), v.strip()
            if v in (">", "|", ">-", "|-"): key, mode = k, ("fold" if v[0] == ">" else "lit")
            elif v == "": data[k] = {}; cur_map = k
            else:
                if v.startswith("[") and v.endswith("]"): v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                else: v = v.strip("'\"")
                data[k] = v
        elif mode in ("fold","lit"): buf.append(raw)
        elif cur_map and ":" in raw:
            k, v = raw.strip().split(":", 1); data[cur_map][k.strip()] = v.strip().strip("'\"")
    flush()
    return data, body

MAX_SCAN = 2_000_000

def read(p):
    """Read text safely: skip symlinks and oversized files, tolerate BOM and CRLF."""
    try:
        if p.is_symlink() or p.stat().st_size > MAX_SCAN: return None
        return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    except (OSError, UnicodeDecodeError): return None

def load_json(p, code):
    t = read(p)
    if t is None: add("error", code, p, "unreadable"); return None
    try: return json.loads(t)
    except ValueError as e: add("error", code, p, f"invalid JSON: {e}"); return None

def check_skill(sdir, opts, plugin_files):
    sm = sdir / "SKILL.md"
    t = read(sm)
    if t is None: add("error", "S001", sdir, "missing SKILL.md"); return
    fm, body = parse_frontmatter(t)
    if fm is None: add("error", "S001", sm, "frontmatter missing or not closed (opening --- must be line 1)"); return
    name = fm.get("name", "")
    if not name: add("error", "S002", sm, "missing name")
    else:
        if name != sdir.name: add("error", "S002", sm, f"name '{name}' != folder '{sdir.name}'")
        if not SLUG.match(name) or len(name) > 64: add("error", "S002", sm, "name must be lowercase kebab-case, <=64 chars")
        if re.search(r"claude|anthropic", name):
            add("error" if opts["target"] == "upload" else "info", "S003", sm, "name contains a reserved word (claude/anthropic): rejected when the skill is uploaded on its own to claude.ai/API; fine as a plugin component")
        if opts["must"] and not name.startswith(opts["must"]): add("error", "S004", sm, f"name must start with '{opts['must']}' (project rule)")
    d = fm.get("description", "")
    if not d: add("error", "S005", sm, "missing description")
    else:
        if len(d) > 1024: add("error" if opts["target"] == "upload" else "warn", "S005", sm, f"description {len(d)} chars (>1024 API limit)")
        if len(d) + len(fm.get("when_to_use", "")) > 1536: add("warn", "S005", sm, "description+when_to_use >1536 chars: truncated in listing")
        if not re.search(r"\b(use|when|whenever|trigger)", d, re.I): add("warn", "S005", sm, "description lacks a 'when to use' cue")
    extra = set(fm) - UPLOAD_KEYS
    if extra:
        sev = "error" if opts["target"] == "upload" else "info"
        add(sev, "S006", sm, f"non-portable frontmatter keys {sorted(extra)}: fail claude.ai/API upload (fine in Claude Code plugins)")
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    for k in opts["meta"]:
        if not (meta.get(k) or fm.get(k)): add("error", "S007", sm, f"metadata.{k} required")
    if len(body.splitlines()) > 500: add("warn", "S008", sm, f"body {len(body.splitlines())} lines (>500): move detail to references/")
    if "scratchpad" not in (t.lower() + "".join((read(p) or "").lower() for p in (sdir/"references").glob("*.md") if (sdir/"references").exists())):
        add("warn", "S009", sm, "no scratchpad step (extension standard)")
    for f in sdir.rglob("*"):
        if f.is_symlink(): add("warn", "X002", f, "symlink skipped (not packaged or scanned)"); continue
        if f.is_file() and f.suffix in {".md",".py",".json",".sh",".js",".txt"}:
            c = read(f) or ""
            if PLACEHOLDER.search(c) and f.name != "validate_extension.py": add("error", "S010", f, "placeholder text (TODO/FIXME/TBD/FILL)")
            if SECRET.search(c): add("error", "X001", f, "looks like a literal secret")
            if f.suffix == ".md" and re.search(r"\]\([\w./-]*\\[\w./\\-]*\)", c): add("warn", "S014", f, "backslash path in a link: use forward slashes")
            if f.suffix == ".md" and f.parent.name == "references" and len(c.splitlines()) > 100 and not re.search(r"contents", c[:1500], re.I):
                add("warn", "S011", f, ">100 lines without a contents list (Anthropic guidance)")
    refs = sdir / "references"
    if refs.exists():
        for f in refs.glob("*.md"):
            if not any(f.name in (read(p) or "") for p in plugin_files): add("warn", "S012", f, "orphan reference (not mentioned anywhere)")
    for p in plugin_files:
        for tok in re.findall(r"`([a-z0-9\-]+/(?:references|scripts)/[\w.\-]+)`", read(p) or ""):
            if not (sdir.parent / tok).exists() and not (sdir.parent.parent / tok).exists():
                add("error", "S013", p, f"broken reference `{tok}`")

def check_agent(f):
    fm, _ = parse_frontmatter(read(f) or "")
    if not fm: add("warn", "A001", f, "no frontmatter: treated as documentation"); return
    n = fm.get("name", "")
    if not n: add("warn", "A001", f, "no name: loaded under filename only")
    if n.startswith("-") or ":" in n: add("error", "A002", f, "name cannot start with '-' or contain ':'")
    if not fm.get("description"): add("error", "A003", f, "missing description: file is skipped")
    if fm.get("color") and fm["color"] not in COLORS: add("warn", "A004", f, f"color '{fm['color']}' not in {sorted(COLORS)}")
    bad = PLUGIN_IGNORED_AGENT_KEYS & set(fm)
    if bad: add("warn", "A005", f, f"keys ignored for plugin agents: {sorted(bad)}")

def check_hooks(f):
    d = load_json(f, "H001")
    if not isinstance(d, dict): return
    mods = d.get("modules")
    if mods is not None:
        if not (isinstance(mods, list) and len(mods) == 1 and isinstance(mods[0], str)): add("error", "H006", f, "modules must be an array with exactly one path")
        else:
            mp = (f.parent / mods[0])
            if not mods[0].startswith("./") or ".." in mods[0]: add("error", "H006", f, f"module path '{mods[0]}' must start with ./ and stay inside the plugin")
            elif not mp.is_file(): add("error", "H006", f, f"hooks module '{mods[0]}' not found")
            elif mp.suffix not in {".js",".mjs",".cjs",".jsx",".ts",".mts",".cts",".tsx"}: add("error", "H006", f, "hooks module must be .js/.mjs/.cjs/.jsx/.ts/.mts/.cts/.tsx")
            elif "register" not in (read(mp) or ""): add("warn", "H007", mp, "hooks module should export register(on, options)")
    hooks = d.get("hooks", {k: v for k, v in d.items() if k not in ("modules", "description")})
    if not isinstance(hooks, dict): add("error", "H001", f, "hooks must be an object"); return
    for ev, groups in hooks.items():
        if ev not in EVENTS: add("error", "H002", f, f"unknown event '{ev}'")
        for g in (groups if isinstance(groups, list) else []):
            for h in (g.get("hooks", []) if isinstance(g, dict) else []):
                if not isinstance(h, dict): add("error", "H003", f, f"{ev}: handler must be an object"); continue
                if h.get("type") not in HOOK_TYPES: add("error", "H003", f, f"{ev}: bad handler type {h.get('type')}")
                c = h.get("command", "")
                if h.get("type") == "command" and "args" not in h and "${CLAUDE_PLUGIN_ROOT}" in c and '"${CLAUDE_PLUGIN_ROOT}' not in c and '\\"${CLAUDE_PLUGIN_ROOT}' not in c:
                    add("warn", "H004", f, f"{ev}: unquoted ${{CLAUDE_PLUGIN_ROOT}} in shell form; use exec form (args)")
                if "${user_config." in c and "args" not in h: add("error", "H005", f, f"{ev}: ${{user_config.*}} not allowed in shell-form command")
                if SECRET.search(json.dumps(h)): add("error", "X001", f, f"{ev}: literal secret")

def check_mcp(f, servers=None):
    d = servers if servers is not None else load_json(f, "M001")
    if d is None: return
    d = d.get("mcpServers", d) if isinstance(d, dict) else {}
    if not isinstance(d, dict): add("error", "M001", f, "mcpServers must be an object"); return
    for n, s in d.items():
        if not isinstance(s, dict) or not (s.get("command") or s.get("url")): add("error", "M002", f, f"server '{n}' needs command or url"); continue
        blob = json.dumps(s)
        if SECRET.search(blob): add("error", "M003", f, f"server '{n}': literal credential; use ${{VAR}} or ${{user_config.KEY}}")
        if re.search(r"\"(/home/|/Users/|[A-Z]:\\\\)", blob): add("warn", "M004", f, f"server '{n}': absolute path; use ${{CLAUDE_PLUGIN_ROOT}}")
        if s.get("url") and re.search(r"\$\{(ANTHROPIC_[A-Z_]+|AWS_[A-Z_]+|NPM_TOKEN|HTTPS_PROXY)", blob): add("warn", "M005", f, f"server '{n}': credential env var reads empty in remote url/headers")
        if str(s.get("url","")).startswith("http://") and "localhost" not in s["url"] and "127.0.0.1" not in s["url"]: add("warn", "M006", f, f"server '{n}': plain http")

def check_extras(root, m):
    """Workflows, themes, monitors, LSP, output styles, plugin settings, official eval suite."""
    for f in sorted((root / "workflows").glob("*.js")) if (root / "workflows").is_dir() else []:
        c = read(f) or ""
        first = next((l for l in c.splitlines() if l.strip() and not l.strip().startswith("//")), "")
        if not first.startswith("export const meta"): add("error", "W001", f, "first statement must be `export const meta = {...}`")
        mm = re.search(r"export const meta\s*=\s*\{(.*?)\}", c, re.S)
        if mm and not (re.search(r"name\s*:\s*['\"]", mm.group(1)) and re.search(r"description\s*:\s*['\"]", mm.group(1))): add("error", "W002", f, "meta needs literal name and description")
        if re.search(r"\bimport\s*\(|^\s*import\s", c, re.M): add("error", "W003", f, "workflow scripts cannot import modules")
        if re.search(r"Date\.now\(|Math\.random\(|new Date\(\)", c): add("error", "W004", f, "Date.now/Math.random/new Date() throw inside workflows; pass values via args")
    for f in sorted((root / "themes").glob("*.json")) if (root / "themes").is_dir() else []:
        d = load_json(f, "T001")
        if isinstance(d, dict) and not d.get("name"): add("error", "T002", f, "theme needs a name")
        elif d is not None and not isinstance(d, dict): add("error", "T002", f, "theme must be an object")
        if isinstance(d, dict):
            if "base" in d and not (isinstance(d["base"], str) and d["base"]): add("error", "T003", f, "theme base must be a preset name string such as dark or light")
            if "overrides" in d and not (isinstance(d["overrides"], dict) and all(isinstance(v, str) for v in d["overrides"].values())): add("error", "T004", f, "theme overrides must be an object of token to color string")
    mf = root / "monitors" / "monitors.json"
    if mf.exists():
        d = load_json(mf, "N001")
        for e in (d if isinstance(d, list) else []):
            if not (isinstance(e, dict) and e.get("name") and e.get("command") and e.get("description")): add("error", "N002", mf, "each monitor needs name, command, description")
            elif "${user_config." in e["command"]: add("error", "N003", mf, f"monitor '{e['name']}': ${{user_config.*}} unavailable in monitors")
        if d is not None and not isinstance(d, list): add("error", "N002", mf, "monitors.json must be an array")
    lf = root / ".lsp.json"
    if lf.exists():
        d = load_json(lf, "L001")
        for n, s in (d.items() if isinstance(d, dict) else []):
            e2l = s.get("extensionToLanguage") if isinstance(s, dict) else None
            if not (isinstance(s, dict) and s.get("command")): add("error", "L002", lf, f"'{n}': command required")
            elif " " in s["command"] and not s["command"].startswith("/"): add("error", "L002", lf, f"'{n}': command must be a binary name; put arguments in args")
            if not isinstance(e2l, dict) or not e2l or any(not str(k).startswith(".") for k in e2l): add("error", "L003", lf, f"'{n}': extensionToLanguage needs >=1 entry, keys starting with '.'")
    od = root / "output-styles"
    for f in sorted(od.glob("*.md")) if od.is_dir() else []:
        fm, _ = parse_frontmatter(read(f) or "")
        if not fm or not fm.get("name") or not fm.get("description"): add("warn", "O001", f, "output style should have name and description frontmatter")
    sj = root / "settings.json"
    if sj.exists():
        d = load_json(sj, "G001")
        extra = set(d) - {"agent", "subagentStatusLine"} if isinstance(d, dict) else set()
        if extra: add("warn", "G002", sj, f"plugin settings.json: only agent and subagentStatusLine take effect; dropped: {sorted(extra)}")
    ev = root / "evals"
    if ev.is_dir():
        for c in sorted(p for p in ev.iterdir() if p.is_dir() and p.name not in ("results", "mocks")):
            if (c / "prompt.md").exists() or (c / "case.yaml").exists():
                gs = list((c / "graders").glob("*.md")) if (c / "graders").is_dir() else []
                if not gs and "graders" not in (read(c / "case.yaml") or ""): add("error", "E001", c, "eval case has no graders (fails to load)")
                for g in gs:
                    fm, _ = parse_frontmatter(read(g) or "")
                    if not fm or fm.get("type") not in {"regex","tool_used","tool_order","file_exists","llm","baseline"}: add("error", "E002", g, f"grader type must be one of regex/tool_used/tool_order/file_exists/llm/baseline (got {fm.get('type') if fm else None})")
                pm, _ = parse_frontmatter(read(c / "prompt.md") or "") if (c / "prompt.md").exists() else ({}, "")
                for k in (pm or {}).get("env", {}) if isinstance((pm or {}).get("env"), dict) else []:
                    if not re.match(r"^EVAL_[A-Z0-9_]*$", k): add("error", "E003", c / "prompt.md", f"env key '{k}' must match EVAL_[A-Z0-9_]*")

LAUNCH_PIN = re.compile(r".+(@|==)v?\d+\.\d+\.\d+")
RESERVED_NAMES = {"claude","anthropic","official","plugin","mcp","test"}
DEVICE = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?$", re.I)
TEXTLIKE_IMG = {".png",".jpg",".jpeg",".gif",".webp"}
FONTS = {".ttf",".otf",".woff",".woff2"}

def launcher_issue(s):
    cmd = str(s.get("command", "")).split("/")[-1]; args = [str(a) for a in s.get("args", []) or []]
    if cmd in ("npx", "bunx", "uvx") or (cmd in ("pnpm", "yarn") and "dlx" in args) or (cmd == "pipx" and "run" in args):
        pkgs = [a for a in args if not a.startswith("-") and a not in ("dlx", "run")]
        return None if pkgs and LAUNCH_PIN.match(pkgs[0]) else "package launcher without an exact version pin"
    if cmd == "uv" and "run" in args and not ({"--locked", "--frozen"} & set(args)): return "uv run without --locked or --frozen"
    return None

def check_directory(root, m, name):
    """Anthropic directory pre-submission checks (claude.com/docs/plugins/pre-submission-checklist, 2026-10-03)."""
    if not re.match(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$", str(name)): add("error", "D001", root, f"name '{name}' must be ASCII lowercase letters/digits/hyphens, <=64, starting and ending alphanumeric")
    if name in RESERVED_NAMES: add("error", "D001", root, f"name '{name}' is a reserved word")
    rd = next((p for p in root.iterdir() if p.is_file() and p.name.lower().startswith("readme")), None)
    if rd is None: add("error", "D002", root, "README missing")
    else:
        words = len(re.sub(r"```.*?```", " ", read(rd) or "", flags=re.S).split())
        if words < 40: add("error", "D002", rd, f"README has {words} words outside code blocks (>=40 required)")
    if not (root / "LICENSE").exists() and not m.get("license"): add("error", "D003", root, "no LICENSE file and no license in plugin.json")
    files = [p for p in root.rglob("*") if ".git" not in p.relative_to(root).parts]
    seen = {}
    for p in files:
        rel = p.relative_to(root)
        if p.name in {".DS_Store", "Thumbs.db", "desktop.ini"} or "__MACOSX" in rel.parts: add("error", "D004", rel, "system file: remove")
        if p.is_symlink(): add("error", "D005", rel, "symbolic link: commit a regular file")
        if any(re.search(r'[:<>"|?*]|[. ]$', part) or DEVICE.match(part) for part in rel.parts): add("error", "D011", rel, "name invalid on Windows/macOS")
        low = rel.as_posix().lower()
        if low in seen: add("error", "D011", rel, f"differs only by case from {seen[low]}")
        seen[low] = rel.as_posix()
    regular = [p for p in files if p.is_file() and not p.is_symlink()]
    if len(regular) > 512: add("warn", "D006", root, f"{len(regular)} files (>512: held for a reviewer)")
    for p in regular:
        ext = p.suffix.lower(); rel = p.relative_to(root)
        if ext in TEXTLIKE_IMG or ext in FONTS: continue
        try: size = p.stat().st_size; p.read_bytes()[:4096].decode("utf-8")
        except UnicodeDecodeError: add("warn", "D006", rel, "binary file other than PNG/JPEG/GIF/WebP/font: held for a reviewer"); continue
        except OSError: continue
        if size > 256 * 1024: add("warn", "D006", rel, f"{size // 1024} KiB (>256 KiB non-image file: held for a reviewer)")
    servers = {}
    if (root / ".mcp.json").exists():
        d = load_json(root / ".mcp.json", "M001"); d = d.get("mcpServers", d) if isinstance(d, dict) else {}
        servers.update(d if isinstance(d, dict) else {})
    if isinstance(m.get("mcpServers"), dict): servers.update(m["mcpServers"])
    has_launcher = False
    for n, s in servers.items():
        if not isinstance(s, dict): continue
        iss = launcher_issue(s)
        if iss: add("error", "D007", root, f"server '{n}': {iss}"); has_launcher = True
        u = s.get("url")
        if u is not None and not (re.match(r"^(https|wss)://", str(u)) or str(u).startswith("${user_config.") or u == ""): add("error", "D009", root, f"server '{n}': url must be https://, wss://, a ${{user_config.*}} reference, or empty")
        if re.search(r"\.(mcpb|dxt)\b", json.dumps(s)): add("warn", "D010", root, f"server '{n}': .mcpb/.dxt bundles are held for a reviewer; declare command/args or url")
    if has_launcher:
        for cfg in (".npmrc", "bunfig.toml", "uv.toml"):
            if (root / cfg).exists(): add("error", "D008", root / cfg, "package-source config next to a launcher")

def check_prompts(root, name=""):
    """Prompt Builder companion prompt (prompts/*.json): created by claude-packager/scripts/companion_prompt.py."""
    pd = root / "prompts"
    files = sorted(pd.glob("*.json")) if pd.is_dir() else []
    if not files:
        add("info", "C000", root, "no companion prompt in prompts/: the packager creates one (companion_prompt.py)"); return
    try:
        sys.dont_write_bytecode = True  # never leave __pycache__ inside the plugin being checked
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "claude-packager" / "scripts"))
        from companion_prompt import check as cp_check
    except ImportError:
        add("info", "C000", pd, "companion prompt checker not found; skipped"); return
    for f in files:
        d = load_json(f, "C001")
        if d is None: continue
        E, W = cp_check(d)
        for e in E: add("error", "C002", f, e)
        for w in W: add("warn", "C003", f, w)
        slugs = set(re.findall(r"(?<![\w/])/([a-z0-9][a-z0-9-]*)(?::[a-z0-9-]+)?", " ".join(str(p.get("content", "")) for p in d.get("prompts", []) if isinstance(p, dict)))) if isinstance(d, dict) else set()
        if name and not (slugs & {name}): add("warn", "C004", f, f"prompt never starts the extension: add `/{name}` (or `/{name}:<skill>`) to its content")

def check_plugin(root, opts):
    pj = root / ".claude-plugin" / "plugin.json"
    m = load_json(pj, "P001")
    if not isinstance(m, dict):
        if m is not None: add("error", "P001", pj, "plugin.json must be a JSON object")
        return
    name = m.get("name", "")
    if not name: add("error", "P002", pj, "missing name")
    elif not SLUG.match(name): add("warn", "P002", pj, "name should be kebab-case")
    if name:
        n = re.sub(r"[-_.\s]+", "-", name.lower())
        if re.match(r"^(claude|anthropic|anthropics|cc-plugin)-", n) or n in ("claude", "anthropic", "anthropics", "claude-code", "claude-mods") \
                or re.search(r"(^|-)official(-|$)", n) and re.search(r"(^|-)(claude|anthropic)(-|$)", n):
            add("error", "P016", pj, f"plugin name '{name}' is reserved: it passes as one of Anthropic's own (claude plugin validate errors)")
        elif re.search(r"(^|-)(claude|anthropic|anthropics)(-|$)", n):
            add("warn", "P016", pj, f"plugin name '{name}' reads as one of Anthropic's own; put the brand in displayName instead")
    for k in LISTING_URLS:
        if k in m and not str(m[k]).startswith("https://"): add("error", "P017", pj, f"{k} must be an https:// URL")
    if "icon" in m and not (isinstance(m["icon"], str) and m["icon"].startswith("./") and (root / m["icon"]).is_file()): add("error", "P017", pj, "icon must be a ./path to an image file inside the plugin")
    for k in set(m) - PLUGIN_KEYS: add("warn", "P003", pj, f"unrecognized top-level key '{k}' (stripped by Claude Code)")
    if not m.get("displayName"): add("warn", "P004", pj, "no displayName (human-facing name)")
    if not m.get("description"): add("warn", "P004", pj, "no description")
    if not isinstance(m.get("author"), dict) or not m["author"].get("name"): add("warn", "P004", pj, "author.name missing")
    v = m.get("version", "")
    if not SEMVER.match(v): add("warn", "P005", pj, f"version '{v}' is not semver")
    for k in opts["meta"]:
        au = m.get("author", {}) if isinstance(m.get("author"), dict) else {}
        have = (m.get("metadata", {}) or {}).get(k) or au.get(k) or (au.get("name") if k == "author" else None)
        if not have: add("error", "P006", pj, f"{k} required in plugin metadata")
    for key in ("skills","commands","agents","outputStyles","workflows"):
        val = m.get(key)
        vals = [val] if isinstance(val, str) else (val if isinstance(val, list) else list(val.values()) if isinstance(val, dict) else [])
        for p in vals:
            p = p.get("source") if isinstance(p, dict) else p
            if not isinstance(p, str): continue
            if p not in (".", "./") and not p.startswith("./"): add("error", "P007", pj, f"{key}: path '{p}' must start with ./")
            elif ".." in p: add("error", "P007", pj, f"{key}: path '{p}' escapes plugin root")
            elif not (root / p).exists(): add("error", "P007", pj, f"{key}: path '{p}' not found")
            elif key == "agents" and not p.endswith(".md"): add("error", "P007", pj, "agents entries must be .md files")
    sk = root / "skills"
    sdirs = sorted(d for d in sk.iterdir() if d.is_dir() and not d.is_symlink()) if sk.is_dir() else []
    if sk.exists() and not sk.is_dir(): add("error", "P008", sk, "skills must be a directory")
    if not sdirs: add("warn", "P008", root, "no skills/ directory")
    if name and sdirs and not (sk / name / "SKILL.md").exists(): add("warn", "P009", sk, f"no router skill named '{name}' (router slug must equal plugin slug)")
    md_files = [p for p in root.rglob("*.md") if ".git" not in p.parts and not p.is_symlink() and p.name != "CHANGELOG.md"]
    for d in sdirs: check_skill(d, opts, md_files)
    meta = m.get("metadata") if isinstance(m.get("metadata"), dict) else {}
    if meta.get("version") and meta["version"] != v: add("warn", "P015", pj, f"metadata.version {meta['version']} != version {v}")
    if meta.get("displayName") and m.get("displayName") and meta["displayName"] != m["displayName"]: add("warn", "P015", pj, "metadata.displayName differs from displayName")
    for d in sdirs:
        fm, _ = parse_frontmatter(read(d / "SKILL.md") or "")
        sv = (fm or {}).get("metadata", {}).get("version") if isinstance((fm or {}).get("metadata"), dict) else None
        if sv and v and sv != v: add("warn", "S015", d / "SKILL.md", f"metadata.version {sv} != plugin version {v} (move them together)")
    if (root / "agents").exists():
        for f in (root / "agents").rglob("*.md"): check_agent(f)
    if (root / "hooks" / "hooks.json").exists(): check_hooks(root / "hooks" / "hooks.json")
    if (root / ".mcp.json").exists(): check_mcp(root / ".mcp.json")
    if isinstance(m.get("mcpServers"), dict): check_mcp(pj, m["mcpServers"])
    check_extras(root, m)
    check_prompts(root, name)
    if opts["target"] == "directory": check_directory(root, m, name)
    if (root / "CLAUDE.md").exists(): add("warn", "P010", root, "root CLAUDE.md is not loaded; put instructions in a skill")
    if (root / "bin").exists(): add("error" if opts["target"] == "cowork" else "warn", "P011", root / "bin", "claude.ai/Cowork do not install plugins containing bin/")
    lic = read(root / "LICENSE") if (root / "LICENSE").exists() else None
    if lic is None: add("warn", "P012", root, "no LICENSE file")
    elif m.get("license") == "MIT" and "MIT License" not in lic: add("warn", "P012", root, "LICENSE text does not match declared MIT")
    elif m.get("license", "").startswith("Apache") and "Apache License" not in lic: add("warn", "P012", root, "LICENSE text does not match declared Apache")
    for n in ("README.md","CHANGELOG.md"):
        if not (root / n).exists(): add("warn", "P013", root, f"missing {n}")
    cl = read(root / "CHANGELOG.md") or ""
    mv = re.search(r"^##\s*\[?v?(\d+\.\d+\.\d+)", cl, re.M)
    if cl and v and (not mv or mv.group(1) != v): add("warn", "P014", root / "CHANGELOG.md", f"top entry {mv.group(1) if mv else 'none'} != plugin version {v}")
    mk = root / ".claude-plugin" / "marketplace.json"
    if mk.exists():
        d = load_json(mk, "K001")
        if isinstance(d, dict):
            for k in ("name","owner","plugins"):
                if k not in d: add("error", "K002", mk, f"missing '{k}'")
            for e in d.get("plugins", []):
                if e.get("name") != name: add("error", "K003", mk, f"entry name '{e.get('name')}' != manifest name '{name}'")
                src = e.get("source")
                if isinstance(src, str) and (".." in src or not (root / src).exists()): add("error", "K004", mk, f"bad relative source '{src}'")

def main(argv):
    opts = {"target": "all", "meta": [], "must": "", "strict": False, "json": False}
    args, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a == "--target": opts["target"] = argv[i+1]; i += 1
        elif a == "--require-meta": opts["meta"] = [x for x in argv[i+1].split(",") if x]; i += 1
        elif a == "--must-contain": opts["must"] = argv[i+1]; i += 1
        elif a == "--strict": opts["strict"] = True
        elif a == "--json": opts["json"] = True
        elif a.startswith("-"): print(__doc__); return 2
        else: args.append(a)
        i += 1
    if len(args) != 1 or opts["target"] not in ("all","claude-code","upload","cowork","directory"): print(__doc__); return 2
    root = Path(args[0]).resolve()
    if not root.is_dir(): print(f"not a directory: {root}"); return 2
    if (root / ".claude-plugin" / "plugin.json").exists(): kind = "plugin"; check_plugin(root, opts)
    elif (root / "SKILL.md").exists(): kind = "skill"; check_skill(root, opts, [p for p in root.rglob("*.md")]); check_prompts(root, (parse_frontmatter(read(root / "SKILL.md") or "")[0] or {}).get("name", ""))
    else: print(f"not a plugin or skill directory: {root}"); return 2
    F[:] = list(dict.fromkeys(F))
    E = [f for f in F if f[0] == "error"]; W = [f for f in F if f[0] == "warn"]; I = [f for f in F if f[0] == "info"]
    if opts["json"]: print(json.dumps([dict(zip(("severity","code","where","message"), f)) for f in F], indent=2))
    else:
        print(f"### Scratchpad — Extension Validation\n**Scope:** {kind} `{root.name}`, target={opts['target']}\n")
        print(f"| Errors | Warnings | Info |\n|---|---|---|\n| {len(E)} | {len(W)} | {len(I)} |\n")
        for sev, items in (("Errors", E), ("Warnings", W), ("Info", I)):
            if items:
                print(f"**{sev}**")
                for _, c, w, m in items: print(f"- `{c}` {Path(w).relative_to(root) if Path(w).is_absolute() and root in Path(w).parents else w}: {m}")
        if not F: print("All checks passed.")
    return 1 if E or (opts["strict"] and W) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
