#!/usr/bin/env python3
"""Secret and private-data engine shared by scan_secrets.py and validate_extension.py. Pure standard library.

Finds, in text, file names, git history and built packages: provider keys and tokens (GitHub, OpenAI, Anthropic,
AWS, Slack, Google), private keys, Bearer tokens, password/secret assignments, high-entropy strings, personal
e-mail addresses, absolute user paths (Windows, macOS, Linux), internal hosts, and files that must never be published
(.env, keys, logs, memory or progress notes). Every finding is blocking. Values are always masked in reports.

Allowlist file (default `.public-safety-allow` at the scanned root), one rule per line, `#` starts a comment:
    <rule>:<path-glob>[:<value-substring>]       e.g.  email:README.md:support@example.org
    <rule> is a rule id or `*`; <path-glob> uses * and ? against the repo-relative path with forward slashes.
Only the exact false positives belong there; never a real credential (rotate that instead).
"""
import fnmatch, math, re, subprocess, sys, zipfile, io
from pathlib import Path

sys.dont_write_bytecode = True

MAX_BYTES = 2_000_000
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
ALLOW_FILE = ".public-safety-allow"

# (rule id, label, regex). First match on a line wins: one finding per line.
KEY_RULES = [
    ("github-token", "GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("anthropic-key", "Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai-key", "OpenAI-style key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_\-]{20,}")),
    ("aws-key", "AWS access key id", re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b")),
    ("slack-token", "Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9\-]{10,}")),
    ("google-key", "Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("google-oauth", "Google OAuth token", re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}")),
    ("private-key", "private key block", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("bearer", "Bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/\-]{20,}=*")),
]
PLACEHOLDER = re.compile(r"(?i)(env|config|process|getenv|example|your|placeholder|xxxx|\*\*\*|changeme|dummy|redacted|sample|user_config|plugin_root|none|null|false|true|string|secret_value|<|>|\$\{|\$\(|%\w+%|\{\{)")
ASSIGN = re.compile(r"""(?i)\b([\w-]*?(?:api[_-]?key|apikey|secret|token|passw(?:or)?d|passwd|pwd|access[_-]?key|private[_-]?key))["']?\s*[:=]\s*["']?([^\s"'`<>,;(){}\[\]]{6,})""")
BASIC = re.compile(r"""(?i)Authorization["']?\s*:\s*["']Basic\s+([A-Za-z0-9+/=]{16,})""")
TOKENISH = re.compile(r"[A-Za-z0-9+/=_\-]{32,}")
EMAIL = re.compile(r"(?<![\w.%+\-])([A-Za-z0-9][A-Za-z0-9._%+\-]*)@((?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,})\b")
EMAIL_LOCAL_OK = {"git", "you", "user", "name", "your", "email", "someone", "me", "x", "a", "foo", "bar", "test", "info@example"}
EMAIL_DOMAIN_OK = re.compile(r"(?i)(^|\.)(example\.(com|org|net)|example|invalid|localhost|test|users\.noreply\.github\.com|noreply\.github\.com|domain\.com|company\.com|yourdomain\.com|email\.com)$")
EMAIL_NOREPLY = re.compile(r"(?i)no-?reply|do-?not-?reply|^your[-_.]|[-_.]your$|placeholder|<|>|\.\.\.")
USER_PATH = [
    re.compile(r"(?i)\b[A-Z]:[\\/]+Users[\\/]+([^\\/\s\"'`<>*|:?]+)"),
    re.compile(r"(?<![\w.~])/(?:Users|home)/([^/\s\"'`<>*|:?]+)"),
]
USER_OK = re.compile(r"(?i)^(public|default|default user|all users|user|username|you|your|yourname|name|me|example|runner|ubuntu|root|vsts|admin|someone|%\w+%|\$\w+|\{.*\}|<.*>|\.\.\.|x+|ci|node|app|claude|\*)$")
INTERNAL_HOST = re.compile(r"(?i)\bhttps?://(?:(?:10|127\.0\.0|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.[\d.]+|[\w\-.]+\.(?:internal|corp|lan|intranet|local))(?:[:/\s\"'`)]|$)")
PRIVATE_NAMES = [
    (".env", "environment file"), (".env.*", "environment file"), ("*.pem", "key file"), ("*.key", "key file"),
    ("*.p12", "key store"), ("*.pfx", "key store"), ("id_rsa", "ssh key"), ("id_rsa.*", "ssh key"), ("id_ed25519", "ssh key"),
    ("id_ecdsa", "ssh key"), ("credentials.json", "credentials"), ("service-account*.json", "credentials"),
    ("*.log", "log file"), (".npmrc", "registry credentials"), (".pypirc", "registry credentials"), (".netrc", "credentials"),
    ("memory.md", "memory note"), ("progress.md", "progress note"), ("*.progress.md", "progress note"),
]
GITIGNORE_PRESET = """# --- public-safety preset: private data never reaches git ---
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
id_rsa*
id_ed25519*
credentials*.json
service-account*.json
secrets.*
*.log
logs/
memory/
.claude/memory/
.claude/progress/
progress*.md
*.local.md
.claude/settings.local.json
.npmrc
.pypirc
.netrc
private/
# --- end public-safety preset ---
"""
GITIGNORE_REQUIRED = [l for l in GITIGNORE_PRESET.splitlines() if l and not l.startswith("#")]
ENV_VALUE = re.compile(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*(\S+)", re.M)

def env_values(text):
    """Variables in an .env.example that carry a value (names only are allowed; <...>, empty and ${...} are fine)."""
    return [m.group(0).strip() for m in ENV_VALUE.finditer(text) if not re.match(r"^(<.*>|\$\{.*\}|\"\"|\'\')$", m.group(1))]

PRIVATE_OK = (".env.example", ".env.sample", ".env.template")
PRIVATE_DIRS = ("memory/", ".claude/memory/", ".claude/progress/", "logs/")

def entropy(s):
    return -sum(c / len(s) * math.log2(c / len(s)) for c in (s.count(x) for x in set(s)))

def mask(v):
    v = str(v)
    return v[:4] + "..." if len(v) > 8 else v[:2] + "..."

def mask_email(local, domain):
    return local[:2] + "***@" + domain

def scan_line(line):
    """First finding on the line: (rule, label, masked) or None."""
    for rule, label, rx in KEY_RULES:
        m = rx.search(line)
        if m: return rule, label, mask(m.group(0))
    m = BASIC.search(line)
    if m: return "basic-auth", "Basic authorization", mask(m.group(1))
    for g in ASSIGN.finditer(line):
        v = g.group(2)
        if PLACEHOLDER.search(v): continue
        key = g.group(1).lower()
        if "pass" in key or "pwd" in key:
            if len(v) >= 6 and not v.startswith(("$", "%")): return "password", "password assignment", g.group(1) + "=" + mask(v)
        elif re.search(r"\d", v) and re.search(r"[A-Za-z]", v) and len(set(v)) > 8:
            return "key-assignment", "key-like value", g.group(1) + "=" + mask(v)
    for m in EMAIL.finditer(line):
        local, dom = m.group(1), m.group(2)
        if local.lower() in EMAIL_LOCAL_OK or EMAIL_DOMAIN_OK.search(dom) or EMAIL_NOREPLY.search(local) or dom.lower().endswith((".md", ".json", ".py", ".yml", ".yaml", ".txt", ".js")): continue
        return "email", "personal e-mail address", mask_email(local, dom)
    for rx in USER_PATH:
        for m in rx.finditer(line):
            if not USER_OK.match(m.group(1)): return "user-path", "absolute local user path", m.group(0)[:3] + "..." + m.group(1)[:2] + "***"
    m = INTERNAL_HOST.search(line)
    if m: return "internal-host", "internal URL or host", mask(m.group(0))
    for m in TOKENISH.finditer(line):
        t = m.group(0)
        if "/" in t.strip("/") and t.count("/") > 1: continue
        if re.fullmatch(r"[0-9a-fA-F]+", t) or not (re.search(r"[a-z]", t) and re.search(r"[A-Z]", t) and re.search(r"\d", t)) or PLACEHOLDER.search(t): continue
        if "-" in t and t.count("-") > 2: continue
        if entropy(t) >= 4.5: return "high-entropy", "high-entropy string", mask(t)
    return None

def private_name(rel):
    """(rule, label) when the file name or folder says the file must never be published."""
    rel = rel.replace("\\", "/")
    name = rel.rsplit("/", 1)[-1]
    if name in PRIVATE_OK or name.endswith(PRIVATE_OK): return None
    for pat, label in PRIVATE_NAMES:
        if fnmatch.fnmatch(name, pat): return "private-file", label
    if any(rel.startswith(d) or ("/" + d) in rel for d in PRIVATE_DIRS): return "private-file", "private notes or logs folder"
    return None

def load_allowlist(path):
    rules = []
    try: lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError: return rules
    for l in lines:
        l = l.strip()
        if not l or l.startswith("#"): continue
        parts = l.split(":", 2)
        if len(parts) < 2: continue
        rules.append((parts[0].strip(), parts[1].strip(), parts[2].strip() if len(parts) > 2 else ""))
    return rules

def is_text(b):
    return b"\0" not in b[:2048]

def scan_text(rel, text, rules, where=""):
    """Yield dict findings for one text; one per line."""
    for no, line in enumerate(text.splitlines(), 1):
        if len(line) > 4000: line = line[:4000]
        f = scan_line(line)
        if not f: continue
        rule, label, masked = f
        if allowed_text(rules, rule, rel, line, masked): continue
        yield {"file": rel, "line": no, "rule": rule, "kind": label, "value": masked, "where": where}

def allowed_text(rules, rule, rel, line, masked):
    rel = rel.replace("\\", "/")
    for r, g, v in rules:
        if r not in ("*", rule): continue
        if not (fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel.rsplit("/", 1)[-1], g)): continue
        if v and v not in line: continue
        return True
    return False

