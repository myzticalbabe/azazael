"""Pin checker for the STEM ladder wing.

The wing answers one question: does every rung of the ladder in
``ARC/stem/ladder.json`` have exactly one pin in ``ARC/stem/pins.json``, and does
that pin's quoted standard actually appear, verbatim, in the document the rung
cites?

The quote check is not re-implemented here.  HED-8 says extend the default, do
not shadow it: the sentence matcher is loaded from ``tools/arc_provenance.py`` by
path, so a pin that this tool calls verbatim is verbatim by the same rule the
provenance leg applies to every other wing.

What this tool cannot say is as important as what it can.  Every pin here cites a
document this tree wrote, so a located quote proves the registry and the proposal
agree and have not drifted.  It does not prove the standard has standing with an
accreditor, a board of education or a professional body: none was read at source.
That gap is carried in the ladder's ``declared_gaps`` and printed on every run
rather than rounded into the verdict.

Verdicts and exit codes:

    0  READY   every rung has one verbatim-backed pin, and every rung's own
                declaration says a machine reads its artifact with a full
                instrument
    0  PARTIAL structurally clean, but at least one rung declares less than a
                full instrument (``declared-blind``, ``partial``, ``external``,
                or ``machine_readable`` not ``yes``); the rungs are named
    1  GAPS    a rung is unpinned, a pin is malformed, a quote is not verbatim, a
                rung's instrument is claimed and missing, or the registry's
                recorded head cannot be confirmed
    2  BLIND   the ledger, the ladder or the cited document cannot be read

PARTIAL is not READY.  A ladder whose middle rung is graded by an instrument
that proves a quotation rather than competence is not fully graded, and a
verdict that printed READY beside that fact would be HED-9's defect: the count
and its denominator on separate lines, one of them easy to quote.  PARTIAL
carries exit 0 because it is declared coverage debt rather than a defect, so a
caller reading only the exit code is not told a defect exists.  The container
still maps this verdict to its own INCOMPLETE, because missing coverage is
missing coverage: the exit code answers "is anything broken", the verdict
answers "is everything graded", and those are different questions.

Declared gaps are debt, not defects: they print as ``[declared]`` lines every
run and only fail the run under ``--strict``, the way recorded test debt behaves
in golden_arrow.  ``--strict`` promotes both the declared gaps and PARTIAL
coverage to GAPS.

The head check asks whether the provenance line can still be confirmed.  Both
registries record the commit they were written at, so a head that does not
resolve in this clone is a claim nobody can check, and ladder and ledger
disagreeing about it is one provenance record contradicting another.  Either is
GAPS.  A head that resolves but which the cited sources have moved past is
printed as a ``[head]`` line naming the files that changed, because the pins
were verified against a tree that no longer holds them and the reader should not
have to discover that by hand.

Usage:
    python tools/stem_pins.py --check
    python tools/stem_pins.py --check --json logs/stem_pins.json
    python tools/stem_pins.py --check --strict
    python tools/stem_pins.py --check --prove   # remove a pin, break a quote
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent

VERDICT_READY = "READY"
VERDICT_PARTIAL = "PARTIAL"
VERDICT_GAPS = "GAPS"
VERDICT_BLIND = "BLIND"

EXIT_READY = 0
EXIT_PARTIAL = 0  # declared coverage debt: structurally clean, not READY
EXIT_GAPS = 1
EXIT_BLIND = 2

# A rung is fully covered only when both of its own declarations say a machine
# reads the artifact and the instrument that grades it exists in this tree.
# Read from the rung, never inferred: the verdict reports the ladder's statement
# about itself rather than improving on it.
FULL_COVERAGE = (("machine_readable", "yes"), ("instrument_status", "exists"))
GIT_TIMEOUT = 30
CHILD_TIMEOUT = 300  # a control run reads two JSON files and one document

TIERS = ("A", "B", "C")
# Stronger tier, larger number. A pin may not claim less than its rung's floor.
TIER_STRENGTH = {"A": 3, "B": 2, "C": 1}
RUNG_RE = re.compile(r"^E(\d+)$")

REQUIRED_RUNG_KEYS = (
    "rung",
    "who",
    "standard",
    "artifact",
    "machine_readable",
    "instrument",
    "instrument_status",
    "min_tier",
    "characteristic_failure",
)
REQUIRED_PIN_KEYS = (
    "id",
    "rung",
    "demand",
    "authority",
    "cite",
    "text",
    "tier",
    "verified",
    "source",
    "satisfied_by",
    "does_not_prove",
)
MACHINE_READABLE = ("yes", "no", "partly")
# ``external`` exists because a rung's instrument can be real and still not be a
# file in this tree. E8's is the ``pmb__lesson_impact`` MCP tool: claim it as
# ``exists`` and the existence check fails (correctly) because there is no
# tools/lesson_impact.py; claim it as ``declared-blind`` and the rung is
# understated. The third state is the true one, and it must name how it is
# invoked so the claim is checkable by running it.
INSTRUMENT_STATUS = ("exists", "partial", "declared-blind", "external")

DEFAULT_LEDGER = ROOT / "ARC" / "stem" / "pins.json"
DEFAULT_LADDER = ROOT / "ARC" / "stem" / "ladder.json"


class Blinded(Exception):
    """A surface this tool needs could not be read. Never a pass."""


def _load_json(path: Path, label: str) -> Dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Blinded("%s unreadable at %s: %s" % (label, path, exc))
    try:
        loaded = json.loads(raw)
    except ValueError as exc:
        raise Blinded("%s is not JSON at %s: %s" % (label, path, exc))
    if not isinstance(loaded, dict):
        raise Blinded("%s at %s holds %s, not an object" % (label, path, type(loaded).__name__))
    return loaded


def load_quote_matcher():
    """The provenance leg's own sentence matcher, by path.

    Imported rather than copied: a second matcher would drift from the first and
    then a pin this tool called verbatim would fail the provenance leg, or the
    reverse, which is the failure mode HED-8 exists to prevent.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    try:
        import arc_provenance  # noqa: PLC0415 -- loaded by path on purpose
    except Exception as exc:  # noqa: BLE001 - a missing matcher is BLIND, named
        raise Blinded(
            "quote matcher unavailable: tools/arc_provenance.py did not import: %s: %s"
            % (type(exc).__name__, exc)
        )
    return arc_provenance.quote_presence


