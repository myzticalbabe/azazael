#!/usr/bin/env python3
# coding: utf-8
"""Check a canon corpus written in biblical form, and generate its genealogies.

WHY A CHECKER AT ALL
--------------------
A Bible-shaped document earns its authority from citation: a verse exists so
another verse can lean on it. That only works if a reference resolves, and it
only stays honest if the thing it cites has not been quietly changed. So the
corpus is data -- `docs/bible/bible.json` -- and this tool is its apparatus:
numbering that must be contiguous, citations that must land, statutes that must
name both the rule they come from and the check that proves they are kept, and a
hard refusal of any figure whose command is not written beside it.

WHAT IT REFUSES, AND WHY EACH REFUSAL IS A WAY THE TEXT WOULD LIE
----------------------------------------------------------------
* **A dangling citation.** "As it is written in Genesis 4:9" is a claim; if the
  verse is not there, the claim is unfalsifiable and the reader cannot tell a
  quotation from an invention.
* **A number with no command.** Any digit in a verse demands a `source` naming a
  path in this repository. This is the rule `docs/index.md` already states for
  prose -- every number names the command that produced it -- made mechanical,
  because a scripture quoting an unmeasured figure is the most quotable possible
  form of a false one.
* **A statute with no check.** A law with nothing executing it is a proverb. It
  belongs in the wisdom book, and the validator says so instead of letting a
  commandment masquerade as a gate.
* **A statute whose rule is not in canon.** The corpus narrates canon; it does
  not legislate. A statute must cite a RULE that exists in `MANDATES.md`, so the
  Bible cannot become a second source of truth.
* **A name.** Refused substrings and contact shapes are rejected outright, on
  the same line `Project_Nurse_Ratchet/DISCLOSURE_POLICY.md` draws: methodology
  ships, people do not.
* **Growth without a cap.** A canon of sixty-six books is a parody with a
  bibliography. The corpus declares its own limits and the validator enforces
  them, so the next author must retire a book to add one.

GENEALOGY IS GENERATED, NOT COMPOSED
-----------------------------------
" And A begat B" is an import edge. `--genealogy` reads `src/` with `ast`, counts
cross-package imports, and writes `docs/bible/GENEALOGY.md` with the command that
produced it. A genealogy a reader can re-run is the one part of a scripture that
cannot be embellished.

Usage:
  python tools/bible_check.py                 # summary
  python tools/bible_check.py --check         # exit 1 on any defect (the gate)
  python tools/bible_check.py --json
  python tools/bible_check.py --genealogy     # print the generations
  python tools/bible_check.py --genealogy --write   # regenerate GENEALOGY.md
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "docs" / "bible" / "bible.json"
GENEALOGY = REPO / "docs" / "bible" / "GENEALOGY.md"
MANDATES = REPO / "MANDATES.md"
SRC = REPO / "src"

SCHEMA = "azazael/bible@1"
STATUSES = ("seed", "drafting", "complete")

#: A genre per book, because the Bible is an anthology and a single register for
#: twelve books is pastiche. Each name here is a job, not a mood.
GENRES = (
    "etiology", "law", "history", "chronicle", "wisdom", "lament", "prophecy",
    "gospel", "epistle", "apocalypse", "genealogy",
)

#: Declared ceilings. `limits` in the corpus may tighten these and may never
#: exceed them: a cap the author can raise is not a cap.
HARD_MAX_BOOKS = 24
HARD_MAX_VERSES = 200

#: The disclosure line, in the same terms the package's manifest refuses.
REFUSED_SUBSTRINGS = (
    "bcc_audit", "REINVESTIGATION", "FETCH_LOG", "edge_proof_ledger",
    "identity_tiebreak", "new_sources_log",
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<![\d-])\d{3}[-.\s]\d{3}[-.\s]\d{4}(?![\d-])")
DIGIT_RE = re.compile(r"[0-9]")
#: Any repository-relative path, not just the six directories this tree happens
#: to keep tools in: `Project_Nurse_Ratchet/README.md` is the provenance of a
#: defect recorded in that package, and a checker that could not name it would
#: push the author to cite the wrong file instead. The lookbehind refuses to
#: begin inside a URL, so `https://host/x.md` cannot masquerade as a local path.
PATH_RE = re.compile(r"(?<![\w/:.-])(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
                     r"\.(?:py|json|md|js|ps1|sh|yml|yaml)")
REF_RE = re.compile(r"^([a-z][a-z0-9_]*)\s+([0-9]+):([0-9]+)$")
RULE_RE = re.compile(r"\bRULE\s+[0-9][0-9A-Za-z-]*")

#: The annotated-edition layer. An Oxford-style Bible is not a bare text: it
#: carries a book introduction, pericope headings, footnotes sorted by kind, and a
#: glossary. The kinds matter because a textual note and a historical note fail
#: differently -- one is a reading, the other is a claim about the world -- and a
#: reader is entitled to know which they are reading.
ANNOTATION_KINDS = ("textual", "historical", "translation", "editorial", "cross")

TOP_KEYS = {"schema", "title", "status", "updated", "limits", "note", "books",
            "glossary", "edition"}
BOOK_KEYS = {"id", "name", "subtitle", "genre", "introduction", "chapters"}
CHAPTER_KEYS = {"number", "sections", "verses"}
VERSE_KEYS = {"number", "text", "cites", "source", "statute", "variants",
              "annotations", "note"}
STATUTE_KEYS = {"rule", "check", "why"}
VARIANT_KEYS = {"reading", "text", "source"}
ANNOTATION_KEYS = {"kind", "note", "source"}
SECTION_KEYS = {"before_verse", "heading"}
INTRODUCTION_KEYS = {"paragraphs", "sources"}
GLOSSARY_KEYS = {"term", "gloss", "see", "source"}
EDITION_KEYS = {"name", "basis"}
LIMIT_KEYS = {"max_books", "max_verses_per_chapter"}


class CorpusError(Exception):
    """Malformed corpus. Never downgraded to a warning."""


def load(path: Path = CORPUS) -> Dict:
    if not path.exists():
        raise CorpusError("%s is absent; there is no corpus to check" % path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CorpusError("%s is not valid JSON: %s" % (path.name, exc)) from exc


def _paths_in(text: str) -> List[str]:
    return PATH_RE.findall(text or "")


def _provenance_problems(source, where: str, repo: Path) -> List[str]:
    """A figure must name a command that exists. Verbs alone do not count.

    `python some_tool.py` with no path is a memory of a command; a path that
    resolves is a command someone can run. Paths under `logs/` are exempt from
    existence because reports are rotated and the corpus may cite one that has
    since been replaced -- but the token must still be written down.
    """
    if not isinstance(source, str) or not source.strip():
        return ["%s: a number needs `source`: the command or path that produced it"
                % where]
    tokens = _paths_in(source)
    if not tokens:
        return ["%s: source names no repository path (%r); a figure with no "
                "re-runnable command is a claim, not evidence" % (where, source)]
    problems = []
    for token in tokens:
        head = token.split("/", 1)[0]
        if head == "logs":
            continue
        if not (Path(repo) / token.split("#", 1)[0]).exists():
            problems.append("%s: source path does not exist here: %s" % (where, token))
    return problems


def _text_problems(text, where: str) -> List[str]:
    problems: List[str] = []
    if not isinstance(text, str) or not text.strip():
        return ["%s: text is empty" % where]
    if not re.search(r"[A-Za-z]", text):
        problems.append("%s: text carries no words" % where)
    lowered = text.lower()
    for token in REFUSED_SUBSTRINGS:
        if token.lower() in lowered:
            problems.append("%s: refused substring %r -- methodology ships, people "
                            "do not" % (where, token))
    if EMAIL_RE.search(text):
        problems.append("%s: an email address is refused" % where)
    if PHONE_RE.search(text):
        problems.append("%s: a phone number is refused" % where)
    return problems


def _prose_block_problems(paragraphs, sources, where: str, repo: Path) -> List[str]:
    """An introduction or a gloss is prose, but it still may not assert a figure
    for free: the moment it carries a digit, the block must name its sources."""
    problems: List[str] = []
    if not isinstance(paragraphs, list) or not paragraphs:
        return ["%s: paragraphs must be a non-empty list" % where]
    carries_digit = False
    for index, paragraph in enumerate(paragraphs):
        problems.extend(_text_problems(paragraph, "%s paragraph %d" % (where, index + 1)))
        if isinstance(paragraph, str) and DIGIT_RE.search(paragraph):
            carries_digit = True
    if sources is not None and not isinstance(sources, list):
        problems.append("%s: sources must be a list" % where)
        sources = []
    if carries_digit:
        if not sources:
            problems.append("%s: a paragraph carries a figure, so the block must name "
                            "`sources` -- or spell the number out" % where)
        for source in sources or []:
            problems.extend(_provenance_problems(source, where, repo))
    return problems


def _statute_problems(statute, where: str, repo: Path, canon: Optional[str]) -> List[str]:
    if not isinstance(statute, dict):
        return ["%s: statute must be an object with `rule` and `check`" % where]
    problems: List[str] = []
    unknown = set(statute) - STATUTE_KEYS
    if unknown:
        problems.append("%s: unknown statute key(s) %s" % (where, sorted(unknown)))
    rule = statute.get("rule")
    if not isinstance(rule, str) or not RULE_RE.search(rule):
        problems.append("%s: statute.rule must name a RULE (e.g. \"RULE 0B\")" % where)
    elif canon is None:
        problems.append("%s: MANDATES.md is unreadable -- the rule %r cannot be "
                        "verified against canon" % (where, rule))
    elif RULE_RE.search(rule).group(0) not in canon:
        problems.append("%s: %r is not in MANDATES.md; the corpus narrates canon, "
                        "it does not legislate" % (where, rule))
    check = statute.get("check")
    if not isinstance(check, str) or not check.strip():
        problems.append("%s: statute.check is empty -- a law with nothing executing "
                        "it is a proverb, not a statute" % where)
    else:
        tokens = _paths_in(check)
        if not tokens:
            problems.append("%s: statute.check names no repository path (%r)"
                            % (where, check))
        for token in tokens:
            if not (Path(repo) / token.split("#", 1)[0]).exists():
                problems.append("%s: statute.check does not exist here: %s"
                                % (where, token))
    return problems


def validate(data: Dict, repo: Path = REPO) -> None:
    """Collect every problem, then raise once. A gate that stops at the first
    finding makes the author re-run it one typo at a time."""
    problems: List[str] = []
    canon = MANDATES.read_text(encoding="utf-8", errors="replace") \
        if MANDATES.exists() else None

    unknown = set(data) - TOP_KEYS
    if unknown:
        problems.append("unknown top-level key(s) %s" % sorted(unknown))
    if data.get("schema") != SCHEMA:
        problems.append("schema must be %r, found %r" % (SCHEMA, data.get("schema")))
    if not isinstance(data.get("title"), str) or not data.get("title", "").strip():
        problems.append("title is empty")
    if data.get("status") not in STATUSES:
        problems.append("status must be one of %s" % (STATUSES,))
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(data.get("updated", ""))):
        problems.append("updated must be YYYY-MM-DD")

    limits = data.get("limits", {})
    if not isinstance(limits, dict):
        problems.append("limits must be an object")
        limits = {}
    unknown = set(limits) - LIMIT_KEYS
    if unknown:
        problems.append("unknown limits key(s) %s" % sorted(unknown))
    max_books = limits.get("max_books", 12)
    max_verses = limits.get("max_verses_per_chapter", 60)
    for name, value, ceiling in (("max_books", max_books, HARD_MAX_BOOKS),
                                 ("max_verses_per_chapter", max_verses, HARD_MAX_VERSES)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            problems.append("limits.%s must be a positive integer" % name)
        elif value > ceiling:
            problems.append("limits.%s may not exceed %d; a cap the author can raise "
                            "is not a cap" % (name, ceiling))

    edition = data.get("edition")
    if edition is not None:
        if not isinstance(edition, dict):
            problems.append("edition must be an object")
        else:
            unknown = set(edition) - EDITION_KEYS
            if unknown:
                problems.append("unknown edition key(s) %s" % sorted(unknown))
            for key in sorted(EDITION_KEYS):
                if not isinstance(edition.get(key), str) or not edition.get(key, "").strip():
                    problems.append("edition.%s is empty" % key)

    glossary = data.get("glossary", [])
    if not isinstance(glossary, list):
        problems.append("glossary must be a list")
        glossary = []
    for index, entry in enumerate(glossary):
        where = "glossary[%d]" % index
        if not isinstance(entry, dict):
            problems.append("%s: must be an object" % where)
            continue
        unknown = set(entry) - GLOSSARY_KEYS
        if unknown:
            problems.append("%s: unknown key(s) %s" % (where, sorted(unknown)))
        for key in ("term", "gloss"):
            if not isinstance(entry.get(key), str) or not entry.get(key, "").strip():
                problems.append("%s: %s is empty" % (where, key))
        problems.extend(_text_problems(entry.get("gloss"), "%s gloss" % where))
        if isinstance(entry.get("gloss"), str) and DIGIT_RE.search(entry["gloss"]):
            problems.extend(_provenance_problems(entry.get("source"), where, repo))
        if "see" in entry and (not isinstance(entry["see"], str)
                                or not REF_RE.match(entry["see"])):
            problems.append("%s: see must read \"<book> <chapter>:<verse>\"" % where)

    books = data.get("books")
    if not isinstance(books, list) or not books:
        problems.append("books must be a non-empty list")
        books = []
    if isinstance(max_books, int) and len(books) > max_books:
        problems.append("%d books declared, limit is %d -- retire one to add one"
                        % (len(books), max_books))

    index: Dict[str, Dict[int, Dict[int, str]]] = {}
    verse_total = 0
    for position, book in enumerate(books):
        where = "books[%d]" % position
        if not isinstance(book, dict):
            problems.append("%s: must be an object" % where)
            continue
        unknown = set(book) - BOOK_KEYS
        if unknown:
            problems.append("%s: unknown key(s) %s" % (where, sorted(unknown)))
        identifier = book.get("id")
        if not isinstance(identifier, str) or not re.match(r"^[a-z][a-z0-9_]*$", identifier):
            problems.append("%s: id must be lower_snake_case" % where)
            continue
        where = "book %r" % identifier
        if identifier in index:
            problems.append("%s: duplicate book id" % where)
            continue
        for key in ("name", "subtitle"):
            if not isinstance(book.get(key), str) or not book.get(key, "").strip():
                problems.append("%s: %s is empty" % (where, key))
        if book.get("genre") not in GENRES:
            problems.append("%s: genre must be one of %s" % (where, GENRES))
        introduction = book.get("introduction")
        if introduction is not None:
            if not isinstance(introduction, dict):
                problems.append("%s: introduction must be an object" % where)
            else:
                unknown = set(introduction) - INTRODUCTION_KEYS
                if unknown:
                    problems.append("%s: unknown introduction key(s) %s"
                                    % (where, sorted(unknown)))
                problems.extend(_prose_block_problems(introduction.get("paragraphs"),
                                                     introduction.get("sources", []),
                                                     "%s introduction" % where, repo))
        chapters = book.get("chapters")
        if not isinstance(chapters, list) or not chapters:
            problems.append("%s: chapters must be a non-empty list" % where)
            continue
        index[identifier] = {}
        for chapter_position, chapter in enumerate(chapters):
            cwhere = "%s chapter %d" % (where, chapter_position + 1)
            if not isinstance(chapter, dict):
                problems.append("%s: must be an object" % cwhere)
                continue
            unknown = set(chapter) - CHAPTER_KEYS
            if unknown:
                problems.append("%s: unknown key(s) %s" % (cwhere, sorted(unknown)))
            number = chapter.get("number")
            if number != chapter_position + 1:
                problems.append("%s: chapter numbering must be contiguous from 1; "
                                "found %r at position %d"
                                % (cwhere, number, chapter_position + 1))
                continue
            verses = chapter.get("verses")
            if not isinstance(verses, list) or not verses:
                problems.append("%s: verses must be a non-empty list" % cwhere)
                continue
            if isinstance(max_verses, int) and len(verses) > max_verses:
                problems.append("%s: %d verses, limit is %d"
                                % (cwhere, len(verses), max_verses))
            sections = chapter.get("sections", [])
            if not isinstance(sections, list):
                problems.append("%s: sections must be a list" % cwhere)
                sections = []
            previous = 0
            for section_position, section in enumerate(sections):
                swhere = "%s section %d" % (cwhere, section_position + 1)
                if not isinstance(section, dict):
                    problems.append("%s: must be an object" % swhere)
                    continue
                unknown = set(section) - SECTION_KEYS
                if unknown:
                    problems.append("%s: unknown key(s) %s" % (swhere, sorted(unknown)))
                start = section.get("before_verse")
                if not isinstance(start, int) or isinstance(start, bool) or \
                        not 1 <= start <= len(verses):
                    problems.append("%s: before_verse must name a verse in this chapter "
                                    "(1..%d)" % (swhere, len(verses)))
                elif start <= previous:
                    problems.append("%s: sections must ascend; %d follows %d"
                                    % (swhere, start, previous))
                else:
                    previous = start
                heading = section.get("heading")
                problems.extend(_text_problems(heading, "%s heading" % swhere))
                if isinstance(heading, str) and DIGIT_RE.search(heading):
                    problems.append("%s: a heading is a label, not a claim -- a figure "
                                    "belongs in a verse, where it must name its "
                                    "command" % swhere)
            index[identifier][number] = {}
            for verse_position, verse in enumerate(verses):
                vwhere = "%s chapter %d verse %d" % (where, number, verse_position + 1)
                if not isinstance(verse, dict):
                    problems.append("%s: must be an object" % vwhere)
                    continue
                unknown = set(verse) - VERSE_KEYS
                if unknown:
                    problems.append("%s: unknown key(s) %s" % (vwhere, sorted(unknown)))
                if verse.get("number") != verse_position + 1:
                    problems.append("%s: verse numbering must be contiguous from 1; "
                                    "found %r" % (vwhere, verse.get("number")))
                    continue
                text = verse.get("text")
                problems.extend(_text_problems(text, vwhere))
                index[identifier][number][verse_position + 1] = text if \
                    isinstance(text, str) else ""
                verse_total += 1
                if isinstance(text, str) and DIGIT_RE.search(text):
                    problems.extend(_provenance_problems(verse.get("source"),
                                                         vwhere, repo))
                citations = verse.get("cites", [])
                if not isinstance(citations, list):
                    problems.append("%s: cites must be a list" % vwhere)
                    citations = []
                for citation in citations:
                    if not isinstance(citation, str) or not REF_RE.match(citation):
                        problems.append("%s: citation %r must read \"<book> <chapter>:"
                                        "<verse>\"" % (vwhere, citation))
                if "statute" in verse:
                    problems.extend(_statute_problems(verse["statute"], vwhere, repo,
                                                      canon))
                variants = verse.get("variants", [])
                if not isinstance(variants, list):
                    problems.append("%s: variants must be a list" % vwhere)
                    variants = []
                for variant_position, variant in enumerate(variants):
                    xwhere = "%s variant %d" % (vwhere, variant_position + 1)
                    if not isinstance(variant, dict):
                        problems.append("%s: must be an object" % xwhere)
                        continue
                    unknown = set(variant) - VARIANT_KEYS
                    if unknown:
                        problems.append("%s: unknown key(s) %s" % (xwhere, sorted(unknown)))
                    if not isinstance(variant.get("reading"), str) or \
                            not variant.get("reading", "").strip():
                        problems.append("%s: reading is empty (name the manuscript "
                                        "or the source of the variant)" % xwhere)
                    problems.extend(_text_problems(variant.get("text"), xwhere))
                    if not isinstance(variant.get("source"), str) or \
                            not variant.get("source", "").strip():
                        problems.append("%s: a variant must say where its reading comes "
                                        "from; that is the whole point of an apparatus"
                                        % xwhere)
                annotations = verse.get("annotations", [])
                if not isinstance(annotations, list):
                    problems.append("%s: annotations must be a list" % vwhere)
                    annotations = []
                for note_position, annotation in enumerate(annotations):
                    nwhere = "%s annotation %d" % (vwhere, note_position + 1)
                    if not isinstance(annotation, dict):
                        problems.append("%s: must be an object" % nwhere)
                        continue
                    unknown = set(annotation) - ANNOTATION_KEYS
                    if unknown:
                        problems.append("%s: unknown key(s) %s"
                                        % (nwhere, sorted(unknown)))
                    if annotation.get("kind") not in ANNOTATION_KINDS:
                        problems.append("%s: kind must be one of %s -- a reader is "
                                        "entitled to know whether a note is a reading "
                                        "or a claim" % (nwhere, ANNOTATION_KINDS))
                    problems.extend(_text_problems(annotation.get("note"),
                                                  "%s note" % nwhere))
                    if isinstance(annotation.get("note"), str) and \
                            DIGIT_RE.search(annotation["note"]):
                        problems.extend(_provenance_problems(annotation.get("source"),
                                                             nwhere, repo))

    # Citations are resolved after the whole index exists, so a verse may cite
    # forward -- the canon is read as a whole, not streamed.
    for identifier, chapters in index.items():
        for number, verses in chapters.items():
            for verse_number, _text in verses.items():
                verse = _verse_at(books, identifier, number, verse_number)
                for citation in (verse.get("cites", []) if verse else []):
                    if not isinstance(citation, str) or not REF_RE.match(citation):
                        continue        # already reported
                    book_id, chapter_text, verse_text = REF_RE.match(citation).groups()
                    if book_id not in index:
                        problems.append("%s %d:%d cites unknown book %r"
                                        % (identifier, number, verse_number, book_id))
                    elif int(chapter_text) not in index[book_id] or \
                            int(verse_text) not in index[book_id][int(chapter_text)]:
                        problems.append("%s %d:%d cites %s, which does not exist"
                                        % (identifier, number, verse_number, citation))

    # A glossary entry that points at a verse is a citation like any other, and
    # the apparatus's own cross-references are the first thing to rot.
    for position, entry in enumerate(glossary):
        reference = entry.get("see") if isinstance(entry, dict) else None
        if not isinstance(reference, str) or not REF_RE.match(reference):
            continue
        book_id, chapter_text, verse_text = REF_RE.match(reference).groups()
        if book_id not in index or int(chapter_text) not in index[book_id] or \
                int(verse_text) not in index[book_id][int(chapter_text)]:
            problems.append("glossary[%d]: see %s, which does not exist"
                            % (position, reference))

    if problems:
        raise CorpusError("%s failed %d check(s):\n  - %s"
                          % (CORPUS.name, len(problems), "\n  - ".join(problems)))
    verses_flat = [verse for book in books for chapter in book["chapters"]
                   for verse in chapter["verses"]]
    diagnostics = {"books": len(books),
                   "chapters": sum(len(book.get("chapters", [])) for book in books),
                   "verses": verse_total,
                   "citations": sum(len(verse.get("cites", []) or [])
                                    for verse in verses_flat),
                   "statutes": sum(1 for verse in verses_flat if "statute" in verse),
                   "variants": sum(len(verse.get("variants", []) or [])
                                   for verse in verses_flat),
                   "annotations": sum(len(verse.get("annotations", []) or [])
                                      for verse in verses_flat),
                   "sections": sum(len(chapter.get("sections", []) or [])
                                   for book in books for chapter in book["chapters"]),
                   "glossary": len(glossary),
                   "introductions": sum(1 for book in books if "introduction" in book)}
    data.setdefault("_diagnostics", diagnostics)


def _verse_at(books: Sequence[Dict], book_id: str, chapter: int, verse: int) -> Optional[Dict]:
    for book in books:
        if book.get("id") != book_id:
            continue
        for chapter_entry in book.get("chapters", []):
            if chapter_entry.get("number") != chapter:
                continue
            for verse_entry in chapter_entry.get("verses", []):
                if verse_entry.get("number") == verse:
                    return verse_entry
    return None


# --------------------------------------------------------------------------- #
# Generations: the import graph, which cannot be embellished                   #
# --------------------------------------------------------------------------- #

def import_graph(root: Path = SRC) -> Tuple[Dict[str, Dict[str, int]], List[str]]:
    """Top-level packages under `root`, and how often one imports another."""
    if not root.is_dir():
        return {}, []
    packages = sorted({path.parts[0] for path in
                       (p.relative_to(root) for p in root.rglob("*.py")
                        if "__pycache__" not in p.parts)
                       if len(path.parts) > 1})
    known = set(packages)
    edges: Dict[str, Dict[str, int]] = {package: {} for package in packages}
    unreadable: List[str] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root)
        if len(relative.parts) < 2:
            continue
        source = relative.parts[0]
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            unreadable.append(str(relative).replace("\\", "/"))
            continue
        targets: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level:              # relative: stays inside the package
                    continue
                if node.module:
                    targets.append(node.module)
        for target in targets:
            head = target.split(".", 1)[0]
            if head in known and head != source:
                edges[source][head] = edges[source].get(head, 0) + 1
    return edges, unreadable


def render_genealogy(edges: Dict[str, Dict[str, int]], unreadable: Sequence[str]) -> str:
    total_edges = sum(sum(level.values()) for level in edges.values())
    houses = len(edges)
    lines = [
        "# The generations of the tree",
        "",
        "Generated, never composed: each \"begat\" below is an import edge found by",
        "reading `src/` with `ast`. Re-run it and the numbers must be the same.",
        "",
        "```bash",
        "python tools/bible_check.py --genealogy --write",
        "```",
        "",
        "%d houses, %d edges between them." % (houses, total_edges),
        "",
    ]
    for house in sorted(edges, key=lambda name: (-len(edges[name]), name)):
        children = edges[house]
        if not children:
            lines.append("And **%s** begat no other house." % house)
            continue
        ordered = sorted(children, key=lambda name: (-children[name], name))
        named = ["**%s**" % child for child in ordered[:3]]
        if len(ordered) > 3:
            rest = len(ordered) - 3
            lines.append("And **%s** begat %s, and of the rest there were %d."
                         % (house, ", ".join(named), rest))
        elif len(ordered) == 1:
            lines.append("And **%s** begat %s." % (house, named[0]))
        else:
            lines.append("And **%s** begat %s and %s."
                         % (house, ", ".join(named[:-1]), named[-1]))
    lines.extend(["", "| house | begat | edges out |", "|---|---|---|"])
    for house in sorted(edges):
        children = ", ".join(sorted(edges[house], key=lambda name: (-edges[house][name],
                                                                   name))) or "--"
        lines.append("| %s | %s | %d |"
                     % (house, children, sum(edges[house].values())))
    if unreadable:
        lines.extend(["", "Unreadable on this run (not counted): %s."
                      % ", ".join(unreadable)])
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="exit 1 on any defect (the gate)")
    group.add_argument("--genealogy", action="store_true",
                       help="derive the generations from the import graph")
    parser.add_argument("--write", action="store_true",
                        help="with --genealogy, write docs/bible/GENEALOGY.md")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--corpus", default=str(CORPUS))
    args = parser.parse_args(argv)

    if args.genealogy:
        edges, unreadable = import_graph()
        text = render_genealogy(edges, unreadable)
        if args.write:
            GENEALOGY.parent.mkdir(parents=True, exist_ok=True)
            GENEALOGY.write_text(text, encoding="utf-8", newline="\n")
            print("wrote %s (%d houses, %d edges)"
                  % (GENEALOGY.relative_to(REPO), len(edges),
                     sum(sum(level.values()) for level in edges.values())))
            return 0
        print(text)
        return 0

    try:
        data = load(Path(args.corpus))
        validate(data, REPO)
    except CorpusError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    summary = data.get("_diagnostics", {})
    if args.json:
        print(json.dumps({"title": data.get("title"), "status": data.get("status"),
                          "summary": summary}, indent=1))
        return 0
    print("%s -- %s, %d book(s), %d chapter(s), %d verse(s), %d citation(s), "
          "%d statute(s), %d variant(s), %d annotation(s), %d section(s), "
          "%d gloss(es), %d introduction(s)"
          % (data.get("title"), data.get("status"), summary.get("books", 0),
             summary.get("chapters", 0), summary.get("verses", 0),
             summary.get("citations", 0), summary.get("statutes", 0),
             summary.get("variants", 0), summary.get("annotations", 0),
             summary.get("sections", 0), summary.get("glossary", 0),
             summary.get("introductions", 0)))
    if args.check:
        print("clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
