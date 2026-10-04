#!/usr/bin/env python3
"""Self-test for the builder's own scripts. Usage: selftest.py   (exit 0 = all passed)

Builds a fixture plugin with the scaffolder, checks the validator passes it, breaks it in known ways and
checks each break is caught, packages it in both formats, and exercises the eval aggregator and report.
"""
import json, subprocess, sys, tempfile, zipfile
from pathlib import Path

S = Path(__file__).resolve().parents[2]
RUN = lambda *a: subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)
V = S / "claude-reviewer/scripts/validate_extension.py"
results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    r = RUN(S / "claude-developer/scripts/scaffold_extension.py", td, "--slug", "ab-demo", "--display", "AB Demo", "--author", "@t", "--company", "Co", "--email", "a@b.co", "--roles", "developer", "--prefix", "ab", "--hooks", "--agents")
    check("scaffold ok", r.returncode == 0, r.stderr)
    p = td / "ab-demo"
    r = RUN(S / "claude-developer/scripts/scaffold_mcp_server.py", p, "--name", "ab-srv", "--lang", "python")
    check("mcp scaffold ok", r.returncode == 0, r.stderr)
    r = RUN(V, p, "--require-meta", "author,company")
    check("validator passes clean fixture", r.returncode == 0, r.stdout)

    def broken(label, code, mutate, args=()):
        import shutil
        q = td / ("b-" + label); shutil.copytree(p, q); mutate(q)
        r = RUN(V, q, *args); check(f"catches {label}", r.returncode == 1 and code in r.stdout, r.stdout[-300:])
    sk = lambda q: q / "skills/ab-developer/SKILL.md"
    broken("name mismatch", "S002", lambda q: sk(q).write_text(sk(q).read_text().replace("name: ab-developer", "name: other")))
    broken("missing description", "S005", lambda q: sk(q).write_text(sk(q).read_text().replace("description:", "desc:")))
    broken("literal secret", "X001", lambda q: (q / "skills/ab-developer/references").mkdir(exist_ok=True) or (q / "skills/ab-developer/references/x.md").write_text("key sk-" + "a" * 30))
    broken("placeholder text", "S010", lambda q: sk(q).write_text(sk(q).read_text() + "\nTODO finish\n"))
    broken("bad hook event", "H002", lambda q: (q / "hooks/hooks.json").write_text('{"hooks":{"Nope":[]}}'))
    broken("secret in mcp", "M003", lambda q: (q / ".mcp.json").write_text('{"mcpServers":{"x":{"url":"https://a.b/c","headers":{"Authorization":"Bearer ' + "a" * 30 + '"}}}}'))
    broken("upload-incompatible keys", "S006", lambda q: sk(q).write_text(sk(q).read_text().replace("license:", "model: sonnet\nlicense:")), ("--target", "upload"))
    broken("bad manifest path", "P007", lambda q: (q / ".claude-plugin/plugin.json").write_text(json.dumps({**json.loads((q / ".claude-plugin/plugin.json").read_text()), "agents": ["./nope.md"]})))

    # robustness
    import os, shutil
    q = td / "crlf"; shutil.copytree(p, q); s = sk(q); s.write_bytes(b"\xef\xbb\xbf" + s.read_text().replace("\n", "\r\n").encode())
    r = RUN(V, q, "--require-meta", "author,company"); check("accepts BOM + CRLF skill files", r.returncode == 0, r.stdout[-300:])
    q = td / "arr"; shutil.copytree(p, q); (q / ".claude-plugin/plugin.json").write_text("[]")
    r = RUN(V, q); check("rejects non-object plugin.json", r.returncode == 1 and "P001" in r.stdout, r.stdout[-200:])
    q = td / "badjson"; shutil.copytree(p, q); (q / ".claude-plugin/plugin.json").write_text("{nope")
    r = RUN(V, q); check("rejects invalid JSON", r.returncode == 1 and "P001" in r.stdout, r.stdout[-200:])
    q = td / "hookobj"; shutil.copytree(p, q); (q / "hooks/hooks.json").write_text('{"hooks":{"Stop":[{"hooks":["x"]}]}}')
    r = RUN(V, q); check("rejects non-object hook handler without crashing", r.returncode == 1 and "H003" in r.stdout and "Traceback" not in r.stderr, r.stderr[-200:])
    r = RUN(V, td / "does-not-exist"); check("missing dir exits 2", r.returncode == 2)
    (td / "empty").mkdir(); r = RUN(V, td / "empty"); check("empty dir exits 2", r.returncode == 2)
    q = td / "sym"; shutil.copytree(p, q)
    try:
        os.symlink("/etc/hostname", q / "leak.md"); r = RUN(S / "claude-packager/scripts/package_extension.py", q, "--format", "zip", "--out", td / "o2")
        names = zipfile.ZipFile(next((td / "o2").glob("*.zip"))).namelist()
        check("packager skips symlinks", r.returncode == 0 and not any(n.endswith("leak.md") for n in names), str(names))
    except OSError: check("packager skips symlinks (symlinks unsupported here, skipped)", True)
    q = td / "nover"; shutil.copytree(p, q); m = json.loads((q / ".claude-plugin/plugin.json").read_text()); m.pop("version"); (q / ".claude-plugin/plugin.json").write_text(json.dumps(m))
    r = RUN(S / "claude-packager/scripts/package_extension.py", q, "--format", "zip", "--skip-validate", "--out", td / "o3"); check("packager defaults missing version", r.returncode == 0 and any("v0.0.1" in x.name for x in (td / "o3").glob("*.zip")), r.stdout + r.stderr)
    r = RUN(S / "claude-reviewer/scripts/simulate.py", p, "install"); check("simulator: install", r.returncode == 0 and "Router skill = plugin name | yes" in r.stdout, r.stdout[-400:])
    r = RUN(S / "claude-reviewer/scripts/simulate.py", S.parent, "triggers"); check("simulator: builder triggers", r.returncode == 0, r.stdout[-400:])
    r = RUN(S / "claude-reviewer/scripts/simulate.py", S.parent, "install"); check("simulator: builder install", r.returncode == 0, r.stdout[-400:])

    def mk(label, files):
        q = td / ("x-" + label); shutil.copytree(p, q)
        for rel, body in files.items():
            (q / rel).parent.mkdir(parents=True, exist_ok=True); (q / rel).write_text(body)
        return q
    good_wf = "export const meta = { name: 'a', description: 'b' }\nconst r = await agent('x')\nreturn r\n"
    r = RUN(V, mk("wf-ok", {"workflows/a.js": good_wf})); check("accepts valid workflow", r.returncode == 0, r.stdout[-300:])
    r = RUN(V, mk("wf-import", {"workflows/a.js": good_wf + "import x from 'y'\n"})); check("rejects workflow import", r.returncode == 1 and "W003" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("wf-date", {"workflows/a.js": good_wf + "const t = Date.now()\n"})); check("rejects Date.now in workflow", r.returncode == 1 and "W004" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("wf-meta", {"workflows/a.js": "const x = 1\n"})); check("rejects workflow without meta", r.returncode == 1 and "W001" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("lsp-bad", {".lsp.json": '{"go":{"command":"gopls serve","extensionToLanguage":{"go":"go"}}}'})); check("rejects bad LSP config", r.returncode == 1 and "L002" in r.stdout and "L003" in r.stdout, r.stdout[-300:])
    r = RUN(V, mk("mon-bad", {"monitors/monitors.json": '[{"name":"x","command":"echo ${user_config.k}","description":"d"}]'})); check("rejects user_config in monitor", r.returncode == 1 and "N003" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("theme-bad", {"themes/t.json": '{"base":"dark"}'})); check("rejects nameless theme", r.returncode == 1 and "T002" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("eval-nograder", {"evals/c1/prompt.md": "---\nmax_turns: 5\n---\n\nhi\n"})); check("rejects eval case without graders", r.returncode == 1 and "E001" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("eval-badtype", {"evals/c1/prompt.md": "hi\n", "evals/c1/graders/g.md": "---\ntype: magic\n---\n"})); check("rejects unknown grader type", r.returncode == 1 and "E002" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("settings-extra", {"settings.json": '{"agent":"a","model":"x"}'})); check("warns on dropped plugin settings keys", "G002" in r.stdout, r.stdout[-200:])

    r = RUN(V, mk("mod-ok", {"hooks/hooks.json": '{"modules": ["./register.js"]}', "hooks/register.js": "export function register(on) {}\n"})); check("accepts a valid mod", r.returncode == 0, r.stdout[-300:])
    r = RUN(V, mk("mod-missing", {"hooks/hooks.json": '{"modules": ["./register.js"]}'})); check("rejects missing hooks module", r.returncode == 1 and "H006" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("mod-two", {"hooks/hooks.json": '{"modules": ["./a.js", "./b.js"]}'})); check("rejects more than one module path", r.returncode == 1 and "H006" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("theme-base", {"themes/t.json": '{"name":"x","base":7}'})); check("rejects non-string theme base", r.returncode == 1 and "T003" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("dir-short", {}), "--target", "directory"); check("directory: short README blocks", r.returncode == 1 and "D002" in r.stdout, r.stdout[-200:])
    long_readme = "# Demo\n\n" + " ".join(["word"] * 60) + "\n"
    r = RUN(V, mk("dir-ok", {"README.md": long_readme}), "--target", "directory"); check("directory: clean fixture passes", r.returncode == 0, r.stdout[-300:])
    r = RUN(V, mk("dir-npx", {"README.md": long_readme, ".mcp.json": '{"mcpServers":{"x":{"command":"npx","args":["-y","some-pkg@latest"]}}}'}), "--target", "directory"); check("directory: unpinned npx blocks", r.returncode == 1 and "D007" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("dir-pinned", {"README.md": long_readme, ".mcp.json": '{"mcpServers":{"x":{"command":"npx","args":["-y","some-pkg@1.2.3"]}}}'}), "--target", "directory"); check("directory: pinned npx passes", r.returncode == 0, r.stdout[-300:])
    r = RUN(V, mk("dir-sys", {"README.md": long_readme, ".DS_Store": "x"}), "--target", "directory"); check("directory: system file blocks", r.returncode == 1 and "D004" in r.stdout, r.stdout[-200:])
    r = RUN(V, mk("dir-http", {"README.md": long_readme, ".mcp.json": '{"mcpServers":{"x":{"type":"http","url":"http://example.com/mcp"}}}'}), "--target", "directory"); check("directory: non-https MCP url blocks", r.returncode == 1 and "D009" in r.stdout, r.stdout[-200:])

    for fmt in ("plugin", "zip"):
        r = RUN(S / "claude-packager/scripts/package_extension.py", p, "--format", fmt, "--out", td / "out")
        ext = ".plugin" if fmt == "plugin" else ".zip"
        f = td / "out" / f"AB Demo v0.0.1{ext}"
        check(f"package {fmt}", r.returncode == 0 and f.exists(), r.stdout + r.stderr)
        if f.exists():
            names = zipfile.ZipFile(f).namelist()
            check(f"{fmt} archive root", (".claude-plugin/plugin.json" in names) if fmt == "plugin" else ("ab-demo/.claude-plugin/plugin.json" in names))
    it = td / "it"
    for e in ("e1", "e2"):
        for c in ("with", "baseline"):
            d = it / e / c; d.mkdir(parents=True)
            (d / "grading.json").write_text(json.dumps({"expectations": [{"text": "t", "passed": c == "with", "evidence": "x"}]}))
            (d / "timing.json").write_text('{"total_tokens": 100, "duration_ms": 1000}')
    r = RUN(S / "claude-developer/scripts/aggregate_results.py", it); check("aggregate", r.returncode == 0 and "+100%" in r.stdout, r.stdout)
    r = RUN(S / "claude-developer/scripts/eval_report.py", it); check("eval report", r.returncode == 0 and (it / "report.html").exists(), r.stdout)
    r = RUN(V, S.parent, "--require-meta", "author,company"); check("builder validates itself", r.returncode == 0, r.stdout[-400:])
    r = RUN(V, S.parent, "--target", "directory", "--strict"); check("builder passes directory checks", r.returncode == 0, r.stdout[-400:])

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
