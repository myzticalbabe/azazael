#!/usr/bin/env python3
"""orphan_triage.py — classify `orphan_scan.py`'s unreachable modules.

`tools/orphan_scan.py` answers *"is this module reachable from an entry point?"*
and prints 350 unreachable rows. That is a worklist, not a disposition: an
application's own `main` module is unimported **by design**, while a library
module nothing reaches is dead capability. This tool draws that distinction so the
list can be acted on.

FOUR CLASSES, in priority order:

  APP-ENTRY   the module has an `if __name__ == "__main__"` guard (or a top-level
              `main()` call), so it is a PROGRAM shipped to be executed. Being
              unimported is correct behaviour, not a defect. Nothing to do.
  DYNAMIC     the module's basename appears as a STRING LITERAL somewhere in the
              tree — an `importlib.import_module("X")`, a registry row, a
              subprocess `-c` payload. `orphan_scan` documents that it cannot see
              these (`--dynamic` counts them); they are reachability blind spots,
              not orphans. Each row names where the string was seen.
  TEST-ONLY   only `tests/` imports it. Reachable from the suite, invisible to
              production. A real finding, with a different remedy from DEAD.
  DEAD        none of the above. Nothing imports it, nothing names it, it is not a
              program. This is the genuine worklist.

SOURCE OF TRUTH: this tool consumes `orphan_scan --json`; it does not re-implement
reachability. Run `python tools/orphan_scan.py --json state/orphan_scan.json`
first. If that file is missing this tool refuses rather than reporting an empty
triage -- an absent input is not a clean bill of health.

Usage:
    python tools/orphan_scan.py --json state/orphan_scan.json
    python tools/orphan_triage.py                    # summary + counts
    python tools/orphan_triage.py --md OUT.md        # also write the report
"""
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

#: Tolerance on the module-count comparison. `orphan_scan`'s candidate set is
#: `.py` files under `src/` minus `__pycache__`; this tool's proxy count runs one
#: high on this tree (708 vs 707), so an exact test would cry stale on every run.
#: Wide enough to absorb that off-by-one, narrow enough to catch the real case
#: it was written for: a tracked scan reporting 701 against a 708-file tree.
STALE_TOLERANCE = 5

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
DEFAULT_JSON = REPO / "state" / "orphan_scan.json"

#: A module is an APP-ENTRY if it carries the conventional guard. Matched loosely
#: on purpose (`__name__` compared to `"__main__"` in either quote style, with or
#: without spaces) because the tree uses both.
MAIN_GUARD = re.compile(r"""__name__\s*==\s*['"]__main__['"]""")

#: Directories that are not this repository's own code and must not be searched
#: when looking for dynamic references.
SKIP_PARTS = {"__pycache__", "archive", "archived", "archived_unified",
              "site-packages", "node_modules", ".build", ".venvs",
              "nuitka_build_backup", "dist", "build"}


def _tree_module_count() -> int:
    """`.py` files under `src/` ignoring `__pycache__` -- the scan's candidate set."""
    return len([p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts])


def _stale(data: dict, jp: Path) -> bool:
    """True when the scan's module count describes a different-size tree."""
    recorded = data.get("n_modules")
    if not isinstance(recorded, int):
        return True                      # no provenance at all is worth flagging
    return abs(recorded - _tree_module_count()) > STALE_TOLERANCE


def _dotted_to_path(mod: str) -> Path:
    """`CORE.WORMS.x` -> `src/CORE/WORMS/x.py` (package fallback to `__init__`)."""
    p = SRC / (mod.replace(".", "/") + ".py")
    if p.is_file():
        return p
    return SRC / mod.replace(".", "/") / "__init__.py"


