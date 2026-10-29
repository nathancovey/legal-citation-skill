# Bluebook 22d edition coverage map

This maps each Bluepages rule (B1–B23, BT1–BT2) and the Whitepages rules and tables that matter for memos, briefs, and law review footnotes to where the skill covers it. Each row gives the status **before** this audit (skill version 1.5.0) and where the rule is covered **now**.

**Sources.** *The Bluebook: A Uniform System of Citation* (22d ed. 2025), read in full for the Bluepages and BT tables, and rule by rule for Whitepages Rules 1–12, 18, and tables T1, T6–T8, T10, T12, and T16. *Bluebook Uncovered* (22d ed., Aug. 6, 2025) was used as a cross-check only. Where the two differ, the skill follows the Bluebook (see "Bluebook Uncovered versus the Bluebook" below).

**Status key.**

- **Covered:** the skill states the rule correctly.
- **Partly:** some of the rule is stated, or it is only gestured at.
- **Missing:** not stated at all.
- **Contradicted:** the skill said something the 22d edition doesn't allow.

File names below are in `plugins/legal-citation/skills/legal-citation/references/`.

## Contradictions fixed

| # | The skill said | The 22d edition says | Fixed in |
|---|---|---|---|
| 1 | *But cf.* needs a parenthetical only "if relevance is unclear." | A parenthetical is **required** (Rule 1.2(c)). | `signals-and-parentheticals.md` |
| 2 | *See generally* needs a parenthetical only "if relevance is unclear." | A parenthetical is **required** after each authority (Rule 1.2(d)). | `signals-and-parentheticals.md` |
| 3 | `F.Supp.2d` and `S.Ct.` are always wrong. | In court documents with word limits, reporter abbreviations may be closed up (B6, B10.1.2). Still wrong in memos and law reviews (Rule 6.1(a)). | `case-citations.md`, `abbreviations.md` |
| 4 | A database-stripped docket number is fine if used consistently. | Cite the docket number as it appears on the court's documents. Only a leading digit and colon, and the judge's initials at the end, may be dropped (Rule 10.8.1(a); B10.1.4 tip). | `case-citations.md` |
| 5 | A clause ending at a semicolon "is not a full sentence" for a quoting parenthetical. | Material that reads as a full sentence may be quoted as one, with the omitted end marked by an ellipsis (Rules 1.5(a)(ii), 5.3(b)(iii)). | `signals-and-parentheticals.md` |
| 6 | `SKILL.md` and `word-documents.md` modeled a record citation as `missed two shifts (Id. at 4).` | Parenthesized court-document citations enclose the whole citation sentence, period inside: `(Def.'s Resp. to Pl.'s Interrog. No. 3.)` (B17.1.1 tip). *Id.* is used for court documents only when it saves significant space (B17.2 tip). | `SKILL.md`, `word-documents.md`, `court-documents.md` |
| 7 | T6 abbreviations: Advertising `Adver.`, Digital `Dig.`, Employer `Emp'r`, Employment `Emp't`, Entertainment `Entm't`, Environmental `Envtl.`, Investor `Inv'r`, Laboratory `Lab.`, Professional `Prof'l`, Refining `Ref.` | `Advert.`, `Digit.`, `Emp.`, `Emp.`, `Ent.`, `Env't`, `Inv.`, `Lab'y` (`Lab.` is Labor), `Pro.`, `Refin.` (`Ref.` is Referee) (T6). | `abbreviations.md` |
| 8 | Gender `Gend.`, Schools `Sch.`, Pharmaceuticals `Pharm.` | Gender isn't in T6 and has under eight letters, so it is spelled out. Plurals add "s": `Schs.`, `Pharms.` (T6). | `abbreviations.md` |
| 9 | Reporter names "United States Supreme Court Reports" for `U.S.` and "Lawyer's Edition." | "United States Reports"; "United States Supreme Court Reports, Lawyers' Edition" (T1). | `abbreviations.md` |
| 10 | Texas Court of Criminal Appeals listed as an intermediate or trial court. Unlisted courts: "copy the form from a recent opinion." | It is the state's highest criminal court. Unlisted courts use T1, then a composite from T7 and T10 (Rule 10.4). | `abbreviations.md` |
| 11 | (Silent, so agents used 21st-edition practice) `(internal quotation marks omitted)`. | Keep the internal marks and add `(quoting …)`, or omit them only when they span the whole quotation (Rule 5.2(f)), or modify the quotation and write `(citation modified)` (B5.3). `(internal quotation marks omitted)` and `(cleaned up)` are not 22d-edition devices (B5.3 tip). | `quotations.md` |

