#!/usr/bin/env node
/**
 * Install the Legal Citation Skill into an agent's skills folder.
 *
 *   npx legal-citation-skill                  ~/.claude/skills/legal-citation
 *   npx legal-citation-skill --project        ./.claude/skills/legal-citation
 *   npx legal-citation-skill --dir <path>     <path>/legal-citation  (any agent)
 *   npx legal-citation-skill --uninstall      remove it again (same flags)
 *
 * No dependencies and no install-time scripts: nothing runs unless you run it.
 */
import { cpSync, existsSync, readFileSync, rmSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const NAME = "legal-citation";
const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "..", "plugins", NAME, "skills", NAME);

const USAGE = `Install the Legal Citation Skill for an AI agent.

Usage:
  npx legal-citation-skill [--project | --dir <path>] [--force]
  npx legal-citation-skill --uninstall [--project | --dir <path>]

  (default)       install to ~/.claude/skills/${NAME} (every project)
  --project       install to ./.claude/skills/${NAME} (this project only)
  --dir <path>    install to <path>/${NAME} — use your agent's skills folder
  --force         replace an existing copy
  --uninstall     remove the installed copy`;

const args = process.argv.slice(2);
const known = new Set(["--project", "--dir", "--force", "--uninstall", "--help", "-h"]);

function fail(message) {
  console.error(`${message}\n\n${USAGE}`);
  process.exit(1);
}

const dirIndex = args.indexOf("--dir");
const dir = dirIndex >= 0 ? args[dirIndex + 1] : undefined;
if (dirIndex >= 0 && (!dir || dir.startsWith("--"))) fail("--dir needs a path.");
const isDirValue = (i) => dirIndex >= 0 && i === dirIndex + 1;
const unknown = args.filter((a, i) => !known.has(a) && !isDirValue(i));
if (unknown.length) fail(`Unknown option: ${unknown.join(" ")}`);
if (args.includes("--help") || args.includes("-h")) {
  console.log(USAGE);
  process.exit(0);
}
if (dir && args.includes("--project")) fail("Use either --project or --dir, not both.");

const root = dir
  ? resolve(dir)
  : args.includes("--project")
    ? resolve(".claude", "skills")
    : join(homedir(), ".claude", "skills");
const target = join(root, NAME);

/** Only ever delete a folder that is recognizably this skill. */
function isOurs(path) {
  const skill = join(path, "SKILL.md");
  return existsSync(skill) && readFileSync(skill, "utf8").includes(`name: ${NAME}\n`);
}

if (args.includes("--uninstall")) {
  if (!existsSync(target)) {
    console.log(`Nothing installed at ${target}`);
    process.exit(0);
  }
  if (!isOurs(target)) fail(`${target} exists but isn't this skill; leaving it alone.`);
  rmSync(target, { recursive: true });
  console.log(`Removed ${target}`);
  process.exit(0);
}

if (existsSync(target)) {
  if (!args.includes("--force")) fail(`${target} already exists. Re-run with --force to replace it.`);
  if (!isOurs(target)) fail(`${target} exists but isn't this skill; refusing to replace it.`);
  rmSync(target, { recursive: true });
}

cpSync(source, target, { recursive: true });
console.log(`Installed the Legal Citation Skill to ${target}`);
console.log("Start a new agent session to pick it up.");
