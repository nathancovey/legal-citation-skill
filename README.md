# Legal Citation Skill

A skill for AI agents that writes, checks, and corrects U.S. legal citations — full and short case citations, *Id.*, signals, explanatory parentheticals, quotations, pincites, and italics — for memos, briefs, and law review footnotes.

Its first principle: **an agent must never invent a number.** Every volume, page, pincite, and year is traced to a source the agent can see, or left as `___` and flagged. The skill ships a tool that finds the reporter page of any passage in a PDF printout using star pagination (`*138`).

## Install

### Claude Code

```
/plugin marketplace add nathancovey/legal-citation-skill
/plugin install legal-citation@legal-citation-skill
```

### Any agent, with npx

```bash
npx legal-citation-skill                     # ~/.claude/skills/legal-citation (all projects)
npx legal-citation-skill --project           # ./.claude/skills/legal-citation (this project)
npx legal-citation-skill --dir <skills-dir>  # any agent that reads a skills folder
npx legal-citation-skill --uninstall         # remove it (same flags)
```

`bunx legal-citation-skill` and `pnpm dlx legal-citation-skill` work the same way. The installer has no dependencies and no install-time scripts.

### Claude apps (claude.ai, desktop)

Zip the `plugins/legal-citation/skills/legal-citation` folder and upload it under Skills in Claude's settings.

### Other agents

The skill is a plain folder in the open Agent Skills format: a `SKILL.md` with a name and description, plus `references/` and `scripts/` that the agent loads only when needed. Copy the folder wherever your agent reads skills, or use `--dir` above. For an agent without skill support, put `SKILL.md` in its instructions and give it read access to `references/`.

## What's inside

```
plugins/legal-citation/skills/legal-citation/
├── SKILL.md                         workflow, the five rules, reporting format
├── references/
│   ├── case-citations.md            full citations, case names, courts, reporters, pincites
│   ├── short-forms.md               short citations and Id.
│   ├── signals-and-parentheticals.md
│   ├── quotations.md                block quotes, ellipses, brackets, candor
│   ├── typeface-and-placement.md    italics; citation sentences vs. clauses
│   ├── verification.md              sourcing numbers, star pagination
│   ├── abbreviations.md             case-name words, states, reporters, courts
│   └── LICENSE-reporters-db.txt
└── scripts/
    ├── find_pincite.py              reporter page for a passage in a PDF
    └── test_find_pincite.py         self-test
```

### The pincite tool

```bash
pip install pypdf
python3 scripts/find_pincite.py packet.pdf "would have been free to leave"
python3 scripts/find_pincite.py packet.pdf --markers
```

It ignores line breaks, quote style, hyphenation, and the markers themselves. A passage that crosses a page break is reported as a range (`217–18`), and star pages restart for each opinion in a multi-case packet. To run the self-test: `pip install reportlab`, then `python3 scripts/test_find_pincite.py`.

## Scope

Case citations are covered in depth. For statutes, regulations, books, articles, and websites, the skill applies the same verification discipline and defers to the user's style guide for form. Court rules, instructors, and firm style guides always override it.

This is a writing aid, not legal advice. Check citations against the rules your court or institution requires.

## License

MIT. The abbreviation lists are derived from Free Law Project's [reporters-db](https://github.com/freelawproject/reporters-db) under its BSD 3-Clause license.
