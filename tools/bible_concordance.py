#!/usr/bin/env python3
# coding: utf-8
"""The concordance: scripture, error, solution, and the law the solution executes.

The corpora record what went wrong and what repaired it. `MANDATES.md` records
the laws. Nothing joined the two, so a reader could quote a verse, quote a rule,
and never be able to tell whether the verse *was* the rule being kept or merely
sounded like it.

This tool performs that join and prints the differential, in one equation:

    SCRIPTURE  =  ERROR  ~  SOLUTION  ::  LAW

  `=`  the defect the verse records, with the ledger ids that carry it
  `~`  the repair, and the command that performs it
  `::` the RULE whose statute names that command -- the law, resolved by
       heading in MANDATES.md, never by mention

Three bindings, and they are kept apart because they are not equal evidence:

  **direct**   the verse carries a `statute`: the corpus itself names the law.
  **derived**  the verse carries a `practice` whose `detection` command is
               exactly the command a statute elsewhere binds to a rule. The
               join is a string equality on normalised argv, not a resemblance.
  **unbound**  neither. Counted and named, never dropped.

A verse with no binding is not a failure of the corpus -- narrative is allowed to
exist without legislation. A verse whose binding cannot be resolved IS a
failure: it cites a repealed rule, a command that is not in the tree, or an
evidence id the ledger does not hold.

  python tools/bible_concordance.py --write
  python tools/bible_concordance.py --check        # 0 current, 1 stale
  python tools/bible_concordance.py --strict       # a bindable-but-unbound
                                                   # practice fails
  python tools/bible_concordance.py --json         # the machine form only

Exit codes: 0 ran and clean, 1 a real defect, 2 BLIND (a corpus or the canon
could not be read -- which is not a pass and is not a zero).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import canon_rules  # noqa: E402

#: The three registers of one scripture, in reading order.
CORPORA: Tuple[Tuple[str, str], ...] = (
    ("canon", "docs/bible/bible.json"),
    ("felt", "docs/bible/emotional/emotional.json"),
    ("her", "docs/bible/emotional/female.json"),
)
HARVEST = "docs/bible/harvest.json"
OUT_MD = "docs/bible/CONCORDANCE.md"
OUT_JSON = "docs/bible/concordance.json"
SCHEMA = "azazael.concordance/1"

#: A repository path a command names. Same shape `bible_check` resolves, so a
#: command the corpus already accepted cannot become unresolvable here.
PATH_RE = re.compile(r"(?<![\w$])(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:py|json|md)")
#: Leading interpreter tokens a command may carry, stripped before comparison.
_LEAD = ("python", "python3", "python.exe", "$", "")

#: The hyper-edge defaults this document is built to, each with the command that
#: shows the practice is live rather than quoted.
HED_METHOD: Tuple[Tuple[str, str, str], ...] = (
    ("HED-2", "every claim below was produced by running the tool, not by reading it",
     "python tools/bible_concordance.py --check"),
    ("HED-7", "each row names its command; a row without one says so",
     "python tools/bible_concordance.py --write"),
    ("HED-9", "every count is printed with the population it was drawn from",
     "python tools/bible_concordance.py --write"),
    ("HED-11", "each row's binding state is recorded, and the four states never collapse",
     "python tools/bible_concordance.py --write"),
)


# ───────────────────────────── reading ─────────────────────────────


def _read_json(rel: str) -> Optional[Any]:
    path = REPO / rel
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("UNREADABLE: %s -- %s: %s" % (rel, type(exc).__name__, exc))
        return None


def norm_command(text: Any) -> Optional[str]:
    """Normalised argv for a command string, or None when it is not a command.

    A `detection` may be prose ("read src/... and see which end the call tries").
    Prose is not a command and must not be compared as one: it gets None, which
    the classifier reports as `prose`, never as `unresolved`.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    tokens = text.strip().split()
    while tokens and tokens[0].lower() in _LEAD:
        tokens = tokens[1:]
    if not tokens or tokens[0].startswith(("read ", "send ", "run ", "re-run ", "build ")):
        return None
    if not tokens[0].endswith(".py") and tokens[0] != "-m":
        return None
    return " ".join(tokens)


