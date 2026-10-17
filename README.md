# Legal Citation Skill

A skill for AI agents that writes, checks, and corrects U.S. legal citations — full and short case citations, *Id.*, signals, explanatory parentheticals, quotations, pincites, and italics — for memos, briefs, and law review footnotes.

Its first principle: **an agent must never invent a number.** Every volume, page, pincite, and year is traced to a source the agent can see, or left as `___` and flagged.

It can also make the fixes in your Word document, as tracked changes **in your name** for you to accept or reject. It never touches a file you have open, and it proves nothing else in the document changed.

## Install

```bash
npx legal-citation-skill
```

That's it. Start a new session and your agent has the skill.

**No Node.js?** On macOS or Linux, this needs nothing but `curl`:

```bash
curl -fsSL https://raw.githubusercontent.com/nathancovey/legal-citation-skill/main/install.sh | sh
```

**Using Claude on the web or desktop app?** Download [legal-citation.zip](https://github.com/nathancovey/legal-citation-skill/releases/latest/download/legal-citation.zip) and upload it under Skills in Claude's settings.

<details>
<summary>Options and other ways to install</summary>

Both one-line installers put the skill in `~/.claude/skills/legal-citation`, where Claude Code finds it in every project. They take the same options. With `curl`, put them after `sh -s --`, for example `… | sh -s -- --project`.

| Option | Effect |
|---|---|
| `--project` | Install to `./.claude/skills` — this project only |
| `--dir <path>` | Install to another agent's skills folder |
| `--force` | Replace an existing copy |
| `--uninstall` | Remove it (`npx` only; otherwise delete the folder) |

`bunx legal-citation-skill` and `pnpm dlx legal-citation-skill` work the same as `npx`.

**Claude Code plugin manager** — installs through Claude Code and updates with `/plugin update`:

```
/plugin marketplace add nathancovey/legal-citation-skill
/plugin install legal-citation@legal-citation-skill
```

**Any other agent** — the skill is a plain folder in the open Agent Skills format: a `SKILL.md` plus `references/` and `scripts/` that load only when needed. Copy `plugins/legal-citation/skills/legal-citation` wherever your agent reads skills. For an agent without skill support, put `SKILL.md` in its instructions and give it read access to `references/`.

</details>

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
│   ├── word-documents.md            fixing a Word file safely, as tracked changes
│   └── LICENSE-reporters-db.txt
└── scripts/
    ├── find_pincite.py              reporter page for a passage in a PDF
    ├── docx_read.py                 read a .docx with italics and tracked changes shown
    ├── docx_edit.py                 apply edits as tracked changes in the user's name
    ├── test_find_pincite.py         self-test
    └── test_docx_edit.py            self-test
```

### The Word tools

```bash
python3 scripts/docx_read.py memo.docx --revisions
python3 scripts/docx_edit.py memo.docx edits.json -o "memo (edited).docx"
```

`docx_edit.py` takes a JSON list of edits (each finds text in one paragraph and replaces, deletes, inserts, or changes italic, bold, or underline). Every edit becomes a tracked change authored by the user — the name comes from the document's own metadata. Before writing, the script proves that rejecting all changes restores the original, that accepting them gives exactly the intended text, and that nothing else changed. Standard library only; see `references/word-documents.md` for the format. Self-test: `python3 scripts/test_docx_edit.py`.

### The pincite tool

```bash
pip install pypdf
python3 scripts/find_pincite.py packet.pdf "would have been free to leave"
python3 scripts/find_pincite.py packet.pdf --markers
```

It finds the reporter page of a passage in a database printout using star pagination (`*138`). It ignores line breaks, quote style, hyphenation, and the markers themselves. A passage that crosses a page break is reported as a range (`217–18`), and star pages restart for each opinion in a multi-case packet. To run the self-test: `pip install reportlab`, then `python3 scripts/test_find_pincite.py`.

## Scope

Case citations are covered in depth. For statutes, regulations, books, articles, and websites, the skill applies the same verification discipline and defers to the user's style guide for form. Court rules, instructors, and firm style guides always override it.

This is a writing aid, not legal advice. Check citations against the rules your court or institution requires.

## License

MIT. The abbreviation lists are derived from Free Law Project's [reporters-db](https://github.com/freelawproject/reporters-db) under its BSD 3-Clause license.
