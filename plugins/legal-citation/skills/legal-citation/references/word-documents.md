# Editing Word documents

When the user asks you to fix their document, not just report problems, make the changes as **tracked changes in the user's name** so they can review each one in Word.

## Rules

1. **The user is the author.** Tracked changes carry the user's name, never yours or any AI's. `docx_edit.py` takes the name from the document's metadata (last modified by, then creator). If it's missing, pass `--author` with the user's name, and ask if you don't know it. The script refuses agent names. Metadata names whoever saved the file last. So if the document might belong to someone else — a classmate's draft, a professor's template — confirm the name with the user. The script prints which name it used and where it came from.
2. **Never replace a file that's open.** Word keeps its own copy in memory. Replacing the file underneath it leads to an overwrite or a conflicting copy. Cloud-synced files (OneDrive, SharePoint, Dropbox) often have no `~$` lock file, so check which programs hold the file. `--in-place` does this with `lsof` and refuses if any other program has the file open. Cloud sync services, which hold synced files permanently, are ignored. If it's open, write a copy and tell the user, or ask them to close it.
3. **Write a copy unless the user asks you to edit in place.** `--in-place` keeps a backup of the original first.
4. **Fix only what's certain.** Leave judgment calls as notes for the user: restructuring a sentence, a citation you couldn't verify, anything that needs the source.
5. **Find each edit by its exact text.** If any edit matches nothing, or more often than asked, the whole batch stops before anything is written. Narrow it with `in`, `occurrence`, or `all`. A miss is usually an invisible character: a non-breaking space (common after `§`), a curly quote, or a different dash. The script points out a near-match and shows the document's exact text. Misspelled fields and wrong value types (`"italic": "false"` in quotes) are refused, not guessed at.
6. **Don't round-trip the document through a general-purpose Word or XML library.** Many silently rewrite markup they don't model — comments, revision ids, compatibility settings — and Word may then report the file as damaged. `docx_edit.py` rewrites only the runs it changes and copies everything else byte for byte.
7. **Resolve existing tracked changes first.** The script won't edit a paragraph that already has pending changes. Ask the user to accept or reject them.

## Workflow

1. **Read** with formatting visible:
   ```bash
   python3 scripts/docx_read.py memo.docx --revisions
   ```
   Italic text shows as `‹…›`, underlining as `«…»`, bold as `⟦…⟧`. Pending tracked changes are listed with their authors.
2. **Write the edits** to a JSON file (format below).
3. **Apply** them:
   ```bash
   python3 scripts/docx_edit.py memo.docx edits.json -o "memo (edited).docx"
   ```
   Before writing, the script proves that rejecting every change restores the original text, that accepting every change gives exactly the intended text, and that no other paragraph changed.
4. **Hand it over.** The user reviews in Word under Review → Track Changes and accepts what they agree with.
5. **Check afterwards.** Run `docx_read.py --revisions` again and confirm nothing is still pending. One-character insertions, like a period or a single letter, are easy to miss when accepting changes one by one.

## Edit format

A JSON list. Each edit finds text inside one paragraph and does one thing.

| Field | Meaning |
|---|---|
| `find` | Text to locate, within a single paragraph. Required. |
| `target` | The part of `find` to change. Defaults to all of it. Must occur once inside `find`. |
| `in` | Only search paragraphs that start with this text. |
| `occurrence` | Which match to use, counting from 1. Without it, `find` must match exactly once. |
| `all` | `true` to apply to every match. |
| Action | Exactly one of: `replace`: "text", `delete`: true, `insert_before`: "text", `insert_after`: "text", or any of `italic` / `bold` / `underline`: true or false. |

Typical citation fixes:

```json
[
  {"find": "Smith v. Acme Holdings, Inc., 9", "target": ", Inc.", "italic": true},
  {"find": "Smith, Acme", "target": ", ", "italic": false},
  {"find": "Smith, 721 at", "target": "721", "insert_after": " F.3d"},
  {"find": "Id.at 12", "target": "Id.", "insert_after": " "},
  {"find": "at *8 However", "target": "at *8", "insert_after": "."},
  {"find": "aff'd sub nom.", "italic": true},
  {"find": "Jonse", "replace": "Jones", "all": true},
  {"in": "In the present case", "find": "; see Smith", "target": "see ", "delete": true}
]
```

These do, in order: italicize a case name through "Inc."; take italics off the comma after a case name; add a missing reporter; add a missing space after *Id.*; add a missing period; italicize a history phrase; fix a misspelled name everywhere; and drop a repeated signal in one paragraph.

## Limits

- Each edit stays within one paragraph; it can't move text between paragraphs.
- Covers the main text, footnotes, and endnotes, but not headers, text boxes, or comments.
- `find` can't span a tab, line break, or symbol character.
- Refuses to split runs that contain tabs or fields, such as citations inserted by a reference manager.
- Formatting changes cover italic, bold, and underline.
- Works on `.docx` only. Convert an old `.doc` file first.