def git_files(root):
    """Files git would publish: tracked plus untracked-not-ignored. None when root is not a git work tree."""
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError): return None
    if r.returncode != 0: return None
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode == 0 and Path(top.stdout.strip()).resolve() != Path(root).resolve(): return None
    return [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x]

def scan_tree(root, rules, include_artifacts=True):
    root = Path(root)
    names = git_files(root)
    if names is None:
        names = []
        for f in sorted(root.rglob("*")):
            rel = f.relative_to(root)
            if set(rel.parts) & SKIP_DIRS or not f.is_file() or f.is_symlink(): continue
            names.append(rel.as_posix())
    for rel in names:
        f = root / rel
        if set(Path(rel).parts) & SKIP_DIRS or f.is_symlink() or not f.is_file(): continue
        pn = private_name(rel)
        if pn and not allowed_text(rules, pn[0], rel, "", ""):
            yield {"file": rel, "line": 0, "rule": pn[0], "kind": pn[1] + " (must not be published)", "value": f.name, "where": ""}
        try:
            if f.stat().st_size > MAX_BYTES: continue
            data = f.read_bytes()
        except OSError: continue
        if f.suffix in (".zip", ".plugin") and include_artifacts:
            yield from scan_zip_bytes(data, rel, rules); continue
        if not is_text(data): continue
        yield from scan_text(rel, data.decode("utf-8-sig", "replace"), rules)