## Bluepages

| Rule | Topic | Before | Now |
|---|---|---|---|
| Intro | Local rules; Whitepages supplement the Bluepages; underscoring = italics | Partly (local authority rule) | `SKILL.md` (edition, rule 5, style choice) |
| B1.1 | Citation sentences and clauses | Covered | `typeface-and-placement.md` |
| B1.2 | Signals, table and order | **Contradicted** (*but cf.*, *see generally*); *Contrast … with* missing | `signals-and-parentheticals.md` |
| B1.3 | Explanatory parentheticals | Partly ("short statement" form missing) | `signals-and-parentheticals.md` |
| B2 | Typeface for court documents | Partly | `typeface-and-placement.md` (Bluepages/Whitepages table) |
| B3 | Subdivisions | Partly (pages and footnotes only) | `case-citations.md`, `statutes-and-other-sources.md`, `abbreviations.md` (T16) |
| B4 | *Id.*, *supra*, *hereinafter* | Partly (*id.*; "no supra for cases") | `short-forms.md`, `statutes-and-other-sources.md` |
| B5.1 | Quotations generally | Covered | `quotations.md` |
| B5.2 | Block quotations | Partly ("justified" missing) | `quotations.md` |
| B5.3 | Modifying quotations, "(citation modified)" (new) | **Missing** | `quotations.md`, `signals-and-parentheticals.md` (placement) |
| B6 | Abbreviations, numerals, symbols | **Contradicted** (closing up); numerals missing | `abbreviations.md` |
| B7 | Italicization for style | Partly | `typeface-and-placement.md` |
| B8 | Capitalization | **Missing** | `typeface-and-placement.md`, `court-documents.md` |
| B9 | Titles of judges | **Missing** | `typeface-and-placement.md`, `signals-and-parentheticals.md` |
| B10.1.1 | Case names | Partly | `case-citations.md` |
| B10.1.2 | Reporters, pincites | Covered (*passim* missing) | `case-citations.md` |
| B10.1.3 | Court and year; parallel citations in state courts | Partly (parallel citations missing) | `case-citations.md` |
| B10.1.4 | Pending and unreported cases | Partly (WL only); docket rule **contradicted** | `case-citations.md` |
| B10.1.5 | Weight of authority | Partly (order list only) | `signals-and-parentheticals.md` |
| B10.1.6 | Prior and subsequent history | Partly ("check a full style guide") | `case-citations.md`, `abbreviations.md` (T8) |
| B10.2 | Case short forms, *id.* | Covered (*id.* across opinions missing) | `short-forms.md` |
| B11 | Constitutions | **Missing** | `statutes-and-other-sources.md` |
| B12 | Statutes, rules, restatements, tax | **Missing** (deferred to "style guide") | `statutes-and-other-sources.md` |
| B13 | Legislative materials | **Missing** | `statutes-and-other-sources.md` |
| B14 | Administrative materials | **Missing** | `statutes-and-other-sources.md` |
| B15 | Books | **Missing** | `statutes-and-other-sources.md` |
| B16 | Periodicals | **Missing** | `statutes-and-other-sources.md` |
| B17 | Court and litigation documents | **Missing**; examples **contradicted** it | `court-documents.md` (new) |
| B18 | Internet | **Missing** | `statutes-and-other-sources.md` |
| B19 | Services | **Missing** | `statutes-and-other-sources.md` |
| B20 | Foreign materials | **Missing** | Outlined, `statutes-and-other-sources.md` |
| B21 | International materials | **Missing** | Outlined, `statutes-and-other-sources.md` |
| B22 | Tribal Nations (new in this numbering) | **Missing** | Outlined, `statutes-and-other-sources.md` |
| B23 | Archival sources | **Missing** | Outlined, `statutes-and-other-sources.md` |
| BT1 | Court-document abbreviations | **Missing** | `court-documents.md` (full table) |
| BT2 | Jurisdiction-specific rules | Partly | `SKILL.md` rule 5, `court-documents.md`, `case-citations.md` |

## Whitepages rules

