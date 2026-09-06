# coding: utf-8
"""


__all__ = [
    "cache_status",
    "ensure_registry_warm",
    "get_registry_validation",
    "registry_importability_by_category",
    "warm_caches_background",
    "warm_caches_blocking",
    "warm_caches_now",
    "warm_caches_ready",
]

startup_warm.py — Pre-warm caches and lazy init at system startup.

Prevents the 38-45s discover_worms() cold start from blocking session
recording or other time-sensitive operations (Error #57 permanent fix).

The worm registry cache is warmed in a background daemon thread so that
the first session recording call finds a ready cache in <0.1s.

Usage:
    # At the top of your startup script or entry point:
    from CORE.startup_warm import warm_caches_background

    # Non-blocking: returns immediately, cache warms in background
    warm_caches_background()

    # Or block until ready (for startup where you have time):
    # from CORE.startup_warm import warm_caches_blocking
    # warm_caches_blocking(timeout=60)

Created: June 11, 2026 — Error #57 permanent fix
"""

import sys
import time
import logging
import threading
from pathlib import Path
from typing import Callable

_log = logging.getLogger("startup_warm")


# ── Lazy cache warm (background thread, non-blocking) ──────────────

_warmed = threading.Event()
_warm_thread: (threading.Thread | None) = None
_warm_lock = threading.Lock()  # Guard for thread creation race
_last_warm_time: (float | None) = None  # time.monotonic() when warm completed

# Registry importability validation result (filled once after warm).
_registry_validation: (dict | None) = None
_validation_lock = threading.Lock()


def _run_registry_validation():
    """Validate all registered worms are importable, auto-repairing failures.

    Runs after registry warm so that every module is already imported in this
    process (imports resolve via sys.modules — no cold-start cost). If broken
    entries are found (typically a stale pickle cache after module renames),
    re-runs discover_worms() to rebuild from current source, then re-validates.
    Always non-fatal: startup must not block on a broken worm.

    Stored result keys:
        repair_attempted: bool       — whether a repair was attempted
        repaired: int                — broken entries fixed by re-discovery
        repair_still_broken: list    — broken entries that remain after repair
    """
    global _registry_validation
    try:
        from CORE.worm_registry import repair_registry, validate_registry_importable
        try:
            result = validate_registry_importable()
        except Exception:
            result = {"valid": True, "total": 0, "checked": 0, "broken": []}

        if result.get("broken"):
            _log.warning(
                "Registry validation: %d/%d worms not importable; attempting repair",
                len(result.get("broken") or []), result.get("total", 0),
            )
            try:
                repair = repair_registry()
                result["repair_attempted"] = repair.get("attempt", False)
                result["repaired"] = repair.get("repaired", 0)
                result["repair_still_broken"] = repair.get("still_broken") or []
                if repair.get("valid"):
                    result["valid"] = True
                    result["broken"] = []
                    for k in ("total", "checked"):
                        if k in repair:
                            result[k] = repair[k]
                    _log.info("...re-discovery repaired %d broken registry entries",
                              repair.get("repaired", 0))
                else:
                    _log.warning(
                        "...%d registry entries still not importable after repair",
                        len(repair.get("still_broken") or []),
                    )
            except Exception as rexc:
                _log.warning("Registry auto-repair failed (non-fatal): %s", rexc)

        with _validation_lock:
            _registry_validation = result
    except Exception as exc:
        _log.warning("Registry validation failed (non-fatal): %s", exc)


def get_registry_validation() -> (dict | None):
    """Return the last registry importability validation result (or None)."""
    with _validation_lock:
        return _registry_validation


def _warm_worker(on_complete: (Callable | None) = None):
    """Background worker: pre-warms the worm registry cache.

    Runs discover_worms() which checks the pickle cache first.
    - If cache is fresh: returns in <0.1s, no-op.
    - If cache is stale/missing: runs full discovery (38-45s) and saves cache.
    """
    try:
        # Ensure src directory is on sys.path
        src_dir = str(Path(__file__).resolve().parent.parent)
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        # Import and run registry discovery (uses cache internally)
        from CORE.worm_registry import discover_worms

        start = time.time()
        count = discover_worms()
        elapsed = time.time() - start

        if elapsed > 1.0:
            _log.info(
                "Cache warm completed in %.1fs (discovered %d worms)",
                elapsed, count,
            )
        else:
            _log.debug("Cache warm: ready in %.2fs (cache hit)", elapsed)

    except Exception as exc:
        _log.warning("Cache warm failed (non-fatal): %s", exc)
    finally:
        global _last_warm_time
        _last_warm_time = time.monotonic()
        _warmed.set()
        _run_registry_validation()
        if on_complete:
            try:
                on_complete()
            except Exception:
                pass


def warm_caches_background(on_complete: (Callable | None) = None) -> threading.Thread:
    """Start cache warming in a background daemon thread. Non-blocking.

    Thread-safe: uses a lock to prevent duplicate warm threads.
    Safe to call multiple times — only one warm thread is started.
    Call warm_caches_ready() later to check if warming completed.

    Args:
        on_complete: Optional callback invoked when warming finishes
            (called from the background thread).

    Returns:
        The background threading.Thread instance.
    """
    global _warm_thread

    if _warmed.is_set():
        _log.debug("Caches already warm, skipping background warm")
        return _warm_thread

    with _warm_lock:
        if _warmed.is_set():
            return _warm_thread
        if _warm_thread is not None and _warm_thread.is_alive():
            _log.debug("Cache warm already in progress")
            return _warm_thread

        _warm_thread = threading.Thread(
            target=_warm_worker,
            args=(on_complete,),
            name="cache-warm",
            daemon=True,
        )
        _warm_thread.start()
        _log.debug("Cache warm started in background thread")
        return _warm_thread


