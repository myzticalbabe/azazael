# coding: utf-8
"""
Circuit Breaker Pattern for AZAZAEL Production Worms
====================================================
Implements open/half-open/closed states with:
  - Exponential backoff retry
  - Dead letter queue for failed executions
  - Cancellation tokens for timeout handling
  - Health scoring per worm
"""
import contextlib
import logging
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List

__all__ = [
    "CircuitBreaker", "BreakerRegistry", "CircuitConfig", "CircuitState",
    "DeadLetter", "breaker_registry", "replan_from_dead_letters",
    "replan_after_failures",
]

log = logging.getLogger(__name__)

#: Fail-open swallows recorded when the runtime recorder is unavailable. An
#: unrecorded swallow is indistinguishable from success, so every handler here
#: records first (a breaker must never break the thing it guards, but its
#: degradation must not be invisible either).
_SWALLOWED: List[str] = []


try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # runtime absent: stay importable
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def _note_failure(where: str, exc: BaseException | None = None) -> None:
    """Record a fail-open swallow. Never raises."""
    try:
        note_failure(where, exc)
    except Exception as _e:
        _SWALLOWED.append("%s:%s" % (where, type(_e).__name__))


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_requests: int = 3
    retry_base_delay: float = 0.1
    retry_max_delay: float = 60.0
    retry_backoff: float = 2.0
    dead_letter_max: int = 1000


#: EP129 phase taxonomy (Agent Failure Taxonomy, 2502.05915). A failure is a
#: PLANNING, EXECUTION or RESPONSE failure and each one needs a different
#: repair; grouping the dead-letter queue by phase is what makes that possible.
PHASES = ("planning", "execution", "response")
#: The honest default: the caller did not say which phase failed. Never
#: guessed, because a wrong phase produces a wrong replan.
PHASE_UNKNOWN = "unknown"


@dataclass
class DeadLetter:
    worm_name: str
    args: tuple
    kwargs: dict
    error: str
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    #: EP129. Defaulted, so every pre-existing construction site keeps working
    #: unchanged; a caller that declares a phase (see
    #: `CircuitBreaker.declared_phase`) gets it recorded here.
    phase: str = PHASE_UNKNOWN


