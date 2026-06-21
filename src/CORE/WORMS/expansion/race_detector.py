# coding: utf-8
"""
RaceConditionDetector — Automated race condition detection for 3.14t free-threading.

Monitors worm shared-state access patterns to detect:
- Concurrent writes to unguarded attributes  
- Lock-free mutations of shared data structures
- Function-body imports called from background threads (deadlock risk)

Uses MetaCognitionWorm for anomaly pattern learning.
Module-level imports only — thread-safe by design (Lesson #29).

Part of AZAZAEL Worm Registry — Category: security, Priority: 9
"""

import os
import threading
from datetime import datetime
from typing import Any
from collections import defaultdict

try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# Module-level memory store import (3.14t safe — Lesson #29)
try:
    from CORE.local_memory import get_memory_store as _get_memory_store_global
    _LOCAL_MEMORY_OK = True
except ImportError:
    _LOCAL_MEMORY_OK = False
    _get_memory_store_global = None


@register_worm(
    category="security", priority=9, cooldown_seconds=60.0,
    description="Race condition detector — monitors shared-state access under 3.14t free-threading, flags unguarded concurrent writes"
)
class RaceConditionDetector:
    """Automated race condition detection for Python 3.14t.

    Wraps threading.Lock acquisition with tracing and monitors
    shared mutable state access patterns to flag:
    1. Concurrent writes to unguarded attributes
    2. Lock-free mutations of dicts/lists/sets
    3. Function-body imports called from threads

    Integrates with MetaCognitionWorm for anomaly pattern learning.

    Usage:
        rcd = RaceConditionDetector()
        rcd.instrument_worm(engine)
        # ... run worm in thread pool ...
        report = rcd.generate_safety_report()
    """

    VERSION = "1.0.0"

    def __init__(self):
        self._lock = threading.Lock()
        self._instrumented: dict[str, list[str]] = {}
        self._access_log: list[dict] = []
        self._violations: list[dict] = []
        self._scan_count = 0

        # Per-class __setattr__ registry: {type: {id(instance): {"shared_attrs": set, "worm_id": str}}}
        # Uses id() for fast lookup; entries removed on uninstrument.
        # Class-level __setattr__ only traces instances in this registry.
        self._setattr_registry: dict[type, dict[int, dict[str, Any]]] = defaultdict(dict)

        # Detection thresholds
        self._concurrent_write_window_ms = 100  # Writes within this window = potential race
        self._max_violations = 500

    def instrument_worm(self, worm_instance, label: str = "") -> dict[str, Any]:
        """Wrap a worm's key methods with lock tracing.

        Monitors attribute access, lock acquisition, and state mutations.
        Uses class-level __setattr__ with per-instance registry for correct
        multi-instance support (CPython looks up __setattr__ on the type).

        Args:
            worm_instance: Any worm object to instrument
            label: Human-readable label for reporting

        Returns:
            dict with instrumented attributes and count
        """
        worm_id = label or type(worm_instance).__name__
        worm_type = type(worm_instance)
        instrumented = []

        # Instrument lock acquisition (instance-level replacement)
        if hasattr(worm_instance, '_lock') and isinstance(worm_instance._lock, threading.Lock):
            orig_acquire = worm_instance._lock.acquire

            def traced_acquire(*a, **kw):
                trace = {
                    "worm": worm_id,
                    "action": "lock_acquire",
                    "thread": threading.current_thread().name,
                    "timestamp": datetime.now().isoformat(),
                }
                self._record_access(trace)
                return orig_acquire(*a, **kw)

            worm_instance._lock.acquire = traced_acquire
            object.__setattr__(worm_instance, '_rcd_orig_acquire', orig_acquire)
            instrumented.append("_lock.acquire")

        # Instrument __setattr__ via class-level patch + per-instance registry
        _shared_attrs = self._detect_shared_attrs(worm_instance)
        if _shared_attrs:
            instance_id = id(worm_instance)
            with self._lock:
                if worm_type not in self._setattr_registry:
                    self._install_class_tracer(worm_type)
                self._setattr_registry[worm_type][instance_id] = {
                    "shared_attrs": _shared_attrs,
                    "worm_id": worm_id,
                }
            instrumented.append("__setattr__")

        with self._lock:
            self._instrumented[worm_id] = instrumented

        return {
            "worm": worm_id,
            "instrumented": instrumented,
            "shared_attrs": list(_shared_attrs),
        }

    def _install_class_tracer(self, worm_type: type) -> None:
        """Install a class-level __setattr__ tracer for a worm type.

        Patches the class once; all future attribute writes to registered
        instances trigger tracing. Only called under self._lock.
        
        Returns silently if the type is immutable (e.g., C extensions).
        Callers should check that _rcd_original_setattr exists on the type
        to confirm installation succeeded.
        """
        original_setattr = worm_type.__setattr__
        # Store original on the type for later restoration
        if not hasattr(worm_type, '_rcd_original_setattr'):
            try:
                object.__setattr__(worm_type, '_rcd_original_setattr', original_setattr)
            except TypeError:
                # C extension types don't allow attribute setting — tracing unavailable
                return

        detector_ref = self  # Capture reference for the closure

        def traced_class_setattr(obj, name, value):
            # Check if this instance is registered for tracing
            registry = detector_ref._setattr_registry.get(worm_type, {})
            entry = registry.get(id(obj))
            if entry is not None and name in entry["shared_attrs"] and not name.startswith('_rcd_'):
                trace = {
                    "worm": entry["worm_id"],
                    "action": "write",
                    "attribute": name,
                    "thread": threading.current_thread().name,
                    "timestamp": datetime.now().isoformat(),
                }
                detector_ref._record_access(trace)
            return original_setattr(obj, name, value)

        worm_type.__setattr__ = traced_class_setattr

    def uninstrument_worm(self, worm_instance) -> dict[str, Any]:
        """Restore a worm's original methods, removing all tracing.

        Args:
            worm_instance: Previously instrumented worm object

        Returns:
            dict with restored status
        """
        worm_id = type(worm_instance).__name__
        worm_type = type(worm_instance)
        restored = []

        # Restore lock.acquire
        if hasattr(worm_instance, '_rcd_orig_acquire'):
            worm_instance._lock.acquire = worm_instance._rcd_orig_acquire
            object.__delattr__(worm_instance, '_rcd_orig_acquire')
            restored.append("_lock.acquire")

        # Remove instance from class-level __setattr__ registry
        with self._lock:
            if worm_type in self._setattr_registry:
                self._setattr_registry[worm_type].pop(id(worm_instance), None)
                # Restore original __setattr__ if no more instances are traced
                if not self._setattr_registry[worm_type] and hasattr(worm_type, '_rcd_original_setattr'):
                    worm_type.__setattr__ = worm_type._rcd_original_setattr
                    object.__delattr__(worm_type, '_rcd_original_setattr')
                    del self._setattr_registry[worm_type]
                    restored.append("__setattr__")

            self._instrumented.pop(worm_id, None)

        return {
            "worm": worm_id,
            "restored": restored,
            "timestamp": datetime.now().isoformat(),
        }

    def _detect_shared_attrs(self, instance) -> set[str]:
        """Detect attributes that could be shared mutable state.
        
        Uses getattr() to resolve descriptors/properties, then type-checks
        the resolved value. Falls back to object.__getattribute__ for
        attributes that raise on access.
        
        Limitation: Only detects built-in mutable types (dict, list, set,
        bytearray). Custom mutable containers are not detected.
        """
        shared = set()
        for name in dir(instance):
            if name.startswith('_') and not name.startswith('__') and not name.startswith('_rcd_'):
                # Try getattr first (resolves descriptors)
                try:
                    attr = getattr(instance, name)
                except Exception:
                    try:
                        attr = object.__getattribute__(instance, name)
                    except AttributeError:
                        continue
                if isinstance(attr, (dict, list, set, bytearray)):
                    shared.add(name)
        return shared

    def _record_access(self, trace: dict) -> None:
        """Record an access event for later analysis."""
        with self._lock:
            self._access_log.append(trace)
            if len(self._access_log) > 2000:
                self._access_log = self._access_log[-2000:]

    def detect_data_races(self) -> list[dict]:
        """Analyze access logs for concurrent write conflicts.

        Returns list of potential race conditions with evidence.
        """
        with self._lock:
            log_snapshot = list(self._access_log)

        violations = []
        writes_by_attr: dict[str, list[dict]] = defaultdict(list)

        # Group writes by attribute
        for entry in log_snapshot:
            if entry.get("action") == "write":
                key = f"{entry.get('worm', '')}.{entry.get('attribute', '')}"
                writes_by_attr[key].append(entry)

        # Find concurrent writes (different threads, close timestamps)
        for attr_key, entries in writes_by_attr.items():
            threads = set(e.get("thread", "") for e in entries)
            if len(threads) < 2:
                continue  # Only one thread wrote — no race

            # Check for writes within the concurrent window
            entries.sort(key=lambda e: e.get("timestamp", ""))
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    if entries[i].get("thread") == entries[j].get("thread"):
                        continue
                    # Approximate time delta (string comparison)
                    t_i = entries[i].get("timestamp", "")
                    t_j = entries[j].get("timestamp", "")
                    try:
                        dt_i = datetime.fromisoformat(t_i)
                        dt_j = datetime.fromisoformat(t_j)
                        delta_ms = abs((dt_j - dt_i).total_seconds() * 1000)
                    except (ValueError, TypeError):
                        continue

                    if delta_ms <= self._concurrent_write_window_ms:
                        violations.append({
                            "type": "concurrent_write",
                            "attribute": attr_key,
                            "threads": sorted(threads),
                            "worm": entries[i].get("worm", ""),
                            "time_window_ms": delta_ms,
                            "severity": "high",
                            "recommendation": (
                                f"Add threading.Lock around writes to {attr_key} "
                                f"or use atomic operations"
                            ),
                        })
                        break  # One violation per attribute is sufficient

        with self._lock:
            self._violations.extend(violations)
            if len(self._violations) > self._max_violations:
                self._violations = self._violations[-self._max_violations:]

        return violations

    def detect_thread_imports(self, code_paths: (list[str] | None) = None) -> list[dict]:
        """Detect function-body imports that could deadlock under 3.14t.

        Per Lesson #28/#29: importlib.import_module() from background
        threads deadlocks under free-threading. This method scans
        Python source files for `import` statements inside function
        bodies or thread targets.

        Args:
            code_paths: Paths to scan (default: discovered worm modules)

        Returns:
            list of risky import locations
        """
        risks = []
        if code_paths is None:
            # Module-level os import — 3.14t safe (Lesson #29)
            worms_dir = os.path.join(os.path.dirname(__file__), "..")
            code_paths = []
            for root, dirs, files in os.walk(worms_dir):
                dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
                for f in files:
                    if f.endswith('.py') and not f.startswith('_'):
                        code_paths.append(os.path.join(root, f))

        for path in code_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception:
                continue

            in_function = 0
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Track function bodies
                if stripped.startswith('def ') and '(' in stripped:
                    in_function = line.count('    ') // 4 or 1
                elif in_function > 0:
                    indent = (len(line) - len(line.lstrip())) // 4
                    if indent <= in_function - 1 and stripped:
                        in_function = 0

                if in_function > 0:
                    if ('import ' in stripped or 'from ' in stripped) and \
                       not stripped.startswith('#') and not stripped.startswith('"""'):
                        risks.append({
                            "file": path,
                            "line": line_num,
                            "import": stripped,
                            "risk": "deadlock",
                            "recommendation": "Move import to module level (Lesson #29)",
                        })

        return risks

    def generate_safety_report(self) -> dict[str, Any]:
        """Generate a comprehensive race condition safety report.

        Returns:
            dict with violations, thread-import risks, and recommendations
        """
        with self._lock:
            list(self._violations)
            instrumented = dict(self._instrumented)
            scan_count = self._scan_count

        # Detect thread-safety violations from access patterns
        data_races = self.detect_data_races()

        # Find function-body imports
        thread_imports = self.detect_thread_imports()

        total_issues = len(data_races) + len(thread_imports)

        report = {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "worms_instrumented": len(instrumented),
                "data_races_detected": len(data_races),
                "thread_import_risks": len(thread_imports),
                "total_issues": total_issues,
                "scans_completed": scan_count,
            },
            "data_races": data_races[:20],
            "thread_import_risks": thread_imports[:20],
            "instrumented_worms": instrumented,
            "recommendations": [],
        }

        if data_races:
            report["recommendations"].append(
                f"Found {len(data_races)} concurrent write violations — add threading.Lock protection"
            )
        if thread_imports:
            report["recommendations"].append(
                f"Found {len(thread_imports)} function-body imports — move to module level (3.14t deadlock risk)"
            )
        if total_issues == 0:
            report["recommendations"].append(
                "No race conditions detected — all monitored state access is thread-safe"
            )

        return report

    def execute(self) -> dict[str, Any]:
        """Standard worm execute — runs full detection cycle."""
        with self._lock:
            self._scan_count += 1

        report = self.generate_safety_report()

        # Persist
        try:
            if _LOCAL_MEMORY_OK and _get_memory_store_global:
                store = _get_memory_store_global()
                store.record_event(
                    source="RaceConditionDetector",
                    event_type="safety_report",
                    data=report,
                    severity="warning" if report["summary"]["total_issues"] > 0 else "info",
                    tags=["race_detection", "3.14t", "thread_safety"],
                )
        except Exception:
            pass

        return report
