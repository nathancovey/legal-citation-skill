#!/usr/bin/env python3
"""Check that this skill stays within the open Agent Skills format.

    python3 test_skill_format.py

Agents that read the format (Claude, ChatGPT, OpenAI Codex, Cursor, Gemini CLI,
GitHub Copilot, and others) share a few hard rules. Breaking one can make an
agent skip the skill silently, so they are checked here rather than trusted.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  — {detail}" if detail and not ok else ""))


skill = open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read()
fm = re.match(r"---\n(.*?)\n---\n", skill, re.S)
check("SKILL.md starts with a frontmatter block", bool(fm))
front = fm.group(1) if fm else ""
fields = dict(re.findall(r"^([a-z-]+): (.*)$", front, re.M))
name, desc = fields.get("name", ""), fields.get("description", "")

check("name is lowercase letters, digits, and single hyphens",
      bool(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)), name)
check("name is at most 64 characters", 0 < len(name) <= 64, len(name))
check("name matches the folder name", name == os.path.basename(ROOT), f"{name} vs {os.path.basename(ROOT)}")
check("description is present and at most 1024 characters", 0 < len(desc) <= 1024, len(desc))
check("frontmatter has no angle brackets (some agents reject them)", "<" not in front and ">" not in front)
check("SKILL.md body stays under 500 lines", len(skill.splitlines()) < 500, len(skill.splitlines()))

for ref in sorted(set(re.findall(r"`((?:references|scripts)/[\w.-]+)`", skill))):
    check(f"{ref} exists", os.path.exists(os.path.join(ROOT, ref)))

version = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
check("VERSION is a plain x.y.z version", bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), version)
repo = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
for manifest in ("package.json", "plugins/legal-citation/.claude-plugin/plugin.json"):
    path = os.path.join(repo, manifest)
    if os.path.exists(path):  # only when run from the source repository
        found = re.search(r'"version":\s*"([^"]+)"', open(path, encoding="utf-8").read()).group(1)
        check(f"VERSION matches {manifest}", found == version, f"{found} vs {version}")

agent_specific = re.findall(r"\b(Claude Code|ChatGPT|Codex|Cursor|Gemini|Copilot)\b", skill.split("---", 2)[2])
check("instructions don't assume a particular agent", not agent_specific, agent_specific)

print("\nall passed" if not failures else f"\n{failures} failed")
sys.exit(1 if failures else 0)