def scan_zip_bytes(data, label, rules, depth=0):
    try: zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile: return
    with zf:
        for n in zf.namelist():
            if n.endswith("/") or set(n.split("/")) & SKIP_DIRS: continue
            full = f"{label}!{n}"
            pn = private_name(n)
            if pn and not allowed_text(rules, pn[0], n, "", ""):
                yield {"file": full, "line": 0, "rule": pn[0], "kind": pn[1] + " (inside package)", "value": Path(n).name, "where": ""}
            info = zf.getinfo(n)
            if info.file_size > MAX_BYTES: continue
            b = zf.read(n)
            if n.endswith((".zip", ".plugin")) and depth < 2: yield from scan_zip_bytes(b, full, rules, depth + 1); continue
            if is_text(b): yield from scan_text(n, b.decode("utf-8-sig", "replace"), rules, where=label)

def scan_artifacts(paths, rules):
    """Zips and .plugin files: each given file, or every one found under a given folder (dist included)."""
    for p in map(Path, paths):
        files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.suffix in (".zip", ".plugin") and not x.is_symlink()) if p.is_dir() else []
        for f in files:
            try: data = f.read_bytes()
            except OSError: continue
            for r in scan_zip_bytes(data, f.name, rules): yield r

def scan_history(repo, rules):
    """Every line ever added on any ref (`git log --all -p`), plus private files ever committed."""
    try:
        p = subprocess.Popen(["git", "-C", str(repo), "log", "--all", "-p", "--no-color", "--no-ext-diff", "--format=%x01%h"],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError: return
    commit = file = ""; new = 0; seen = {}
    for raw in p.stdout:
        line = raw.decode("utf-8", "replace").rstrip("\n")
        if line.startswith("\x01"): commit = line[1:]; file = ""; continue
        if line.startswith("+++ "):
            file = line[6:] if line.startswith("+++ b/") else ""
            if file:
                pn = private_name(file)
                if pn and not allowed_text(rules, pn[0], file, "", ""):
                    k = (pn[0], file)
                    if k not in seen: seen[k] = 1; yield {"file": file, "line": 0, "rule": pn[0], "kind": pn[1] + " (committed in history)", "value": Path(file).name, "where": "commit " + commit}
            continue
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)", line); new = int(m.group(1)) if m else 0; continue
        if line.startswith("+") and file:
            for f in scan_text(file, line[1:], rules, where="commit " + commit):
                f["line"] = new
                k = (f["rule"], f["file"], f["value"])
                if k not in seen: seen[k] = 1; yield f
            new += 1
        elif line.startswith(" "): new += 1
    p.wait()
