# Verifying citations against sources

## Numbers are copied, never generated

Every volume, first page, pincite, year, and docket number must trace to text you can see: the opinion, a reporter page, a database page header, or a court's own citation of the case. If you can't see it:

- write `___` in its place,
- say exactly what is missing ("pincite for the 'not dominated by the police' passage"),
- never fill in a plausible number.

Two failures this rule exists to prevent, both from real drafts:

- An AI assistant supplied a pincite from memory. The writer adopted it before anyone noticed it was invented.
- A draft cited a page of a Supreme Court case that appeared in none of the writer's sources. Every other pincite to that case in the materials had been redacted.

## Finding the page: star pagination

Database printouts mark where each page of the official reporter begins with an inline marker: `*138` means page 138 starts here.

- Text after a marker is on that page until the next marker.
- Text before the first marker of an opinion is on the opinion's **first page**, the number in its citation.
- Markers restart with each opinion. In a packet of several cases, track them per case. Westlaw ends each document with "End of Document."
- A passage that crosses a marker spans both pages: `217–18`.
- A second reporter's pages may be marked with a double asterisk (`**5`). Don't mix the two.
- Search snippets and PDF page numbers are not reporter pages.

`scripts/find_pincite.py` does this mechanically:

```bash
python3 scripts/find_pincite.py packet.pdf "would have been free to leave"
```

## What isn't the opinion

- **Syllabi, headnotes, synopses, and key-number summaries** are written by the reporter or publisher, not the court. Never quote or cite them as the court's words. In U.S. Reports the syllabus comes before the opinion. The opinion begins where a Justice "delivered the opinion of the Court."
- **Database captions and running headers** are not citation form. They abbreviate in house style (`U.S. v. Brownlee`). Rebuild the case name from the rules.

## Redacted or edited materials

Course packets and closed-universe assignments often blank out pincites on purpose (for example, `468 U.S. at 4`). Before filling them in from outside research, ask whether outside sources are allowed. Follow the answer. Once the user says the instructor permits it, stop flagging it.

## Read before you characterize

- **Pull the full paragraph, not a search hit.** A search that cut off one sentence early once led to a confident and wrong claim about what a case said. The next sentence said exactly what the writer had paraphrased.
- **Check what the court did with the language.** A rule statement can come from a case that applied it against your position. For example, a court may say an officer's intent doesn't matter while *finding* that an interrogation occurred. Citing that case for the rule without distinguishing its result is a trap.
- **Don't promote a factor into a test**, and don't attach one case's phrasing to another case.
- **Compare quotations character by character.** Watch for dropped words, changed verbs, and sentences that really end in a semicolon.

## Review discipline

- **One citation, one verdict.** If you would propose two different rewrites of the same citation, stop and say you're unsure rather than reporting both.
- **Confidence has to be earned.** Call a correction *certain* only when you have checked both the rule and the source. Otherwise label it *check* and say which part is unverified.
- **When challenged, re-check before you reply.** If the user is right, concede plainly and fix it. If not, show the rule or the source text.
- **Respect a decision once it's made.** After the user decides — "my instructor allows it" — note it once and move on.
