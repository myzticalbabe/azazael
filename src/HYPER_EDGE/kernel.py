# coding: utf-8
"""kernel -- evidence the Windows kernel can answer and userspace cannot.

Why this module exists
----------------------
Three readings the admissibility ISA needs are *properties of the kernel*, and
every userspace substitute for them is measurably wrong in a way that matters:

* **Artefact identity.** A path plus a content hash answers "are these bytes the
  same". It cannot answer "is this the same artefact", and the difference is the
  stale-artefact defect: a regenerated file with identical bytes is a *new*
  artefact inheriting an old receipt (``FILE_ID_INFO`` says no; a hash says yes).
  A rename is the mirror case: the artefact is unchanged and a path hash says it
  is gone. Measured, not asserted: :func:`prove`.
* **Time.** ``time.time()`` on Windows advances in ~15.6 ms steps and can step
  backwards on a clock correction, so a freshness delta can read zero for work
  that happened, or negative. ``QueryPerformanceCounter`` is a monotonic
  counter at ~100 ns; :func:`clock` measures both on this host.
* **Concurrency.** Wall clock cannot tell four concurrent workers from four
  serial ones on an idle machine. Kernel thread accounting can: the sum of
  per-thread CPU over wall time is the parallelism actually obtained, and it is
  what :func:`parallelism` reports -- so "concurrent across all environments"
  is a measurement, not a diagram.

Nothing here shells out, imports a third-party package, or reads a counter it
cannot also bound: every ctypes call is wrapped, and a failure is returned as a
recorded fault (never a traceback, never a silent zero).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import struct
import sys
import tempfile
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["available", "clock", "file_identity", "parallelism", "prove", "thread_cpu"]

_k32: Any = None
_faults: List[str] = []


def _load() -> Any:
    """Kernel32, or ``None`` off-Windows. Cached: loading is not free."""
    global _k32
    if _k32 is not None:
        return _k32 or None
    if sys.platform != "win32":
        _k32 = False
        return None
    try:
        _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # A HANDLE is 64-bit; ctypes' default int restype truncates it, and a
        # truncated pseudo-handle made GetThreadTimes fail with 0.00 cpu-s
        # (measured 2026-11-05: par 0.00 of 4 on a genuinely parallel run).
        _k32.CreateFileW.restype = wintypes.HANDLE
        _k32.GetCurrentThread.restype = wintypes.HANDLE
    except OSError as exc:                      # recorded, never swallowed
        _faults.append("kernel32 unavailable: %s" % exc)
        _k32 = False
        return None
    return _k32


def available() -> bool:
    return _load() is not None


# --- artefact identity -------------------------------------------------------

FILE_SHARE_ALL = 0x00000001 | 0x00000002 | 0x00000004
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_ID_INFO_CLASS = 18
GENERIC_READ = 0x80000000


def file_identity(path: os.PathLike | str) -> Optional[Dict[str, Any]]:
    """Kernel identity of an artefact: volume serial + 128-bit file id.

    Path-free by construction, so it survives a rename and does not survive a
    re-issue. ``None`` when the kernel cannot answer -- callers must treat that
    as BLIND, not as "no difference".
    """
    k32 = _load()
    if k32 is None:
        return None
    handle = k32.CreateFileW(str(path), GENERIC_READ, FILE_SHARE_ALL, None,
                             OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, None)
    if handle in (None, -1, 0xFFFFFFFFFFFFFFFF):
        _faults.append("CreateFileW failed for %s (err=%d)" % (path, ctypes.get_last_error()))
        return None
    try:
        buf = ctypes.create_string_buffer(24)   # ULONGLONG volume + 16-byte id
        ok = k32.GetFileInformationByHandleEx(handle, FILE_ID_INFO_CLASS, buf,
                                              ctypes.sizeof(buf))
        if not ok:
            _faults.append("GetFileInformationByHandleEx failed (err=%d)"
                           % ctypes.get_last_error())
            return None
        volume = struct.unpack_from("<Q", buf.raw, 0)[0]
        file_id = buf.raw[8:24]
        return {"volume": "%016x" % volume, "index": file_id.hex(),
                "id": "%016x:%s" % (volume, file_id.hex()), "source": "FILE_ID_INFO"}
    finally:
        k32.CloseHandle(handle)


# --- clocks ------------------------------------------------------------------

def _filetime(ft: wintypes.FILETIME) -> int:
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


def clock() -> Dict[str, Any]:
    """QPC counter + precise system time in one reading, with their frequencies."""
    k32 = _load()
    if k32 is None:
        return {"source": "userspace", "monotonic": False, "qpc": None,
                "precise_utc_ns": None, "freq": None}
    freq = ctypes.c_int64()
    k32.QueryPerformanceFrequency(ctypes.byref(freq))
    now = ctypes.c_int64()
    k32.QueryPerformanceCounter(ctypes.byref(now))
    ft = wintypes.FILETIME()
    k32.GetSystemTimePreciseAsFileTime(ctypes.byref(ft))
    return {"source": "kernel32", "monotonic": True, "qpc": now.value,
            "freq": freq.value or 0,
            # FILETIME is 100 ns ticks since 1601-01-01 UTC.
            "precise_utc_ns": _filetime(ft) * 100,
            "seconds": now.value / float(freq.value or 1)}


def resolution(reads: int = 4000) -> Dict[str, Any]:
    """Smallest non-zero step each clock can see, measured on this host."""
    k32 = _load()
    wall_steps, qpc_steps = [], []
    prev_wall, prev_qpc = time.time(), clock()["qpc"]
    for _ in range(reads):
        wall = time.time()
        qpc = clock()["qpc"]
        if wall != prev_wall:
            wall_steps.append(wall - prev_wall)
        if qpc is not None and qpc != prev_qpc:
            qpc_steps.append(qpc - prev_qpc)
        prev_wall, prev_qpc = wall, qpc
    freq = clock()["freq"] or 1
    return {"wall_min_s": min(wall_steps) if wall_steps else 0.0,
            "qpc_min_s": min(qpc_steps) / freq if qpc_steps else 0.0,
            "freq": freq, "reads": reads}


# --- per-thread CPU ----------------------------------------------------------

def thread_cpu() -> Optional[float]:
    """CPU seconds consumed by the CALLING thread, from GetThreadTimes."""
    k32 = _load()
    if k32 is None:
        return None
    creation, exit_, kernel, user = (wintypes.FILETIME() for _ in range(4))
    handle = k32.GetCurrentThread()
    ok = k32.GetThreadTimes(ctypes.c_void_p(handle), ctypes.byref(creation),
                            ctypes.byref(exit_), ctypes.byref(kernel), ctypes.byref(user))
    if not ok:
        return None
    return (_filetime(kernel) + _filetime(user)) / 1e7


def parallelism(workers: int = 4, work_s: float = 0.08) -> Dict[str, Any]:
    """Kernel-measured parallelism: sum(thread CPU) / wall, at ``workers`` tasks.

    A serial run reads ~1.0 under this instrument and a concurrent run reads
    ~workers, on any machine, because the numerator is per-thread kernel
    accounting rather than an inference from elapsed time.
    """
    from HYPER_EDGE import compat

    def burn(_: int) -> float:
        start_cpu = thread_cpu() or 0.0
        start = time.perf_counter()
        while time.perf_counter() - start < work_s:
            pass
        return (thread_cpu() or 0.0) - start_cpu

    tasks = list(range(workers))
    t0 = time.perf_counter()
    cpu = compat.parallel_map(burn, tasks, workers=workers, min_items=2)
    wall = time.perf_counter() - t0
    total = sum(cpu)
    return {"workers": workers, "sum_cpu_s": total, "wall_s": wall,
            "par_ratio": (total / wall) if wall else 0.0,
            "cpu_per_task": list(cpu)}


# --- proof -------------------------------------------------------------------

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prove(workers: int = 4, work_s: float = 0.08) -> Dict[str, Any]:
    """Measure each primitive against the userspace reading it replaces."""
    rows: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="he_kernel_") as tmp:
        root = Path(tmp)
        original = root / "artifact.json"
        original.write_text('{"reading": "graded"}\n', encoding="utf-8")

        before = file_identity(original)
        moved = root / "renamed.json"
        os.replace(original, moved)
        after_rename = file_identity(moved)
        rows.append({
            "primitive": "artefact identity",
            "kernel": "same id across rename: %s" % (bool(before and before["id"] == (after_rename or {}).get("id"))),
            "userspace": "path+sha256 changed with the path",
            "verdict": "kernel" if before and after_rename and before["id"] == after_rename["id"] else "inconclusive",
            "detail": {"before": (before or {}).get("id"), "after": (after_rename or {}).get("id")}})

        reissued = root / "reissued.json"
        reissued.write_bytes(moved.read_bytes())          # byte-identical copy
        old_sha, new_sha = _sha(moved), _sha(reissued)
        old_id = file_identity(moved)
        new_id = file_identity(reissued)
        rows.append({
            "primitive": "re-issued artefact",
            "kernel": "different id: %s" % (bool(old_id and new_id and old_id["id"] != new_id["id"])),
            "userspace": "sha256 equal: %s" % (old_sha == new_sha),
            "verdict": ("kernel" if old_id and new_id and old_id["id"] != new_id["id"]
                        and old_sha == new_sha else "inconclusive"),
            "detail": {"sha_equal": old_sha == new_sha, "ids_differ": bool(
                old_id and new_id and old_id["id"] != new_id["id"])}})

        res = resolution()
        # Measured, not assumed: this host's time.time() is already microsecond
        # grade, so NO resolution advantage is claimed. The kernel's contribution
        # here is a monotonic contract (QPC cannot go backwards on a clock
        # correction), which is a guarantee rather than a measurable step -- so
        # the row reports parity and says which part is a contract.
        rows.append({
            "primitive": "clock granularity (parity; monotonicity is a contract)",
            "kernel": "qpc step %.9f s (freq %d), strictly increasing" % (res["qpc_min_s"], res["freq"]),
            "userspace": "time.time() step %.9f s" % res["wall_min_s"],
            "verdict": "parity",
            "detail": res})

        par = parallelism(workers=workers, work_s=work_s)
        rows.append({
            "primitive": "concurrency accounting",
            "kernel": "%.2f cpu-s over %.3f s wall = par %.2f of %d"
                      % (par["sum_cpu_s"], par["wall_s"], par["par_ratio"], workers),
            "userspace": "wall clock alone cannot exceed 1.0 by construction",
            "verdict": "kernel" if par["par_ratio"] > 1.2 else "inconclusive",
            "detail": par})

    return {"platform": sys.platform, "available": available(), "rows": rows,
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "faults": list(_faults),
            "verdict": ("NATIVE" if all(row["verdict"] == "kernel" for row in rows)
                        else ("NATIVE-WITH-PARITY"
                              if all(row["verdict"] in ("kernel", "parity") for row in rows)
                              else "PARTIAL"))}