def banding_tier(ladder: Dict[str, Any]) -> Dict[str, str]:
    """rung -> tier, read from the ladder's own banding table."""
    out: Dict[str, str] = {}
    banding = ladder.get("banding")
    if not isinstance(banding, dict):
        return out
    for tier, rungs in banding.items():
        if not isinstance(rungs, list):
            continue
        for rung in rungs:
            out[str(rung)] = str(tier).upper()
    return out


def git_read(*args: str) -> Tuple[bool, Optional[str]]:
    """One git read, as ``(ran, output)``.

    ``ran`` is False when git itself or this repository could not be used: a
    tarball, a missing binary, a timeout.  That is "unverified" and the caller
    prints it, never "clean" -- an absent reading is not a reading (HED-9).
    ``ran=True, output=None`` means git answered and the answer was "no", which
    is a fact about the tree rather than a failure of the tool.
    """
    command = ["git", "-C", str(ROOT)] + list(args)
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        return False, None
    if proc.returncode != 0:
        return True, None
    return True, (proc.stdout or "").strip()


def rel_in_tree(path: Path) -> Optional[str]:
    """The path as a git pathspec, or None when this tree cannot name it.

    Two different failures land here and both leave the caller without a
    pathspec: ``ValueError`` is ``relative_to`` answering "not under ROOT", and
    ``OSError`` is the filesystem refusing to resolve the path at all.  Neither
    is a success value -- the caller counts a path it cannot name as
    unconfirmable rather than as unchanged, so an unnameable source can never
    make the head check read cleaner than it is.
    """
    relative: Optional[str]
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except (OSError, ValueError):
        relative = None
    return relative