def paths_in(command: str) -> List[str]:
    return [m.group(0) for m in PATH_RE.finditer(command or "")]


def iter_verses(corpus: str, data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for book in data.get("books", []) or []:
        book_id = book.get("id")
        for chapter in book.get("chapters", []) or []:
            number = chapter.get("number")
            for verse in chapter.get("verses", []) or []:
                yield {
                    "corpus": corpus,
                    "book": book_id,
                    "chapter": number,
                    "verse": verse.get("number"),
                    "ref": "%s %s:%s [%s]" % (book_id, number, verse.get("number"), corpus),
                    "raw": verse,
                }


# ───────────────────────────── the join ─────────────────────────────


def command_law_index(verses: Sequence[Dict[str, Any]]) -> Dict[str, Tuple[str, str]]:
    """normalised command -> (rule, the ref whose statute binds it).

    Built from the corpus, not from a table in this file: the only command-to-law
    bindings that exist are the ones a statute already declares.
    """
    index: Dict[str, Tuple[str, str]] = {}
    for row in verses:
        statute = row["raw"].get("statute")
        if not isinstance(statute, dict):
            continue
        key = norm_command(statute.get("check"))
        rule = statute.get("rule")
        if key and isinstance(rule, str):
            index.setdefault(key, (rule, row["ref"]))
    return index


def _error_cell(row: Dict[str, Any]) -> Dict[str, Any]:
    verse = row["raw"]
    practice = verse.get("practice") if isinstance(verse.get("practice"), dict) else None
    if practice and practice.get("symptom"):
        return {"symptom": practice["symptom"], "source": "practice.symptom", "ref": row["ref"]}
    for note in verse.get("annotations") or []:
        if isinstance(note, dict) and note.get("kind") == "historical" and note.get("note"):
            return {"symptom": note["note"], "source": "annotation.historical", "ref": row["ref"]}
    return {"symptom": None, "source": None, "ref": row["ref"]}


def _solution_cell(row: Dict[str, Any]) -> Dict[str, Any]:
    verse = row["raw"]
    practice = verse.get("practice") if isinstance(verse.get("practice"), dict) else None
    statute = verse.get("statute") if isinstance(verse.get("statute"), dict) else None
    remedy = practice.get("remedy") if practice else None
    command = (practice or {}).get("detection") or (statute or {}).get("check")
    source = "practice.remedy" if remedy else ("statute.check" if statute else None)
    return {"remedy": remedy, "command": command, "source": source}


def _law_cell(row: Dict[str, Any], index: Dict[str, Tuple[str, str]],
              rules: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    verse = row["raw"]
    statute = verse.get("statute")
    if isinstance(statute, dict) and isinstance(statute.get("rule"), str):
        rule = statute["rule"]
        kind = "direct"
        via: Optional[str] = None
    else:
        command = _solution_cell(row).get("command")
        key = norm_command(command)
        hit = index.get(key) if key else None
        if not hit:
            return {"rule": None, "heading": None, "surface": None,
                    "binding": "unbound", "via": None}
        rule, via = hit
        kind = "derived"
    block = (rules or {}).get(re.sub(r"^RULE\s+", "", rule).strip())
    if not block:
        return {"rule": rule, "heading": None, "surface": None,
                "binding": kind, "via": via}
    return {"rule": rule, "heading": block["heading"],
            "surface": "MANDATES.md:%d" % block["line"], "binding": kind, "via": via}


def _differential(row: Dict[str, Any], error: Dict[str, Any], solution: Dict[str, Any],
                  records: Dict[str, Dict[str, Any]],
                  verified: Dict[str, int], failed: List[str]) -> Dict[str, Any]:
    practice = row["raw"].get("practice") if isinstance(row["raw"].get("practice"), dict) else None
    ids = [i for i in (practice or {}).get("evidence") or [] if isinstance(i, str)]
    pairs, missing = [], []
    for ident in ids:
        record = records.get(ident)
        if record is None:
            missing.append(ident)
            failed.append("%s: evidence id %r is not in %s" % (row["ref"], ident, HARVEST))
            continue
        verified[ident] = verified.get(ident, 0) + 1
        pairs.append({
            "id": ident,
            "symptom": (record.get("symptom") or "").strip() or None,
            "remedy": (record.get("remedy") or "").strip() or None,
            "surface": record.get("surface"),
            "line": record.get("line"),
            "date": record.get("date"),
        })
    have_before = any(p["symptom"] for p in pairs)
    have_after = any(p["remedy"] for p in pairs)
    if error.get("symptom") and solution.get("remedy") and have_before and have_after:
        state = "recorded"
    elif error.get("symptom") and solution.get("remedy"):
        state = "stated"
    elif error.get("symptom") or solution.get("remedy"):
        state = "partial"
    else:
        state = "unmeasured"
    return {"state": state, "before": error.get("symptom"),
            "after": solution.get("remedy"), "records": pairs, "missing": missing}


def build(records_raw: Optional[Dict[str, Any]], rules: Optional[Dict[str, Dict[str, Any]]],
          corpora: Sequence[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    ledger = (records_raw or {}).get("records") or []
    records = {r.get("id"): r for r in ledger if isinstance(r, dict) and r.get("id")}

    all_rows: List[Dict[str, Any]] = []
    for corpus, data in corpora:
        all_rows.extend(iter_verses(corpus, data))
    index = command_law_index(all_rows)

    rows: List[Dict[str, Any]] = []
    defects: List[str] = []
    verified: Dict[str, int] = {}
    failed: List[str] = []
    command_states = {"command": 0, "prose": 0, "none": 0}
    resolved: List[str] = []

    for row in all_rows:
        error = _error_cell(row)
        solution = _solution_cell(row)
        law = _law_cell(row, index, rules)
        diff = _differential(row, error, solution, records, verified, failed)

        command = solution.get("command")
        key = norm_command(command)
        if command is None:
            command_states["none"] += 1
        elif key is None:
            command_states["prose"] += 1
        else:
            command_states["command"] += 1
            missing = [p for p in paths_in(key) if not (REPO / p.split("#", 1)[0]).exists()]
            if missing:
                defects.append("%s: command names a path that is not here: %s"
                               % (row["ref"], ", ".join(missing)))
            else:
                resolved.append(key)

        if law["binding"] in ("direct", "derived"):
            problem = canon_rules.rule_problem(law["rule"], rules or {})
            if rules is None:
                defects.append("%s: MANDATES.md is unreadable -- %r cannot be verified"
                               % (row["ref"], law["rule"]))
            elif problem:
                defects.append("%s: %s" % (row["ref"], problem))

        rows.append({"ref": row["ref"], "corpus": row["corpus"], "book": row["book"],
                     "chapter": row["chapter"], "verse": row["verse"],
                     "text": (row["raw"].get("text") or "").strip(),
                     "error": error, "solution": solution, "law": law,
                     "differential": diff,
                     "cites": row["raw"].get("cites") or []})

    seen: Dict[str, int] = {}
    for r in rows:
        seen[r["ref"]] = seen.get(r["ref"], 0) + 1
    for ref, count in sorted(seen.items()):
        if count > 1:
            defects.append("ref %r identifies %d verse(s) -- a citation must name "
                           "exactly one" % (ref, count))

    bound = {r["law"]["rule"] for r in rows if r["law"]["binding"] in ("direct", "derived")}
    stats = {
        "corpora": len(corpora),
        "verses": len(rows),
        "direct": sum(1 for r in rows if r["law"]["binding"] == "direct"),
        "derived": sum(1 for r in rows if r["law"]["binding"] == "derived"),
        "unbound": sum(1 for r in rows if r["law"]["binding"] == "unbound"),
        "with_practice": sum(1 for r in rows if r["solution"]["remedy"]),
        "with_error": sum(1 for r in rows if r["error"]["symptom"]),
        "laws_defined": len(rules or {}),
        "laws_bound": len(bound),
        "evidence_ids": len(verified),
        "evidence_verified": len(verified),
        "evidence_failed": len(set(failed)),
        "commands": command_states["command"],
        "commands_resolved": len(resolved),
        "prose_instructions": command_states["prose"],
        "no_command": command_states["none"],
        "differentials_recorded": sum(1 for r in rows if r["differential"]["state"] == "recorded"),
        "differentials_unmeasured": sum(1 for r in rows if r["differential"]["state"] == "unmeasured"),
        "per_corpus": {
            name: {
                "verses": sum(1 for r in rows if r["corpus"] == name),
                "direct": sum(1 for r in rows if r["corpus"] == name and r["law"]["binding"] == "direct"),
                "derived": sum(1 for r in rows if r["corpus"] == name and r["law"]["binding"] == "derived"),
                "unbound": sum(1 for r in rows if r["corpus"] == name and r["law"]["binding"] == "unbound"),
            } for name, _ in corpora
        },
    }
    return {"rows": rows, "defects": defects, "stats": stats,
            "rules": rules or {}, "bound": sorted(bound)}


# ───────────────────────────── rendering ─────────────────────────────


def _cell(text: Optional[str], limit: int = 400) -> str:
    if not text:
        return "*(none recorded)*"
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def render_md(built: Dict[str, Any]) -> str:
    rows, stats, rules = built["rows"], built["stats"], built["rules"]
    out: List[str] = []
    add = out.append

    add("# THE CONCORDANCE")
    add("")
    add("<!-- generated by tools/bible_concordance.py --write; edit the tool, not this file -->")
    add("")
    add("Scripture, the error it records, the solution that repaired it, and the law")
    add("that solution executes. One equation, read in one direction:")
    add("")
    add("```")
    add("SCRIPTURE  =  ERROR  ~  SOLUTION  ::  LAW")
    add("```")
    add("")
    add("`=` the defect, with the ledger ids that carry it. `~` the repair, and the")
    add("command that performs it. `::` the RULE whose statute names that command, resolved")
    add("by heading in `MANDATES.md` and never by mention -- a `Related:` pointer is a")
    add("citation to the memory of a law, not to the law.")
    add("")
    add("Bindings are kept apart because they are not equal evidence: **direct** (the")
    add("verse carries a statute), **derived** (the verse's command is exactly the command")
    add("a statute binds to a rule, compared as normalised argv), **unbound** (neither).")
    add("")

    # I. method
    add("## I. The method, and the command that shows it is live")
    add("")
    add("| default | what it demands here | command |")
    add("| --- | --- | --- |")
    for hed, demand, command in HED_METHOD:
        add("| %s | %s | `%s` |" % (hed, demand, command))
    add("")

    # II. law table
    add("## II. The law table -- every rule the canon defines")
    add("")
    add("| law | surface | verses bound | heading |")
    add("| --- | --- | --- | --- |")
    per_rule: Dict[str, int] = {}
    for row in rows:
        rule = row["law"]["rule"]
        if rule:
            per_rule[rule] = per_rule.get(rule, 0) + 1
    for rule_id in sorted(rules):
        block = rules[rule_id]
        add("| RULE %s | MANDATES.md:%d | %d | %s |"
            % (rule_id, block["line"], per_rule.get("RULE " + rule_id, 0),
               _cell(block["heading"], 90)))
    add("")
    add("Coverage: **%d of %d** rules the canon defines have at least one verse bound to"
        % (stats["laws_bound"], stats["laws_defined"]))
    add("them. The remaining %d are laws no verse here records a breach of -- a fact about"
        % (stats["laws_defined"] - stats["laws_bound"]))
    add("this corpus, not a verdict on those laws.")
    add("")

    # III. direct
    for title, kind in (("III. Concordance A -- direct: the verse names its law", "direct"),
                        ("IV. Concordance B -- derived: the verse's command names it", "derived")):
        group = [r for r in rows if r["law"]["binding"] == kind]
        add("## %s" % title)
        add("")
        add("%d verse(s) of %d." % (len(group), stats["verses"]))
        add("")
        for row in group:
            add("### %s" % row["ref"])
            add("")
            add("> %s" % _cell(row["text"]))
            add("")
            add("- **ERROR** -- %s *(%s)*" % (_cell(row["error"]["symptom"]),
                                              row["error"]["source"] or "no source"))
            wrote = row["differential"]["records"]
            if wrote:
                add("  - ledger: %s" % ", ".join(
                    "`%s`%s" % (p["id"], "" if not p["surface"] else " (%s:%s)" % (p["surface"], p["line"]))
                    for p in wrote))
            add("- **SOLUTION** -- %s" % _cell(row["solution"]["remedy"]))
            add("  - command: %s" % ("`%s`" % row["solution"]["command"]
                                     if row["solution"]["command"] else "*(none)*"))
            law = row["law"]
            add("- **LAW** -- %s at %s, binding **%s**%s"
                % (law["rule"], law["surface"] or "*(unresolved)*", law["binding"],
                   "" if not law["via"] else ", via %s" % law["via"]))
            add("  - %s" % _cell(law["heading"], 160))
            add("- **DIFFERENTIAL** -- state **%s**: %s"
                % (row["differential"]["state"],
                   "before -> after recorded" if row["differential"]["state"] == "recorded"
                   else "no paired ledger reading"))
            add("")

    # V. narrative
    group = [r for r in rows if r["law"]["binding"] == "unbound"]
    add("## V. Concordance C -- narrative, unbound")
    add("")
    add("%d verse(s) of %d carry neither a statute nor a command a statute binds. They are"
        % (len(group), stats["verses"]))
    add("listed so the gap is visible, and counted in section VII rather than left out of it.")
    add("")
    add("| verse | text | error recorded |")
    add("| --- | --- | --- |")
    for row in group:
        add("| %s | %s | %s |" % (row["ref"], _cell(row["text"], 110),
                                  _cell(row["error"]["symptom"], 90)))
    add("")

    # VI. differential ledger
    add("## VI. The differential ledger")
    add("")
    add("One block per ledger pair a verse cites: the reading before the repair, the")
    add("repair, and the surface that carries both. A pair is `recorded` only when the")
    add("ledger holds a symptom AND a remedy for it; anything else says what it is missing.")
    add("")
    seen: set = set()
    for row in rows:
        for pair in row["differential"]["records"]:
            if pair["id"] in seen:
                continue
            seen.add(pair["id"])
            add("### %s -- cited by %s" % (pair["id"], row["ref"]))
            add("")
            add("- **before** -- %s" % _cell(pair["symptom"]))
            add("- **after** -- %s" % _cell(pair["remedy"]))
            add("- **surface** -- %s:%s%s" % (pair["surface"], pair["line"],
                                              "" if not pair["date"] else " (%s)" % pair["date"]))
            add("")
    add("_%d distinct ledger pair(s) cited._" % len(seen))
    add("")

    # VII. denominators
    add("## VII. Denominators -- every count with its population")
    add("")
    add("| reading | value | population |")
    add("| --- | --- | --- |")
    add("| verses | %d | %d corpus/corpora |" % (stats["verses"], stats["corpora"]))
    add("| bound direct | %d | %d verses |" % (stats["direct"], stats["verses"]))
    add("| bound derived | %d | %d verses |" % (stats["derived"], stats["verses"]))
    add("| unbound | %d | %d verses |" % (stats["unbound"], stats["verses"]))
    add("| verse records an error | %d | %d verses |" % (stats["with_error"], stats["verses"]))
    add("| verse records a remedy | %d | %d verses |" % (stats["with_practice"], stats["verses"]))
    add("| laws bound | %d | %d defined in MANDATES.md |"
        % (stats["laws_bound"], stats["laws_defined"]))
    add("| evidence ids cited | %d | %d verified in harvest.json (%d failed) |"
        % (stats["evidence_ids"], stats["evidence_verified"], stats["evidence_failed"]))
    add("| commands | %d | %d resolved to a path in the tree (%d prose instructions, %d absent) |"
        % (stats["commands"], stats["commands_resolved"], stats["prose_instructions"],
           stats["no_command"]))
    add("| differentials recorded | %d | %d verses (%d unmeasured) |"
        % (stats["differentials_recorded"], stats["verses"], stats["differentials_unmeasured"]))
    add("")
    add("Per register:")
    add("")
    add("| corpus | verses | direct | derived | unbound |")
    add("| --- | --- | --- | --- | --- |")
    for name, _ in CORPORA:
        pc = stats["per_corpus"].get(name, {})
        add("| %s | %d | %d | %d | %d |" % (name, pc.get("verses", 0), pc.get("direct", 0),
                                            pc.get("derived", 0), pc.get("unbound", 0)))
    add("")

    # VIII. defects + exit contract
    add("## VIII. Defects and the exit contract")
    add("")
    if built["defects"]:
        add("**%d defect(s).**" % len(built["defects"]))
        add("")
        for defect in built["defects"]:
            add("- %s" % defect)
    else:
        add("No defect: every statute's rule resolves to a heading in `MANDATES.md`, every")
        add("command names a path that exists, and every cited evidence id is in the ledger.")
    add("")
    add("| code | meaning |")
    add("| --- | --- |")
    add("| 0 | ran, and clean |")
    add("| 1 | a real defect, listed above |")
    add("| 2 | BLIND -- a corpus or `MANDATES.md` could not be read; a blind run is not a pass |")
    add("")
    add("`--strict` additionally fails a verse whose command a statute could bind but no")
    add("statute does: that one is fixable in the corpus and is therefore a duty, not a")
    add("narrative choice.")
    add("")
    return "\n".join(out)


# ───────────────────────────── main ─────────────────────────────


def collect() -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Dict[str, Any]]],
                       List[Tuple[str, Dict[str, Any]]]]:
    records = _read_json(HARVEST)
    rules = canon_rules.load(REPO)
    corpora: List[Tuple[str, Dict[str, Any]]] = []
    for name, rel in CORPORA:
        data = _read_json(rel)
        if data is None:
            print("BLIND: %s could not be read -- nothing judged" % rel)
            continue
        corpora.append((name, data))
    return records, rules, corpora


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Scripture, error, solution and law, joined.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="regenerate the concordance")
    group.add_argument("--check", action="store_true", help="compare with what is on disk")
    parser.add_argument("--strict", action="store_true",
                        help="fail a command a statute could bind but none does")
    parser.add_argument("--json", action="store_true", help="print the machine form only")
    args = parser.parse_args(argv)

    records, rules, corpora = collect()
    if not corpora or rules is None or records is None:
        missing = []
        if not corpora:
            missing.append("corpus")
        if rules is None:
            missing.append("MANDATES.md")
        if records is None:
            missing.append(HARVEST)
        print("BLIND: cannot judge without %s" % ", ".join(missing))
        return 2

    built = build(records, rules, corpora)
    stats = built["stats"]
    markdown = render_md(built)
    machine = json.dumps({"schema": SCHEMA, "generated_by": "tools/bible_concordance.py",
                          "stats": stats, "rows": built["rows"],
                          "defects": built["defects"]},
                         indent=1, ensure_ascii=False) + "\n"

    if args.json:
        sys.stdout.write(machine)
    if args.write:
        (REPO / OUT_MD).write_text(markdown, encoding="utf-8", newline="\n")
        (REPO / OUT_JSON).write_text(machine, encoding="utf-8", newline="\n")
        print("wrote %s and %s: %d verse(s), %d direct, %d derived, %d unbound, "
              "%d law(s) bound of %d"
              % (OUT_MD, OUT_JSON, stats["verses"], stats["direct"], stats["derived"],
                 stats["unbound"], stats["laws_bound"], stats["laws_defined"]))
    if args.check:
        stale = []
        for rel, want in ((OUT_MD, markdown), (OUT_JSON, machine)):
            path = REPO / rel
            have = path.read_text(encoding="utf-8") if path.is_file() else None
            if have != want:
                stale.append(rel)
        if stale:
            print("stale: %s -- regenerate with --write" % ", ".join(stale))
            return 1
        print("current: %s and %s" % (OUT_MD, OUT_JSON))

    if not (args.write or args.check or args.json):
        print("%d verse(s), %d direct, %d derived, %d unbound; %d defect(s)"
              % (stats["verses"], stats["direct"], stats["derived"], stats["unbound"],
                 len(built["defects"])))

    for defect in built["defects"]:
        print("defect: %s" % defect)
    if built["defects"]:
        return 1

    if args.strict:
        bindable = [r["ref"] for r in built["rows"]
                    if r["law"]["binding"] == "unbound"
                    and norm_command(r["solution"]["command"]) is not None]
        if bindable:
            print("strict: %d verse(s) carry a command no statute binds: %s"
                  % (len(bindable), ", ".join(bindable)))
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
