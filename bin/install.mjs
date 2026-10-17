#!/usr/bin/env node
/**
 * Install the Legal Citation Skill for AI agents.
 *
 *   npx legal-citation-skill                    every supported agent found on this computer
 *   npx legal-citation-skill --agent codex      a specific agent (repeat for several)
 *   npx legal-citation-skill --project          this project's skill folders instead of your home folder
 *   npx legal-citation-skill --dir <path>       any other agent's skills folder
 *   npx legal-citation-skill --uninstall        remove it again (same flags)
 *   npx legal-citation-skill --list             show where each agent looks
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

// Where each agent reads skills. `home` is the folder whose presence means the agent is installed.
// Cursor has no per-user folder of its own: it also reads skills installed for Claude Code and Codex.
const AGENTS = {
  claude: { label: "Claude Code", home: ".claude", global: ".claude/skills", project: ".claude/skills" },
  codex: { label: "OpenAI Codex", home: ".codex", global: ".codex/skills", project: ".agents/skills" },
  cursor: { label: "Cursor", home: null, global: null, project: ".cursor/skills" },
  gemini: { label: "Gemini CLI", home: ".gemini", global: ".gemini/skills", project: ".gemini/skills" },
  copilot: { label: "GitHub Copilot", home: ".copilot", global: ".copilot/skills", project: ".github/skills" },
  agents: { label: "shared .agents folder", home: null, global: ".agents/skills", project: ".agents/skills" },
};
const DETECTED = ["claude", "codex", "gemini", "copilot"];

const USAGE = `Install the Legal Citation Skill for AI agents.

Usage:
  npx legal-citation-skill [--agent <name>]... [--project] [--force]
  npx legal-citation-skill --dir <path> [--force]
  npx legal-citation-skill --uninstall [--agent <name>]... [--project | --dir <path>]
  npx legal-citation-skill --list

  (no --agent)    every supported agent found on this computer
  --agent <name>  ${Object.keys(AGENTS).join(", ")} (repeatable)
  --project       install into this project's folders instead of your home folder
  --dir <path>    install into <path>/${NAME} — any agent's skills folder
  --force         replace an existing copy
  --uninstall     remove installed copies
  --list          show where each agent looks

ChatGPT and the Claude apps install by upload instead: see the README.`;

function fail(message) {
  console.error(`${message}\n\n${USAGE}`);
  process.exit(1);
}

// ------------------------------------------------------------- arguments
const args = process.argv.slice(2);
const flags = new Set();
const agents = [];
let dir;
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--agent" || a === "--dir") {
    const v = args[++i];
    if (!v || v.startsWith("--")) fail(`${a} needs a value.`);
    if (a === "--dir") dir = v;
    else if (!AGENTS[v]) fail(`Unknown agent: ${v}`);
    else agents.push(v);
  } else if (["--project", "--force", "--uninstall", "--list", "--help", "-h"].includes(a)) {
    flags.add(a);
  } else {
    fail(`Unknown option: ${a}`);
  }
}
if (flags.has("--help") || flags.has("-h")) {
  console.log(USAGE);
  process.exit(0);
}
if (dir && (agents.length || flags.has("--project"))) fail("Use --dir on its own, without --agent or --project.");

if (flags.has("--list")) {
  console.log("Where each agent reads skills (your home folder / a project):");
  for (const [key, a] of Object.entries(AGENTS)) {
    console.log(`  ${key.padEnd(8)} ${a.label.padEnd(22)} ${a.global ? "~/" + a.global : "—"}  /  ./${a.project}`);
  }
  process.exit(0);
}

// -------------------------------------------------------------- targets
const home = homedir();
const project = flags.has("--project");
let chosen = agents;
if (!dir && !chosen.length) {
  chosen = DETECTED.filter((k) => existsSync(join(home, AGENTS[k].home)));
  if (!chosen.length) {
    fail("No supported agent found on this computer. Pick one with --agent, or give its skills folder with --dir.");
  }
}

const targets = new Map(); // skills folder -> labels of the agents that read it
if (dir) {
  targets.set(resolve(dir), ["the folder you gave"]);
} else {
  for (const key of chosen) {
    const a = AGENTS[key];
    const rel = project ? a.project : a.global;
    if (!rel) {
      fail(`${a.label} has no per-user skills folder of its own; it reads skills installed for Claude Code or Codex. Use --project to install into this project.`);
    }
    const folder = project ? resolve(rel) : join(home, rel);
    targets.set(folder, [...(targets.get(folder) || []), a.label]);
  }
}

/** Only ever delete a folder that is recognizably this skill. */
function isOurs(path) {
  const skill = join(path, "SKILL.md");
  return existsSync(skill) && readFileSync(skill, "utf8").includes(`name: ${NAME}\n`);
}

// ---------------------------------------------------------------- act
const problems = [];
for (const [root, labels] of targets) {
  const target = join(root, NAME);
  const who = labels.join(", ");
  if (flags.has("--uninstall")) {
    if (!existsSync(target)) continue;
    if (!isOurs(target)) {
      problems.push(`${target} exists but isn't this skill; left it alone.`);
      continue;
    }
    rmSync(target, { recursive: true });
    console.log(`Removed from ${who}: ${target}`);
    continue;
  }
  if (existsSync(target)) {
    if (!flags.has("--force")) {
      problems.push(`${target} already exists (${who}). Re-run with --force to replace it.`);
      continue;
    }
    if (!isOurs(target)) {
      problems.push(`${target} exists but isn't this skill; refusing to replace it.`);
      continue;
    }
    rmSync(target, { recursive: true });
  }
  cpSync(source, target, { recursive: true });
  console.log(`Installed for ${who}: ${target}`);
}

for (const p of problems) console.error(p);
if (!flags.has("--uninstall") && problems.length < targets.size) {
  console.log("Start a new agent session to pick it up.");
}
process.exit(problems.length ? 1 : 0);