class CircuitBreaker:
    """Production circuit breaker with retry and dead letter queue."""

    def __init__(self, name: str = "default", config: (CircuitConfig | None) = None,
                 threshold: (int | None) = None, cooldown: (float | None) = None):
        self.name = name
        if config is None:
            config = CircuitConfig()
        if threshold is not None:
            config.failure_threshold = threshold
        if cooldown is not None:
            config.recovery_timeout = cooldown
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.half_open_requests = 0
        self.dead_letters: deque = deque(maxlen=self.config.dead_letter_max)
        # Operator-trip provenance. `test_circuit_breaker_integration.py` has
        # called `force_trip()` since the file was written, but the method was
        # never implemented, so the documented operator channel did not exist.
        self.trip_reason = ""
        self.tripped_at = 0.0
        self.tripped_by_operator = False
        self._lock = threading.Lock()
        self._cancelled = threading.Event()
        # EP129: the phase currently being attempted, set by declared_phase().
        # Empty means "the caller did not say" and stays PHASE_UNKNOWN in the
        # dead letter rather than being guessed.
        self._phase = ""
        self._phase_lock = threading.Lock()

    @property
    def health_score(self) -> float:
        """0.0 = dead, 1.0 = perfect health. Thread-safe via _lock."""
        with self._lock:
            total = self.failure_count + self.success_count
            if total == 0:
                return 1.0
            return self.success_count / total

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self.state == CircuitState.OPEN

    def cancel_all(self):
        """Cancel all pending operations. Thread-safe."""
        with self._lock:
            self._cancelled.set()

    def force_trip(self, reason: str = "operator") -> dict:
        """Trip the breaker OPEN by operator decision. Thread-safe.

        An automatic trip needs `failure_threshold` real failures; an operator
        needs a way to take an unhealthy dependency out of service *now*
        (a known-bad deploy, a provider being drained, a security hold).
        Without this the only path to OPEN was to provoke real failures.

        This is deliberately a state change and not a fake failure: no dead
        letter is written, because the DLQ is a record of failed executions
        and a trip has no execution to record. The provenance lives in
        `trip_reason` / `tripped_at`, which `stats()` surfaces, so the
        decision is still auditable.

        `last_failure_time` is stamped so the OPEN -> HALF_OPEN cooldown is
        measured from the trip, which is what makes the trip recoverable.
        """
        reason = str(reason or "operator")[:200]
        with self._lock:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            self.half_open_requests = 0
            # Keep the counters consistent with the state, so health_score and
            # the failure threshold cannot contradict `state == OPEN`.
            self.failure_count = max(self.failure_count,
                                    self.config.failure_threshold)
            self.trip_reason = reason
            self.tripped_at = self.last_failure_time
            self.tripped_by_operator = True
            log.warning(f"CircuitBreaker({self.name}): FORCE TRIP -> OPEN ({reason})")
        return {"success": True, "name": self.name, "state": self.state.value,
                "reason": reason, "retry_in": self.config.recovery_timeout}

    @contextlib.contextmanager
    def declared_phase(self, phase: str):
        """Declare the phase of the work inside this block (EP129).

        Failures recorded inside the block carry this phase, so the dead-letter
        queue can be grouped into planning / execution / response failures -
        each of which needs a different repair. An unrecognised name is
        recorded as PHASE_UNKNOWN rather than coerced into a real phase.
        Nesting restores the previous value. Never raises.
        """
        name = str(phase or "").strip().lower()
        if name not in PHASES:
            name = PHASE_UNKNOWN
        previous = ""
        try:
            with self._phase_lock:
                previous = self._phase
                self._phase = name
        except Exception:
            note_failure("circuit_breaker:L195", None)
            previous = ""
        try:
            yield name
        finally:
            try:
                with self._phase_lock:
                    self._phase = previous
            except Exception as exc:              # noqa: BLE001 — phase is advisory
                _note_failure("circuit_breaker:phase-restore", exc)

    def hold(self) -> bool:
        """True while an operator trip is still in force.

        An operator trip must not be silently undone by the ordinary
        HALF_OPEN -> CLOSED success path: `reset()` is the documented way to
        release a hold, so callers that want automatic recovery can read this
        and decide. Thread-safe.
        """
        with self._lock:
            return bool(self.tripped_by_operator)

    def reset(self):
        """Reset the circuit breaker. Thread-safe.

        Clears the cancellation flag, resets state to CLOSED,
        and zeros failure/request counts. Also releases an operator trip —
        this is the documented way to clear a `force_trip()` hold.
        """
        with self._lock:
            self._cancelled.clear()
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_requests = 0
            self.trip_reason = ""
            self.tripped_at = 0.0
            self.tripped_by_operator = False

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with circuit breaker protection."""
        if self._cancelled.is_set():
            raise RuntimeError(f"CircuitBreaker({self.name}): cancelled")

        with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                    log.info(f"CircuitBreaker({self.name}): OPEN -> HALF_OPEN")
                else:
                    raise RuntimeError(
                        f"CircuitBreaker({self.name}): OPEN — "
                        f"retry in {self.config.recovery_timeout - (time.time() - self.last_failure_time):.0f}s"
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_max_requests:
                    raise RuntimeError(
                        f"CircuitBreaker({self.name}): HALF_OPEN limit reached"
                    )
                self.half_open_requests += 1

        try:
            result = func(*args, **kwargs)
            with self._lock:
                self.success_count += 1
                self.last_success_time = time.time()
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    log.info(f"CircuitBreaker({self.name}): HALF_OPEN -> CLOSED")
            return result
        except Exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if (self.state == CircuitState.CLOSED and
                        self.failure_count >= self.config.failure_threshold):
                    self.state = CircuitState.OPEN
                    log.warning(f"CircuitBreaker({self.name}): CLOSED -> OPEN ({self.failure_count} failures)")
                elif self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    log.warning(f"CircuitBreaker({self.name}): HALF_OPEN -> OPEN")

                # Best-effort: only a declared phase, never a guess.
                failure_phase = self._phase or PHASE_UNKNOWN
                self.dead_letters.append(DeadLetter(
                    worm_name=self.name,
                    args=args, kwargs=kwargs,
                    error=str(e),
                    phase=failure_phase,
                ))
            # EP113 + EP294: the failure is now recorded, which makes this the
            # one place a lesson can be written from certain knowledge. Called
            # OUTSIDE the breaker lock (a reflection is a memory write, and
            # holding _lock across it would serialise every caller) and fully
            # fail-open, so it can never change this method's behaviour.
            _reflect_on_failure(self, str(e), failure_phase)
            raise

    def retry_with_backoff(self, func: Callable, *args, max_retries: int = 3, **kwargs) -> Any:
        """Execute with exponential backoff retry."""
        last_error = None
        delay = self.config.retry_base_delay

        for attempt in range(max_retries + 1):
            if self._cancelled.is_set():
                raise RuntimeError(f"CircuitBreaker({self.name}): cancelled")
            try:
                return self.execute(func, *args, **kwargs)
            except RuntimeError:
                raise
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    log.warning(
                        f"CircuitBreaker({self.name}): attempt {attempt+1}/{max_retries+1} "
                        f"failed, retrying in {delay:.1f}s"
                    )
                    time.sleep(delay)
                    delay = min(delay * self.config.retry_backoff, self.config.retry_max_delay)

        raise last_error or RuntimeError(f"CircuitBreaker({self.name}): all retries exhausted")

    def stats(self) -> dict:
        """Return circuit breaker statistics. Thread-safe via _lock."""
        with self._lock:
            # Compute health inline — calling self.health_score here would
            # re-acquire the non-reentrant _lock and self-deadlock.
            total = self.failure_count + self.success_count
            health = 1.0 if total == 0 else self.success_count / total
            return {
                "name": self.name,
                "state": self.state.value,
                "failures": self.failure_count,
                "successes": self.success_count,
                "health": round(health, 3),
                "dead_letters": len(self.dead_letters),
                "last_failure": self.last_failure_time,
                "cancelled": self._cancelled.is_set(),
                "trip_reason": self.trip_reason,
                "tripped_at": self.tripped_at,
                "held": self.tripped_by_operator,
            }


# --- Global Circuit Breaker Registry ---

class BreakerRegistry:
    """Registry of all circuit breakers for monitoring."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get(self, name: str, config: (CircuitConfig | None) = None) -> CircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]

    def all_stats(self) -> list[dict]:
        return [b.stats() for b in self._breakers.values()]

    def cancel_all(self):
        """Cancel all pending operations across ALL breakers. Thread-safe."""
        with self._lock:
            for b in self._breakers.values():
                b.cancel_all()

    def reset_all(self):
        """Reset all circuit breakers to closed state. Thread-safe."""
        with self._lock:
            for b in self._breakers.values():
                b.reset()

    # -- Dead Letter Queue Monitoring ------------------------------

    def get_dead_letters(self, name: (str | None) = None,
                         since: float = 0) -> list[DeadLetter]:
        """Get dead letters, optionally filtered by breaker name and time.
        
        Returns chronologically ordered (most recent first) dead letters
        for the specified breaker, or all breakers if name is None.
        Thread-safe: acquires both registry and per-breaker locks.
        """
        letters = []
        with self._lock:
            names = [name] if name else list(self._breakers.keys())
            for n in names:
                breaker = self._breakers.get(n)
                if breaker:
                    with breaker._lock:
                        for dl in list(breaker.dead_letters):
                            if dl.timestamp >= since:
                                letters.append(dl)
        # Most recent first
        letters.sort(key=lambda x: x.timestamp, reverse=True)
        return letters

    def get_dead_letter_summary(self, lookback_seconds: float = 3600) -> dict[str, Any]:
        """Get a summary of dead letters grouped by breaker.
        
        Args:
            lookback_seconds: How far back to include recent errors (default 1 hour)
        
        Returns:
            dict with total count, per-breaker counts, and most recent errors
        """
        summary: dict[str, Any] = {
            "total_dead_letters": 0,
            "per_breaker": {},
            "recent_errors": [],
        }
        cutoff = time.time() - lookback_seconds
        
        with self._lock:
            for name, breaker in self._breakers.items():
                n_letters = len(breaker.dead_letters)
                if n_letters > 0:
                    summary["per_breaker"][name] = n_letters
                    summary["total_dead_letters"] += n_letters
                    # Collect recent errors
                    for dl in breaker.dead_letters:
                        if dl.timestamp >= cutoff:
                            summary["recent_errors"].append({
                                "breaker": name,
                                "error": dl.error[:120],
                                "timestamp": dl.timestamp,
                                "retry_count": dl.retry_count,
                            })
        
        # Limit recent errors to 20
        summary["recent_errors"] = sorted(
            summary["recent_errors"],
            key=lambda x: x["timestamp"], reverse=True
        )[:20]
        
        return summary

    def purge_dead_letters(self, name: (str | None) = None):
        """Clear dead letters for a specific breaker, or all if name is None."""
        with self._lock:
            if name:
                breaker = self._breakers.get(name)
                if breaker:
                    with breaker._lock:
                        breaker.dead_letters.clear()
            else:
                for breaker in self._breakers.values():
                    with breaker._lock:
                        breaker.dead_letters.clear()


