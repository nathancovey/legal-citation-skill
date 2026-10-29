#!/usr/bin/env python3
"""Make edits to a Word document as tracked changes, in the user's name.

    python3 docx_edit.py memo.docx edits.json -o memo-edited.docx
    python3 docx_edit.py memo.docx edits.json --in-place

edits.json is a list. Each edit finds text inside one paragraph and does one thing:

    [
      {"find": "Jonse", "replace": "Jones", "all": true},
      {"find": "Acme Holdings, Inc., 9", "target": ", Inc.", "italic": true},
      {"find": "at *8 However", "target": "at *8", "insert_after": "."},
      {"find": "; see Smith", "target": "see ", "delete": true},
      {"in": "In the present case", "find": "aff'd sub nom.", "italic": true}
    ]

  find            text to locate (within a single paragraph)
  target          the part of `find` to change (default: all of it); must occur once in `find`
  in              only search paragraphs that start with this text
  occurrence      which match to use, counting from 1 (default: `find` must match exactly once)
  all             true to apply to every match
  action, exactly one of:
    replace "text" | delete true | insert_before "text" | insert_after "text"
    | any of italic / bold / underline: true or false

Inserted text (replace, insert_before, insert_after) takes the formatting of the
text next to it. To make part of it italic, wrap that part in ‹…›, the markers
docx_read.py shows: {"find": "two shifts", "insert_after": " (‹Id.› at 4)."}
inserts "Id." in italics and the rest in roman.

Safety, by design:
  - Every change is a tracked change the user can accept or reject in Word.
  - The author is the user, never the agent: taken from --author, else from the
    document's own metadata (last modified by, then creator).
  - Only the runs an edit touches are rewritten. Everything else in the package
    is copied byte for byte.
  - An edit that matches zero times, or more times than asked for, stops the
    whole run before anything is written. So do overlapping edits, edits that
    touch fields or tabs, and paragraphs that already contain tracked changes.
  - Before writing, it proves that rejecting every change gives back the
    original text, accepting every change gives exactly the intended text, and
    no other paragraph changed.
  - --in-place refuses while another program has the file open, and keeps a
    backup of the original first.

Covers the main text, footnotes, and endnotes.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from html import escape, unescape

PARTS = ("word/document.xml", "word/footnotes.xml", "word/endnotes.xml")
RUN = re.compile(r"<w:r(?:\s[^>]*)?>.*?</w:r>", re.S)
PARA = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)
T = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>|<w:t(?:\s[^>]*)?/>", re.S)
CACHE_HINT = re.compile(r"<w:lastRenderedPageBreak/>")
REVISION = re.compile(r"<w:(?:ins|del|moveFrom|moveTo|rPrChange|pPrChange)\b")
ITALIC = re.compile("‹([^‹›]+)›")  # italic span inside inserted text, as docx_read.py displays it
# Order of run properties required by the WordprocessingML schema.
ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
         "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
         "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText",
         "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]
PROPS = {"italic": (("i", "<w:i/>"), ("iCs", "<w:iCs/>")),
         "bold": (("b", "<w:b/>"), ("bCs", "<w:bCs/>")),
         "underline": (("u", '<w:u w:val="single"/>'),)}
SYNC_SERVICES = {"fileproviderd", "bird", "cloudd", "OneDrive", "OneDrive File Provider", "Dropbox",
                 "Google Drive", "mds", "mds_stores", "mdworker", "mdworker_shared", "QuickLookUIService"}
FIELDS = {"find": str, "target": str, "in": str, "occurrence": int, "all": bool, "replace": str,
          "delete": bool, "insert_before": str, "insert_after": str, "italic": bool, "bold": bool, "underline": bool}
NOT_AUTHORS = {"claude", "assistant", "ai", "chatgpt", "copilot", "agent"}


try:  # an update notice must never stop the tool itself
    from update_check import announce
except Exception:  # noqa: BLE001
    def announce():
        pass


class EditError(Exception):
    pass


# ------------------------------------------------------------------ runs
def parse_run(xml):
    open_tag, inner = re.match(r"(<w:r(?:\s[^>]*)?>)(.*)</w:r>$", xml, re.S).groups()
    m = re.match(r"(<w:rPr>.*?</w:rPr>|<w:rPr/>)", inner, re.S)
    rpr = m.group(1) if m else ""
    rest = inner[m.end():] if m else inner
    rest = CACHE_HINT.sub("", rest)  # layout cache Word regenerates; safe to drop from a rewritten run
    return {"xml": xml, "open": open_tag, "rpr": rpr,
            "text": unescape("".join(t or "" for t in T.findall(rest))),
            "simple": not T.sub("", rest).strip()}


def para_text(pxml):
    return "".join(parse_run(m.group(0))["text"] for m in RUN.finditer(pxml))


def rpr_children(rpr):
    if rpr in ("", "<w:rPr/>"):
        return []
    inner = rpr[len("<w:rPr>"):-len("</w:rPr>")]
    kids = [(m.group(1) or m.group(2), m.group(0))
            for m in re.finditer(r"<w:(\w+)\b[^>]*?/>|<w:(\w+)\b[^>]*>.*?</w:\2>", inner, re.S)]
    if "".join(x for _, x in kids) != inner:
        raise EditError(f"unrecognized run formatting, not touching it: {inner[:100]}")
    return kids


def set_props(kids, changes):
    """Turn italic / bold / underline on or off in a list of run properties, in schema order."""
    for prop, on in changes.items():
        tags = PROPS[prop]
        kids = [(n, x) for n, x in kids if n not in {t for t, _ in tags}]
        if on:
            for tag, xml in tags:
                pos = next((k for k, (n, _) in enumerate(kids)
                            if n in ORDER and ORDER.index(n) > ORDER.index(tag)), len(kids))
                kids.insert(pos, (tag, xml))
    return kids


class Writer:
    """Builds revision markup with unique ids, author, and date."""

    def __init__(self, author, first_id):
        self.author, self.next = escape(author), first_id
        self.date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def attrs(self):
        self.next += 1
        return f'w:id="{self.next}" w:author="{self.author}" w:date="{self.date}"'

    def formatted(self, rpr, changes):
        kids = rpr_children(rpr)
        old = "".join(x for _, x in kids)
        kids = set_props(kids, changes)
        if "".join(x for _, x in kids) == old:  # already formatted that way: no change to track
            return rpr
        change = f"<w:rPrChange {self.attrs()}><w:rPr>{old}</w:rPr></w:rPrChange>"
        return "<w:rPr>" + "".join(x for _, x in kids) + change + "</w:rPr>"

    def piece(self, run, text, mode=None, fmt=None):
        t = escape(text, quote=False)
        if mode == "del":
            return (f'<w:del {self.attrs()}>{run["open"]}{run["rpr"]}'
                    f'<w:delText xml:space="preserve">{t}</w:delText></w:r></w:del>')
        rpr = self.formatted(run["rpr"], fmt) if mode == "fmt" else run["rpr"]
        return f'{run["open"]}{rpr}<w:t xml:space="preserve">{t}</w:t></w:r>'

    def insertion(self, run, text, segments=None):
        """One tracked insertion formatted like `run`; segments [(text, italic)] set italics piece by piece."""
        pieces = [(run["rpr"], text)]
        if segments:  # a new run needs no rPrChange: rejecting the insertion removes it whole
            kids = rpr_children(run["rpr"])
            pieces = []
            for t, italic in segments:
                props = "".join(x for _, x in set_props(kids, {"italic": italic}))
                pieces.append((f"<w:rPr>{props}</w:rPr>" if props else "", t))
        runs = "".join(f'{run["open"]}{rpr}<w:t xml:space="preserve">{escape(t, quote=False)}</w:t></w:r>'
                       for rpr, t in pieces)
        return f'<w:ins {self.attrs()}>{runs}</w:ins>'


def edit_paragraph(pxml, ops, w):
    """ops: ('del', a, b) | ('fmt', a, b, {prop: bool}) | ('ins', at, text, copy_from, segments)."""
    segs, pos = [], 0
    for m in RUN.finditer(pxml):
        segs += [("raw", pxml[pos:m.start()]), ("run", parse_run(m.group(0)))]
        pos = m.end()
    segs.append(("raw", pxml[pos:]))
    spans, off = [], 0
    for kind, s in segs:
        if kind == "run":
            spans.append((off, off + len(s["text"]), s))
            off += len(s["text"])

    def run_at(i):
        return next(r for a, b, r in spans if a <= i < b)

    ranged = [op for op in ops if op[0] != "ins"]
    cuts = {c for op in ranged for c in op[1:3]} | {op[1] for op in ops if op[0] == "ins"}
    inserts = {}
    for op in ops:
        if op[0] == "ins":
            inserts.setdefault(op[1], []).append(w.insertion(run_at(op[3]), op[2], op[4]))

    out = []
    for kind, s in segs:
        if kind == "raw":
            out.append(s)
            continue
        a, b, r = next(x for x in spans if x[2] is s)
        bounds = sorted({a, b} | {c for c in cuts if a < c < b})
        touched = a < b and (len(bounds) > 2 or any(op[1] < b and op[2] > a for op in ranged))
        if not touched:
            out.append("".join(inserts.pop(a, [])))
            out.append(r["xml"])
            continue
        if not r["simple"]:
            raise EditError(f"an edit touches a run with a tab, field, or other non-text content: {r['text']!r}")
        for x, y in zip(bounds, bounds[1:]):
            out.append("".join(inserts.pop(x, [])))
            mode, fmt = None, None
            for op in ranged:
                if op[1] <= x and y <= op[2]:
                    mode, fmt = op[0], (op[3] if op[0] == "fmt" else None)
            out.append(w.piece(r, r["text"][x - a:y - a], mode, fmt))
    if inserts:  # insertion at the very end of the paragraph
        tail = "".join(v for k in sorted(inserts) for v in inserts[k])
        last = max(i for i, o in enumerate(out) if "</w:r>" in o)
        out.insert(last + 1, tail)
    return "".join(out)


def accepted_text(text, ops):
    chars = [[c] for c in text] + [[]]
    for op in ops:
        if op[0] == "del":
            for i in range(op[1], op[2]):
                chars[i] = []
    for op in sorted((o for o in ops if o[0] == "ins"), key=lambda o: -o[1]):
        chars[op[1]].insert(0, op[2])
    return "".join("".join(c) for c in chars)


def view(pxml, accepted):
    if accepted:
        pxml = re.sub(r"<w:del\b[^>]*>.*?</w:del>", "", pxml, flags=re.S)
    else:
        pxml = re.sub(r"<w:ins\b[^>]*>.*?</w:ins>", "", pxml, flags=re.S)
        pxml = pxml.replace("<w:delText", "<w:t").replace("</w:delText>", "</w:t>")
    return para_text(pxml)


# --------------------------------------------------------------- planning
def fold(text):
    """Collapse look-alike characters, only to suggest what the user meant."""
    return text.translate(str.maketrans({"\u00a0": " ", "\u2018": "'", "\u2019": "'", "\u201c": '"',
                                         "\u201d": '"', "\u2013": "-", "\u2014": "-", "\u2011": "-"}))


def italic_segments(text):
    """Split inserted text on ‹…›: (text without markers, ((piece, italic), ...)), or (text, None) if unmarked."""
    if not ITALIC.search(text):
        return text, None
    segments, pos = [], 0
    for m in ITALIC.finditer(text):
        segments += [(text[pos:m.start()], False), (m.group(1), True)]
        pos = m.end()
    segments.append((text[pos:], False))
    segments = tuple((t, i) for t, i in segments if t)
    return "".join(t for t, _ in segments), segments


def plan(edits, paragraphs):
    """Turn edits into per-paragraph ops. paragraphs: list of (key, text)."""
    ops, report = {}, []
    for n, e in enumerate(edits, 1):
        if not isinstance(e, dict):
            raise EditError(f"edit {n}: each edit must be a JSON object")
        label = f"edit {n} ({e.get('find', '')!r})"
        unknown = set(e) - set(FIELDS)
        if unknown:
            raise EditError(f"{label}: unknown field(s) {sorted(unknown)} — check the spelling")
        for key, value in e.items():
            kind = FIELDS[key]
            if key in ("delete", "all"):
                ok, want = value is True, "true"
            elif kind is bool:
                ok, want = isinstance(value, bool), "true or false"
            elif kind is int:
                ok, want = isinstance(value, int) and not isinstance(value, bool) and value > 0, "a number from 1 up"
            else:
                ok, want = isinstance(value, str), "text in quotes"
            if not ok:
                raise EditError(f"{label}: '{key}' must be {want}, not {json.dumps(value)}")
        if not e.get("find"):
            raise EditError(f"{label}: needs a 'find'")
        for key in ("replace", "insert_before", "insert_after"):
            if key in e and e[key] == "":
                raise EditError(f"{label}: '{key}' is empty — use \"delete\": true to remove text")
        actions = [k for k in ("replace", "delete", "insert_before", "insert_after") if k in e]
        fmt = {k: bool(e[k]) for k in PROPS if k in e}
        if len(actions) + bool(fmt) != 1 or len(actions) > 1:
            hint = (" — to italicize inserted text, wrap that part in ‹…›"
                    if e.get("italic") and set(actions) - {"delete"} else "")
            raise EditError(f"{label}: give exactly one action (replace, delete, insert_before, "
                            f"insert_after) or formatting (italic / bold / underline){hint}")
        inserted, segments = None, None
        if actions and actions[0] != "delete":
            if re.search("[‹›]", ITALIC.sub("", e[actions[0]])):
                raise EditError(f"{label}: '{actions[0]}' has an unmatched or empty italic marker; wrap each "
                                f"italic part in one pair, as in ‹Id.›")
            inserted, segments = italic_segments(e[actions[0]])
        target = e.get("target", e["find"])
        if e["find"].count(target) != 1:
            raise EditError(f"{label}: 'target' {target!r} must appear exactly once inside 'find'")
        offset = e["find"].index(target)

        hits = []
        for key, text in paragraphs:
            if "in" in e and not text.startswith(e["in"]):
                continue
            hits += [(key, m.start()) for m in re.finditer(re.escape(e["find"]), text)]
        if e.get("all"):
            chosen = hits
        elif "occurrence" in e:
            k = int(e["occurrence"])
            chosen = hits[k - 1:k] if 0 < k <= len(hits) else []
        else:
            chosen = hits if len(hits) == 1 else []
            if len(hits) > 1:
                raise EditError(f"{label}: matches {len(hits)} times; add 'in', 'occurrence', or 'all'")
        if not chosen:
            hint = ""
            if not hits:
                loose = fold(e["find"])
                near = [text[i:i + len(e["find"])] for _, text in paragraphs
                        for i in range(len(text)) if fold(text[i:i + len(e["find"])]) == loose][:1]
                if near:
                    hint = f". The document has {near[0]!r} — it differs in spaces, quotes, or dashes; copy it exactly"
            raise EditError(f"{label}: no match{' at that occurrence' if hits else ''}{hint or ' — check the exact wording'}")

        for key, start in chosen:
            s = start + offset
            t = s + len(target)
            if fmt:
                new = [("fmt", s, t, fmt)]
            elif "delete" in e:
                new = [("del", s, t)]
            elif "replace" in e:
                new = [("del", s, t), ("ins", t, inserted, s, segments)]
            elif "insert_before" in e:
                new = [("ins", s, inserted, s, segments)]
            else:
                new = [("ins", t, inserted, t - 1, segments)]
            for op in new:
                for other in ops.get(key, []):
                    if op[0] != "ins" and other[0] != "ins" and op[1] < other[2] and other[1] < op[2]:
                        raise EditError(f"{label}: overlaps another edit in the same paragraph")
            ops.setdefault(key, []).extend(new)
        report.append((label, len(chosen)))
    return ops, report


# ---------------------------------------------------------------- package
def default_author(z):
    if "docProps/core.xml" not in z.namelist():
        return None
    core = z.read("docProps/core.xml").decode("utf-8")
    for tag in ("cp:lastModifiedBy", "dc:creator"):
        m = re.search(rf"<{tag}>([^<]+)</{tag}>", core)
        if m and m.group(1).strip():
            return unescape(m.group(1).strip())
    return None


def open_by_others(path):
    """Programs other than us holding the file, plus Word's ~$ lock file if present."""
    holders = set()
    try:
        out = subprocess.run(["lsof", "-F", "pc", "--", path], capture_output=True, text=True).stdout
        pid = None
        for line in out.splitlines():
            if line.startswith("p"):
                pid = int(line[1:])
            elif line.startswith("c") and pid != os.getpid() and line[1:] not in SYNC_SERVICES:
                holders.add(line[1:])
    except FileNotFoundError:  # no lsof (e.g. Windows): Word's lock file is the only signal
        pass
    holders = sorted(holders)
    folder, name = os.path.split(os.path.abspath(path))
    lock = os.path.join(folder, "~$" + name[2:])
    if os.path.exists(lock):
        holders.append(f"Word lock file {os.path.basename(lock)}")
    return holders


