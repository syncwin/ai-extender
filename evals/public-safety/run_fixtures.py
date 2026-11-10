#!/usr/bin/env python3
"""Fixture tests for the secret and private-data scan. Pure standard library. Exit 0 when every check passes.

Usage: run_fixtures.py
The fixtures hold no real or literal fake secrets: `*.tmpl` files carry @@KEY@@-style slots, and this script
assembles the fake values at run time inside a temporary folder. Checks:
  clean fixture passes (tree, git history, zip)
  leaky fixture fails (tree), a deleted key is still found in git history, a key inside a built zip is found,
  a committed .env is found, an allowlisted public contact passes.
"""
import os, subprocess, sys, tempfile, shutil, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCAN = HERE.parents[1] / "skills" / "aiaddon-review" / "scripts" / "scan_secrets.py"
FAKE = {
    "@@GITHUB@@": "gh" + "p_" + "Ab1" * 12,
    "@@OPENAI@@": "sk-" + "proj-" + "Qz7" * 10,
    "@@AWS@@": "AKIA" + "IOSFODNN7EXAMPLQ",
    "@@USERPATH@@": "C:" + "\\Users\\" + "jdoe42\\projects",
    "@@PASSWORD@@": "pass" + "word=" + "Tr0ub4dor3xyz",
}

def run(*a):
    r = subprocess.run([sys.executable, "-B", str(SCAN), *map(str, a)], capture_output=True, text=True)
    return r.returncode, r.stdout

def git(cwd, *a):
    subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull, "-C", str(cwd), *a], capture_output=True, text=True, check=True)  # no user hooks: the fixture repo is throwaway

def materialize(src, dst):
    shutil.copytree(src, dst)
    for f in list(dst.rglob("*.tmpl")):
        t = f.read_text(encoding="utf-8")
        for k, v in FAKE.items(): t = t.replace(k, v)
        target = f.with_suffix("")
        if target.name == "env.example": target = target.with_name(".env.example")  # kept as a template so tooling that blocks .env* files never sees one
        target.write_text(t, encoding="utf-8"); f.unlink()

results = []
def check(name, ok, detail=""):
    results.append(ok); print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail and not ok else ""))

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    clean, leaky = td / "clean", td / "leaky"
    materialize(HERE / "fixtures" / "clean", clean); materialize(HERE / "fixtures" / "leaky", leaky)
    rc, out = run(clean); check("clean fixture passes the scan", rc == 0, out[-300:])
    rc, out = run(leaky)
    check("fixture with fake keys fails the scan", rc == 1 and all(x in out for x in ("known key format", "absolute local user path", "password")), out[-500:])
    check("report masks the values", not any(v in out for v in FAKE.values()), out[-300:])
    # allowlist: an exact public contact passes, a key never does
    rc, out = run(clean); check("allowlisted public contact passes", rc == 0 and "support@example.org" in (clean / "README.md").read_text(encoding="utf-8"), out[-200:])
    # history: key committed, then deleted: working tree clean, history not
    try:
        g = td / "hist"; shutil.copytree(clean, g)
        git(g, "init", "-q"); git(g, "config", "user.email", "ci@example.org"); git(g, "config", "user.name", "ci"); git(g, "config", "commit.gpgsign", "false"); git(g, "add", "-A"); git(g, "commit", "-qm", "clean")
        (g / "leak.txt").write_text("token " + FAKE["@@GITHUB@@"] + "\n", encoding="utf-8"); git(g, "add", "-A"); git(g, "commit", "-qm", "add")
        (g / "leak.txt").unlink(); git(g, "add", "-A"); git(g, "commit", "-qm", "remove")
        rc0, _ = run(g); rc1, out1 = run(g, "--history")
        check("a deleted key is still found in git history", rc0 == 0 and rc1 == 1 and "commit" in out1 and FAKE["@@GITHUB@@"] not in out1, out1[-400:])
        (g / ".env").write_text("A=1\n", encoding="utf-8"); git(g, "add", "-f", ".env"); git(g, "commit", "-qm", "env")
        rc, out = run(g); check("a committed .env file is flagged", rc == 1 and ".env" in out, out[-300:])
    except (OSError, subprocess.CalledProcessError) as e:
        check("git history fixtures (git is required)", False, str(e))
    # artifacts: a key inside a built zip
    z = td / "built.zip"
    with zipfile.ZipFile(z, "w") as zf: zf.writestr("skills/x/SKILL.md", "ok\n"); zf.writestr("servers/x.py", "KEY = '" + FAKE["@@OPENAI@@"] + "'\n")
    rc, out = run(clean, "--artifacts", z); check("a key inside a built zip is found", rc == 1 and "built.zip" in out, out[-300:])
    zc = td / "clean.zip"
    with zipfile.ZipFile(zc, "w") as zf: zf.writestr("skills/x/SKILL.md", "ok\n")
    rc, out = run(clean, "--artifacts", zc); check("a clean zip passes", rc == 0, out[-300:])

print(f"\n{sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