breaker_registry = BreakerRegistry()


#: EP129 - signature -> the concrete next-attempt adjustment. Rule-based and
#: deliberately blunt: the point is that a failure produces a DIFFERENT next
#: attempt, not that the advice is clever.
_REPLAN_RULES = (
    ("timeout", "raise the timeout AND shrink the batch - at planning a timeout "
                "means the plan is too large, not that the work is slow"),
    ("timed out", "raise the timeout AND shrink the batch - a large plan is the "
                  "usual cause"),
    ("connection", "treat the dependency as down: let the cooldown elapse, then "
                   "retry as a single HALF_OPEN probe"),
    ("refused", "the dependency is not accepting work - back off, do not "
                "hot-loop the retry"),
    ("memory", "shrink the batch or stream the input; never retry at the same size"),
    ("permission", "STOP retrying - escalate for credentials/scope; a retry "
                   "cannot fix this"),
    ("denied", "STOP retrying - escalate for credentials/scope"),
    ("not found", "resolve the id/path once and cache it before the next attempt"),
    ("no such file", "resolve the path before the next attempt"),
    ("rate limit", "back off and spread the load - the retry itself is the problem"),
    ("429", "back off and spread the load"),
    ("json", "re-request the input in a stricter format before parsing it again"),
    ("parse", "re-request the input in a stricter format before parsing it again"),
    ("assert", "the precondition is wrong, not the work: check the plan's inputs"),
)


