#!/bin/sh
# Install the Legal Citation Skill for AI agents. Needs only curl and tar.
#
#   curl -fsSL https://raw.githubusercontent.com/nathancovey/legal-citation-skill/main/install.sh | sh
#
# With no options it installs for every supported agent found on this computer.
# Options go after "sh -s --":
#   ... | sh -s -- --agent codex     a specific agent (repeatable): claude codex cursor gemini copilot agents
#   ... | sh -s -- --project         this project's skill folders instead of your home folder
#   ... | sh -s -- --dir <path>      any other agent's skills folder
#   ... | sh -s -- --force           replace an existing copy
set -eu

NAME=legal-citation
REPO=nathancovey/legal-citation-skill
REF=${LEGAL_CITATION_REF:-main}
agents=""
project=0
dir=""
force=0

usage() {
  echo "Usage: curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | sh -s -- [--agent <name>]... [--project] [--dir <path>] [--force]"
  echo "Agents: claude codex cursor gemini copilot agents"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --agent)
      [ $# -ge 2 ] || { echo "--agent needs a name" >&2; usage >&2; exit 1; }
      case "$2" in
        claude | codex | cursor | gemini | copilot | agents) agents="$agents $2" ;;
        *) echo "Unknown agent: $2" >&2; usage >&2; exit 1 ;;
      esac
      shift
      ;;
    --dir)
      [ $# -ge 2 ] || { echo "--dir needs a path" >&2; usage >&2; exit 1; }
      dir=$2
      shift
      ;;
    --project) project=1 ;;
    --force) force=1 ;;
    -h | --help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

# Where each agent reads skills. Cursor also reads the Claude Code and Codex
# folders, so it only gets its own copy when neither is present.
folder_for() {
  if [ "$project" -eq 1 ]; then
    case "$1" in
      claude) echo "$PWD/.claude/skills" ;;
      codex | agents) echo "$PWD/.agents/skills" ;;
      cursor) echo "$PWD/.cursor/skills" ;;
      gemini) echo "$PWD/.gemini/skills" ;;
      copilot) echo "$PWD/.github/skills" ;;
    esac
  else
    case "$1" in
      claude) echo "$HOME/.claude/skills" ;;
      codex) echo "$HOME/.codex/skills" ;;
      gemini) echo "$HOME/.gemini/skills" ;;
      copilot) echo "$HOME/.copilot/skills" ;;
      agents) echo "$HOME/.agents/skills" ;;
      cursor) echo "$HOME/.cursor/skills" ;;
    esac
  fi
}

targets=""
add_target() { printf '%s\n' "$targets" | grep -qxF "$1" || targets="$targets
$1"; }

if [ -n "$dir" ]; then
  [ -z "$agents" ] && [ "$project" -eq 0 ] || { echo "Use --dir on its own, without --agent or --project." >&2; exit 1; }
  add_target "$dir"
else
  if [ -z "$agents" ]; then
    for a in claude codex cursor gemini copilot; do
      [ -d "$HOME/.$a" ] && agents="$agents $a"
    done
    case "$agents" in
      *claude* | *codex*)
        case "$agents" in *cursor*)
          agents=$(echo "$agents" | sed 's/ cursor//')
          echo "Cursor will use the copy installed for Claude Code or Codex." ;;
        esac ;;
    esac
    [ -n "$agents" ] || { echo "No supported agent found on this computer. Pick one with --agent, or give its skills folder with --dir." >&2; usage >&2; exit 1; }
  fi
  for a in $agents; do
    f=$(folder_for "$a")
    add_target "$f"
  done
fi

# Only ever replace a folder that is recognizably this skill.
is_ours() { [ -f "$1/SKILL.md" ] && grep -q "^name: $NAME\$" "$1/SKILL.md"; }

for tool in curl tar; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool is required" >&2; exit 1; }
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
curl -fsSL "https://github.com/$REPO/archive/$REF.tar.gz" | tar -xz -C "$tmp"
src=$(find "$tmp" -type d -path "*/plugins/$NAME/skills/$NAME" | head -n 1)
[ -n "$src" ] && [ -f "$src/SKILL.md" ] || { echo "The download didn't contain the skill." >&2; exit 1; }

status=0
installed=0
printf '%s\n' "$targets" | sed '/^$/d' >"$tmp/targets"
while IFS= read -r root; do
  target="$root/$NAME"
  if [ -e "$target" ]; then
    if [ "$force" -ne 1 ]; then
      echo "$target already exists. Re-run with --force to replace it." >&2; status=1; continue
    fi
    is_ours "$target" || { echo "$target exists but isn't this skill; refusing to replace it." >&2; status=1; continue; }
    rm -rf "$target"
  fi
  mkdir -p "$root"
  cp -R "$src" "$target"
  echo curl >"$target/.installed-by" # lets the update notice show the right command
  echo "Installed: $target"
  installed=1
done <"$tmp/targets"

[ "$installed" -eq 1 ] && echo "Start a new agent session to pick it up."
exit "$status"
