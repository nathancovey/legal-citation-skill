---
name: legal-citation
description: Write, check, and correct U.S. legal citations under the Bluebook (22d ed. 2025), in either Bluepages style (briefs, memos, motions) or Whitepages style (law review footnotes) — full and short case citations, "Id.", record and court-document citations, statutes and other sources, signals, parentheticals, quotations, pincites, and italics. Use when drafting or reviewing a legal memo, brief, motion, opinion, or law review footnote; when asked whether a citation is formatted correctly; or when turning a rough reference like "(Smith v. Jones, 2004)" into a proper citation. Can make the fixes directly in a Word document as tracked changes in the user's name. Never invents page numbers — every number is traced to a source.
---

# Legal Citation Skill

How to format U.S. legal citations — what goes where, what is italicized, when to shorten — and, more important, how to avoid putting a wrong number into someone's brief.

**Edition.** This skill follows *The Bluebook: A Uniform System of Citation* (22d ed. 2025). Rule numbers in the references (B17, Rule 5.2(f)) are to that edition. Study guides and older editions sometimes differ. When one conflicts with the Bluebook's text, follow the Bluebook. Changes new in the 22d edition, such as "(citation modified)" in place of "(internal quotation marks omitted)," are marked where they come up.

## Five rules that override everything else

1. **Never originate a number.** Volume, first page, pincite, year, docket number: copy each one from a source you can actually see. If you can't see it, write `___` and say exactly what is missing. A plausible wrong pincite is worse than a blank, because it looks finished.
2. **Pincites come from the page, not from memory.** Database printouts mark where each reporter page begins with an inline marker such as `*138`. Use `scripts/find_pincite.py` to locate the page for a passage in a PDF. No local copy? Look the opinion up online — see `references/verification.md`.
3. **A citation must support the sentence it is attached to.** A case cannot prove a fact from your own record, and no signal fixes that. Restructure the sentence instead.
4. **Read the whole passage before saying what a case holds.** Search snippets mislead. Check what the court *did* with the language — a rule statement may come from a case that applied it against your position.
5. **Local authority wins.** Court rules (Bluebook table BT2 lists them), an instructor's instructions, or a firm style guide override this skill. Once the user says something is permitted, stop flagging it.

## Pick the style first

The Bluebook has two styles. Both are fully supported, and they differ mainly in typeface, placement, and short-form timing:

| Document | Style | What changes |
|---|---|---|
| Briefs, motions, memos, opinions, court filings | **Bluepages** (practitioner) | Citations sit in the text. Case names italicized (or underlined) in full and short citations. No small capitals. Record citations under B17. *(citation modified)* is available. |
| Law review articles, notes, seminar papers written for a journal | **Whitepages** (academic) | Citations sit in footnotes. Case names are roman in full footnote citations but italic in short forms and in textual sentences. Books, periodicals, and codes use large-and-small capitals. Short forms follow the five-footnote rule; *supra* takes a note number. |

**Decide before you edit or rewrite anything.** Use these signs:

- **Bluepages:** a memo heading (To / From / Re), a court caption, "Brief," "Motion," or "Memorandum" in the title, citations in the body text, record cites like `R. at 5`.
- **Whitepages:** a journal or article format, nearly every citation in footnotes, small capitals for book or journal names, roman case names in full footnote citations.
- **If you can't tell, ask the user which style they want before making changes.** For example, the user pasted citations without the document, the document mixes signs, or it's a student paper with footnotes that could go either way. A one-line question beats rewriting every case name in the wrong typeface. Once the user answers, use that style for the whole document.

Italics and underlining are interchangeable in Bluepages style. Pick one and use it everywhere. Details: `references/typeface-and-placement.md`.

## Reviewing citations

1. **Settle the style** (Bluepages or Whitepages), asking if it's unclear.
2. **List every citation in document order**, including short forms, `Id.`, and record citations. Whether a short form is allowed depends on what came before it.
3. **Check form** against the references below.
4. **Trace every number** to the source. If you have the PDF, run the pincite script. If you don't, and you can browse the web, find the opinion online (`references/verification.md`). Anything you still can't trace goes on a separate list.
5. **Compare quotations character by character** with the source.
6. **Check fit.** Does the authority support the sentence it is attached to, with the right signal?
7. **Report** in the format below.

## Fixing the document itself

If the user asks you to make the fixes in their Word file, follow `references/word-documents.md`. In short:

