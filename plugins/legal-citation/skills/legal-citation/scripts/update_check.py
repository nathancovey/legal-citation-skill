#!/usr/bin/env python3
"""Tell the user when a newer version of this skill exists. Never installs anything.

The skill's own tools call `notice()` when they finish, so the message shows up
the next time an agent uses them. Run directly to check now:

    python3 update_check.py

  - Asks the npm registry for the latest version: one small request with no
    user data, at most once every 7 days.
  - Silent on any failure: offline, sandboxed, slow network, read-only folder.
  - Turn it off with the environment variable LEGAL_CITATION_NO_UPDATE_CHECK=1.
"""

import json
import os
import sys
import tempfile
import time
import urllib.request

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = os.environ.get("LEGAL_CITATION_UPDATE_URL", "https://registry.npmjs.org/legal-citation-skill/latest")
WEEK = 7 * 24 * 3600
COMMANDS = {
    "npx": "npx legal-citation-skill@latest --force",
    "curl": "curl -fsSL https://raw.githubusercontent.com/nathancovey/legal-citation-skill/main/install.sh | sh -s -- --force",
    "plugin": "/plugin update legal-citation@legal-citation-skill",
}


def installed_version():
    with open(os.path.join(SKILL, "VERSION"), encoding="utf-8") as f:
        return f.read().strip()


def parse(version):
    return tuple(int(p) for p in version.split("-")[0].split(".")[:3])


def update_command():
    """The update command for however this copy was installed."""
    try:
        with open(os.path.join(SKILL, ".installed-by"), encoding="utf-8") as f:
            method = f.read().strip()
    except OSError:
        method = "plugin" if f"{os.sep}plugins{os.sep}" in SKILL else ""
    return COMMANDS.get(method, COMMANDS["npx"] + "  (or see the README for other ways)")


def state_file():
    for folder in (SKILL, tempfile.gettempdir()):
        path = os.path.join(folder, ".update-check.json")
        if os.access(folder, os.W_OK):
            return path
    return None


def latest_version():
    with urllib.request.urlopen(URL, timeout=2) as resp:
        return json.load(resp)["version"]


def notice(force=False):
    """A one-line update message, or None. Never raises."""
    try:
        if os.environ.get("LEGAL_CITATION_NO_UPDATE_CHECK"):
            return None
        path = state_file()
        if path and not force:
            try:
                with open(path, encoding="utf-8") as f:
                    if time.time() - json.load(f).get("checked", 0) < WEEK:
                        return None
            except (OSError, ValueError):
                pass
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"checked": time.time()}, f)
        current, latest = installed_version(), latest_version()
        if parse(latest) > parse(current):
            return (f"Update available for the Legal Citation Skill: {current} → {latest}. "
                    f"To update: {update_command()}")
    except Exception:  # noqa: BLE001 — an update check must never break the tool it rides on
        return None
    return None


def announce():
    """Print the notice, if any, after a tool's own output."""
    message = notice()
    if message:
        print(f"\n{message}", file=sys.stderr)


if __name__ == "__main__":
    message = notice(force=True)
    print(message or f"Legal Citation Skill {installed_version()}: no newer version found.")
