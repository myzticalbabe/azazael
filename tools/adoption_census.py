#!/usr/bin/env python3
"""adoption_census.py — the T-15 instrument: production call sites per technique.

Why this exists
---------------
The retired instrument was the exercise harness's `engaged=181` counter. It read
the registry back to itself: a technique whose only caller is an adapter in
`src/CORE/technique_wiring/` scored exactly the same as a technique that real
production code calls on its own. That made "the technique is adopted" and "an
exercise invoked the technique" indistinguishable numbers — see
`state/ACTION_REGISTRY_2026-10-10.md` H-2 and `TODO_315T_BUILD.md` T-15, which
mandate this replacement: count PRODUCTION call sites per technique and score
exercise-only engagement as **zero**.

What counts as production
-------------------------
  production surface : `src/` EXCEPT `src/CORE/technique_wiring/`, plus `tools/`
                       and `scripts/` (operator/CI-invoked code)
  exercise layer     : `src/CORE/technique_wiring/`  (counted separately, never as adoption)
  non-production     : `tests/`, `archive/`, `*.pre_gate_backup`, generated reports

A call site is a line mentioning the symbol that is not the symbol's own
definition, not a docstring/comment mention, and not a `register()` host string.
Docstring Usage examples and comments are excluded (the same rule the wire-decision
worklist used) so the number cannot be inflated by prose.

Verdicts
--------
  PRODUCTION     >=1 production call site            -> adopted
  EXERCISE-ONLY  only the exercise layer references it -> adoption score ZERO
  UNREFERENCED   nothing outside tests/docs references it

Usage
-----
    python tools/adoption_census.py                    # human summary
    python tools/adoption_census.py --json state/adoption_census.json
    python tools/adoption_census.py --self-test        # positive + negative control
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve()
REPO = HERE.parent.parent
_REL_MAP = Path("state") / "sota_batches" / "batch06" / "technique_codebase_map.json"


def _find_map() -> Path:
    """Locate the technique map.

    It is a `state/` artifact that has lived under both the repo root and the
    project root (the level above this checkout) across sessions, so resolve it
    instead of hardcoding one — a hardcoded miss made the first run of this tool
    fail with FileNotFoundError rather than reporting.
    """
    for cand in (REPO / _REL_MAP, REPO.parent / _REL_MAP,
                 REPO.parent / "azazael" / _REL_MAP):
        if cand.exists():
            return cand
    hits = sorted(p for p in REPO.parent.glob(f"*/{_REL_MAP.as_posix()}"))
    if hits:
        return hits[0]
    return REPO / _REL_MAP  # report the miss at read time, with the path shown


MAP = _find_map()

EXERCISE_DIR = "src/CORE/technique_wiring/"
PROD_ROOTS = ("src/", "tools/", "scripts/")
NON_PROD_PREFIXES = ("tests/", "archive/", ".build/", "desktop/", "packages/")

#: A line that merely names the symbol in prose is not a call site.
_PROSE = re.compile(r'^\s*(#|"""|\'\'\'|:param|:return|>>>)')

#: An import is a wiring INTENT, not a use. Counting it as adoption is how the
#: retired engaged=181 counter inflated itself, so imports are excluded.
_IMPORT = re.compile(r'^\s*(from|import)\s')

#: This tool must never measure itself (its own self-test names symbols).
_SELF = "tools/adoption_census.py"


def _is_prose_context(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if _PROSE.match(line):
        return True
    # a bare docstring line inside one has no syntax markers; treat quoted-only as prose
    if s.startswith(('"', "'")) and s.endswith(('"', "'")):
        return True
    return False


def _noncode_lines(text: str) -> set:
    """1-based line numbers that cannot hold a call site.

    The line-oriented filters above only recognise prose that OPENS with a marker
    (a comment, a triple-quote, a `>>>` example). Prose in the BODY of a docstring
    has none, and two real rows were inflated by exactly that:
      * `src/CORE/technique_runtime.py:11` is a docstring table row reading
        `dispatch_plan.py       plan_dag/assign_roles  2 callers (both exercises)`
        -- counted as a production call site for `plan_dag`;
      * `src/CORE/WORMS/METACLUSTER.py:339` is the continuation line of a
        parenthesised `from CORE.dispatch_plan import (...)` -- matched as a call.
    Both are found by parsing instead of pattern-matching: every string literal's
    line span and every import statement's line span is excluded. Files that do not
    parse (the tree holds non-Python and py2-era sources) fall back to the regex
    filters alone rather than crashing the census.
    """
    skip: set = set()
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, MemoryError):
        return skip
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lo, hi = node.lineno, getattr(node, "end_lineno", node.lineno)
            skip.update(range(lo, hi + 1))
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lo, hi = node.lineno, getattr(node, "end_lineno", node.lineno)
            if hi > lo:                       # multi-line literals: docstrings, tables
                skip.update(range(lo, hi + 1))
    return skip


