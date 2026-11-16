#!/usr/bin/env python3
# coding: utf-8
"""figures.py — reproduce the figures Project_ELIZA publishes about itself.

Every reading prints ``<key> <value>`` on one line, so a pin can quote the exact
string that was printed. ``--json`` emits the same readings as data. A reading
that cannot be taken prints ``<group>.blind true`` on stdout, the reason on
stderr, and the process exits 2: a figure that could not be measured is never
reported as a pass.

What this instrument deliberately does not do: it does not parse the project's
prose as data. Counts are read from the objects that define them
(``traits.ITEMS``, ``bcc_bypass.FLOCK_DEFINITIONS``, ...), timings come from
calls made here, and where the README publishes a number this run does not
reproduce, the reading says so rather than reconciling it by hand.

usage:
    python tools/figures.py                # every reading
    python tools/figures.py --json         # same readings as JSON
    python tools/figures.py --only loop    # one group
"""
from __future__ import annotations

import argparse
import ast
import json
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: A planted edge is generated and then recovered; these are the run's own
#: parameters, printed alongside the result so the reading is repeatable.
OBSERVATIONS = 120
PLANTED_COEFFICIENT = 0.6
SEED = 20261114

#: Timed repetitions are medians, not single samples: one scheduler hiccup on a
#: shared box would otherwise become a published figure.
TIMING_REPEATS = 200
TURNS = 200
BUDGET_MS = 50.0

#: Readings that measure this run's clock rather than the artifact. These move
#: between two runs on one machine, so they may be quoted in prose but never
#: compared pass/fail: a comparison would report the scheduler's mood as the
#: project's behaviour.
VOLATILE_READINGS = (
    "intuition.deliberate_us",
    "intuition.fast_us",
    "loop.median_ms",
)

#: Readings whose name looks like a duration but whose value is a bound the run
#: was handed, not a measurement it took. `loop.budget_ms` is 50.0 on every
#: machine, so comparing it compares the caller's argument -- and skipping it
#: because its name ends in `_ms` would drop a real assertion.
CONSTANT_DURATIONS = ("loop.budget_ms",)

#: Values a name binds at import time without calling anything. A module-level
#: `X = (...)` is an evaluated constant; `X = build()` is not, because its value
#: is a call result and can differ per run.
LITERAL_NODES = (ast.Constant, ast.Tuple, ast.List, ast.Dict, ast.Set, ast.JoinedStr)


class Blinded(Exception):
    """A reading could not be taken. Never a pass."""


# --- readings ----------------------------------------------------------------


def reading_traits() -> Dict[str, object]:
    """The persona layer: how many constants are evaluated, and is keying balanced."""
    files = [ROOT / "eliza" / "psyche" / "traits.py", ROOT / "eliza" / "psyche" / "affect.py"]
    names: List[str] = []
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
            elif isinstance(node, ast.AnnAssign):
                target = node.target
            else:
                continue
            value = getattr(node, "value", None)
            if isinstance(target, ast.Name) and isinstance(value, LITERAL_NODES):
                names.append(target.id)

    from eliza.psyche import affect, traits

    per_domain = {d: [0, 0] for d in traits.DOMAINS}
    for domain, _facet, positively_keyed, _text in traits.ITEMS:
        per_domain[domain][0 if positively_keyed else 1] += 1
    balanced = all(pos == neg for pos, neg in per_domain.values())

    return {
        "traits.module_constants": len(names),
        "traits.domains": len(traits.DOMAINS),
        "traits.facets": sum(len(v) for v in traits.FACETS.values()),
        "traits.items": len(traits.ITEMS),
        "traits.keying_balanced": balanced,
        "traits.occ_families": len(affect.OCC_FAMILIES),
        "traits.temperament_weights": sum(len(row) for row in affect.TEMPERAMENT_WEIGHTS.values()),
    }


def _persona_index():
    """A small persona with two trusted prototypes, shared by network/intuition/loop."""
    from eliza.psyche.intuition import IntuitionIndex
    from eliza.psyche.network import PersonNetwork

    network = PersonNetwork(nodes=["threat", "avoidance", "mood", "support"])
    index = IntuitionIndex(network, min_support=2)
    for _ in range(5):
        index.absorb({"threat": 0.8, "avoidance": 0.7, "mood": -0.5}, name="threat-response")
    for _ in range(5):
        index.absorb({"threat": -0.2, "avoidance": -0.1, "mood": 0.6}, name="settled")
    return network, index


