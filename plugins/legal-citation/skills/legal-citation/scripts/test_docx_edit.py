#!/usr/bin/env python3
"""Self-test for docx_edit.py and docx_read.py.

    python3 test_docx_edit.py

Builds a small Word document — italic and split runs, a comment, a footnote,
and a paragraph that already has a tracked change — then runs every edit type
and every refusal through the real command line.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["LEGAL_CITATION_NO_UPDATE_CHECK"] = "1"  # tests never touch the network
EDIT, READ = os.path.join(HERE, "docx_edit.py"), os.path.join(HERE, "docx_read.py")
NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
I = "<w:rPr><w:i/><w:iCs/></w:rPr>"
TNR = '<w:rFonts w:ascii="Times New Roman"/>{}<w:sz w:val="24"/>'  # formatting around where italics go

DOC = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document {NS}><w:body>
<w:p><w:r><w:t xml:space="preserve">See </w:t></w:r><w:r>{I}<w:t>Doe v. Roe Co</w:t></w:r><w:r><w:t>, Inc., 12 A.3d 1, 5 (Del. 2015). Jonse met Jonse.</w:t></w:r></w:p>
<w:p><w:r>{I}<w:t>S</w:t></w:r><w:r>{I}<w:t>ee Smith</w:t></w:r><w:r><w:t xml:space="preserve">, 9 A.3d at 4. Id.at 6 Then</w:t></w:r></w:p>
<w:p><w:commentRangeStart w:id="0"/><w:r><w:t>Commented text stays put.</w:t></w:r><w:commentRangeEnd w:id="0"/><w:r><w:commentReference w:id="0"/></w:r></w:p>
<w:p><w:ins w:id="1" w:author="Someone" w:date="2026-01-01T00:00:00Z"><w:r><w:t>Already tracked.</w:t></w:r></w:ins></w:p>
<w:p><w:r><w:t xml:space="preserve">Before the page </w:t><w:lastRenderedPageBreak/><w:t>breaks here.</w:t></w:r></w:p>
<w:p><w:r><w:t>See 29 U.S.C. § 2612.</w:t></w:r></w:p>
<w:p><w:r><w:rPr>{TNR.format("")}</w:rPr><w:t>She missed two shifts</w:t></w:r></w:p>
<w:p><w:r>{I}<w:t>Smith</w:t></w:r><w:r><w:t xml:space="preserve"> held otherwise.</w:t></w:r></w:p>
</w:body></w:document>"""
FOOTNOTES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes {NS}><w:footnote w:id="1"><w:p><w:r><w:t xml:space="preserve">Roe, 12 A.3d at 5.</w:t></w:r></w:p></w:footnote></w:footnotes>"""
CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>Pat Lawyer</dc:creator><cp:lastModifiedBy>Pat Lawyer</cp:lastModifiedBy></cp:coreProperties>"""

failures = 0


def check(name, ok, detail=""):
    global failures
    failures += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f"  — {detail}" if detail and not ok else ""))


def build(path):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", DOC)
        z.writestr("word/footnotes.xml", FOOTNOTES)
        z.writestr("docProps/core.xml", CORE)


def run(tmp, src, edits, *extra):
    ej = os.path.join(tmp, "edits.json")
    json.dump(edits, open(ej, "w"))
    return subprocess.run([sys.executable, EDIT, src, ej, *extra], capture_output=True, text=True)


def part(path, name="word/document.xml"):
    return zipfile.ZipFile(path).read(name).decode()


def read(path):
    return subprocess.run([sys.executable, READ, path, "--revisions"], capture_output=True, text=True).stdout


