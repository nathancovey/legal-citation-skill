#!/usr/bin/env python3
"""Find the reporter page a passage falls on, using star pagination.

Database printouts (Westlaw, Lexis) mark where each page of the official
reporter begins with an inline marker such as "*138". This locates a phrase in
a PDF and reports the page that governs it, so a pincite is copied from the
source instead of guessed.

    python3 find_pincite.py packet.pdf "inappropriately expansive response"
    python3 find_pincite.py packet.pdf --markers

Matching ignores case, line breaks, curly-versus-straight quotes, hyphens and
dashes, and the star markers themselves, so a passage that crosses a page
break is still found and reported as a range ("217-18").

Requires pypdf:  pip install pypdf
"""

import argparse
import re
import sys

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("find_pincite.py needs pypdf:  pip install pypdf")

# "*138" (primary reporter) or "**5" (a parallel reporter). Must not touch a
# word character on either side, so "* * *" and footnote numbers don't match.
MARKER = re.compile(r"(?<![\w*])(\*{1,2})(\d{1,5})(?!\w)")
# Westlaw closes every document with this line; star pages restart after it.
DOC_END = re.compile(r"End of Document", re.IGNORECASE)
# A citation in a running header: "State v. Andrews, 843 A.2d 136 (Del. Super. Ct. 2003)".
CAPTION = re.compile(r"(\S+ v\. [^,\n]{1,60}, \d{1,4} [^()\n]{1,25}? \d{1,5} \([^)\n]*?\d{4}\))")

FOLD = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", " ": " ", "­": None,
})


def normalize(text, skip=()):
    """Fold text for matching; return it with a map back to source offsets."""
    out, where = [], []
    last_space, last_hyphen = True, False
    for i, ch in enumerate(text):
        if i in skip:
            continue
        c = ch.translate(FOLD).lower()
        if not c:
            continue
        if c == "-":
            # A hyphen at a line break may be part of the word ("non-
            # threatening") or only typesetting ("ordi- nary"); the PDF text
            # can't tell us which. Ignoring hyphens and dashes on both sides
            # lets either spelling match.
            last_hyphen = True
            continue
        if c.isspace():
            # Collapse runs of whitespace, including the break after a hyphen.
            if last_space or last_hyphen:
                continue
            c = " "
        out.append(c)
        where.append(i)
        last_space = c == " "
        last_hyphen = c == "-"
    return "".join(out), where


def page_range(first, last):
    """Format a page range, keeping the last two digits: 217-18, 1065-69."""
    if first == last:
        return str(first)
    a, b = str(first), str(last)
    if len(a) == len(b):
        common = 0
        while common < len(a) and a[common] == b[common]:
            common += 1
        b = b[min(common, len(b) - 2):]
    return f"{a}–{b}"


def load(path):
    reader = PdfReader(path)
    stream, starts = "", []
    for page in reader.pages:
        starts.append(len(stream))
        stream += (page.extract_text() or "") + "\n"
    return stream, starts


def pdf_page(offset, starts):
    n = 0
    for i, s in enumerate(starts):
        if s <= offset:
            n = i
    return n + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdf")
    ap.add_argument("phrase", nargs="?", help="text to locate (any length)")
    ap.add_argument("--markers", action="store_true", help="list the star markers on each PDF page")
    ap.add_argument("--context", type=int, default=90, help="characters of context to print (default 90)")
    args = ap.parse_args()

    stream, starts = load(args.pdf)
    markers = [(m.start(), m.end(), len(m.group(1)), int(m.group(2))) for m in MARKER.finditer(stream)]
    doc_ends = [m.start() for m in DOC_END.finditer(stream)]

    if args.markers:
        for p, s in enumerate(starts, 1):
            e = starts[p] if p < len(starts) else len(stream)
            here = [("*" * stars) + str(n) for a, _, stars, n in markers if s <= a < e]
            print(f"PDF page {p}: {' '.join(here) or '(none)'}")
        return

    if not args.phrase:
        ap.error("give a phrase to find, or --markers")

    skip = set()
    for a, b, _, _ in markers:
        skip.update(range(a, b))
    hay, where = normalize(stream, skip)
    needle, _ = normalize(args.phrase)
    needle = needle.strip()
    if not needle:
        ap.error("the phrase is empty after normalization")

    hits = [m.start() for m in re.finditer(re.escape(needle), hay)]
    if not hits:
        print(f'Not found: "{args.phrase}"')
        print("Check the wording against the source; a quotation that can't be found may be misquoted.")
        sys.exit(1)

    for n, h in enumerate(hits, 1):
        a, b = where[h], where[h + len(needle) - 1]
        doc_start = max([d for d in doc_ends if d < a], default=0)
        primary = [m for m in markers if m[2] == 1 and doc_start <= m[0]]
        before = [m for m in primary if m[0] < a]
        inside = [m for m in primary if a < m[0] < b]

        p = pdf_page(a, starts)
        caption = CAPTION.search(stream, starts[p - 1], starts[p] if p < len(starts) else len(stream))
        case = caption.group(1) if caption else None

        if before:
            first = before[-1][3]
            last = inside[-1][3] if inside else first
            page = page_range(first, last)
            how = f"after the *{first} marker"
        else:
            m = re.search(r", (\d{1,4}) [^()]{1,25}? (\d{1,5}) \(", case or "")
            opening = m.group(2) if m else None
            last = inside[-1][3] if inside else None
            if opening and last:
                page = page_range(int(opening), last)
            elif opening:
                page = opening
            else:
                page = "the opinion's first page"
            how = "before the opinion's first star marker, so it is on the first page"

        ctx_a = max(0, h - args.context)
        ctx_b = min(len(hay), h + len(needle) + args.context)
        print(f"Match {n}: reporter page {page}  (PDF page {pdf_page(a, starts)}; {how})")
        if case:
            print(f"  case: {case}")
        print(f"  …{hay[ctx_a:ctx_b]}…")
        print()


if __name__ == "__main__":
    main()