def _error_signature(error: str) -> str:
    """Coarse, group-by-able signature for an error string (EP129).

    Errors from the same cause differ in ids, paths and addresses; normalising
    those out is what lets the queue be counted rather than merely listed.
    """
    s = str(error or "").lower()
    s = re.sub(r"0x[0-9a-f]+", "<hex>", s)
    s = re.sub(r"[a-z]:[\\/][^\s,;)]+", "<path>", s)
    s = re.sub(r"['\"][^'\"]{0,120}['\"]", "<str>", s)
    s = re.sub(r"\d+", "<n>", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:160] or "(empty)"


def replan_from_dead_letters(registry=None, limit: int = 50) -> dict:
    """Group dead letters by phase and signature and propose the replan (EP129).

    Why this exists: the dead-letter queue recorded failures that nothing read.
    `get_dead_letters()` and `get_dead_letter_summary()` counted letters but no
    code turned a recorded failure into a DIFFERENT next attempt. This is that
    consumer - the missing half of the failure taxonomy.

    Returns {n_letters, phases, signatures, worst, replan, gaps}. `replan` is
    an ordered list of concrete adjustments, worst signature first. Fail-open:
    an unreadable queue yields zeros plus a named gap, never an exception.
    """
    out: dict[str, Any] = {"n_letters": 0, "phases": {}, "signatures": {},
                           "worst": {}, "replan": [], "gaps": []}
    try:
        reg = registry if registry is not None else breaker_registry
        letters = list(reg.get_dead_letters() or [])[:max(1, int(limit))]
    except Exception as exc:
        note_failure("circuit_breaker:L510", exc)
        out["gaps"].append(f"unreadable-dlq:{type(exc).__name__}")
        return out

    out["n_letters"] = len(letters)
    phases: dict[str, int] = out["phases"]
    sigs: dict[str, int] = out["signatures"]
    for dl in letters:
        phase = str(getattr(dl, "phase", PHASE_UNKNOWN) or PHASE_UNKNOWN)
        phases[phase] = phases.get(phase, 0) + 1
        sig = _error_signature(getattr(dl, "error", ""))
        sigs[sig] = sigs.get(sig, 0) + 1

    if sigs:
        worst_sig, worst_n = max(sigs.items(), key=lambda kv: kv[1])
        out["worst"] = {"signature": worst_sig, "count": worst_n}

    for sig, count in sorted(sigs.items(), key=lambda kv: (-kv[1], kv[0])):
        advice = ""
        for needle, hint in _REPLAN_RULES:
            if needle in sig:
                advice = hint
                break
        if not advice:
            advice = ("re-run once with identical inputs to confirm it is "
                      "deterministic; a deterministic failure is in the input")
        out["replan"].append(f"x{count} {sig[:70]} -> {advice}")

    if not letters:
        out["gaps"].append("empty-dead-letter-queue")
    return out


