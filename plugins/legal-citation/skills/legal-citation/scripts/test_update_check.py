#!/usr/bin/env python3
"""Self-test for update_check.py. Never touches the network.

    python3 test_update_check.py

Copies the checker into a throwaway skill folder and points it at a fake
registry answer stored in a local file.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  — {detail}" if detail and not ok else ""))


def make_skill(root, version="1.4.0", installed_by=None):
    os.makedirs(os.path.join(root, "scripts"))
    shutil.copy(os.path.join(HERE, "update_check.py"), os.path.join(root, "scripts"))
    open(os.path.join(root, "VERSION"), "w").write(version + "\n")
    if installed_by:
        open(os.path.join(root, ".installed-by"), "w").write(installed_by + "\n")
    return root


def run(skill, latest, tmp, *code, extra_env=None):
    registry = os.path.join(tmp, "latest.json")
    json.dump({"version": latest}, open(registry, "w"))
    env = {k: v for k, v in os.environ.items() if k != "LEGAL_CITATION_NO_UPDATE_CHECK"}
    env.update(LEGAL_CITATION_UPDATE_URL="file://" + registry, TMPDIR=os.path.join(tmp, "t"))
    env.update(extra_env or {})
    os.makedirs(env["TMPDIR"], exist_ok=True)
    args = [sys.executable, "-c", code[0]] if code else [sys.executable, os.path.join(skill, "scripts", "update_check.py")]
    return subprocess.run(args, capture_output=True, text=True, cwd=os.path.join(skill, "scripts"), env=env)


NOTICE = "import update_check; print(update_check.notice())"


def main():
    with tempfile.TemporaryDirectory() as tmp:
        s = make_skill(os.path.join(tmp, "a", "legal-citation"))
        out = run(s, "1.5.0", tmp).stdout
        check("reports a newer version", "1.4.0 → 1.5.0" in out, out)
        check("suggests the npx update when the install method is unknown", "npx legal-citation-skill@latest --force" in out, out)

        s = make_skill(os.path.join(tmp, "w", "legal-citation"))
        first, second = run(s, "1.5.0", tmp, NOTICE).stdout, run(s, "1.5.0", tmp, NOTICE).stdout
        check("tools show it at most once a week", "1.5.0" in first and second.strip() == "None", f"{first!r} / {second!r}")

        s = make_skill(os.path.join(tmp, "b", "legal-citation"), installed_by="curl")
        out = run(s, "2.0.0", tmp).stdout
        check("gives the curl command for a curl install", "install.sh | sh -s -- --force" in out, out)

        s = make_skill(os.path.join(tmp, "plugins", "cache", "legal-citation"))
        out = run(s, "2.0.0", tmp).stdout
        check("gives the plugin command inside a plugin manager's folder", "/plugin update" in out, out)

        s = make_skill(os.path.join(tmp, "c", "legal-citation"))
        check("silent when up to date", "no newer version" in run(s, "1.4.0", tmp).stdout)
        check("silent when the registry is older", "no newer version" in run(s, "1.3.0", tmp).stdout)

        s = make_skill(os.path.join(tmp, "d", "legal-citation"))
        r = run(s, "9.9.9", tmp, NOTICE, extra_env={"LEGAL_CITATION_NO_UPDATE_CHECK": "1"})
        check("can be turned off", r.stdout.strip() == "None", r.stdout)

        s = make_skill(os.path.join(tmp, "e", "legal-citation"))
        r = run(s, "1.5.0", tmp, NOTICE, extra_env={"LEGAL_CITATION_UPDATE_URL": "file:///nonexistent/latest.json"})
        check("silent and harmless when offline", r.returncode == 0 and r.stdout.strip() == "None", r.stdout + r.stderr)

        s = make_skill(os.path.join(tmp, "f", "legal-citation"))
        os.chmod(s, stat.S_IRUSR | stat.S_IXUSR)
        try:
            r = run(s, "1.5.0", tmp, NOTICE)
        finally:
            os.chmod(s, stat.S_IRWXU)
        check("works when the skill folder is read-only", "1.5.0" in r.stdout, r.stdout + r.stderr)

    print("\nall passed" if not failures else f"\n{failures} failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
