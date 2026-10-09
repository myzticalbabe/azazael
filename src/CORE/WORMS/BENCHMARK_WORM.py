# coding: utf-8
"""BENCHMARK_WORM — Performance Benchmarking Worm"""

from __future__ import annotations
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

__all__ = ['BenchmarkWorm']

try:
    from CORE.worm_registry import register_worm
except ImportError:
    note_failure("BENCHMARK_WORM:L10", None)
    def register_worm(**kw):
        return lambda cls: cls


@register_worm(
    category="telemetry",
    priority=4,
    cooldown_seconds=300.0,
    description="Performance benchmark worm — runs system and worm benchmarks",
)
class BenchmarkWorm:
    """Performance Benchmark Worm — measures system and worm performance."""

    VERSION = "1.0.0"

    def __init__(self):
        self._results: list = []

    def get_summary(self):
        return {"status": "ok", "worm": "BenchmarkWorm"}