- Every change is a **tracked change in the user's name**, never yours.
- **Never replace a file that's open** in Word. Write a copy instead.
- **Fix only what's certain.** Leave the "check" items for the user.
- **Mark italics in inserted text.** Inserted text copies the formatting next to it, so an `Id.` added after roman text comes out roman. Write `" ‹Id.› at 874."` to italicize only `Id.`
- Use `scripts/docx_edit.py`, which proves before writing that nothing else in the document changed. Once the user has accepted the changes, confirm with `scripts/docx_read.py --revisions` that none are still pending.

## Building a citation from a rough reference

Collect from the opinion itself: the case name (from the start of the opinion, not a database header), volume, reporter, first page, pincite, court, and year. Anything you cannot see stays `___`. Then assemble it per `references/case-citations.md`.

## Reporting format

For each problem:

> **As written:** `Bonner, 643 at 15.`
> **Corrected:** `Bonner, 643 A.2d at 15.`
> **Why:** the short form dropped the reporter abbreviation.
> **Confidence:** certain

- **Certain** means you checked both the rule and the source. **Check** means one of them is unverified — say which.
- End with a list headed **Numbers I could not verify**.
- One citation, one verdict. If you would propose two different rewrites for the same citation, you don't know the answer; say that instead.
- Do not report citation *placement* as an error. A citation sentence, a citation clause, and a case named in the prose with the rest of its citation in the following sentence are all correct.
- When the user pushes back, re-read the source before answering. Concede plainly if they are right; quote the rule if they are not.

## References

Load the one you need.

| File | Covers |
|---|---|
| `references/case-citations.md` | Full case citations, case names, courts, reporters, pincites, Westlaw and Lexis cites, docket numbers, prior and subsequent history (B10, Rules 3, 10) |
| `references/short-forms.md` | Short citations and `Id.` — forms, when each is allowed, the five-footnote rule (B4, B10.2, Rules 4, 10.9) |
| `references/court-documents.md` | Record and court-document citations: BT1 abbreviations, pinpoints, dates, docket numbers, parentheses, `Id.` (B17, BT1, Rule 10.8.3) |
| `references/statutes-and-other-sources.md` | Constitutions, statutes, rules, restatements, regulations, legislative materials, books, articles, websites, AI output (B11–B23, Rules 11–18) |
| `references/signals-and-parentheticals.md` | Signals, explanatory and weight-of-authority parentheticals, their order, quoting and citing (B1, Rules 1, 10.6) |
| `references/quotations.md` | Block quotations, ellipses, brackets, alterations, internal quotation marks, `(citation modified)`, candor (B5, Rule 5) |
| `references/typeface-and-placement.md` | Bluepages versus Whitepages typeface; citation sentences versus clauses; capitalization; judges (B1, B2, B7–B9, Rules 1.1, 2, 7–9) |
| `references/verification.md` | Sourcing numbers, star pagination, what is not part of the opinion |
| `references/abbreviations.md` | Spacing, numerals and symbols, case-name words, places, reporters, courts, history phrases, months, subdivisions (B6, Rule 6, T1, T6–T8, T10, T12, T16) |
| `references/word-documents.md` | Making fixes in a Word file safely, as tracked changes in the user's name |

## Scripts

`scripts/find_pincite.py` finds a phrase in a PDF and reports the reporter page it falls on, using star pagination. It handles passages that cross a page break and packets that contain several opinions.

```bash
python3 scripts/find_pincite.py packet.pdf "inappropriately expansive response"
python3 scripts/find_pincite.py packet.pdf --markers
```

Requires `pypdf` (`pip install pypdf`).

`scripts/docx_read.py` shows a Word document with italics, underlining, and bold marked, and lists pending tracked changes. `scripts/docx_edit.py` applies edits as tracked changes. Both use only the Python standard library.

Any of these tools may end with a one-line notice that a newer version of this skill exists. When one appears, pass it on to the user once, at the end of your reply.

```bash
python3 scripts/docx_read.py memo.docx --revisions
python3 scripts/docx_edit.py memo.docx edits.json -o "memo (edited).docx"
```

## Scope

Cases, short forms, the record, signals, parentheticals, quotations, and typeface are covered in depth, for both Bluepages and Whitepages style. Constitutions, statutes, rules, regulations, legislative materials, books, articles, and websites are covered in their Bluepages forms. Foreign, international, tribal, and archival sources (B20–B23) are outlined only. Look up the specific Bluebook rule before citing one, and apply the same discipline everywhere: verify every number, never invent one.