def _parse_segments(target: str) -> List[Tuple[str, List[str]]]:
    """Parse a map `target` into [(host_path, [symbols]), ...].

    Real targets are compound, e.g.
      `CORE/local_memory.py :: LocalMemoryStore + CORE/structured_action.py :: observe`
      `azazael/src/CORE/skill_library.py :: protocol_artifact, commit_gate, family_index`
      `CORE/freethreading.py :: WorkStealingPool ; CORE/dispatch_plan.py :: ...`
    and some are prefixed `nearest:`. The first version of this tool treated the
    whole string as one `path :: symbol` pair, which silently mis-measured every
    multi-symbol and multi-host row.
    """
    raw = (target or "").strip()
    if not raw or raw in {"\ufffd", "-", "n/a", "N/A"}:
        return []
    raw = re.sub(r"^nearest\s*:\s*", "", raw, flags=re.IGNORECASE)
    out: List[Tuple[str, List[str]]] = []
    for seg in re.split(r"\s*(?:\+|;)\s*", raw):
        if "::" not in seg:
            continue
        path, _, symbols = seg.partition("::")
        # The map wraps paths and symbols in backticks/asterisks in many rows
        # (`CORE/x.py`, **y**); leaving them on made valid hosts unresolvable and
        # produced symbol literals like "`" that matched nothing.
        path = path.strip().strip("`*\"' ").replace("\\", "/").lstrip("/")
        if path.startswith("azazael/"):
            path = path[len("azazael/"):]
        syms: List[str] = []
        for raw_sym in re.split(r"[,]", symbols):
            s = raw_sym.strip().strip("`*\"' ")
            s = re.split(r"\s+", s)[0] if s else ""
            # Symbols are identifiers (optionally dotted). The map writes some as
            # `cast_quarantine_vote`)` / `prefix_inject`)` -- a trailing backtick and
            # bracket from the surrounding prose. Left on, those matched nothing and
            # the row scored as if the symbol had no caller anywhere.
            s = re.split(r"[^A-Za-z0-9_.]", s)[0]
            # drop parenthetical/prose fragments the map mixes into symbol lists
            if not s or s in {"~L956)", "-"} or s.startswith(("~", "(", ")")):
                continue
            syms.append(s)
        if path and syms:
            out.append((path, syms))
    return out


def _is_call_occurrence(line: str, symbol: str, def_owner: bool) -> bool:
    """True when `line` mentions `symbol` as something other than its own def."""
    if symbol not in line:
        return False
    if _is_prose_context(line):
        return False
    if _IMPORT.match(line):
        return False
    if def_owner and re.match(r"\s*(def|class)\s+" + re.escape(symbol.split(".")[-1]) + r"\b", line):
        return False
    return True


#: Per-file cache: (text, non-code line numbers). Without it every (row, file,
#: symbol) triple re-read AND re-parsed the same file -- 141 rows x ~1100 candidate
#: files x ~1.5 symbols is >200k ast.parse calls, which took the census past a
#: 10-minute timeout. The files do not change during a run, so one pass is enough.
_FILE_CACHE: Dict[Path, Tuple[str, set]] = {}


def _load(path: Path) -> Tuple[str, set]:
    """Return (text, non-code lines) for `path`, parsed once per run."""
    hit = _FILE_CACHE.get(path)
    if hit is None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        hit = (text, _noncode_lines(text))
        _FILE_CACHE[path] = hit
    return hit


