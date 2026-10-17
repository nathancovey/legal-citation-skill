# Legal Citation Skill

A skill for AI agents that writes, checks, and corrects U.S. legal citations: full and short case citations, *Id.*, signals, explanatory parentheticals, quotations, pincites, and italics, for memos, briefs, and law review footnotes.

Its first principle: **an agent must never invent a number.** Every volume, page, pincite, and year is traced to a source the agent can see, or left as `___` and flagged.

It can also make the fixes in your Word document, as tracked changes **in your name** for you to accept or reject. It never touches a file you have open, and it proves nothing else in the document changed.

## Works with

| Agent | How to install |
|---|---|
| Claude Code | `npx legal-citation-skill` |
| Claude (web and desktop apps) | Upload [the zip](https://github.com/nathancovey/legal-citation-skill/releases/latest/download/legal-citation.zip) under Skills in settings |
| ChatGPT | Upload [the zip](https://github.com/nathancovey/legal-citation-skill/releases/latest/download/legal-citation.zip) as a skill (Create → Upload from your computer) |
| OpenAI Codex | `npx legal-citation-skill` |
| Cursor | `npx legal-citation-skill` |
| Gemini CLI | `npx legal-citation-skill` |
| GitHub Copilot | `npx legal-citation-skill` |
| Any other agent that reads the open Agent Skills format | `npx legal-citation-skill --dir <its skills folder>` |
| Any other AI assistant | Paste `SKILL.md` into its instructions and give it the files in `references/` |

## Install

```bash
npx legal-citation-skill
```

That installs it for every supported agent on your computer. Start a new session and it's ready.

**No Node.js?** On macOS or Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/nathancovey/legal-citation-skill/main/install.sh | sh
```

**ChatGPT or the Claude apps?** Download [legal-citation.zip](https://github.com/nathancovey/legal-citation-skill/releases/latest/download/legal-citation.zip), then:
- **ChatGPT:** upload it as a skill (Create → Upload from your computer). ChatGPT scans uploaded skills before they become available.
- **Claude (web or desktop):** upload it under Skills in settings.

<details>
<summary>Choose agents, install into a project, and other options</summary>

| Agent | `--agent` | Your home folder | A project |
|---|---|---|---|
| Claude Code | `claude` | `~/.claude/skills` | `.claude/skills` |
| OpenAI Codex | `codex` | `~/.codex/skills` | `.agents/skills` |
| Cursor | `cursor` | `~/.cursor/skills`, only when Claude Code and Codex aren't installed (Cursor also reads their folders) | `.cursor/skills` |
| Gemini CLI | `gemini` | `~/.gemini/skills` | `.gemini/skills` |
| GitHub Copilot | `copilot` | `~/.copilot/skills` | `.github/skills` |
| Shared folder | `agents` | `~/.agents/skills` | `.agents/skills` |

```bash
npx legal-citation-skill --agent codex --agent gemini   # specific agents
npx legal-citation-skill --project                      # this project's folders
npx legal-citation-skill --dir <skills-folder>          # any other agent
npx legal-citation-skill --list                         # show the table above
npx legal-citation-skill --uninstall                    # remove it (same flags)
```

With `curl`, put options after `sh -s --`, for example `… | sh -s -- --agent codex`. `bunx` and `pnpm dlx` work the same as `npx`.

**Claude Code plugin manager**, which updates with `/plugin update`:

```
/plugin marketplace add nathancovey/legal-citation-skill
/plugin install legal-citation@legal-citation-skill
```

**An agent without skill support:** put `SKILL.md` in its instructions and give it read access to `references/`.

</details>

## Updating

| Installed with | Update with |
|---|---|
| `npx` | `npx legal-citation-skill@latest --force` |
| `curl` | the same `curl` line, with `… \| sh -s -- --force` |
| Claude Code plugin manager | `/plugin update legal-citation@legal-citation-skill` |
| ChatGPT or Claude apps | upload the latest zip again |

**You'll be told when there's a new version.** The next time your agent uses one of the skill's tools (reading or editing a Word file, or finding a page number), it adds a one-line note with the update command for however you installed it. The check runs at most once a week. It sends nothing about you: it's one request to the npm registry for the latest version number. It stays silent when offline. To turn it off, set the environment variable `LEGAL_CITATION_NO_UPDATE_CHECK=1`. Uploaded copies in ChatGPT and the Claude apps run in a sandbox and won't see the note; check the [releases page](https://github.com/nathancovey/legal-citation-skill/releases) instead.

## Compatibility

- **Format.** The skill is a folder in the open Agent Skills format: a `SKILL.md` with a name and description, plus `references/` and `scripts/` that the agent loads only when needed. `scripts/test_skill_format.py` checks the format's rules: name style and length, description length, and links that resolve. It also checks that the instructions don't assume a particular agent.
- **Scripts.** Python 3. The Word tools use only the standard library. The page-finding tool needs `pypdf`, or its older name `PyPDF2`. An agent that can't run code still gets every rule; it just can't run the tools.
- **Tested.** Built and tested end to end with Claude Code, including reviewing and fixing a real memo in Microsoft Word. Other agents read the same format from the folders their makers document; please report anything that behaves differently.

## What's inside

```
plugins/legal-citation/skills/legal-citation/
├── SKILL.md                         workflow, the five rules, reporting format
├── VERSION
├── references/
│   ├── case-citations.md            full citations, case names, courts, reporters, pincites
│   ├── short-forms.md               short citations and Id.
│   ├── signals-and-parentheticals.md
│   ├── quotations.md                block quotes, ellipses, brackets, candor
│   ├── typeface-and-placement.md    italics; citation sentences vs. clauses
│   ├── verification.md              sourcing numbers, star pagination, looking cases up online
│   ├── abbreviations.md             case-name words, states, reporters, courts
│   ├── word-documents.md            fixing a Word file safely, as tracked changes
│   └── LICENSE-reporters-db.txt
└── scripts/
    ├── find_pincite.py              reporter page for a passage in a PDF
    ├── docx_read.py                 read a .docx with italics and tracked changes shown
    ├── docx_edit.py                 apply edits as tracked changes in the user's name
    ├── update_check.py              weekly "new version available" note
    ├── test_find_pincite.py         self-test
    ├── test_docx_edit.py            self-test
    ├── test_update_check.py         self-test
    └── test_skill_format.py         format check
```

### The pincite tool

```bash
pip install pypdf
python3 scripts/find_pincite.py packet.pdf "would have been free to leave"
python3 scripts/find_pincite.py packet.pdf --markers
```

It finds the reporter page of a passage in a database printout using star pagination (`*138`). It ignores line breaks, quote style, hyphenation, and the markers themselves. A passage that crosses a page break is reported as a range (`217–18`), and star pages restart for each opinion in a multi-case packet. To run the self-test: `pip install reportlab`, then `python3 scripts/test_find_pincite.py`.

### The Word tools

```bash
python3 scripts/docx_read.py memo.docx --revisions
python3 scripts/docx_edit.py memo.docx edits.json -o "memo (edited).docx"
```

`docx_edit.py` takes a JSON list of edits. Each edit finds text in one paragraph and replaces, deletes, inserts, or changes italic, bold, or underline. Every edit becomes a tracked change authored by the user, with the name taken from the document's own metadata. Before writing, the script proves three things: rejecting all changes restores the original, accepting them gives exactly the intended text, and nothing else changed. See `references/word-documents.md` for the format. Self-test: `python3 scripts/test_docx_edit.py`.

## Scope

Case citations are covered in depth. For statutes, regulations, books, articles, and websites, the skill applies the same verification discipline and defers to the user's style guide for form. Court rules, instructors, and firm style guides always override it.

This is a writing aid, not legal advice. Check citations against the rules your court or institution requires.

## License

MIT. The abbreviation lists are derived from Free Law Project's [reporters-db](https://github.com/freelawproject/reporters-db) under its BSD 3-Clause license.
