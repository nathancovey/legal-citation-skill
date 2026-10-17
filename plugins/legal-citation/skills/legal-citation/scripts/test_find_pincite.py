#!/usr/bin/env python3
"""Self-test for find_pincite.py against a generated two-opinion packet.

    python3 test_find_pincite.py

Builds a small PDF laid out like a database printout — running header with
the citation, star markers mid-sentence, an "End of Document" line between
opinions — and checks that each passage resolves to the page it is printed
on. Needs reportlab to build the fixture (pip install reportlab) as well as
pypdf.
"""

import os
import subprocess
import sys
import tempfile

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit("the self-test needs reportlab to build its fixture:  pip install reportlab")

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["LEGAL_CITATION_NO_UPDATE_CHECK"] = "1"  # tests never touch the network

# Two invented opinions. Each list item is one PDF page of lines.
PACKET = [
    [
        "Doe v. Roe, 100 A.3d 10 (Del. Super. Ct. 2015)",
        "The question is whether the encounter was brief.",
        "The officer approached the car alone and asked for a license.",
        "*11 The driver stayed in the car for the entire stop, and the",
        "officer never raised his voice. The court finds the stop was ordi-",
        "nary in every respect that matters here.",
    ],
    [
        "Doe v. Roe, 100 A.3d 10 (Del. Super. Ct. 2015)",
        "Because the defendant would have been free to go once the",
        "paperwork was done, he was not in custody. *12 The motion is",
        "denied. The court’s view is that nothing more was required.",
        "End of Document",
    ],
    [
        "Poe v. State, 200 A.3d 50 (Del. 2018)",
        "A different opinion begins here, before any star marker.",
        "*51 Text on the second page of the second opinion.",
    ],
]

CASES = [
    # (phrase, expected reporter page)
    ("whether the encounter was brief", "10"),                 # before the first marker
    ("the officer never raised his voice", "11"),
    ("nary in every respect", "11"),                           # line-break hyphen folded
    ("ordinary in every respect", "11"),                       # ...and found when typed whole
    ("he was not in custody. The motion is denied", "11–12"),  # crosses *12
    ("THE COURT'S VIEW", "12"),                                # case and curly-quote folding
    ("A different opinion begins here", "50"),                 # markers reset after End of Document
    ("second page of the second opinion", "51"),
]


def build(path):
    c = canvas.Canvas(path, pagesize=LETTER)
    for lines in PACKET:
        y = 720
        for line in lines:
            c.drawString(72, y, line)
            y -= 18
        c.showPage()
    c.save()


def main():
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        pdf = os.path.join(tmp, "packet.pdf")
        build(pdf)
        script = os.path.join(HERE, "find_pincite.py")
        for phrase, want in CASES:
            out = subprocess.run([sys.executable, script, pdf, phrase],
                                 capture_output=True, text=True).stdout
            first = next((l for l in out.splitlines() if l.startswith("Match 1:")), "")
            ok = f"reporter page {want} " in first + " "
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {phrase!r} -> {first or out.strip()[:80]}")

        missing = subprocess.run([sys.executable, script, pdf, "words that are not there"],
                                 capture_output=True, text=True)
        ok = missing.returncode == 1 and "Not found" in missing.stdout
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} a phrase that isn't in the PDF exits 1")

    print("\nall passed" if not failures else f"\n{failures} failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
