#!/bin/sh
# Install the Legal Citation Skill for an AI agent. Needs only curl and tar.
#
#   curl -fsSL https://raw.githubusercontent.com/nathancovey/legal-citation-skill/main/install.sh | sh
#
# Options go after "sh -s --":
#   ... | sh -s -- --project       install to ./.claude/skills (this project only)
#   ... | sh -s -- --dir <path>    install to <path> (another agent's skills folder)
#   ... | sh -s -- --force         replace an existing copy
set -eu

NAME=legal-citation
REPO=nathancovey/legal-citation-skill
REF=${LEGAL_CITATION_REF:-main}
dest="$HOME/.claude/skills"
force=0

usage() {
  echo "Usage: curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | sh -s -- [--project | --dir <path>] [--force]"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --project) dest="$PWD/.claude/skills" ;;
    --dir)
      [ $# -ge 2 ] || { echo "--dir needs a path" >&2; usage >&2; exit 1; }
      dest=$2
      shift
      ;;
    --force) force=1 ;;
    -h | --help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

target="$dest/$NAME"

# Only ever replace a folder that is recognizably this skill.
is_ours() { [ -f "$1/SKILL.md" ] && grep -q "^name: $NAME\$" "$1/SKILL.md"; }

if [ -e "$target" ]; then
  [ "$force" -eq 1 ] || { echo "$target already exists. Re-run with --force to replace it." >&2; exit 1; }
  is_ours "$target" || { echo "$target exists but isn't this skill; refusing to replace it." >&2; exit 1; }
fi

for tool in curl tar; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool is required" >&2; exit 1; }
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "https://github.com/$REPO/archive/$REF.tar.gz" | tar -xz -C "$tmp"
src=$(find "$tmp" -type d -path "*/plugins/$NAME/skills/$NAME" | head -n 1)
[ -n "$src" ] && [ -f "$src/SKILL.md" ] || { echo "The download didn't contain the skill." >&2; exit 1; }

mkdir -p "$dest"
[ -e "$target" ] && rm -rf "$target"
cp -R "$src" "$target"

echo "Installed the Legal Citation Skill to $target"
echo "Start a new agent session to pick it up."
