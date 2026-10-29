#!/usr/bin/env python3
"""Antibody shards — errors cloned into self-seeking detectors (routable).

Each antibody is derived from one observed error instance and sweeps for
every recurrence of it. Shape follows the shard contract: runnable probe,
JSON-serializable result, self-test. See
docs/ANTIBODY_SHARD_PARADIGM_2026-10-29.md for the paradigm.

Lifecycle (closed loop, evidence-gated):
    seeking -> neutralized -> immune, with reinfection reopening to seeking.
    Status advances only on recorded seek evidence: neutralized requires a
    passing seek; immune requires three consecutive passing seeks. The store
    (antibodies.json) is the deed book: atomic writes (D1) under an
    exclusive lock (D2), same pattern as morphed_registry.

Usage:
    from SHARDS.antibodies import run_antibody, seek_all
    seek_all()   # run every probe, record generations, print JSON
"""

import argparse
import json
import os
import socket
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl  # POSIX file locking (absent on Windows)
except ImportError:
    fcntl = None  # type: ignore[assignment]
try:
    import msvcrt  # Windows file locking (absent on POSIX)
except ImportError:
    msvcrt = None  # type: ignore[assignment]

from SHARDS.polyglot import EXPECTED_SUM, run_shard, supported_shard_langs
from SHARDS import registry as _registry

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here


_STORE_PATH = Path(__file__).with_name("antibodies.json")
_HISTORY_CAP = 50  # bounded growth: the store is a deed book, not a log
_IMMUNE_STREAK = 3  # consecutive passing seeks required for immunity


def _antibody_specs() -> dict:
    """The two first-generation antibodies (cloned from observed instances)."""
    return {
        "seq-range-mismatch": {
            "signature": {
                "namespace": "polyglot",
                "handler_role": "work-golden",
                "exc_type": "none",
                "message_shape": "work sum != EXPECTED_SUM",
                "ast_shape": "n/a (data bug, not structural)",
                "first_seen": "2026-10-29",
                "parent_instance": "bash work golden summed 1..20000 via seq",
            },
            "probe": "work-tier agreement across every toolchain",
        },
        "stale-table-routing": {
            "signature": {
                "namespace": "registry",
                "handler_role": "_measured_order",
                "exc_type": "none",
                "message_shape": "stale medians spent as measurements",
                "ast_shape": "n/a (policy bug, not structural)",
                "first_seen": "2026-10-29",
                "parent_instance": "stale sweep.json drove route_lang with warning only",
            },
            "probe": "forced-stale sweep must degrade to LANG_ORDER",
        },
    }


def _load_store() -> dict:
    try:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"generation": 0, "updated_at": "", "antibodies": {}}


