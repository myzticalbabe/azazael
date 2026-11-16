#!/usr/bin/env python3
# coding: utf-8
"""check_corpus_quotes — prove every corpus quote against the producer's own text.

Why this exists (2026-11-16)
----------------------------
A quote in the corpus is a claim about a document nobody re-opens. Three
instruments were tried on this tree and each one failed in a different
direction:

1. Compare the quote to ``-layout`` text. A two-column page's columns print
   side by side on one line (``pdftotext -layout``), so every sentence that
   crosses a column boundary is broken. False failures, silently.
2. Compare after DELETING things from both sides — bracketed elisions,
   citations, and bare digit runs that looked like footnote callouts — and call
   the result "apparatus". That instrument cannot fail for the reason it
   exists: a quote whose digits were wrong, or whose ``[...]`` stood for a
   paragraph the author never wrote, scored exactly the same as one whose
   callouts really had been flattened by extraction.
3. Trust the declaration. ``apparatus.removed`` is prose written by whoever
   pasted the quote; nothing checked it against the document.

So the verdicts here are the ones the corpus can actually defend:

    STRICT      the quote appears in the producer's text, under one named
                reading, with nothing removed.
    APPARATUS   the block DECLARES what was removed (``apparatus.kind`` plus an
                ``apparatus.removed`` list) and the declaration is PROVEN by
                re-insertion in reverse: delete each declared token from the
                source once and the quote must then be STRICT. A token the
                source does not contain fails the proof; it does not pass.
                Deleting ALL declared tokens before requiring STRICT is
                deliberately stronger than one-at-a-time: a marker sitting
                AFTER the quoted span cannot change the outcome alone, so a
                per-token test passes whether or not the token is real.
                A declaration is validated even when the quote already matches
                verbatim; otherwise the declaration is never read at all and an
                unprovable claim scores as a proven one (measured 2026-11-16).
    UNDECLARED  the old lenient stripping would have matched, but nothing is
                declared. This is the failure instrument (2) hid.
    ABSENT      no reading makes the quote appear. A real defect.
    NO-TEXT     the source text is not on disk. Counted as UNPROVEN, never as
                a pass: an instrument that cannot read the document has not
                checked the quote.

Readings, and why there are two
-------------------------------
A quote is typed on one line; the source was extracted from a PDF. The one
thing extraction does that is *not* reversible is decide whether a hyphen at a
line break belongs to the word or was inserted by justification. The literature
is explicit that this is undecidable in general (a vocabulary or LM is needed to
guess): "self-\nevident" is a soft break to join, "well-\nbeing" is a hard
hyphen to keep. So instead of silently joining every line-break hyphen — which
would glue a genuine compound and make the quote "match" text that says
something else — the checker computes BOTH readings of both sides and reports
which one matched:

    verbatim      hyphens kept, line breaks become spaces (strictest)
    dehyphenated  line-break hyphens and ``word- word`` joins removed

A quote passes only when it is contiguous in the SAME reading of both sides, and
the reading is printed. ``verbatim`` first, so a quote that needs no leniency is
never credited to one.

Why blanket NFKC is refused
---------------------------
NFKC is the reflex fix for extraction artefacts, and it is wrong here for a
reason this corpus cares about specifically: NFKC decomposes the compatibility
forms that include SUPERSCRIPT AND SUBSCRIPT DIGITS (U+00B2, U+00B3, U+00B9,
U+2070-U+2079) to ordinary ASCII digits. The footnote callouts this corpus
declares as an apparatus are exactly superscript digits, so NFKC would erase the
very distinction ``APPARATUS`` exists to police — a declared removal would
become indistinguishable from an outright fabrication, and the re-insertion
proof would have nothing left to find. The artefacts are therefore repaired one
named class at a time, each with its own evidence:

* ligatures U+FB00-U+FB06 -> ASCII, with an optional spurious space absorbed
  (``ﬁ eld`` -> ``field``); explicit map, per docling PR #3057, rather than NFKC.
* soft hyphen U+00AD removed explicitly. It has NO decomposition in any
  normalisation form (UAX #15), so NFKC would leave it in place anyway.
* zero-width characters U+200B/U+200C/U+200D/U+FEFF removed.
* NBSP U+00A0 and narrow NBSP U+202F -> space (UAX #15 compatibility).
* dash variants U+2010-U+2015 and U+2212 -> ``-``. Typographic alternates of the
  hyphen-minus; the font decides which one a PDF stores.
* NBSP, quotes, bullets and space-before-punctuation as before.

Source text
-----------
The corpus carries no source text, so this tool needs a cache of the producer's
own words. It is third-party material and is NOT committed; ``--sources-dir``
(repeatable) names where to look, first match wins, and a missing file is
reported as NO-TEXT rather than skipped. Defaults, in order:

    state/fn_reading     pdftotext -enc UTF-8, no -layout (reading order)
    state/fn_sources     saved HTML/text
    C:/tmp/fn_reading    the working cache on this box
    C:/tmp/fn_sources

``<source_id>.txt`` is the only filename consulted. The ``.layout.txt`` twins
are deliberately NOT read: ``-layout`` puts a two-column page's columns on one
line, which is the false-failure mode described above.

Usage
-----
    python tools/check_corpus_quotes.py
    python tools/check_corpus_quotes.py --corpus /path/to/corrupted-copy.json
    python tools/check_corpus_quotes.py --sources-dir ./fixtures/sources
    python tools/check_corpus_quotes.py --manifest logs/quote_manifest.json
    python tools/check_corpus_quotes.py --json

Exit codes
----------
    0  every quote is STRICT or a PROVEN APPARATUS
    1  a reading was performed and something failed (UNDECLARED, ABSENT, or a
       NO-TEXT block that could not be proven)
    2  the run could not be performed: corpus unreadable, no quotes, or no
       source text resolved at all. ``2`` is not a pass.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO_ROOT / "src" / "PSYCHE" / "data" / "female_needs_hyperedges.json"

#: Searched in order; the first directory holding ``<source_id>.txt`` wins.
DEFAULT_SOURCE_DIRS: Tuple[Path, ...] = (
    REPO_ROOT / "state" / "fn_reading",
    REPO_ROOT / "state" / "fn_sources",
    Path("C:/tmp/fn_reading"),
    Path("C:/tmp/fn_sources"),
)

#: Ordered strictest-first. A quote is credited to the first reading it needs.
READINGS: Tuple[str, ...] = ("verbatim", "dehyphenated")

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_BLIND = 2

# --- artefact normalisation -------------------------------------------------

#: U+FB00-U+FB06. An explicit map, never NFKC -- NFKC also folds superscript
#: digits to ASCII and would erase the footnote-callout apparatus.
LIGATURES: Dict[str, str] = {
    "\ufb00": "ff",
    "\ufb01": "fi",
    "\ufb02": "fl",
    "\ufb03": "ffi",
    "\ufb04": "ffl",
    "\ufb05": "st",
    "\ufb06": "st",
}

#: A ligature glyph optionally followed by the spurious space some extractors
#: emit before the rest of the word (docling #3057: "ﬁ eld" -> "field").
_LIGATURE_RUN = re.compile("([%s])\\s?(?=\\w)" % "".join(LIGATURES))

_ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\ufeff]")
#: U+2010..U+2015 (hyphen, non-breaking hyphen, figure dash, en/em/horizontal
#: bar) and U+2212 (minus). All are typographic alternates of "-".
_DASHES = re.compile("[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]")

#: "informa-\ntion" -- the layout's hyphen at a line break.
_HARD_WRAP = re.compile(r"-\s*\n\s*")
#: "informa- tion" -- the same hyphen with the newline already collapsed.
_SOFT_JOIN = re.compile(r"(?<=[A-Za-z])-\s+(?=[a-z])")

#: A space the extractor inserted before punctuation ("word , word").
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?)\]}\'])")
_WS = re.compile(r"\s+")


def normalise_artifacts(s: str) -> str:
    """Repair extraction artefacts, one named class at a time. No NFKC."""
    s = _LIGATURE_RUN.sub(lambda m: LIGATURES[m.group(1)], s)
    for lig, repl in LIGATURES.items():
        s = s.replace(lig, repl)
    s = s.replace("\u00ad", "")                       # soft hyphen: no decomposition
    s = _ZERO_WIDTH.sub("", s)
    s = s.replace("\u00a0", " ").replace("\u202f", " ")
    s = _DASHES.sub("-", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2022", " ")
    return s


def _tidy(s: str) -> str:
    s = _SPACE_BEFORE_PUNCT.sub(r"\1", s)
    return _WS.sub(" ", s).strip().casefold()


def readings(s: str) -> Dict[str, str]:
    """Both readings of one string, keyed by name. Never a single destructive pass."""
    pre = normalise_artifacts(s or "")
    return {
        "verbatim": _tidy(pre),
        "dehyphenated": _tidy(_SOFT_JOIN.sub("", _HARD_WRAP.sub("", pre))),
    }


# --- the lenient reading, kept only to NAME an undeclared apparatus ---------

ELISION = re.compile(r"\[[^\]]{0,60}\]")
CITATION = re.compile(r"\([^()]{0,120}(?:et al\.|19\d\d|20\d\d)[^()]{0,120}\)")
CALLOUT = re.compile(r"(?<=[A-Za-z])[0-9]{1,2}(?:,[0-9]{1,2})*(?=[\s.,;])")


def lenient(reading: str) -> str:
    """What the old checker compared. Used ONLY to name an UNDECLARED apparatus."""
    s = CALLOUT.sub("", CITATION.sub("", ELISION.sub("", reading)))
    s = re.sub(r"\s*,\s*", " ", s)
    return _WS.sub(" ", s).strip()


def declared_tokens(block: Dict[str, Any]) -> List[str]:
    apparatus = block.get("apparatus")
    if not isinstance(apparatus, dict):
        return []
    removed = apparatus.get("removed")
    if not isinstance(removed, list):
        return []
    return [str(t) for t in removed if str(t).strip()]


# --- verdicts ---------------------------------------------------------------

def match_reading(quote: str, hay: str) -> Optional[str]:
    """The name of the first reading under which the quote is contiguous."""
    q, h = readings(quote), readings(hay)
    for name in READINGS:
        if q[name] and q[name] in h[name]:
            return name
    return None


def reinsert_proof(quote: str, hay: str,
                   tokens: Sequence[str]) -> Tuple[bool, str, str]:
    """(proven, reading, why) — delete every declared token once, then require STRICT.

    The failure reason reported is the one from the strictest reading, which is
    the most conservative thing to say about a quote that matched nowhere.
    """
    q, h = readings(quote), readings(hay)
    strictest_why = ""
    for name in READINGS:
        stripped = h[name]
        why = ""
        for token in tokens:
            needle = readings(token)[name]
            if not needle:
                why = "declared token %r normalises to nothing" % token
                break
            if needle not in stripped:
                why = "declared token %r is not in the source text" % token
                break
            if needle in q[name]:
                why = "declared token %r also appears in the quote" % token
                break
            stripped = stripped.replace(needle, "", 1)
        if why:
            if name == READINGS[0]:
                strictest_why = why
            continue
        if q[name] and q[name] in stripped:
            return True, name, ""
        if name == READINGS[0]:
            strictest_why = "quote is not contiguous once the declared tokens are removed"
    return False, "", strictest_why or "quote is not contiguous once the tokens are removed"


def judge(block: Dict[str, Any], hay: Optional[str]) -> Tuple[str, str, str]:
    """(verdict, reading, why) for one corpus block.

    A present declaration is ALWAYS validated, even when the quote already
    matches verbatim. Returning STRICT first was measured to skip the
    declaration entirely (2026-11-16: a block declaring tokens the source does
    not contain scored STRICT, exit 0), so an unprovable claim passed as a
    proven one. The declaration is a claim about the document; it is checked
    whether or not the quote needed it.
    """
    quote = block.get("quote") or ""
    if hay is None:
        return "NO-TEXT", "", "source text not on disk; the quote is UNPROVEN"
    tokens = declared_tokens(block)
    if tokens:
        ok, reading, why = reinsert_proof(quote, hay, tokens)
        if not ok:
            return "ABSENT", "", why
        note = ""
        if match_reading(quote, hay) is not None:
            note = ("declaration proven, but the quote is contiguous without it "
                    "(the removed material sits outside the quoted span)")
        return "APPARATUS", reading, note
    name = match_reading(quote, hay)
    if name:
        return "STRICT", name, ""
    q, h = readings(quote), readings(hay)
    for reading in READINGS:
        if lenient(q[reading]) and lenient(q[reading]) in lenient(h[reading]):
            return "UNDECLARED", reading, (
                "the lenient reading would have matched -- declare apparatus.kind "
                "and apparatus.removed, or fix the quote")
    return "ABSENT", "", "no reading matches"


# --- sources ----------------------------------------------------------------

def sha256_text(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_source(sid: str, dirs: Sequence[Path]) -> Optional[Path]:
    """First ``<sid>.txt`` found. ``.layout.txt`` is never a candidate."""
    for directory in dirs:
        candidate = Path(directory) / ("%s.txt" % sid)
        if candidate.is_file():
            return candidate
    return None


def _display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except (ValueError, OSError):
        return str(path).replace("\\", "/")


# --- driver -----------------------------------------------------------------

def run(corpus: Path, source_dirs: Sequence[Path]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    doc = json.loads(corpus.read_text(encoding="utf-8", errors="replace"))
    rows: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {}
    for need in doc.get("needs") or []:
        for edge in need.get("edges") or []:
            for label in ("ground", "corroboration"):
                block = edge.get(label)
                if not block:
                    continue
                sid = block.get("source_id") or "?"
                path = resolve_source(sid, source_dirs)
                hay = None
                if path is not None:
                    hay = path.read_text(encoding="utf-8", errors="replace")
                verdict, reading, why = judge(block, hay)
                counts[verdict] = counts.get(verdict, 0) + 1
                rows.append({
                    "edge_id": edge.get("edge_id"),
                    "block": label,
                    "source_id": sid,
                    "source_path": _display(path) if path else "",
                    "source_sha256": sha256_text(path) if path else "",
                    "verdict": verdict,
                    "reading": reading,
                    "note": why,
                })
    return rows, counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Prove every corpus quote against the producer's own text.")
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS),
                        help="corpus JSON to check (default: the tracked corpus)")
    parser.add_argument("--sources-dir", action="append", default=None,
                        metavar="DIR",
                        help="directory holding <source_id>.txt; repeatable, replaces "
                             "the defaults (first match wins)")
    parser.add_argument("--manifest", default=None, metavar="PATH",
                        help="write the per-block evidence (verdicts, reader, sha256)")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)

    corpus = Path(args.corpus)
    if not corpus.is_file():
        print("BLIND: corpus not found: %s" % corpus, file=sys.stderr)
        return EXIT_BLIND
    dirs = ([Path(d) for d in args.sources_dir] if args.sources_dir
            else list(DEFAULT_SOURCE_DIRS))

    try:
        rows, counts = run(corpus, dirs)
    except (OSError, ValueError) as exc:
        print("BLIND: corpus could not be read: %s" % exc, file=sys.stderr)
        return EXIT_BLIND

    total = len(rows)
    no_text = [r for r in rows if r["verdict"] == "NO-TEXT"]
    failing = [r for r in rows if r["verdict"] not in ("STRICT", "APPARATUS")]
    proven = total - len(failing)

    manifest = {
        "tool": "check_corpus_quotes",
        "corpus": str(corpus).replace("\\", "/"),
        "corpus_sha256": sha256_text(corpus),
        "source_dirs": [str(d).replace("\\", "/") for d in dirs],
        "readings": list(READINGS),
        "counts": dict(sorted(counts.items())),
        "denominator": {"total": total, "proven": proven, "unproven": len(failing),
                        "no_text": len(no_text)},
        "rows": rows,
    }
    if args.manifest:
        target = Path(args.manifest)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        for row in rows:
            if row["verdict"] == "STRICT":
                continue
            detail = row["reading"] or "-"
            note = ("  [%s]" % row["note"]) if row["note"] else ""
            print("  %-10s %-12s %-6s %-22s reading=%-12s%s" % (
                row["verdict"], row["edge_id"] or "?", row["block"],
                row["source_id"], detail, note))
        summary = ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items()))
        print("\n%d quotes: %s" % (total, summary or "none"))
        print("proven %d/%d (%d unproven, %d NO-TEXT)" % (
            proven, total, len(failing), len(no_text)))
        if no_text:
            print("  NO-TEXT (unproven, never a pass): %s" % ", ".join(
                sorted({r["source_id"] for r in no_text})))

    if total == 0:
        print("BLIND: the corpus yielded no quotes", file=sys.stderr)
        return EXIT_BLIND
    if len(no_text) == total:
        print("BLIND: no source text resolved from %s" % ", ".join(
            str(d) for d in dirs), file=sys.stderr)
        return EXIT_BLIND
    return EXIT_OK if not failing else EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