def _sniff(path: Path, symbol: str, repo: Path) -> Tuple[bool, List[str], List[str]]:
    """Return (defined_here, prod_hits, exercise_hits) for `symbol` in `path`."""
    rel = path.relative_to(repo).as_posix()
    if not path.exists():
        return False, [], []
    text, skip = _load(path)
    short = symbol.split(".")[-1] if symbol else ""
    defined_here = bool(short) and bool(
        re.search(r"\s*(def|class)\s+" + re.escape(short) + r"\b", text))
    if not short:
        return defined_here, [], []

    # A QUALIFIED symbol (`CascadeRouter.route`) may not be collapsed to its last
    # component. Doing so made `route` match ordinary English prose -- the row for
    # EP208 reported 540 "production call sites" that were sentences like
    # "full_text route is the practical extraction path." and a docstring line
    # `("routing", "expert router sends everything to one expert")`. A file that
    # never names the owner class cannot contain an attribute call on it, so the
    # owner's presence is a precondition for any hit whatsoever.
    parts = symbol.split(".")
    owner = parts[-2] if len(parts) >= 2 else ""
    if owner and not re.search(r"\b" + re.escape(owner) + r"\b", text):
        return defined_here, [], []

    # Aliases: `from X import merge_sops as _MERGE_SOPS` means the real call site
    # says `_MERGE_SOPS(...)`. Without this the tool misses every aliased caller --
    # it reported canon_drift_check.py (the one REAL production caller of
    # merge_sops) as absent.
    names = {short}
    for line in text.splitlines():
        m = re.match(r"\s*from\s+\S+\s+import\s+(.+)$", line)
        if not m:
            continue
        for part in m.group(1).split("#")[0].split(","):
            part = part.strip()
            if not part:
                continue
            bits = re.split(r"\s+as\s+", part)
            if bits[0].strip() == short and len(bits) == 2:
                names.add(bits[1].strip())

    prod: List[str] = []
    exer: List[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        if i in skip:
            continue
        if not any(n in line for n in names):
            continue
        if not _is_call_occurrence(line, short, def_owner=defined_here) and not any(
                _is_call_occurrence(line, n, def_owner=False) for n in names - {short}):
            continue
        loc = f"{rel}:{i}"
        (exer if rel.startswith(EXERCISE_DIR) else prod).append(loc)
    return defined_here, prod, exer


def _resolve_host(repo: Path, path_s: str) -> Path:
    """Resolve a map `target` path to a real file.

    The map writes hosts inconsistently: some rows say `src/CORE/x.py`, others say
    `CORE/x.py` (the package-root form). Treating them differently made the tool
    report every short-form row as having no host at all.
    """
    if not path_s:
        return repo / "__none__"
    for cand in (repo / path_s, repo / "src" / path_s):
        if cand.exists():
            return cand
    return repo / path_s


def _candidate_files(repo: Path = REPO) -> List[Path]:
    """Every file that could hold a call site: production surface + exercise layer."""
    cands: List[Path] = []
    for root in (*PROD_ROOTS, EXERCISE_DIR):
        base = repo / root
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            rel = p.relative_to(repo).as_posix()
            if rel.startswith(NON_PROD_PREFIXES) or ".pre_gate_backup" in rel:
                continue
            if rel == _SELF:
                continue
            cands.append(p)
    return sorted(set(cands))


def production_callers(symbol: str, repo: Path = REPO,
                       cands: (List[Path] | None) = None) -> Tuple[List[str], List[str]]:
    """All call sites for `symbol` across the tree, split production vs exercise.

    This is the whole-tree form. The first version of the self-test called
    `_sniff` on the host file alone, so it could only ever see in-file mentions —
    it reported a false failure for a symbol whose real caller lives in tools/.
    """
    prod: List[str] = []
    exer: List[str] = []
    for p in (cands if cands is not None else _candidate_files(repo)):
        _, ph, eh = _sniff(p, symbol, repo)
        prod.extend(ph)
        exer.extend(eh)
    return sorted(set(prod)), sorted(set(exer))


def _host_reachable(repo: Path, host_stem: str, cands: List[Path],
                    host: (Path | None)) -> bool:
    """Is the host module imported by production code other than itself?

    Distinguishes HOST-COMPOSED from EXERCISE-ONLY. A technique consumed by
    another function in its OWN host is genuinely in production when that host
    is reached by production code -- e.g. `margin_check` is called by
    `verify_before_accept`, which `technique_runtime.verify_boundary` reaches,
    which `sentinel_enforcer.enforce` calls. Counting that as zero adoption
    would be as wrong as counting an exercise adapter as adoption.
    """
    if not host_stem:
        return False
    for p in cands:
        if host is not None and p == host:
            continue
        rel = p.relative_to(repo).as_posix()
        if rel.startswith(EXERCISE_DIR):
            continue
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if _IMPORT.match(line) and host_stem in line:
                    return True
        except OSError:
            continue
    return False


def _extract_rows(data: Any) -> List[Dict[str, Any]]:
    """Pull the row dicts out of the map whatever shape it is wrapped in.

    The artifact is `{"totals": {...}, "rows": [...]}` today; an earlier shape was
    a bare list and the first version of this tool silently grabbed `values()` and
    crashed on the nested list. Walk the structure instead of trusting a shape.
    """
    if isinstance(data, list):
        if all(isinstance(x, dict) and "ep" in x for x in data):
            return list(data)
        for item in data:
            got = _extract_rows(item)
            if got:
                return got
        return []
    if isinstance(data, dict):
        if "ep" in data:
            return [data]
        for key in ("rows", "techniques", "items", "results"):
            if key in data:
                got = _extract_rows(data[key])
                if got:
                    return got
        for value in data.values():
            got = _extract_rows(value)
            if got:
                return got
    return []


def census(repo: Path = REPO) -> Dict[str, Any]:
    """Count production vs exercise call sites for every row in the map."""
    data = json.loads(MAP.read_text(encoding="utf-8"))
    rows = _extract_rows(data)

    # Candidate call-site files: production surface + the exercise layer.
    cands = _candidate_files(repo)

    out_rows: List[Dict[str, Any]] = []
    for r in rows:
        ep = str(r.get("ep", "?"))
        segments = _parse_segments(str(r.get("target", "")))
        # EVERY segment is measured. Reading only segments[0] silently dropped the
        # second and third hosts of 24 rows -- e.g. EP208's `proto_route` and
        # EP223's `tpe_lite_suggest` were never looked for, so a row could score
        # EXERCISE-ONLY while one of its listed techniques sat in production.
        host_file, symbols = segments[0] if segments else ("", [])
        host = _resolve_host(repo, host_file) if host_file else None
        defined_here = False
        prod_hits: List[str] = []
        exer_hits: List[str] = []
        host_internal: List[str] = []
        measured: List[str] = []
        for seg_file, seg_syms in segments:
            seg_host = _resolve_host(repo, seg_file) if seg_file else None
            for sym in seg_syms:
                measured.append(sym)
                if seg_host is not None:
                    dh, ph, eh = _sniff(seg_host, sym, repo)
                    defined_here = defined_here or dh
                    host_internal.extend(ph)  # a host's OWN mentions are not adoption
                    exer_hits.extend(eh)
                for p in cands:
                    if seg_host is not None and p == seg_host:
                        continue
                    _, ph, eh = _sniff(p, sym, repo)
                    prod_hits.extend(ph)
                    exer_hits.extend(eh)

        # ADOPTION requires a caller in a DIFFERENT production module: a technique
        # merely referenced inside its own host file is built, not adopted. This is
        # the distinction the retired engaged=181 counter collapsed.
        prod_hits = sorted(set(prod_hits))
        exer_hits = sorted(set(exer_hits))
        host_internal = sorted(set(host_internal))
        # The host must actually define the symbol before any adoption claim is
        # allowed: otherwise a generic name (`observe`, `plan_dag`) matches
        # unrelated production code elsewhere and the row scores as adopted while
        # pointing at a host that has never heard of it.
        host_stem = Path(host_file).stem if host_file else ""
        reachable = bool(host_internal) and _host_reachable(
            repo, host_stem, cands, host)
        if not symbols:
            verdict = "NO-TARGET"
        elif not defined_here:
            verdict = "TARGET-UNVERIFIED"
        elif prod_hits:
            verdict = "ADOPTED"
        elif reachable:
            verdict = "HOST-COMPOSED"
        elif exer_hits:
            verdict = "EXERCISE-ONLY"
        else:
            verdict = "HOSTED-ONLY"

        out_rows.append({
            "ep": ep, "name": r.get("name", ""), "layer": r.get("layer", ""),
            "coverage": r.get("coverage", ""),
            "target": str(r.get("target", "")), "host_file": host_file,
            "symbol": ", ".join(symbols), "symbols": symbols,
            "hosts": [h for h, _ in segments], "measured_symbols": measured,
            "built": defined_here,
            "host_reachable": reachable,
            "production_call_sites": prod_hits, "exercise_call_sites": exer_hits,
            "host_internal_uses": host_internal,
            "n_production": len(prod_hits), "n_exercise": len(exer_hits),
            "verdict": verdict,
        })

    tally: Dict[str, int] = {}
    for r in out_rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    return {
        "repo": str(repo), "rows": len(out_rows), "tally": tally,
        "adoption_score": tally.get("ADOPTED", 0),
        "in_production": tally.get("ADOPTED", 0) + tally.get("HOST-COMPOSED", 0),
        "built_count": sum(1 for r in out_rows if r["built"]),
        "note": ("adoption_score counts ADOPTED rows (caller in a DIFFERENT "
                 "production module); in_production adds HOST-COMPOSED (consumed "
                 "by production code in its own host, where that host is imported "
                 "by production). EXERCISE-ONLY and HOSTED-ONLY score zero by "
                 "mandate (ACTION_REGISTRY H-2, TODO_315T_BUILD T-15)"),
        "results": out_rows,
    }


def _self_test(repo: Path = REPO) -> int:
    """Positive + negative controls, with fixtures taken from the producer.

    Controls (see AGENTS.md VERIFY_ORACLES — a fixture I invent validates my
    assumptions, not reality, so each fixture below is transcribed from the file
    it tests):
      POSITIVE  `merge_sops` IS called by tools/canon_drift_check.py (the Tier-1
                wiring landed in commit 0426a7fc) -> must score >=1 production site.
      NEGATIVE-A the SAME symbol appears in skill_library.py's own module
                docstring Usage block -> that line must NOT be counted, or the
                number is prose-inflated.
      NEGATIVE-B at least one catalogued symbol must score EXERCISE-ONLY, or the
                instrument cannot tell the exercise layer apart from production.
    """
    failures: List[str] = []

    # POSITIVE control (whole production surface, not just the host file).
    prod, exer = production_callers("merge_sops", repo)
    caller_files = {loc.rsplit(":", 1)[0] for loc in prod}
    if "tools/canon_drift_check.py" not in caller_files:
        failures.append(
            "positive control FAILED: merge_sops is called by "
            "tools/canon_drift_check.py but the census did not find it "
            f"(found {sorted(caller_files) or 'nothing'})")
    else:
        print("positive control OK: merge_sops ->", sorted(caller_files))

    # NEGATIVE-A: the docstring Usage line must not be counted.
    doc_lines = [loc for loc in prod if loc.startswith("src/CORE/skill_library.py:")]
    prose_leak = []
    for loc in doc_lines:
        p, _, ln = loc.rpartition(":")
        try:
            line = (repo / p).read_text(encoding="utf-8", errors="replace").splitlines()[int(ln) - 1]
        except (OSError, IndexError, ValueError):
            continue
        if _is_prose_context(line):
            prose_leak.append((loc, line.strip()[:60]))
    if prose_leak:
        failures.append(f"negative control A FAILED: prose counted as caller: {prose_leak}")
    else:
        print(f"negative control A OK: no docstring/comment line counted "
              f"({len(doc_lines)} in-file occurrence(s) all real)")

    # NEGATIVE-B: the exercise layer must be separable.
    rep = census(repo)
    ex = [r for r in rep["results"] if r["verdict"] in ("EXERCISE-ONLY", "HOSTED-ONLY")]
    if not ex:
        failures.append("negative control B FAILED: no row scored EXERCISE-ONLY — "
                        "the instrument cannot distinguish the exercise layer")
    else:
        print(f"negative control B OK: {len(ex)} row(s) score EXERCISE-ONLY "
              f"(e.g. {ex[0]['ep']} {ex[0]['symbol']} -> {ex[0]['n_production']} prod)")

    # NEGATIVE-C / POSITIVE-C: a QUALIFIED symbol must not be matched on prose.
    # Both fixtures are transcribed from the real files, not invented:
    #   - `scripts/fetch_990_series.py` literally says "full_text route is the
    #     practical extraction path." at lines 25/28/41 and never names
    #     CascadeRouter. Before the owner gate those three sentences were counted
    #     as production call sites (EP208 reported 540 hits of this kind).
    #   - `src/CORE/technique_wiring/_l5_dispatch.py:197` really calls
    #     `router.route("classify", ...)` after importing CascadeRouter, so the
    #     gate must not silence a genuine attribute call.
    prose_fixture = repo / "scripts" / "fetch_990_series.py"
    real_fixture = repo / "src" / "CORE" / "technique_wiring" / "_l5_dispatch.py"
    if prose_fixture.exists():
        _, ph, eh = _sniff(prose_fixture, "CascadeRouter.route", repo)
        if ph or eh:
            failures.append(
                "negative control C FAILED: prose-only scripts/fetch_990_series.py "
                f"scored {len(ph)} production + {len(eh)} exercise hit(s) for "
                f"CascadeRouter.route -> {(ph + eh)[:3]}")
        else:
            print("negative control C OK: English 'route' prose scores nothing for "
                  "the qualified symbol CascadeRouter.route")
    if real_fixture.exists():
        _, ph, eh = _sniff(real_fixture, "CascadeRouter.route", repo)
        if not (ph or eh):
            failures.append(
                "positive control C FAILED: _l5_dispatch.py:197 calls "
                "router.route(...) after importing CascadeRouter but the qualified "
                "symbol matched nothing (the owner gate is too strict)")
        else:
            print(f"positive control C OK: qualified symbol found -> {(ph + eh)[:2]}")

    # NEGATIVE-A also in whole-tree form: prose anywhere must stay uncounted.
    for loc in prod:
        p, _, ln = loc.rpartition(":")
        try:
            line = (repo / p).read_text(encoding="utf-8", errors="replace").splitlines()[int(ln) - 1]
        except (OSError, IndexError, ValueError):
            continue
        if _is_prose_context(line):
            failures.append(f"negative control A FAILED: prose counted as caller: {loc}")

    # Prose must never be counted anywhere in the report.
    for r in rep["results"]:
        for loc in r["production_call_sites"]:
            p, _, ln = loc.rpartition(":")
            try:
                line = (repo / p).read_text(encoding="utf-8", errors="replace").splitlines()[int(ln) - 1]
            except (OSError, IndexError, ValueError):
                continue
            if _is_prose_context(line):
                failures.append(f"prose leak: {loc} counted as a call site")
                break

    if failures:
        print("\nSELF-TEST FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print(f"\nSELF-TEST PASS: adoption_score={rep['adoption_score']} "
          f"of {rep['rows']} rows (built={rep['built_count']})  tally={rep['tally']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", default="", help="write the full report to this path")
    ap.add_argument("--self-test", action="store_true",
                    help="positive + negative control run")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    rep = census()
    if args.json:
        dest = Path(args.json)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"wrote {dest}")

    print(f"adoption census — {rep['rows']} rows")
    print(f"  adoption_score (ADOPTED only):   {rep['adoption_score']}")
    print(f"  in_production (+ HOST-COMPOSED): {rep['in_production']}")
    print(f"  built (host module defines it):  {rep['built_count']}")
    for k in ("ADOPTED", "HOST-COMPOSED", "HOSTED-ONLY", "EXERCISE-ONLY",
              "UNREFERENCED", "TARGET-UNVERIFIED", "NO-TARGET"):
        if k in rep["tally"]:
            print(f"  {k:14s} {rep['tally'][k]}")
    print("\n  HOSTED-ONLY and EXERCISE-ONLY score ZERO adoption by mandate "
          "(ACTION_REGISTRY H-2 / TODO_315T_BUILD T-15).")
    print("\n  NOT YET ADOPTED (the worklist):")
    for r in rep["results"]:
        if r["verdict"] == "ADOPTED":
            continue
        print(f"    {r['verdict']:13s} {r['ep']:8s} {r['symbol'][:40]:40s} "
              f"host={r['host_file'] or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
