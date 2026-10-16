---
name: legal-citation
description: Write, check, and correct U.S. legal citations in the uniform citation style used by American courts, law firms, and law reviews — full and short case citations, "Id.", signals, explanatory parentheticals, quotations, pincites, and italics. Use when drafting or reviewing a legal memo, brief, motion, opinion, or law review footnote; when asked whether a citation is formatted correctly; or when turning a rough reference like "(Smith v. Jones, 2004)" into a proper citation. Never invents page numbers — every number is traced to a source.
---

# Legal Citation Skill

How to format U.S. legal citations — what goes where, what is italicized, when to shorten — and, more important, how to avoid putting a wrong number into someone's brief.

## Five rules that override everything else

1. **Never originate a number.** Volume, first page, pincite, year, docket number: copy each one from a source you can actually see. If you can't see it, write `___` and say exactly what is missing. A plausible wrong pincite is worse than a blank, because it looks finished.
2. **Pincites come from the page, not from memory.** Database printouts mark where each reporter page begins with an inline marker such as `*138`. Use `scripts/find_pincite.py` to locate the page for a passage in a PDF.
3. **A citation must support the sentence it is attached to.** A case cannot prove a fact from your own record, and no signal fixes that. Restructure the sentence instead.
4. **Read the whole passage before saying what a case holds.** Search snippets mislead. Check what the court *did* with the language — a rule statement may come from a case that applied it against your position.
5. **Local authority wins.** Court rules, an instructor's instructions, or a firm style guide override this skill. Once the user says something is permitted, stop flagging it.

## Pick the style first

| Document | Style | What changes |
|---|---|---|
| Briefs, motions, memos, opinions | **Practitioner** (default) | Citations sit in the text. Case names italicized (or underlined) in full and short citations. |
| Law review articles and notes | **Academic** | Citations sit in footnotes. Case names are roman in full footnote citations but italic in short forms and in textual sentences. Some sources use large-and-small capitals. |

Italics and underlining are interchangeable. Pick one and use it everywhere.

## Reviewing citations

1. **List every citation in document order**, including short forms and `Id.` Whether a short form is allowed depends on what came before it.
2. **Check form** against the references below.
3. **Trace every number** to the source. If you have the PDF, run the pincite script. Anything you can't trace goes on a separate list.
4. **Compare quotations character by character** with the source.
5. **Check fit.** Does the authority support the sentence it is attached to, with the right signal?
6. **Report** in the format below.

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
| `references/case-citations.md` | Full case citations, case names, courts, reporters, pincites, page ranges, spacing |
| `references/short-forms.md` | Short citations and `Id.` — forms and when each is allowed |
| `references/signals-and-parentheticals.md` | Signals, explanatory parentheticals, their order |
| `references/quotations.md` | Block quotations, ellipses, brackets, alterations, candor |
| `references/typeface-and-placement.md` | What is italicized; citation sentences versus clauses |
| `references/verification.md` | Sourcing numbers, star pagination, what is not part of the opinion |
| `references/abbreviations.md` | Case-name words, states, reporters, court designations |

## Scripts

`scripts/find_pincite.py` finds a phrase in a PDF and reports the reporter page it falls on, using star pagination. It handles passages that cross a page break and packets that contain several opinions.

```bash
python3 scripts/find_pincite.py packet.pdf "inappropriately expansive response"
python3 scripts/find_pincite.py packet.pdf --markers
```

Requires `pypdf` (`pip install pypdf`).

## Scope

Case citations are covered in depth. For statutes, regulations, constitutions, books, articles, and websites, apply the same discipline — verify every number, never invent one — and follow the user's style guide for form.