def _phase_advice(phase: str, signature: str) -> str:
    """The concrete next-attempt adjustment for a recorded failure (EP129).

    Rule-based and deliberately blunt, like `_REPLAN_RULES`: the point is that a
    failure produces a DIFFERENT next attempt, not that the advice is clever.
    The phase decides the fallback when no signature rule matches, because the
    same error text needs a different repair at planning than at response.
    """
    for needle, hint in _REPLAN_RULES:
        if needle in signature:
            return hint
    if phase == "planning":
        return ("re-plan before retrying: a planning failure means the step list, "
                "not the work, is wrong")
    if phase == "response":
        return ("re-check the response shape/contract before retrying - the work "
                "may have succeeded and the answer been misread")
    return ("re-run once with identical inputs to confirm it is deterministic; "
            "a deterministic failure is in the input, not in the retry")


def _breaker_dlq_view(breaker: "CircuitBreaker") -> Any:
    """A registry-shaped view over ONE breaker's dead letters.

    `replan_from_dead_letters` takes a registry. Scoping it to the breaker that
    just failed keeps the replan cheap (no whole-registry scan on a failure path)
    and relevant (the advice is about this failure, not the fleet's).
    """
    class _View:
        def get_dead_letters(self):
            with breaker._lock:
                return sorted(breaker.dead_letters,
                              key=lambda d: d.timestamp, reverse=True)
    return _View()


def _reflect_on_failure(breaker: "CircuitBreaker", error: str,
                        phase: str = PHASE_UNKNOWN) -> None:
    """Write the verbal reflection for a recorded failure (EP113 + EP129/EP294).

    Why this exists: `reflexion.py` was a complete buffer with NO caller, so no
    failed attempt in this tree produced a lesson and none was ever recalled.
    The dead-letter append in `execute` is the one place a failure is known for
    certain, so the reflection is written there - one per recorded failure, the
    same granularity as the DLQ row, so the two can never disagree.

    `what_next` comes from the error signature and the declared phase; when the
    same signature has failed more than once, the scoped replan is consulted so
    the lesson is the actual next-attempt adjustment rather than a restatement.

    Fail-open by construction: the import is lazy, the body is guarded, and the
    caller ignores the result. A reflection must never affect the breaker.
    """
    try:
        signature = _error_signature(error)
        advice = _phase_advice(phase, signature)
        try:
            if breaker.failure_count >= 2:
                scoped = replan_from_dead_letters(_breaker_dlq_view(breaker),
                                                  limit=10)
                first = (scoped.get("replan") or [None])[0]
                if first:
                    advice = str(first)
        except Exception as exc:                      # noqa: BLE001 — advice optional
            _note_failure("circuit_breaker:reflect-advice", exc)
        from CORE.technique_runtime import reflect_on_failure as _reflect
        _reflect(
            question=f"{breaker.name} failed ({phase})",
            what_failed=f"{phase}: {signature}"[:300],
            what_next=advice[:600],
            decision_id=f"breaker:{breaker.name}")
    except Exception as exc:
        # Fail-open on purpose: a reflection must never affect the breaker.
        # Recorded so the swallow is observable instead of success-shaped.
        _note_failure("circuit_breaker:reflect", exc)
        return


def replan_after_failures(registry=None, limit: int = 50) -> dict:
    """Ask for the next-attempt replan after failures (EP129).

    The explicit entry point for a caller that has just seen failures and wants
    the adjustments rather than the raw queue. Delegates to
    `replan_from_dead_letters`. The production failure path already reaches that
    logic through `_reflect_on_failure` - scoped to the breaker that failed - so
    this exists for a caller that wants the fleet-wide view. Note that the
    per-breaker path is the one that is exercised today; this fleet-wide wrapper
    has no caller yet.
    """
    return replan_from_dead_letters(registry, limit)


if __name__ == "__main__":
    # Quick test
    cb = CircuitBreaker("test_worm", CircuitConfig(failure_threshold=2, recovery_timeout=2))

    def flaky_func(succeed: bool):
        if not succeed:
            raise ValueError("Simulated failure")
        return "OK"

    for i in range(3):
        try:
            result = cb.execute(flaky_func, False)
            print(f"  Attempt {i+1}: {result}")
        except Exception as e:
            print(f"  Attempt {i+1}: {e}")

    print(f"\n  State: {cb.state.value}, Health: {cb.health_score:.2f}")
    print(f"  Dead letters: {len(cb.dead_letters)}")