| Rule | Topic | Before | Now |
|---|---|---|---|
| 1.1 | Sentences and clauses; footnote call numbers | Partly | `typeface-and-placement.md` |
| 1.2 | Signals; parentheticals required; signals as verbs; pincites required (1.2(f)) | **Contradicted** (1.2(c)–(d)); rest missing | `signals-and-parentheticals.md` |
| 1.3 | Order and grouping of signals by type | Partly (grouping missing) | `signals-and-parentheticals.md` |
| 1.4 | Order of authorities: "logical," most helpful first (simplified in 22d) | Covered | `signals-and-parentheticals.md` |
| 1.5(a) | Parenthetical forms | Partly | `signals-and-parentheticals.md` |
| 1.5(b) | Order of parentheticals; nesting; "first quoting … and then quoting" | Covered (order matches exactly); nesting missing | `signals-and-parentheticals.md` |
| 1.6 | Related authority (*quoted in*, *reprinted in*) | Partly | `signals-and-parentheticals.md` |
| 2 | Law review typography; romanized ellipses/brackets; one space | Partly | `typeface-and-placement.md`, `quotations.md` |
| 3.1 | Volumes, parts, supplements | **Missing** | `statutes-and-other-sources.md` (supplements in code years) |
| 3.2 | Pages, footnotes, star pages, *passim* | Partly | `case-citations.md` |
| 3.3 | Sections and paragraphs | **Missing** | `statutes-and-other-sources.md` |
| 3.4 | Appended material (`cmt.`, `app.`, `note`) | **Missing** | `statutes-and-other-sources.md`, `abbreviations.md` (T16) |
| 3.5 | Internal cross-references (*supra*/*infra* Part) | **Missing** | Partly: `abbreviations.md` (T16 `p.`/`note` in cross-references). Law review only. |
| 4.1 | *Id.* | Partly | `short-forms.md` |
| 4.2 | *Supra* and *hereinafter* | **Missing** | `short-forms.md`, `statutes-and-other-sources.md`, `typeface-and-placement.md` |
| 5.1 | Formatting quotations | Covered (paragraph structure missing) | `quotations.md` |
| 5.2(a)–(e) | Alterations, `[sic]`, changes to citations, quotations within quotations | Partly | `quotations.md` |
| 5.2(f) | Internal quotation marks (new) | **Missing** | `quotations.md` |
| 5.3 | Omissions | Covered (5.3(b)(vi) missing) | `quotations.md` |
| 6.1 | Abbreviations, spacing, periods | Partly / **Contradicted** (see #3) | `abbreviations.md` |
| 6.2 | Numerals and symbols | **Missing** | `abbreviations.md` |
| 7 | Italics for style, Latin words | Partly | `typeface-and-placement.md` |
| 8 | Capitalization | **Missing** | `typeface-and-placement.md` |
| 9 | Judges and officials | **Missing** | `typeface-and-placement.md` |
| 10.1–10.2 | Case names | Partly | `case-citations.md` |
| 10.3 | Reporters; parallel and public domain citations | Partly (public domain missing) | `case-citations.md` |
| 10.4 | Court designations | Covered (district-not-division missing) | `case-citations.md`, `abbreviations.md` |
| 10.5 | Dates; F. App'x year only; same-year history | Partly | `case-citations.md` |
| 10.6 | Weight of authority; quoting/citing; order; nesting | Partly | `signals-and-parentheticals.md` |
| 10.7 | Prior and subsequent history; overruled/abrogated/superseded; *sub nom.* | Partly | `case-citations.md` |
| 10.8.1 | Electronic databases (WL, LEXIS, LX, BL); slip opinions | Partly / **Contradicted** (docket) | `case-citations.md` |
| 10.8.2 | Fifth Circuit split | Missing | Not added (rare) |
| 10.8.3 | Briefs and filings in other cases | **Missing** | `court-documents.md` |
| 10.8.4 | Court administrative orders | Missing | Not added (rare) |
| 10.9 | Case short forms; five-footnote rule; *id.* across opinions | Partly | `short-forms.md` |
| 11 | Constitutions | **Missing** | `statutes-and-other-sources.md` |
| 12 | Statutes | **Missing** | `statutes-and-other-sources.md` (code, session laws, state codes, short forms, rules, restatements). 12.4–12.8 details (session-law forms, electronic codes, statutory history) only partly. |
| 13 | Legislative materials | **Missing** | Partly: `statutes-and-other-sources.md` |
| 14 | Administrative materials | **Missing** | Partly: `statutes-and-other-sources.md` |
| 15 | Books | **Missing** | Partly: `statutes-and-other-sources.md` |
| 16 | Periodicals | **Missing** | Partly: `statutes-and-other-sources.md` |
| 17 | Unpublished and forthcoming sources | **Missing** | Partly: `statutes-and-other-sources.md` |
| 18.2 | Internet sources | **Missing** | Partly: `statutes-and-other-sources.md` |
| 18.3 | AI-generated content (new) | **Missing** | `statutes-and-other-sources.md` |
| 18.4 | Commercial databases | Partly | `case-citations.md`, `statutes-and-other-sources.md` |
| 18.5–18.11 | Storage media, video, audio, images, social media, software | Missing | Not added. Rarely used in memos or briefs. |
| 19 | Services | **Missing** | Partly: `statutes-and-other-sources.md` |
| 20–23 | Foreign, international, tribal, archival | **Missing** | Outlined only |

## Tables

| Table | Topic | Before | Now |
|---|---|---|---|
| T1 | U.S. jurisdictions: reporters, courts, codes | Partly; reporter names wrong | `abbreviations.md` (reporters corrected, `N.W.3d`, `A.D.` added); codes pointed to T1.3 |
| T2–T5 | Foreign jurisdictions, IGOs, treaty sources, arbitral reporters | Missing | Not added |
| T6 | Case names and institutional authors | **Contradicted** (see #7–8); about 70 party-name words missing | `abbreviations.md` (corrected; party-name words added; plural and possessive rules) |
| T7 | Court names | Partly | `abbreviations.md` (more courts; composite method) |
| T8 | Explanatory phrases | Partly | `abbreviations.md` (all 41) |
| T9 | Legislative documents | Missing | Not added; examples in `statutes-and-other-sources.md` |
| T10 | Geographical terms | Partly (states only) | `abbreviations.md` (territories, 20 cities) |
| T11 | Judges and officials | Missing | Partly: `typeface-and-placement.md` (B9 forms) |
| T12 | Months, `Sep.` | **Missing** | `abbreviations.md` |
| T13–T15 | Periodical names, publishing terms, services | Missing | Not added; pointed to |
| T16 | Subdivisions | **Missing** | `abbreviations.md` |

## Inconsistencies inside the Bluebook text

The skill follows the specific rule or table over a stray example:

- **"93rd Cong."** in the B13 example contradicts Rule 6.2(b)(ii) (`2d`, `3d` in citations) and Rule 13's own `93d Cong.` The skill uses `93d`.
- **"Cal. Code. Regs."** (extra period) in the B14 example. T1 and Rule 14 give `Cal. Code Regs.` The skill uses `Cal. Code Regs.`
- **U.C.C. publisher:** B12.1.3 gives `(Unif. L. Comm'n 1977)`, Rule 12.9.4 gives `(A.L.I. & Unif. L. Comm'n 1977)`, and the quick-reference page gives `(Unif. Law Comm'n 1977)`. The skill shows the Bluepages form and doesn't flag the others.
- **"Sept."** survives in four examples. T12 gives `Sep.`, and 74 examples use it. The skill follows T12.
- **State-constitution parts in text:** Rule 8(d) capitalizes parts of "a state or the U.S. Constitution," but Rule 11's table writes "article I, section 12" for a state. The skill states the U.S. rule only.
- **Split citations:** B10.1.1(vi) shows the full citation embedded after the case name in text. Rule 10.2.2 and the Rule 2 brief example show the name in text and the rest in the next citation sentence. Both are correct, and the skill tells agents not to flag either.
- **Source oddity:** the provided `Bluebook.docx` contains a Rule 18.1 example dated May 21, 2026 that names "Claude Opus 4.7," which postdates the 2025 edition. The copy may include later online updates or edits. No skill rule depends on that example.

## Bluebook Uncovered versus the Bluebook

_Pending: filled in from the cross-check below._

## Deliberately not covered

- Rule 10.8.2 (Fifth Circuit split), 10.8.4 (court administrative orders), 18.5–18.11 (media), and the detail of Rules 12.4–12.8, 13–17, and 19–23. These rarely appear in memos or briefs. The skill tells agents to look up the specific rule rather than extrapolate.
- Full reproductions of T1, T2–T5, T9, T11, and T13–T15. The skill states rules in its own words and carries only the abbreviation lists an agent needs to apply them.