def main():
    ap = argparse.ArgumentParser(description="Edit a .docx as tracked changes in the user's name.")
    ap.add_argument("docx")
    ap.add_argument("edits", help="JSON file with a list of edits")
    ap.add_argument("-o", "--output", help="write the edited copy here")
    ap.add_argument("--in-place", action="store_true", help="replace the original (refused while it is open)")
    ap.add_argument("--author", help="name to put on the tracked changes (default: from the document)")
    args = ap.parse_args()
    if bool(args.output) == args.in_place:
        ap.error("give either -o OUTPUT or --in-place")

    try:
        edits = json.load(open(args.edits, encoding="utf-8"))
        if not isinstance(edits, list):
            raise EditError("the edits file must contain a JSON list")
        zin = zipfile.ZipFile(args.docx)
        author = (args.author or default_author(zin) or "").strip()
        author_source = "given with --author" if args.author else "from the document's metadata"
        if not author:
            raise EditError("no author name in the document's metadata; pass --author with the user's name")
        if author.lower() in NOT_AUTHORS:
            raise EditError(f"tracked changes belong to the user, not {author!r}; pass --author with the user's name")

        parts = {p: zin.read(p).decode("utf-8") for p in PARTS if p in zin.namelist()}
        ids = [int(i) for x in parts.values() for i in re.findall(r'w:id="(-?\d+)"', x)]
        writer = Writer(author, max(ids + [0]) + 1000)

        paragraphs = []
        for p, xml in parts.items():
            for i, m in enumerate(PARA.finditer(xml)):
                paragraphs.append(((p, i), para_text(m.group(0))))
        ops, report = plan(edits, paragraphs)

        new_parts = {}
        for p, xml in parts.items():
            pieces, last, changed = [], 0, 0
            for i, m in enumerate(PARA.finditer(xml)):
                pieces.append(xml[last:m.start()])
                para = m.group(0)
                if (p, i) in ops:
                    if REVISION.search(para):
                        raise EditError(f"a paragraph to edit already has tracked changes; accept or reject them "
                                        f"first: {para_text(para)[:70]!r}")
                    before = para_text(para)
                    edited = edit_paragraph(para, ops[(p, i)], writer)
                    if view(edited, False) != before:
                        raise EditError(f"self-check failed: rejecting the changes would not restore {before[:60]!r}")
                    if view(edited, True) != accepted_text(before, ops[(p, i)]):
                        raise EditError(f"self-check failed: accepting the changes gives unexpected text in {before[:60]!r}")
                    para, changed = edited, changed + 1
                pieces.append(para)
                last = m.end()
            pieces.append(xml[last:])
            new = "".join(pieces)
            ET.fromstring(new.encode("utf-8"))
            old_paras, new_paras = PARA.findall(xml), PARA.findall(new)
            if len(old_paras) != len(new_paras) or sum(a != b for a, b in zip(old_paras, new_paras)) != changed:
                raise EditError(f"self-check failed: a paragraph changed that shouldn't have in {p}")
            new_parts[p] = new
    except (EditError, json.JSONDecodeError, zipfile.BadZipFile, ET.ParseError) as err:
        sys.exit(f"Nothing written. {err}")

    target = args.docx if args.in_place else args.output
    if args.in_place:
        holders = open_by_others(args.docx)
        if holders:
            sys.exit(f"Nothing written. The file is open in: {', '.join(holders)}. Close it there, or use -o to "
                     f"write a copy.")
        backup = os.path.join(tempfile.mkdtemp(prefix="docx-backup-"), os.path.basename(args.docx))
        shutil.copy2(args.docx, backup)
    tmp = target + ".tmp-edit"
    try:
        with zipfile.ZipFile(tmp, "w") as zout:
            for info in zin.infolist():
                data = new_parts[info.filename].encode("utf-8") if info.filename in new_parts else zin.read(info.filename)
                zout.writestr(info, data, compress_type=info.compress_type)
        os.replace(tmp, target)
    except OSError as err:
        if os.path.exists(tmp):
            os.remove(tmp)
        sys.exit(f"Nothing written. Couldn't save {target}: {err.strerror or err}. If it's open in Word, close it "
                 f"or write a copy with -o.")

    print(f"Wrote {target}  ({writer.next - (max(ids + [0]) + 1000)} tracked changes)")
    print(f"Author: {author} ({author_source}). If that isn't the user, rerun with --author.")
    for label, count in report:
        print(f"  {label}: {count} match{'es' if count != 1 else ''}")
    if args.in_place:
        print(f"Backup of the original: {backup}")


if __name__ == "__main__":
    main()
    announce()
