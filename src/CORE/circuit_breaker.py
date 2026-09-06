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
import time
import threading
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any
from collections import deque

__all__ = [
    "CircuitBreaker", "BreakerRegistry", "CircuitConfig", "CircuitState",
    "DeadLetter", "breaker_registry",
]

log = logging.getLogger(__name__)


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


@dataclass
class DeadLetter:
    worm_name: str
    args: tuple
    kwargs: dict
    error: str
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0


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
        self._lock = threading.Lock()
        self._cancelled = threading.Event()

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

    def reset(self):
        """Reset the circuit breaker. Thread-safe.

        Clears the cancellation flag, resets state to CLOSED,
        and zeros failure/request counts.
        """
        with self._lock:
            self._cancelled.clear()
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.half_open_requests = 0

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

                self.dead_letters.append(DeadLetter(
                    worm_name=self.name,
                    args=args, kwargs=kwargs,
                    error=str(e)
                ))
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
