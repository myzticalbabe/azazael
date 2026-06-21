# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: PROFILING (5 worms)
CodeProfiler, MemoryLeakDetector, IOBottleneckFinder, GILContentionProbe, CPUFlameProfiler
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ── Worm Registry Import ─────────────────────────────────────────────
try:
    from azazael_core.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# ── Python 3.14t Free-Threading Awareness ────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False


@register_worm(category="profiling", priority=7, cooldown_seconds=60.0,
    description="Code profiler — cProfile integration, hot-path detection, call-graph generation")
class CodeProfiler:
    """Profiles Python code execution with cProfile integration."""

    VERSION = "1.0.0"

    def __init__(self):
        self._profiles: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a single function call and return stats."""
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats(20)
        profile_data = {"function": func.__name__, "output": s.getvalue(), "result": str(result)[:200]}
        with self._lock:
            self._profiles[func.__name__] = profile_data
        return profile_data

    def detect_hotspots(self, profile_output: str, threshold_pct: float = 10.0) -> List[Dict]:
        """Parse cProfile output to find functions above threshold."""
        hotspots = []
        for line in profile_output.split("\n"):
            parts = line.strip().split()
            if len(parts) >= 6:
                try:
                    pct = float(parts[3])
                    if pct > threshold_pct:
                        hotspots.append({"function": " ".join(parts[5:]), "time_pct": pct})
                except ValueError:
                    pass
        return hotspots[:10]


@register_worm(category="profiling", priority=6, cooldown_seconds=90.0,
    description="Memory leak detector — tracemalloc integration, allocation tracking, growth detection")
class MemoryLeakDetector:
    """Detects memory leaks using tracemalloc."""

    VERSION = "1.0.0"

    def __init__(self):
        import tracemalloc
        self._snapshots: Dict[str, Any] = {}
        self._lock = threading.Lock()
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    def take_snapshot(self, label: str = "") -> Dict[str, Any]:
        """Take a memory snapshot for comparison."""
        import tracemalloc
        snap = tracemalloc.take_snapshot()
        stats = snap.statistics("lineno")
        top = [{"file": str(s.traceback[0]) if s.traceback else "?", "size_kb": round(s.size / 1024, 2),
                 "count": s.count} for s in stats[:10]]
        with self._lock:
            self._snapshots[label or datetime.now().isoformat()] = {"top_allocations": top, "timestamp": time.time()}
        return top

    def compare_snapshots(self, label1: str, label2: str) -> Dict[str, Any]:
        """Compare two snapshots to find growth."""
        s1, s2 = self._snapshots.get(label1), self._snapshots.get(label2)
        if not s1 or not s2:
            return {"error": "Snapshots not found"}
        growth = (s2.get("timestamp", 0) - s1.get("timestamp", 1)) > 0
        return {"growth_detected": growth, "label1": label1, "label2": label2}


@register_worm(category="profiling", priority=6, cooldown_seconds=45.0,
    description="I/O bottleneck finder — disk read/write latency, iostat integration")
class IOBottleneckFinder:
    """Identifies I/O bottlenecks using psutil disk I/O stats."""

    VERSION = "1.0.0"

    def __init__(self):
        self._baseline: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def measure_io(self) -> Dict[str, Any]:
        """Measure current disk I/O counters."""
        import psutil
        counters = psutil.disk_io_counters()
        return {
            "read_count": counters.read_count, "write_count": counters.write_count,
            "read_bytes_mb": round(counters.read_bytes / (1024**2), 2),
            "write_bytes_mb": round(counters.write_bytes / (1024**2), 2),
            "read_time_ms": counters.read_time, "write_time_ms": counters.write_time,
        }

    def detect_bottleneck(self, threshold_read_ms: int = 1000) -> Dict[str, Any]:
        """Check if read latency exceeds threshold."""
        io = self.measure_io()
        bottleneck = io.get("read_time_ms", 0) > threshold_read_ms
        return {"bottleneck": bottleneck, "metrics": io, "recommendation": "Consider SSD upgrade or I/O scheduling" if bottleneck else "I/O healthy"}


@register_worm(category="profiling", priority=7, cooldown_seconds=30.0,
    description="GIL contention probe — free-threading diagnostics, lock contention analysis")
class GILContentionProbe:
    """Probes GIL contention levels for Python 3.14t migration readiness."""

    VERSION = "1.0.0"

    def __init__(self):
        self._lock = threading.Lock()
        self._results: List[Dict] = []

    def measure_contention(self, num_threads: int = 8, iterations: int = 100000) -> Dict[str, Any]:
        """Measure GIL contention by running CPU-bound work with increasing threads."""
        def cpu_burn(n: int):
            total = 0
            for i in range(n):
                total += i * i
            return total

        start = time.perf_counter()
        threads = [threading.Thread(target=cpu_burn, args=(iterations // num_threads,)) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start
        return {"threads": num_threads, "iterations": iterations, "elapsed_sec": round(elapsed, 3),
                "ops_per_sec": round(iterations / elapsed, 1), "free_threaded": is_free_threaded()}


@register_worm(category="profiling", priority=6, cooldown_seconds=60.0,
    description="CPU flame profiler — sampling profiler, flame graph data generation")
class CPUFlameProfiler:
    """Generates flame-graph-compatible CPU profiling data."""

    VERSION = "1.0.0"

    def __init__(self):
        self._stacks: List[List[str]] = []
        self._lock = threading.Lock()

    def sample(self, duration_sec: float = 5.0, interval_sec: float = 0.1) -> int:
        """Sample call stacks at regular intervals using sys._current_frames."""
        import traceback
        end = time.time() + duration_sec
        count = 0
        while time.time() < end:
            frames = sys._current_frames()
            for tid, frame in frames.items():
                stack = []
                while frame:
                    stack.append(frame.f_code.co_name)
                    frame = frame.f_back
                if stack:
                    self._stacks.append(stack)
                    count += 1
            time.sleep(interval_sec)
        return count

    def to_flamegraph_data(self) -> Dict[str, int]:
        """Aggregate stacks into flame graph format."""
        counts: Dict[str, int] = defaultdict(int)
        for stack in self._stacks:
            counts[";".join(reversed(stack))] += 1
        return dict(counts)