def reading_network() -> Dict[str, object]:
    """Plant one dependency in synthetic observations and report what fit_edges recovers."""
    from eliza.psyche.network import PersonNetwork

    rng = random.Random(SEED)
    network = PersonNetwork(nodes=["threat", "avoidance", "mood"])
    for _ in range(OBSERVATIONS):
        threat = rng.gauss(0.0, 0.4)
        network.observe({
            "threat": threat,
            "avoidance": PLANTED_COEFFICIENT * threat + rng.gauss(0.0, 0.2),
            "mood": rng.gauss(0.0, 0.4),
        })

    edges = network.fit_edges()
    if not edges:
        raise Blinded("fit_edges produced no edges from %d observations" % OBSERVATIONS)
    ranked = sorted(edges, key=lambda e: abs(e.weight), reverse=True)
    planted = [e for e in ranked if {e.a, e.b} == {"threat", "avoidance"}]
    if not planted:
        return {
            "network.observations": OBSERVATIONS,
            "network.planted_coefficient": PLANTED_COEFFICIENT,
            "network.edges": len(edges),
            "network.planted_pcorr": 0.0,
            "network.planted_rank": 0,
            "network.recovered": False,
        }
    edge = planted[0]
    return {
        "network.observations": OBSERVATIONS,
        "network.planted_coefficient": PLANTED_COEFFICIENT,
        "network.edges": len(edges),
        "network.planted_pcorr": round(edge.weight, 3),
        "network.planted_rank": ranked.index(edge) + 1,
        "network.recovered": ranked.index(edge) == 0 and abs(edge.weight) >= 0.2,
    }


def reading_intuition() -> Dict[str, object]:
    """Time the compiled path against deliberate evaluation on the same question."""
    _network, index = _persona_index()
    cues = {"threat": 0.85, "avoidance": 0.75, "mood": -0.55}

    fast = index.read(cues)
    if not fast.known:
        raise Blinded("the fast path has no trusted prototype, so the ratio is not defined")

    fast_us: List[float] = []
    for _ in range(TIMING_REPEATS):
        started = time.perf_counter()
        index.read(cues)
        fast_us.append((time.perf_counter() - started) * 1e6)
    slow_us: List[float] = []
    for _ in range(TIMING_REPEATS):
        started = time.perf_counter()
        index.deliberate(cues)
        slow_us.append((time.perf_counter() - started) * 1e6)

    fast_median = statistics.median(fast_us)
    slow_median = statistics.median(slow_us)
    agreement = index.agreement(cues)
    return {
        "intuition.repeats": TIMING_REPEATS,
        "intuition.fast_us": round(fast_median, 1),
        "intuition.deliberate_us": round(slow_median, 1),
        "intuition.faster": fast_median < slow_median,
        "intuition.agreement": bool(agreement["agree"]) and fast.known,
    }


def reading_loop() -> Dict[str, object]:
    """Run the realtime loop and report the median turn against its own budget."""
    from eliza.psyche.rt_agent import TherapeuticLoop

    network, index = _persona_index()
    loop = TherapeuticLoop(network, index, budget_ms=BUDGET_MS)
    utterances = (
        "I had a long day and I am tired.",
        "My sister called and the conversation went fine.",
        "I cannot focus on the work in front of me.",
        "I feel steadier than I did yesterday.",
    )
    latencies: List[float] = []
    for turn in range(TURNS):
        response = loop.turn(text=utterances[turn % len(utterances)])
        latencies.append(response.latency_ms)

    return {
        "loop.turns": TURNS,
        "loop.median_ms": round(statistics.median(latencies), 3),
        "loop.budget_ms": BUDGET_MS,
        "loop.over_budget": sum(1 for ms in latencies if ms > BUDGET_MS),
    }


def reading_bypass() -> Dict[str, object]:
    """Count the stages the bypass chain actually implements and the sources it declares."""
    from tools import bcc_bypass

    stages = ("fetch_http", "fetch_curl_cffi", "fetch_browser", "fetch_archive")
    present = [name for name in stages if hasattr(bcc_bypass.BCCFetchEngine, name)]

    declared: List[str] = []
    collecting = False
    for line in (bcc_bypass.__doc__ or "").splitlines():
        if line.startswith("Sources:"):
            collecting = True
            declared.append(line.split("Sources:", 1)[1])
            continue
        if collecting:
            if not line.strip():
                break
            declared.append(line)
    sources = [s.strip().rstrip(".") for s in " ".join(declared).split(",") if s.strip()]

    return {
        "bypass.chain_stages": len(present),
        "bypass.declared_sources": len(sources),
        "bypass.flock_definitions": len(bcc_bypass.FLOCK_DEFINITIONS),
        "bypass.tier_definitions": len(bcc_bypass.TIER_DEFINITIONS),
        "bypass.proof_requirements": len(bcc_bypass.PROOF_REQUIREMENTS),
    }


def _wsl_names() -> List[str]:
    """Registered distro names. `wsl -l -q` answers in UTF-16 on this host."""
    import subprocess

    proc = subprocess.run(["wsl", "-l", "-q"], capture_output=True, timeout=15)
    raw = proc.stdout or b""
    text = raw.decode("utf-16-le", "replace") if b"\x00" in raw else raw.decode("utf-8", "replace")
    return [name.strip() for name in text.split() if name.strip()]