def _save_store(store: dict) -> None:
    """Atomic write: temp file in same dir + os.replace (D1 pattern)."""
    store["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload = (json.dumps(store, indent=1) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=str(_STORE_PATH.parent),
                                prefix=".antibodies.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except OSError as e:
                note_failure("antibodies:fsync", e)
        os.replace(tmp, _STORE_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError as e:
            note_failure("antibodies:tmp-cleanup", e)
        raise


@contextmanager
def _store_lock():
    """Exclusive lock for read-modify-write (D2 pattern, guarded imports)."""
    lock_path = _STORE_PATH.with_suffix(".lock")
    fh = open(str(lock_path), "ab")  # noqa: PTH123 -- lock handle, binary
    try:
        if fcntl is not None:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            fh._lock_kind = "flock"
        elif msvcrt is not None:
            try:
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                fh._lock_kind = "msvcrt"
            except OSError as e:
                note_failure("antibodies:msvcrt-lock", e)
                fh._lock_kind = "none"
        else:
            note_failure("antibodies:no-lock-primitive", None)
            fh._lock_kind = "none"
        yield lock_path
    finally:
        try:
            kind = getattr(fh, "_lock_kind", "none")
            if kind == "flock" and fcntl is not None:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            elif kind == "msvcrt" and msvcrt is not None:
                fh.seek(0)
                try:
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError as e:
                    note_failure("antibodies:unlock", e)
        finally:
            fh.close()


def _probe_work_tier() -> dict:
    """Seek every work golden that disagrees with EXPECTED_SUM."""
    instances: list = []
    ran = 0
    for lang in supported_shard_langs():
        res = run_shard(lang, tier="work")
        if res["status"] == "skipped":
            continue
        ran += 1
        if not res["ok"]:
            instances.append(f"{lang}: {res.get('status')}"
                             f" sum_ok={res.get('sum')}")
    return {"ok": not instances, "ran": ran, "instances": instances,
            "expected_sum": EXPECTED_SUM}


def _probe_stale_fallback() -> dict:
    """Stale sweep must degrade to canonical order (forced-stale probe)."""
    old = _registry.SWEEP_MAX_AGE_HOURS
    _registry.SWEEP_MAX_AGE_HOURS = -1  # every table stale by age
    try:
        order = _registry._measured_order()
        ok = order == list(_registry.LANG_ORDER)
    finally:
        _registry.SWEEP_MAX_AGE_HOURS = old
    return {"ok": ok, "ran": 1,
            "instances": [] if ok else ["_measured_order spent stale medians"]}


_PROBES = {
    "seq-range-mismatch": _probe_work_tier,
    "stale-table-routing": _probe_stale_fallback,
}


def run_antibody(name: str) -> dict:
    """Execute one antibody probe; JSON-serializable result (shard shape)."""
    key = (name or "").lower()
    if key not in _PROBES:
        return {"name": key, "status": "unknown-antibody", "ok": False}
    try:
        found = _PROBES[key]()
    except Exception as e:
        note_failure("antibodies:probe", e)
        return {"name": key, "status": "probe-crashed", "ok": False,
                "error": str(e)}
    return {"name": key, "status": "pass" if found["ok"] else "fail",
            "ok": found["ok"], "ran": found["ran"],
            "instances": found["instances"]}


def record_seek(name: str, outcome: dict) -> dict:
    """Append a seek observation as a new generation (Train step).

    Every run is evidence: generation counter advances, history stays
    bounded at _HISTORY_CAP. Returns the recorded generation."""
    key = (name or "").lower()
    if key not in _PROBES:
        return {"ok": False, "error": f"unknown antibody: {key}"}
    with _store_lock():
        store = _load_store()
        store["generation"] = int(store.get("generation", 0)) + 1
        gen = store["generation"]
        entry = store.setdefault("antibodies", {}).setdefault(key, {
            "status": "seeking",
            "signature": _antibody_specs()[key]["signature"],
            "generations": [],
        })
        entry["generations"].append({
            "gen": gen,
            "at": datetime.now(timezone.utc).isoformat(),
            "ok": bool(outcome.get("ok", False)),
            "instances": list(outcome.get("instances", []))[:20],
            "origin": _origin(),
            "uuid": uuid.uuid4().hex[:8],
        })
        entry["generations"] = entry["generations"][-_HISTORY_CAP:]
        try:
            _save_store(store)
        except OSError as e:
            note_failure("antibodies:store", e)
            return {"ok": False, "error": str(e)}
        return {"ok": True, "name": key, "gen": gen,
                "status": entry["status"]}


def _origin() -> str:
    try:
        return socket.gethostname()
    except OSError as e:
        note_failure("antibodies:origin", e)
        return "unknown-host"


def antibody_status(name: str | None = None) -> dict:
    """Current status (and bounded history) for one or all antibodies."""
    specs = _antibody_specs()
    stored = _load_store().get("antibodies", {})
    if name is not None:
        key = name.lower()
        if key not in specs:
            return {"ok": False, "error": f"unknown antibody: {key}"}
        return {"ok": True, "name": key,
                "status": stored.get(key, {}).get("status", "seeking"),
                "generations": stored.get(key, {}).get("generations", []),
                "signature": specs[key]["signature"]}
    return {"ok": True, "antibodies": {
        key: {"status": stored.get(key, {}).get("status", "seeking"),
              "seeks": len(stored.get(key, {}).get("generations", []))}
        for key in specs}}


def _streak(entry: dict) -> int:
    """Consecutive passing seeks at the head of history."""
    streak = 0
    for gen in reversed(entry.get("generations", [])):
        if gen.get("ok"):
            streak += 1
        else:
            break
    return streak


def promote_antibody(name: str, to_status: str) -> dict:
    """Advance (or reopen) an antibody on recorded evidence (Evolve step).

    seeking -> neutralized requires a passing seek on record.
    neutralized -> immune requires _IMMUNE_STREAK consecutive passing seeks.
    Any status -> seeking reopens on reinfection. Refusals are ledger-noted,
    never silent, never crashing."""
    key = (name or "").lower()
    want = (to_status or "").lower()
    if key not in _PROBES:
        return {"ok": False, "error": f"unknown antibody: {key}"}
    if want not in ("seeking", "neutralized", "immune"):
        return {"ok": False, "error": f"unknown status: {want}"}
    with _store_lock():
        store = _load_store()
        entry = store.setdefault("antibodies", {}).setdefault(key, {
            "status": "seeking",
            "signature": _antibody_specs()[key]["signature"],
            "generations": [],
        })
        have = entry.get("status", "seeking")
        if want == "seeking":
            entry["status"] = "seeking"  # reinfection reopens, always allowed
        elif want == "neutralized":
            if have == "immune":
                note_failure("antibodies:promote-skips-immune", None)
                return {"ok": False,
                        "error": "immune -> neutralized skips backward; "
                                 "reopen via seeking on reinfection"}
            last = (entry.get("generations") or [{}])[-1]
            if not last.get("ok", False):
                note_failure("antibodies:promote-no-evidence", None)
                return {"ok": False,
                        "error": "neutralized requires a passing seek on record"}
            entry["status"] = "neutralized"
        elif want == "immune":
            if have != "neutralized":
                note_failure("antibodies:promote-order", None)
                return {"ok": False,
                        "error": "immune requires neutralized first"}
            if _streak(entry) < _IMMUNE_STREAK:
                note_failure("antibodies:promote-streak", None)
                return {"ok": False,
                        "error": f"immune requires {_IMMUNE_STREAK} "
                                 f"consecutive passing seeks"}
            entry["status"] = "immune"
        try:
            _save_store(store)
        except OSError as e:
            note_failure("antibodies:store", e)
            return {"ok": False, "error": str(e)}
        return {"ok": True, "name": key, "from": have, "to": entry["status"]}


def seek_all(record: bool = True) -> dict:
    """Run every probe; optionally record each as a generation (Train).

    Returns {ok, results}. ok is True only when every antibody passes
    on every toolchain present (missing toolchains skip cleanly)."""
    results = []
    for key in _antibody_specs():
        res = run_antibody(key)
        if record:
            record_seek(key, res)
        results.append(res)
    report = {"seek": "PASS" if all(r["ok"] for r in results) else "FAIL",
              "ok": all(r["ok"] for r in results), "results": results}
    print(json.dumps(report, indent=1))
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Azazael antibody shards")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--seek", action="store_true")
    ap.add_argument("--no-record", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--promote", nargs=2, metavar=("NAME", "STATUS"),
                    help="advance an antibody (evidence-gated)")
    args = ap.parse_args(argv)

    if args.list:
        print(json.dumps(
            {"antibodies": list(_antibody_specs()),
             "shard": "antibodies",
             "specs": _antibody_specs()}, indent=1))
        return 0
    if args.seek:
        return 0 if seek_all(record=not args.no_record)["ok"] else 1
    if args.status:
        print(json.dumps(antibody_status(), indent=1))
        return 0
    if args.promote:
        res = promote_antibody(args.promote[0], args.promote[1])
        print(json.dumps(res, indent=1))
        return 0 if res["ok"] else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