#: The literal pattern a dynamic import must match. A module counts as DYNAMIC
#: only when a quoted literal equals its FULL dotted path or is a prefix of it
#: (`f"CORE.technique_wiring.{name}"` quotes the prefix). Matching on the bare
#: basename was the first version's defect: `"config"` and `"version"` are common
#: words, so 73 rows scored DYNAMIC and `TEST-ONLY` collapsed to a false zero.
def _collect_string_literals() -> dict[str, list[tuple[str, int]]]:
    """Map each dotted string literal in the tree to where it was seen.

    One pass over the corpus, not one grep per orphan: 350 modules x a full-tree
    grep is minutes, this is seconds.
    """
    seen: dict[str, list[tuple[str, int]]] = defaultdict(list)
    pat = re.compile(r"""['"]([A-Za-z_][A-Za-z0-9_.]{2,})['"]""")
    for f in REPO.rglob("*.py"):
        parts = set(f.parts)
        if SKIP_PARTS & parts:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(f.relative_to(REPO)).replace("\\", "/")
        for i, line in enumerate(text.splitlines(), 1):
            for lit in pat.findall(line):
                seen[lit].append((rel, i))
    return seen


def _collect_tests() -> list[tuple[str, str]]:
    """Every `tests/*.py` as (relpath, text). Read once, not per orphan."""
    out: list[tuple[str, str]] = []
    for f in (REPO / "tests").rglob("*.py"):
        try:
            out.append((str(f.relative_to(REPO)).replace("\\", "/"),
                        f.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return out


def _test_import_of(mod: str, tests: list[tuple[str, str]]) -> str | None:
    """Return the tests file that imports `mod`, or None.

    A test imports `a.b.c` as `from a.b import c` or `importlib.import_module(
    "a.b.c")`, so BOTH the basename and the parent component must be present in
    the same file. Requiring the pair is what keeps a common basename like
    `config` from matching every test that merely mentions the word.
    """
    tail = mod.rsplit(".", 1)[-1]
    parent = mod.rsplit(".", 1)[0].rsplit(".", 1)[-1] if "." in mod else ""
    tail_re = re.compile(r"\b%s\b" % re.escape(tail))
    par_re = re.compile(r"\b%s\b" % re.escape(parent)) if parent else None
    for rel, text in tests:
        if not tail_re.search(text):
            continue
        if mod in text or (par_re and par_re.search(text)) or tail == parent:
            return rel
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    # REQUIRED, with no default. An earlier version defaulted to
    # `state/orphan_scan.json`, which is a TRACKED artifact from 2026-10-10 that
    # describes a 701-module tree while HEAD has 707 -- so a bare run triaged a
    # four-day-old census and reported it as current. A default input is a
    # cached answer to a question about a tree that has since changed.
    ap.add_argument("--json", required=True,
                    help="orphan_scan --json output to consume (no default: "
                         "pass a scan you just generated)")
    ap.add_argument("--md", help="also write the full markdown report here")
    args = ap.parse_args()

    jp = Path(args.json)
    if not jp.is_file():
        raise SystemExit(
            "REFUSING TO TRIAGE: %s does not exist.\n"
            "Run:  python tools/orphan_scan.py --json %s\n"
            "An absent input is not an empty worklist." % (jp, jp))

    data = json.loads(jp.read_text(encoding="utf-8"))
    orphans: list[str] = data.get("orphans", [])

    # ---- provenance, printed before any number is reported ----
    age_days = max(0.0, (time.time() - jp.stat().st_mtime) / 86400.0)
    print("input               : %s" % jp)
    print("input generated     : %s (%.1f days ago)"
          % (time.strftime("%Y-%m-%d %H:%M", time.localtime(jp.stat().st_mtime)),
             age_days))
    print("input n_modules     : %s" % data.get("n_modules"))
    print("tree src/*.py now   : %d" % _tree_module_count())
    # A scan describes the tree it ran against. If module counts diverge, the
    # worklist below answers for a tree that is not this one.
    if _stale(data, jp):
        print("  ** STALE-INPUT WARNING: the scan's module count differs from the")
        print("     current tree by more than %d. Re-run:" % STALE_TOLERANCE)
        print("       python tools/orphan_scan.py --json %s" % jp)
    print()
    if not orphans:
        raise SystemExit(
            "REFUSING TO TRIAGE: %s lists zero orphans. Either the tree is "
            "genuinely clean or the scan ran from the wrong directory; this "
            "tool cannot tell the difference, so it will not report a pass."
            % jp)

    lits = _collect_string_literals()
    tests = _collect_tests()

    rows: list[tuple[str, str, str]] = []   # class, module, evidence
    for mod in orphans:
        p = _dotted_to_path(mod)
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            rows.append(("MISSING", mod, "no file at %s" % p))
            continue

        # 1. A program's own main module is unimported by design.
        if MAIN_GUARD.search(text):
            rows.append(("APP-ENTRY", mod, "__name__ == '__main__'"))
            continue

        # 2. A definite import edge from the suite outranks a speculative string
        #    reference; `orphan_scan` tags this case `[test-only]`.
        t = _test_import_of(mod, tests)
        if t:
            rows.append(("TEST-ONLY", mod, t))
            continue

        # 3. A dynamic import the scanner cannot see. Compared against the FULL
        #    dotted path so common basenames do not qualify.
        own = str(p.relative_to(REPO)).replace("\\", "/")
        dyn = []
        for lit, sites in lits.items():
            if lit == mod or lit.startswith(mod + ".") or mod.startswith(lit + "."):
                dyn += [(r, l) for r, l in sites if r != own]
        if dyn:
            r, l = sorted(dyn)[0]
            rows.append(("DYNAMIC", mod, "%s:%d (string literal)" % (r, l)))
            continue

        rows.append(("DEAD", mod, "nothing imports it, nothing names it"))

    counts = Counter(c for c, _, _ in rows)
    print("orphan rows         : %d" % len(orphans))
    print()
    for cls in ("APP-ENTRY", "DYNAMIC", "TEST-ONLY", "DEAD", "MISSING"):
        print("  %-10s %d" % (cls, counts.get(cls, 0)))
    print()
    print("  APP-ENTRY and DYNAMIC are NOT defects -- they are the two ways")
    print("  orphan_scan over-reports. DEAD is the real worklist; TEST-ONLY")
    print("  is real but has a different remedy (wire it or retire it).")
    print()
    # Priority disclosure. Without this the counts look like they contradict
    # `orphan_scan`, which tags ANY test-reachable row `[test-only]` -- a
    # superset of the TEST-ONLY class here, because a row that is also a
    # program is claimed by APP-ENTRY first. State it; never leave the reader
    # to discover a disagreement between a tool and its own input.
    print("  Classes are assigned in PRIORITY ORDER (APP-ENTRY > TEST-ONLY >")
    print("  DYNAMIC > DEAD), so each row appears exactly once. `orphan_scan`'s")
    print("  own `[test-only]` tag counts every test-reachable row and is")
    print("  therefore a SUPERSET of the TEST-ONLY class below; the two are not")
    print("  expected to match and the difference is app-entry rows.")
    print()
    print("DEAD (the actionable set):")
    for cls, mod, ev in rows:
        if cls == "DEAD":
            print("  %s" % mod)

    if args.md:
        out = Path(args.md)
        with out.open("w", encoding="utf-8") as fh:
            fh.write("# ORPHAN TRIAGE — %s\n\n" % jp.name)
            fh.write("Consumes `%s` (authoritative reachability). "
                     "Classes and their meanings are in the module docstring of "
                     "`tools/orphan_triage.py`.\n\n" % jp.name)
            fh.write("| class | count |\n|---|---|\n")
            for cls in ("APP-ENTRY", "DYNAMIC", "TEST-ONLY", "DEAD", "MISSING"):
                fh.write("| %s | %d |\n" % (cls, counts.get(cls, 0)))
            fh.write("\n## DEAD — the actionable set\n\n| module | evidence |\n|---|---|\n")
            for cls, mod, ev in rows:
                if cls == "DEAD":
                    fh.write("| `%s` | %s |\n" % (mod, ev))
            fh.write("\n## TEST-ONLY — real, different remedy\n\n"
                     "| module | evidence |\n|---|---|\n")
            for cls, mod, ev in rows:
                if cls == "TEST-ONLY":
                    fh.write("| `%s` | %s |\n" % (mod, ev))
            fh.write("\n## DYNAMIC — reachability blind spots, not orphans\n\n"
                     "| module | first dynamic reference |\n|---|---|\n")
            for cls, mod, ev in rows:
                if cls == "DYNAMIC":
                    fh.write("| `%s` | %s |\n" % (mod, ev))
            fh.write("\n## APP-ENTRY — programs, unimported by design\n\n")
            fh.write(", ".join("`%s`" % m for c, m, _ in rows if c == "APP-ENTRY"))
            fh.write("\n")
        print()
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
