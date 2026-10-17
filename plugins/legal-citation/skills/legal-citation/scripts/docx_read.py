#!/usr/bin/env python3
"""Read a Word document with the formatting that matters for citations.

    python3 docx_read.py memo.docx              # numbered paragraphs
    python3 docx_read.py memo.docx --revisions  # also list pending tracked changes

Italic text is wrapped in ‹…›, underlined text in «…», bold in ⟦…⟧, so you can
see whether a case name, its comma, or the period in "Id." is italicized.
Text reads as if every pending tracked change were accepted; use --revisions
to see what is still pending and who made it. Covers the main text, footnotes,
and endnotes.
"""

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PARTS = (("word/document.xml", "TEXT"), ("word/footnotes.xml", "FOOTNOTES"), ("word/endnotes.xml", "ENDNOTES"))


try:  # an update notice must never stop the tool itself
    from update_check import announce
except Exception:  # noqa: BLE001
    def announce():
        pass


def on(rpr, tag):
    el = rpr.find(W + tag) if rpr is not None else None
    return el is not None and el.get(W + "val") not in ("0", "false", "none")


def paragraphs(xml):
    root = ET.fromstring(xml)
    for p in root.iter(W + "p"):
        parts = []
        for r in p.iter(W + "r"):
            text = "".join(t.text or "" if t.tag == W + "t" else "\t" for t in r if t.tag in (W + "t", W + "tab"))
            if not text:
                continue
            rpr = r.find(W + "rPr")
            parts.append([text, on(rpr, "i"), on(rpr, "u"), on(rpr, "b")])
        merged = []
        for part in parts:
            if merged and merged[-1][1:] == part[1:]:
                merged[-1][0] += part[0]
            else:
                merged.append(part)
        out = ""
        for text, i, u, b in merged:
            if i:
                text = f"‹{text}›"
            if u:
                text = f"«{text}»"
            if b:
                text = f"⟦{text}⟧"
            out += text
        if out.strip():
            yield out


def revisions(xml):
    text = lambda s: "".join(re.findall(r"<w:(?:t|delText)\b[^>]*>([^<]*)</w:(?:t|delText)>", s))
    for m in re.finditer(r"<w:(ins|del)\b([^>]*)>(.*?)</w:\1>|<w:(rPrChange)\b([^>]*)>", xml, re.S):
        kind = m.group(1) or m.group(4)
        attrs = m.group(2) or m.group(5)
        author = re.search(r'w:author="([^"]*)"', attrs)
        label = {"ins": "inserted", "del": "deleted", "rPrChange": "formatting changed"}[kind]
        before = text(xml[max(0, m.start() - 2000):m.start()])[-40:]
        if kind == "rPrChange":  # the change sits inside a run's properties; name that run's words
            end = xml.find("</w:r>", m.end())
            body = text(xml[xml.find("</w:rPr>", m.end()):end])
        else:
            body = text(m.group(3) or "")
        yield f"{label:18} by {author.group(1) if author else '?'}: …{before}[{body}]…"


def main():
    ap = argparse.ArgumentParser(description="Read a .docx with italics, underlining, and bold marked.")
    ap.add_argument("docx")
    ap.add_argument("--revisions", action="store_true", help="list pending tracked changes")
    args = ap.parse_args()
    z = zipfile.ZipFile(args.docx)
    pending = []
    for part, title in PARTS:
        if part not in z.namelist():
            continue
        xml = z.read(part).decode("utf-8")
        paras = list(paragraphs(xml))
        if part != "word/document.xml" and not paras:
            continue
        print(f"=== {title} ===")
        for n, p in enumerate(paras, 1):
            print(f"[{n}] {p}\n")
        pending += list(revisions(xml))
    if args.revisions:
        print(f"=== PENDING TRACKED CHANGES: {len(pending)} ===")
        for line in pending:
            print(line)


if __name__ == "__main__":
    main()
    announce()