def reading_host() -> Dict[str, object]:
    """The box the concurrent guide describes: cores, GIL, stores, and which distros attach.

    Listing is not the property that matters: a distro can be registered and still
    fail to attach its disk, so each name is exercised rather than read off a list.
    """
    import os
    import socket
    import subprocess

    reachable = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        reachable = sock.connect_ex(("127.0.0.1", 8765)) == 0

    names: List[str] = []
    attached: List[str] = []
    #: Why a distro did not attach. A distro that fails to mount its disk is the
    #: difference between "no Kali reading was needed" and "the Kali half of this
    #: reading is blind", so the reason is kept rather than skipped.
    unattached: List[str] = []
    try:
        names = _wsl_names()
    except (OSError, subprocess.TimeoutExpired) as exc:
        names = []
        unattached.append("list: %s" % type(exc).__name__)
    for name in names[:3]:
        try:
            probe = subprocess.run(
                ["wsl", "-d", name, "--", "true"], capture_output=True, timeout=25
            )
            if probe.returncode == 0:
                attached.append(name)
            else:
                unattached.append("%s rc=%d" % (name, probe.returncode))
        except (OSError, subprocess.TimeoutExpired) as exc:
            unattached.append("%s %s" % (name, type(exc).__name__))

    if not names:
        state = "unresponsive"
    elif len(attached) == len(names):
        state = "all"
    elif attached:
        state = "partial"
    else:
        state = "none"

    gil_disabled = bool(getattr(sys, "_is_gil_enabled", lambda: True)() is False)
    return {
        "host.cpus": os.cpu_count() or 0,
        "host.gil_disabled": gil_disabled,
        "host.pmb_reachable": reachable,
        "host.wsl_distros": len(names),
        "host.wsl_attachable": len(attached),
        "host.wsl_unattached": len(unattached),
        "host.wsl_state": state,
    }


def reading_limitation() -> Dict[str, object]:
    """The gradable half of G-ELIZA-1: what the router evaluation can and cannot contain."""
    import json as _json

    import eliza.psyche as psyche_pkg

    corpus = Path(psyche_pkg.__file__).resolve().with_name("data") / "triage_corpus.jsonl"
    if not corpus.is_file():
        raise Blinded("router corpus not found at %s" % corpus.name)

    rows, meta = 0, False
    expectations = 0
    clinical_fields = 0
    clinical_keys = ("outcome", "improved", "gad7", "phq9", "score", "diagnosis")
    for line in corpus.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = _json.loads(line)
        if "_meta" in record:
            meta = True
            continue
        rows += 1
        if "expect_crisis" in record:
            expectations += 1
        clinical_fields += sum(1 for key in record if str(key).lower() in clinical_keys)

    return {
        "limitation.corpus_rows": rows,
        "limitation.corpus_has_meta": meta,
        "limitation.expectation_fields": expectations,
        "limitation.clinical_outcome_fields": clinical_fields,
    }


READINGS = (
    ("traits", reading_traits),
    ("network", reading_network),
    ("intuition", reading_intuition),
    ("loop", reading_loop),
    ("bypass", reading_bypass),
    ("host", reading_host),
    ("limitation", reading_limitation),
)


# --- rendering ---------------------------------------------------------------


def collect(only: Optional[str] = None) -> "tuple[Dict[str, object], Dict[str, str]]":
    """Run every reading. Return (readings, blinded groups with their reasons)."""
    readings: Dict[str, object] = {}
    blinded: Dict[str, str] = {}
    for group, fn in READINGS:
        if only and group != only:
            continue
        try:
            readings.update(fn())
        except Blinded as exc:
            blinded[group] = str(exc)
            readings["%s.blind" % group] = True
        except Exception as exc:  # noqa: BLE001 - a reading that raises is blind, not zero
            blinded[group] = "%s: %s" % (type(exc).__name__, exc)
            readings["%s.blind" % group] = True
    return readings, blinded


def declarations() -> Dict[str, object]:
    """Name which readings move between runs, so no reader has to guess by suffix."""
    return {
        "_volatile": list(VOLATILE_READINGS),
        "_constant_durations": list(CONSTANT_DURATIONS),
    }


def render(readings: Dict[str, object]) -> List[str]:
    lines: List[str] = []
    for key, value in readings.items():
        if isinstance(value, bool):
            value = "true" if value else "false"
        lines.append("%s %s" % (key, value))
    return lines


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit readings as JSON")
    parser.add_argument("--only", choices=[name for name, _ in READINGS], help="one group")
    args = parser.parse_args(argv)

    readings, blinded = collect(args.only)
    payload: Dict[str, object] = dict(readings)
    payload.update(declarations())
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in render(readings):
            print(line)
        for key, value in declarations().items():
            print("%s %s" % (key, ",".join(str(item) for item in value)))

    for group, reason in sorted(blinded.items()):
        print("BLIND %s: %s" % (group, reason), file=sys.stderr)
    return 2 if blinded else 0


if __name__ == "__main__":
    raise SystemExit(main())