def check_head(
    ladder: Dict[str, Any],
    ledger: Dict[str, Any],
    sources: List[str],
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """Can the registries' recorded head still be confirmed from this tree?

    Returns ``(errors, notes, reading)``.  A claim that cannot be checked is a
    defect; a claim that resolves but which the sources have moved past is a
    reading, printed with the files that changed so nothing is guessed.
    """
    errors: List[str] = []
    notes: List[str] = []
    reading: Dict[str, Any] = {
        "recorded": None,
        "head": None,
        "resolves": None,
        "commits_since": None,
        "files_changed_since": [],
    }

    recorded = str(ladder.get("head") or "").strip()
    ledger_head = str(ledger.get("head") or "").strip()
    reading["recorded"] = recorded or None
    if not recorded:
        errors.append("ladder records no head, so its provenance names no tree")
    if not ledger_head:
        errors.append("ledger records no head, so its provenance names no tree")

    anchor = recorded or ledger_head
    ran, head = git_read("rev-parse", "--short", "HEAD")
    if not ran:
        notes.append(
            "unverified: git could not read this tree, so head %r is a claim "
            "nothing here can confirm" % (anchor or "(unrecorded)")
        )
        return errors, notes, reading
    reading["head"] = head
    if not anchor:
        return errors, notes, reading

    # Compare the two recorded heads by what they resolve to, not by how they are
    # spelled: a short sha and a full sha for one commit are one answer, and a
    # string comparison would report a disagreement nobody could act on.
    if recorded and ledger_head and recorded != ledger_head:
        ran_l, canon_l = git_read("rev-parse", "--short", "%s^{commit}" % ledger_head)
        ran_r, canon_r = git_read("rev-parse", "--short", "%s^{commit}" % recorded)
        agreed = bool(ran_l and ran_r and canon_l and canon_r and canon_l == canon_r)
        if not agreed:
            errors.append(
                "ladder records head %s and the ledger records %s; one provenance "
                "record, two answers" % (recorded, ledger_head)
            )

    ran_resolve, resolved = git_read("cat-file", "-e", "%s^{commit}" % anchor)
    if not ran_resolve:
        notes.append("unverified: git could not test whether %s exists" % anchor)
        return errors, notes, reading
    reading["resolves"] = resolved is not None
    if resolved is None:
        errors.append(
            "recorded head %s does not resolve in this clone, so every pin's "
            "provenance cites a tree nobody can examine" % anchor
        )
        return errors, notes, reading

    ran_short, canonical = git_read("rev-parse", "--short", "%s^{commit}" % anchor)
    canonical = canonical or anchor
    if head and canonical == head:
        notes.append("%s is this tree's HEAD" % canonical)
        return errors, notes, reading

    ran_count, count = git_read("rev-list", "--count", "%s..HEAD" % canonical)
    if ran_count and count and count.isdigit():
        reading["commits_since"] = int(count)
    if sources:
        ran_diff, changed = git_read("diff", "--name-only", canonical, "HEAD", "--", *sources)
        if ran_diff and changed:
            reading["files_changed_since"] = [
                line.strip() for line in changed.splitlines() if line.strip()
            ]

    moved = reading["files_changed_since"]
    behind = reading["commits_since"]
    notes.append(
        "%s predates HEAD %s by %s commit(s)%s"
        % (
            canonical,
            head or "(unread)",
            "an unread number of" if behind is None else str(behind),
            (
                "; %d of %d cited source(s) changed since (%s), so the pins were "
                "verified against a tree this one no longer is"
                % (len(moved), len(sources), ", ".join(moved))
            )
            if moved
            else "; none of the cited sources changed since, so the quotes still "
            "describe this tree",
        )
    )
    return errors, notes, reading


def check_ladder(ladder: Dict[str, Any]) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """Structural checks on the rung registry."""
    errors: List[str] = []
    warnings: List[str] = []
    table: Dict[str, Any] = {}

    rungs = ladder.get("rungs")
    if not isinstance(rungs, list) or not rungs:
        raise Blinded("ladder at %s declares no rungs" % DEFAULT_LADDER)

    seen: List[str] = []
    by_rung: Dict[str, Dict[str, Any]] = {}
    for index, rung in enumerate(rungs):
        if not isinstance(rung, dict):
            errors.append("rung %d is %s, not an object" % (index, type(rung).__name__))
            continue
        name = str(rung.get("rung") or "").strip()
        if not RUNG_RE.match(name):
            errors.append("rung %d has no E<number> id (%r)" % (index, name))
            continue
        if name in by_rung:
            errors.append("rung %s is declared twice" % name)
            continue
        by_rung[name] = rung
        seen.append(name)

        for key in REQUIRED_RUNG_KEYS:
            value = rung.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append("rung %s: required key %r is empty or missing" % (name, key))

        readable = str(rung.get("machine_readable") or "").strip().lower()
        if readable not in MACHINE_READABLE:
            errors.append(
                "rung %s: machine_readable %r is not one of %s"
                % (name, readable, ", ".join(MACHINE_READABLE))
            )

        status = str(rung.get("instrument_status") or "").strip().lower()
        if status not in INSTRUMENT_STATUS:
            errors.append(
                "rung %s: instrument_status %r is not one of %s"
                % (name, status, ", ".join(INSTRUMENT_STATUS))
            )
        instrument = str(rung.get("instrument") or "").strip()
        if status == "declared-blind":
            if instrument != "none":
                errors.append(
                    "rung %s: declared-blind but names instrument %r; a blind rung "
                    "names no instrument rather than a placeholder" % (name, instrument)
                )
        elif status == "external":
            invoke = str(rung.get("instrument_invoke") or "").strip()
            if instrument == "none" or not instrument:
                errors.append(
                    "rung %s: instrument_status 'external' with no instrument named" % name
                )
            if not invoke:
                errors.append(
                    "rung %s: names an external instrument %r but no instrument_invoke, so "
                    "nothing says how to run it" % (name, instrument)
                )
        elif status in ("exists", "partial"):
            if instrument == "none" or not instrument:
                errors.append(
                    "rung %s: instrument_status %r with no instrument named" % (name, status)
                )
            else:
                path = (ROOT / instrument).resolve()
                try:
                    path.relative_to(ROOT)
                except ValueError:
                    errors.append("rung %s: instrument %r resolves outside the tree" % (name, instrument))
                else:
                    if not path.is_file():
                        errors.append(
                            "rung %s: instrument %r does not exist in this tree" % (name, instrument)
                        )

        min_tier = str(rung.get("min_tier") or "").strip().upper()
        if min_tier not in TIERS:
            errors.append("rung %s: min_tier %r is not one of A, B, C" % (name, min_tier))

    expected = ["E%d" % index for index in range(len(seen))]
    if seen != expected:
        errors.append(
            "rungs are not contiguous from E0: read %s, expected %s"
            % (", ".join(seen) or "none", ", ".join(expected))
        )

    bands = banding_tier(ladder)
    if not bands:
        errors.append("ladder declares no banding table, so no rung has a tier")
    for name, rung in by_rung.items():
        band = bands.get(name)
        min_tier = str(rung.get("min_tier") or "").strip().upper()
        if band is None:
            errors.append("rung %s is absent from the banding table" % name)
        elif min_tier and band != min_tier:
            errors.append(
                "rung %s: min_tier %s disagrees with banding %s" % (name, min_tier, band)
            )

    table = {"rungs": by_rung, "order": seen, "bands": bands}
    return errors, warnings, table


def check_pins(
    ledger: Dict[str, Any],
    ladder: Dict[str, Any],
    table: Dict[str, Any],
    document_text: str,
    document_rel: str,
    quote_presence,
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """One pin per rung, tier at or above the rung's floor, quote verbatim."""
    errors: List[str] = []
    warnings: List[str] = []
    rows: List[Dict[str, Any]] = []

    pins = ledger.get("pins")
    if not isinstance(pins, list) or not pins:
        errors.append("ledger declares no pins")
        return errors, warnings, rows

    by_rung = table["rungs"]
    bands = table["bands"]
    pinned: Dict[str, str] = {}

    for index, pin in enumerate(pins):
        if not isinstance(pin, dict):
            errors.append("pin %d is %s, not an object" % (index, type(pin).__name__))
            continue
        pin_id = str(pin.get("id") or "").strip()
        label = pin_id or "pin %d" % index
        rung_name = str(pin.get("rung") or "").strip()

        for key in REQUIRED_PIN_KEYS:
            value = pin.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append("%s: required key %r is empty or missing" % (label, key))

        if not RUNG_RE.match(rung_name):
            errors.append("%s: rung %r is not an E<number> id" % (label, rung_name))
            continue
        rung = by_rung.get(rung_name)
        if rung is None:
            errors.append("%s: cites rung %s, which the ladder does not declare" % (label, rung_name))
            continue

        if rung_name in pinned:
            errors.append(
                "rung %s is pinned twice (%s and %s); one rung, one pin"
                % (rung_name, pinned[rung_name], label)
            )
        else:
            pinned[rung_name] = label

        tier = str(pin.get("tier") or "").strip().upper()
        if tier not in TIERS:
            errors.append("%s: tier %r is not one of A, B, C" % (label, tier))
        else:
            min_tier = str(rung.get("min_tier") or "").strip().upper()
            if min_tier in TIER_STRENGTH and TIER_STRENGTH[tier] < TIER_STRENGTH[min_tier]:
                errors.append(
                    "%s: tier %s is below rung %s's floor %s"
                    % (label, tier, rung_name, min_tier)
                )
            band = bands.get(rung_name)
            if tier == "A" and band and band != "A":
                errors.append(
                    "%s: claims tier A at rung %s, whose banding is %s; tier A is "
                    "reserved for the A band" % (label, rung_name, band)
                )

        source = str(pin.get("source") or "").strip()
        if source and source != document_rel:
            warnings.append(
                "%s: cites source %r, which is not the ladder's document %r; its "
                "quote is not checked against the ladder's own text"
                % (label, source, document_rel)
            )

        text = str(pin.get("text") or "")
        found, total = quote_presence(document_text, text)
        if total == 0:
            errors.append(
                "%s: text is shorter than one checkable sentence, so nothing was verified"
                % label
            )
        elif found != total:
            errors.append(
                "%s: %d of %d quoted sentences are not verbatim in %s"
                % (label, total - found, total, document_rel)
            )

        rows.append(
            {
                "id": label,
                "rung": rung_name,
                "tier": tier,
                "band": bands.get(rung_name, ""),
                "quote": "%d/%d" % (found, total),
                "instrument": str(rung.get("instrument") or ""),
                "status": str(rung.get("instrument_status") or ""),
            }
        )

    for rung_name in table["order"]:
        if rung_name not in pinned:
            errors.append("rung %s has no pin; a rung without a pin is unstated" % rung_name)

    for rung in table["order"]:
        standard = str(by_rung[rung].get("standard") or "")
        found, total = quote_presence(document_text, standard)
        if total and found != total:
            warnings.append(
                "rung %s: the ladder's own standard is not verbatim in %s (%d of %d "
                "sentences found); the registry has drifted from the proposal"
                % (rung, document_rel, found, total)
            )

    return errors, warnings, rows


def declared_gaps(ladder: Dict[str, Any]) -> List[str]:
    """The ladder's own debt, phrased as one line each."""
    out: List[str] = []
    gaps = ladder.get("declared_gaps")
    if not isinstance(gaps, list):
        return out
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        out.append(
            "%s: %s - %s"
            % (
                str(gap.get("rung") or "?"),
                str(gap.get("title") or "declared gap"),
                str(gap.get("why") or ""),
            )
        )
    return out


def coverage_gaps(table: Dict[str, Any]) -> List[str]:
    """Rungs whose own declaration says they are not fully graded.

    ``READY`` is reserved for a ladder every rung of which a machine can read and
    grade.  Four of nine rungs here cannot be, by the ladder's own statement, so
    the verdict says PARTIAL and names them: a verdict is a summary of a
    population, and HED-9 says the denominator travels with it.
    """
    out: List[str] = []
    for name in table["order"]:
        rung = table["rungs"][name]
        reasons: List[str] = []
        for key, full in FULL_COVERAGE:
            value = str(rung.get(key) or "").strip().lower()
            if value != full:
                reasons.append("%s=%s" % (key, value or "unset"))
        if reasons:
            out.append("%s (%s)" % (name, ", ".join(reasons)))
    return out


def verdict_for(
    errors: List[str],
    declared: List[str],
    coverage: List[str],
    strict: bool,
) -> str:
    if errors:
        return VERDICT_GAPS
    if strict and (declared or coverage):
        return VERDICT_GAPS
    if coverage:
        return VERDICT_PARTIAL
    return VERDICT_READY


def exit_code_for(name: str) -> int:
    if name == VERDICT_READY:
        return EXIT_READY
    if name == VERDICT_PARTIAL:
        return EXIT_PARTIAL
    if name == VERDICT_BLIND:
        return EXIT_BLIND
    return EXIT_GAPS


def prove(
    ledger: Dict[str, Any], ladder_path: Path, ledger_path: Path
) -> List[Dict[str, Any]]:
    """Two negative controls: remove a pin, then break a quote.

    A checker nobody can make fail is not a checker.  Each control copies the
    ledger, damages exactly one claim, and runs *this* tool against the copy, so
    what is proven is the shipped code path rather than a re-implementation of it
    inside the proof.  ``BITES`` requires both a non-zero exit and the error line
    that names the damage: firing for the wrong reason is reported as such.
    """
    pins = [p for p in ledger.get("pins") or [] if isinstance(p, dict)]
    if not pins:
        raise Blinded("ledger holds no pins, so there is nothing to remove as a control")

    base = json.loads(json.dumps(ledger))
    base["pins"] = pins
    rung = str(pins[0].get("rung") or "?")
    variants: List[Tuple[str, Dict[str, Any], str]] = []

    without = json.loads(json.dumps(base))
    without["pins"] = without["pins"][1:]
    variants.append(("pin-removed", without, "has no pin"))

    broken = json.loads(json.dumps(base))
    broken["pins"][0]["text"] = (
        "No document in this tree contains this sentence, which is precisely what "
        "the control is checking."
    )
    variants.append(("quote-altered", broken, "not verbatim"))

    controls: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="stem_prove_") as tmp:
        temp_ledger = Path(tmp) / "pins.json"
        for label, variant, marker in variants:
            temp_ledger.write_text(json.dumps(variant, indent=2), encoding="utf-8")
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--check",
                "--ledger",
                str(temp_ledger),
                "--ladder",
                str(ladder_path),
            ]
            try:
                proc = subprocess.run(
                    command,
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=CHILD_TIMEOUT,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise Blinded("control %s could not run: %s" % (label, exc))
            output = (proc.stdout or "") + (proc.stderr or "")
            named = marker in output
            if proc.returncode != 0 and named:
                state = "BITES"
            elif proc.returncode == 0:
                state = "SILENT"
            else:
                state = "WRONG-REASON"
            controls.append(
                {
                    "control": label,
                    "rung": rung,
                    "marker": marker,
                    "exit": proc.returncode,
                    "state": state,
                    "detail": output.strip().splitlines()[:4],
                }
            )
    return controls


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the STEM ladder wing: one verbatim pin per rung."
    )
    parser.add_argument("--check", action="store_true", help="validate and exit (default)")
    parser.add_argument("--json", metavar="PATH", help="write the report as JSON")
    parser.add_argument("--ledger", metavar="PATH", default=str(DEFAULT_LEDGER))
    parser.add_argument("--ladder", metavar="PATH", default=str(DEFAULT_LADDER))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="declared gaps and PARTIAL coverage fail the run instead of printing as advisory",
    )
    parser.add_argument(
        "--prove",
        action="store_true",
        help="remove one pin and alter one quote in a copy, and check this tool fires",
    )
    args = parser.parse_args(argv)

    # Every failure leaves a printed verdict and a matching exit code. A traceback
    # exits 1, which is indistinguishable from GAPS, and a silent success is worse.
    try:
        ladder = _load_json(Path(args.ladder), "ladder")
        ledger = _load_json(Path(args.ledger), "ledger")
        document_rel = str(ladder.get("document") or "").strip()
        if not document_rel:
            raise Blinded("ladder names no document, so no quote can be located")
        document_path = (ROOT / document_rel).resolve()
        try:
            document_path.relative_to(ROOT)
        except ValueError:
            raise Blinded("ladder document %r resolves outside the tree" % document_rel)
        try:
            document_text = document_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise Blinded("ladder document unreadable at %s: %s" % (document_rel, exc))
        quote_presence = load_quote_matcher()

        ladder_errors, ladder_warnings, table = check_ladder(ladder)
        pin_errors, pin_warnings, rows = check_pins(
            ledger, ladder, table, document_text, document_rel, quote_presence
        )
        sources = [
            rel
            for rel in (
                rel_in_tree(Path(args.ladder)),
                rel_in_tree(Path(args.ledger)),
                document_rel or None,
            )
            if rel
        ]
        head_errors, head_notes, head_reading = check_head(ladder, ledger, sources)
        coverage = coverage_gaps(table)
        controls: List[Dict[str, Any]] = []
        if args.prove:
            controls = prove(ledger, Path(args.ladder), Path(args.ledger))
        errors = ladder_errors + pin_errors + head_errors
        for control in controls:
            if control["state"] != "BITES":
                errors.append(
                    "control %s: checker exited %d and did not name %r (%s)"
                    % (control["control"], control["exit"], control["marker"], control["state"])
                )
        warnings = ladder_warnings + pin_warnings
        gaps = declared_gaps(ladder)
        name = verdict_for(errors, gaps, coverage, args.strict)
    except Blinded as exc:
        print("verdict: %s" % VERDICT_BLIND)
        print("reason: %s" % exc)
        return EXIT_BLIND
    except Exception as exc:  # noqa: BLE001 - an unhandled defect is BLIND, named
        print("verdict: %s" % VERDICT_BLIND)
        print("reason: checker failed: %s: %s" % (type(exc).__name__, exc))
        return EXIT_BLIND

    pins = [p for p in ledger.get("pins") or [] if isinstance(p, dict)]

    if args.json:
        out = Path(args.json)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                json.dumps(
                    {
                        "verdict": name,
                        "pins": len(pins),
                        "rungs": rows,
                        "head": head_reading,
                        "coverage": coverage,
                        "declared_gaps": gaps,
                        "controls": controls,
                        "errors": errors,
                        "warnings": warnings,
                        "strict": bool(args.strict),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except OSError as exc:
            print("verdict: %s" % VERDICT_BLIND)
            print("reason: report could not be written to %s: %s" % (out, exc))
            return EXIT_BLIND
        print("wrote %s" % out)

    print("verdict: %s" % name)
    print(
        "ledger: %d pins, %d rungs, %d declared gaps (document %s)"
        % (len(pins), len(rows), len(gaps), document_rel)
    )
    for note in head_notes:
        print("  [head] %s" % note)
    for row in rows:
        print(
            "  %-8s %-3s band %-3s quote %-5s instrument %s (%s)"
            % (
                row["rung"],
                row["tier"],
                row["band"],
                row["quote"],
                row["instrument"],
                row["status"],
            )
        )
    if errors:
        print("errors: %d" % len(errors))
        for err in errors:
            print("  [GAP] %s" % err)
    if gaps:
        print("declared gaps: %d%s" % (len(gaps), " (failing under --strict)" if args.strict else ""))
        for gap in gaps:
            print("  [declared] %s" % gap)
    if coverage:
        print(
            "coverage: %d of %d rungs declare less than a full instrument%s"
            % (len(coverage), len(rows), " (failing under --strict)" if args.strict else "")
        )
        for item in coverage:
            print("  [partial] %s" % item)
    for control in controls:
        print(
            "  [CONTROL] %s on %s -> exit %d (%s)"
            % (control["control"], control["rung"], control["exit"], control["state"])
        )
        if control["state"] != "BITES":
            for line in control["detail"]:
                print("            %s" % line)
    if warnings:
        for warn in warnings[:8]:
            print("  [note] %s" % warn)
        if len(warnings) > 8:
            print("  [note] ... and %d more (advisory only)" % (len(warnings) - 8))

    return exit_code_for(name)


if __name__ == "__main__":
    sys.exit(main())