def reject(src, dest, author="Pat Lawyer"):
    """What Word gives back when every insertion and deletion by `author` is rejected."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dest, "w") as zout:
        for info in zin.infolist():
            x = zin.read(info.filename).decode()
            x = re.sub(rf'<w:ins [^>]*w:author="{author}"[^>]*>.*?</w:ins>', "", x, flags=re.S)
            x = re.sub(rf'<w:del [^>]*w:author="{author}"[^>]*>(.*?)</w:del>',
                       lambda m: m.group(1).replace("w:delText", "w:t"), x, flags=re.S)
            zout.writestr(info, x)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        src, out = os.path.join(tmp, "memo.docx"), os.path.join(tmp, "out.docx")
        build(src)

        r = run(tmp, src, [
            {"find": "Jonse", "replace": "Jones", "all": True},
            {"find": "Roe Co, Inc., 12", "target": ", Inc.", "italic": True},
            {"find": "Id.at 6", "target": "Id.", "insert_after": " "},
            {"find": "at 6 Then", "target": "at 6", "insert_after": "."},
            {"find": "6 Then", "target": " Then", "delete": True},
            {"find": "See Smith", "replace": "Cf. Jones"},
            {"find": "Commented text", "target": "Commented", "bold": True},
            {"find": "Roe, 12 A.3d", "target": "Roe", "italic": True},
            {"find": "page breaks here", "target": "breaks", "replace": "ends"},
        ], "-o", out)
        check("edits apply", r.returncode == 0, r.stderr)
        text = read(out)
        check("replace all: both occurrences", "Jones met Jones." in text, text)
        check("italic added across a run boundary", "‹Doe v. Roe Co, Inc.›, 12 A.3d" in text, text)
        check("inserts and a delete in one sentence", "[2] ‹Cf. Jones›, 9 A.3d at 4. Id. at 6.\n" in text, text)
        check("formatting changes name the words they apply to", "formatting changed by Pat Lawyer: …See Doe v. Roe Co[, Inc.]" in text, text)
        check("replace spanning two runs keeps the formatting", "‹Cf. Jones›, 9 A.3d" in text, text)
        check("bold on part of a run", "⟦Commented⟧ text stays put." in text, text)
        check("footnote edited", "‹Roe›, 12 A.3d at 5." in text, text)
        check("edits a run containing Word's page-break marker", "Before the page ends here." in text, text)
        check("reports where the author name came from", "from the document's metadata" in r.stdout, r.stdout)
        doc = part(out)
        authors = set(re.findall(r'w:author="([^"]+)"', doc + part(out, "word/footnotes.xml")))
        check("author taken from the document, never the agent", authors == {"Pat Lawyer", "Someone"}, authors)
        check("comment anchors untouched", doc.count("commentRangeStart") == 1 and doc.count("commentReference") == 1)
        check("paragraph with an earlier tracked change left byte-identical",
              re.findall(r"<w:p>.*?</w:p>", DOC, re.S)[3] in doc)
        ids = re.findall(r'<w:(?:ins|del|rPrChange) w:id="(\d+)"', doc)
        check("revision ids unique", len(ids) == len(set(ids)))
        check("pending changes listed with author", "inserted" in text and "by Pat Lawyer" in text, text)

        mixed, undone = os.path.join(tmp, "mixed.docx"), os.path.join(tmp, "undone.docx")
        r = run(tmp, src, [
            {"find": "two shifts", "insert_after": " (‹Id.› at 4)."},
            {"find": "Smith held", "target": "Smith", "replace": "‹Smith›, 9 A.3d at 4,"},
        ], "-o", mixed)
        check("partly italic insertions apply", r.returncode == 0, r.stderr)
        text = read(mixed)
        check("only the part marked ‹…› is italic", "She missed two shifts (‹Id.› at 4).\n" in text, text)
        check("unmarked inserted text is roman even beside italics", "‹Smith›, 9 A.3d at 4, held otherwise." in text, text)
        check("a partly italic insertion is one tracked change",
              text.count("[ (Id. at 4).]") == 1 and "[Id.]" not in text, text)
        ins = re.search(r"two shifts</w:t></w:r><w:ins [^>]*>(.*?)</w:ins>", part(mixed), re.S)
        runs = re.findall(r"<w:rPr>(.*?)</w:rPr>", ins.group(1)) if ins else []
        check("italics placed in schema order, the rest of the formatting kept, no rPrChange",
              runs == [TNR.format(""), TNR.format("<w:i/><w:iCs/>"), TNR.format("")], runs)
        reject(mixed, undone)
        check("rejecting the partly italic changes restores the original, formatting included",
              read(undone) == read(src), read(undone))

        r = run(tmp, src, [
            {"find": "missed two", "target": "missed", "insert_after": " all"},
            {"find": "missed two", "target": " two", "insert_before": " of"},
            {"find": "two shifts", "insert_after": " (‹Id.›"},
            {"find": "two shifts", "insert_after": " at 4)."},
            {"find": "Smith held", "target": " held", "insert_before": ","},
            {"find": "Smith held", "target": " held", "insert_before": " 9 A.3d at 4,"},
        ], "-o", mixed)
        text = read(mixed)
        check("insertions at the same spot appear in the order listed",
              r.returncode == 0 and "She missed all of two shifts (‹Id.› at 4).\n" in text
              and "‹Smith›, 9 A.3d at 4, held otherwise." in text, r.stderr or text)

        def refused(name, edits, *extra, expect="Nothing written"):
            if os.path.exists(out):
                os.remove(out)
            r = run(tmp, src, edits, *extra, *(["-o", out] if "--in-place" not in extra else []))
            check(name, r.returncode != 0 and expect in r.stdout + r.stderr and not os.path.exists(out),
                  (r.stdout + r.stderr).strip()[:120])

        refused("refuses a phrase that isn't there", [{"find": "Nowhere", "delete": True}], expect="no match")
        refused("refuses an ambiguous match", [{"find": "Jonse", "replace": "X"}], expect="matches 2 times")
        refused("refuses a paragraph with existing tracked changes", [{"find": "Already tracked", "delete": True}],
                expect="already has tracked changes")
        refused("refuses an agent as author", [{"find": "Commented", "bold": True}], "--author", "Claude",
                expect="belong to the user")
        refused("refuses overlapping edits", [{"find": "Commented text", "delete": True},
                                              {"find": "text stays", "delete": True}], expect="overlaps")

        refused("refuses a misspelled field instead of changing all of 'find'",
                [{"find": "Commented text", "targt": "Commented", "delete": True}], expect="unknown field")
        refused("refuses \"false\" in quotes as a formatting value", [{"find": "Commented", "italic": "false"}],
                expect="must be true or false")
        refused("refuses delete: false", [{"find": "Commented", "delete": False}], expect="'delete' must be true")
        refused("refuses an empty replacement", [{"find": "Commented", "replace": ""}], expect="is empty")
        for bad in (" (‹Id. at 4).", " (Id.› at 4).", " (‹‹Id.›› at 4).", " (‹›Id. at 4)."):
            refused(f"refuses unmatched, nested, or empty italic markers: {bad!r}",
                    [{"find": "two shifts", "insert_after": bad}], expect="unmatched or empty italic marker")
        refused("points to ‹…› when an insertion is combined with italic",
                [{"find": "two shifts", "insert_after": " (Id. at 4).", "italic": True}], expect="wrap that part in ‹…›")
        refused("points out a non-breaking space the edit missed",
                [{"find": "U.S.C. \u00a7 2612", "delete": True}], expect="differs in spaces, quotes, or dashes")

        sys.path.insert(0, HERE)
        import docx_edit
        fake = "p981\ncfileproviderd\nf16\np84483\ncMicrosoft Word\nf22\n"
        real_run = docx_edit.subprocess.run
        docx_edit.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=fake, stderr="")
        try:
            held = docx_edit.open_by_others(src)
        finally:
            docx_edit.subprocess.run = real_run
        check("ignores the cloud sync service but still sees Word", held == ["Microsoft Word"], held)

        holder = subprocess.Popen([sys.executable, "-c", f"f = open({src!r}, 'rb'); import time; time.sleep(20)"])
        time.sleep(0.5)
        r = run(tmp, src, [{"find": "Commented", "bold": True}], "--in-place")
        holder.kill()
        check("in-place refused while another program has the file open",
              r.returncode != 0 and "open in" in r.stdout + r.stderr, (r.stdout + r.stderr).strip()[:120])
        r = run(tmp, src, [{"find": "Commented", "bold": True}], "--in-place")
        check("in-place works once the file is closed, with a backup",
              r.returncode == 0 and "Backup of the original" in r.stdout, r.stderr)

    print("\nall passed" if not failures else f"\n{failures} failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