def warm_caches_blocking(timeout: float = 60.0) -> bool:
    """Warm caches in foreground, blocking until ready or timeout.

    Args:
        timeout: Max seconds to wait for warm completion. Default 60.

    Returns:
        True if caches are ready, False if timeout or failure.
    """
    global _warm_thread

    if _warmed.is_set():
        return True

    if _warm_thread is None or not _warm_thread.is_alive():
        # No thread running — start one synchronously
        _warm_worker()
        return _warmed.is_set()

    # Wait for existing thread
    return _warmed.wait(timeout=timeout)


def warm_caches_ready() -> bool:
    """Check if cache warming has completed.

    Returns:
        True if warming finished (or was already done).
    """
    return _warmed.is_set()


def warm_caches_now() -> bool:
    """Force immediate synchronous cache warm. Blocks until done.

    Unlike warm_caches_blocking(), this ALWAYS runs a fresh warm
    regardless of previous thread state. Useful after cache invalidation.

    Returns:
        True if warming succeeded.
    """
    global _warmed, _warm_thread

    _warmed.clear()
    _warm_worker()
    return _warmed.is_set()


# ── DirectMemory short-circuit guard ────────────────────────────────

# DirectMemory's session recording should NOT trigger discover_worms().
# This flag lets DirectMemory check if the registry is ready without
# blocking on a cold start. DirectMemory should import this module and
# check warm_caches_ready() before attempting registry-dependent ops.

def cache_status() -> dict:
    """Report the current state of the cache warm system.

    Returns a dict with:
        - ready (bool): Whether warming has completed.
        - registry_size (int): Number of worms in WORM_REGISTRY (0 if not warm).
        - last_warm_time_ago (float or None): Seconds since last warm completed,
          or None if never warmed.
        - thread_alive (bool): Whether the warm thread is currently running.

    This is a diagnostic/convenience function. No blocking — returns
    immediately with whatever state is currently available.
    """
    ready = _warmed.is_set()
    registry_size = 0
    last_warm_ago = None

    if ready:
        try:
            from CORE.worm_registry import WORM_REGISTRY
            registry_size = sum(len(v) for v in WORM_REGISTRY.values()) if WORM_REGISTRY else 0
        except (ImportError, AttributeError):
            pass

    if _last_warm_time is not None:
        last_warm_ago = time.monotonic() - _last_warm_time

    thread_alive = _warm_thread is not None and _warm_thread.is_alive()

    validation = get_registry_validation()
    by_category = registry_importability_by_category(validation)

    return {
        "ready": ready,
        "registry_size": registry_size,
        "last_warm_time_ago": last_warm_ago,
        "thread_alive": thread_alive,
        "registry_valid": bool(validation and validation.get("valid")),
        "registry_validation": validation,
        "registry_by_category": by_category,
    }


def registry_importability_by_category(
    validation: (dict | None) = None,
) -> dict:
    """Per-category importability breakdown of registered worms.

    Groups WORM_REGISTRY entries by category and reports, for each category:
        - total: number of registered worms in this category
        - checked: number confirmed importable
        - broken: number that failed import validation
    Broken worms are matched by name so a stale registry entry with a removed
    source still lands in the right category. Empty-safe: returns {} when the
    registry or categories are unavailable.

    Args:
        validation: Optional result from validate_registry_importable()
            (or the cached registry_validation). If None, derives broken names
            by running a fresh importability check lazily.

    Returns:
        dict mapping lowercase category -> {total, checked, broken}.
    """
    try:
        from CORE.worm_registry import WORM_REGISTRY, validate_registry_importable
    except (ImportError, AttributeError):
        return {}

    if not WORM_REGISTRY:
        return {}

    # Name -> category lookup from the registry itself.
    name_to_cat: dict = {}
    per_cat_total: dict = {}
    for name, info in list(WORM_REGISTRY.items()):
        cat = str(info.get("category", "utility")).lower()
        name_to_cat[name] = cat
        per_cat_total[cat] = per_cat_total.get(cat, 0) + 1

    # Broken names: prefer the provided validation report, else compute it.
    broken_names = set()
    if validation and isinstance(validation.get("broken"), list):
        broken_names = {b.get("name") for b in validation["broken"] if b.get("name")}
    else:
        try:
            res = validate_registry_importable()
            broken_names = {b.get("name") for b in (res.get("broken") or []) if b.get("name")}
        except Exception:
            broken_names = set()

    breakdown: dict = {}
    for cat, total in sorted(per_cat_total.items()):
        broken_in_cat = sum(1 for name, c in name_to_cat.items() if c == cat and name in broken_names)
        breakdown[cat] = {
            "total": total,
            "broken": broken_in_cat,
            "checked": total - broken_in_cat,
        }
    return breakdown


def ensure_registry_warm() -> bool:
    """Ensure the worm registry is loaded (non-blocking if already warm).

    Safe to call before any session recording. If the cache isn't warm
    yet, starts background warming and returns False (caller should
    proceed without registry-dependent features).

    Returns:
        True if registry is available now, False if warming in background.
    """
    # Try quick import — if already imported, registry is warm
    try:
        from CORE.worm_registry import WORM_REGISTRY
        if WORM_REGISTRY:
            _warmed.set()
            _run_registry_validation()
            return True
    except ImportError:
        pass

    # Start background warm if not already started
    if not _warmed.is_set():
        warm_caches_background()

    return _warmed.is_set()
