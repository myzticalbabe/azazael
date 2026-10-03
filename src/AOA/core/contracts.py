"""AOA typed contracts -- the provenance envelope for Arm results.

Source: AOA_ARCHITECTURE_AUDIT_2026-09-14.md section 5, step 1.

The gap this closes: every Arm returns a plain ``dict`` whose freshness is
merely conventional. ``{"status": "ok", "data": {...}}`` says nothing about
WHEN the enclosed datum was produced, nor how long it stays meaningful, so a
consumer cannot distinguish a live reading from a replay, and no monitor can
age a value it has no timestamp for. That is the same defect class already
repaired in the four live monitors (see the audit, sections 6.7 and 6.8).

``ArmResult`` makes freshness structural: a result carries ``produced_at``
and ``stale_after_s``, so ``is_stale()`` is derived rather than assumed.

Migration is deliberately WARN-ONLY. Nothing in this module raises. Arms that
do not yet declare staleness keep working exactly as before, and the violation
is *counted* so that promotion to a hard failure can later be decided from
measurement rather than optimism. This ordering was the unanimous verdict of
four live inference providers (Gemini, OpenRouter, Cohere, NVIDIA NIM) on
2026-09-14; the reviewing NVIDIA pass supplied the promotion criterion
(observe violation rates first, reject once the false-positive rate is known).
Evidence: ``.inference_cache/20260914_134832_*.log``.

Timestamp convention: naive LOCAL time, via ``datetime.now()``, matching the
router's existing ``started_at`` / ``completed_at`` fields. Mixing naive and
aware datetimes across this layer would turn every existing duration
subtraction into a ``TypeError`` at runtime, so local consistency is chosen
deliberately over theoretical purity. ``parse_timestamp`` accepts aware input
and normalises it to local, so a caller that supplies ``+00:00`` is still
correctly aged rather than silently rejected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging
import threading

log = logging.getLogger(__name__)


# Statuses an Arm is allowed to report. Anything else is a contract
# violation -- not an exception, because existing arms must keep running.
KNOWN_STATUSES = ("ok", "error", "partial", "skipped")

# How far into the future a timestamp may sit before it is treated as bogus.
# Small positive tolerance absorbs clock granularity between processes.
FUTURE_TOLERANCE_S = 5.0

# Provenance of ``produced_at``. Recorded so a reader can tell an Arm's own
# claim from the router's observation of it; the two are not equivalent, and
# conflating them is how a fabricated timestamp becomes indistinguishable
# from a measured one.
PROVENANCE_DECLARED = "arm_declared"
PROVENANCE_OBSERVED = "router_observed"


def now_local() -> datetime:
    """Current naive local time (the AOA layer's convention)."""
    return datetime.now()


def now_iso() -> str:
    """Current naive local time as an ISO-8601 string."""
    return now_local().isoformat()


def parse_timestamp(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp to naive LOCAL time.

    Accepts both naive and timezone-aware input. Aware input is converted to
    local time and stripped, so an Arm that reports UTC cannot be compared
    wrongly against a naive local ``datetime.now()``. Returns None when the
    value is missing or unparseable -- never raises.
    """
    if not value:
        return None
    try:
        text = str(value).strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


@dataclass
class ArmResult:
    """A typed Arm result carrying its own provenance.

    ``stale_after_s`` is optional so nothing is forced to guess. When it is
    None the datum is *unaged*: still returned, still usable, but explicitly
    not a freshness claim, and it counts as a contract violation while the
    migration is warn-only.
    """

    status: str = "ok"
    arm_id: str = ""
    capability: str = ""
    data: Any = None
    error: Optional[str] = None
    produced_at: str = field(default_factory=now_iso)
    stale_after_s: Optional[float] = None
    provenance: str = PROVENANCE_OBSERVED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def age_s(self, at: Optional[datetime] = None) -> Optional[float]:
        """Seconds since ``produced_at``. None when it cannot be parsed."""
        produced = parse_timestamp(self.produced_at)
        if produced is None:
            return None
        reference = at or now_local()
        if reference.tzinfo is not None:
            reference = reference.astimezone().replace(tzinfo=None)
        return (reference - produced).total_seconds()

    def is_stale(self, at: Optional[datetime] = None) -> Optional[bool]:
        """True when past its declared lifetime.

        Returns None -- not False -- when staleness is *undecidable*, i.e.
        the lifetime was never declared or the timestamp is unparseable.
        Collapsing "unknown" into "fresh" is the exact bug this envelope
        exists to prevent, so the three states are kept distinct.
        """
        if self.stale_after_s is None:
            return None
        age = self.age_s(at)
        if age is None:
            return None
        return age > float(self.stale_after_s)

    def to_dict(self) -> Dict[str, Any]:
        """Flatten to a plain dict, preserving the legacy Arm result shape.

        ``status`` / ``data`` / ``error`` / ``arm_id`` keep their existing
        meanings so every current consumer of ``router.route_task`` continues
        to work; the provenance keys are purely additive.
        """
        out: Dict[str, Any] = {
            "status": self.status,
            "arm_id": self.arm_id,
            "capability": self.capability,
            "data": self.data,
            "produced_at": self.produced_at,
            "provenance": self.provenance,
        }
        if self.error is not None:
            out["error"] = self.error
        if self.stale_after_s is not None:
            out["stale_after_s"] = self.stale_after_s
        age = self.age_s()
        if age is not None:
            out["age_s"] = round(age, 3)
        stale = self.is_stale()
        if stale is not None:
            out["is_stale"] = stale
        if self.metadata:
            out["metadata"] = dict(self.metadata)
        return out

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ArmResult":
        """Rebuild an envelope from a flattened dict."""
        return cls(
            status=str(raw.get("status", "ok")),
            arm_id=str(raw.get("arm_id", "") or ""),
            capability=str(raw.get("capability", "") or ""),
            data=raw.get("data"),
            error=raw.get("error"),
            produced_at=str(raw.get("produced_at") or now_iso()),
            stale_after_s=raw.get("stale_after_s"),
            provenance=str(raw.get("provenance") or PROVENANCE_OBSERVED),
            metadata=dict(raw.get("metadata") or {}),
        )

    @classmethod
    def from_arm_output(
        cls,
        raw: Any,
        arm_id: str,
        capability: str,
        stale_after_s: Optional[float] = None,
    ) -> "ArmResult":
        """Wrap a legacy Arm return value without changing its meaning.

        An Arm that already returns an envelope is passed through. A plain
        dict is adopted as-is, with ``produced_at`` taken as NOW and
        ``provenance`` marked ``router_observed`` -- honest labelling: the
        router saw this value at this moment and does not know when the Arm
        computed it. ``stale_after_s`` is left None unless the caller
        supplies a policy default, in which case the provenance is downgraded
        to observed so the *policy's* lifetime is never mistaken for the
        Arm's own claim.
        """
        if isinstance(raw, ArmResult):
            return raw
        if isinstance(raw, dict) and "produced_at" in raw and "status" in raw:
            envelope = cls.from_dict(raw)
            if not envelope.arm_id:
                envelope.arm_id = arm_id
            if not envelope.capability:
                envelope.capability = capability
            return envelope
        if isinstance(raw, dict):
            payload = dict(raw)
            data = payload.get("data")
            return cls(
                status=str(payload.get("status", "ok")),
                arm_id=str(payload.get("arm_id") or arm_id),
                capability=str(payload.get("capability") or capability),
                data=data,
                error=payload.get("error"),
                produced_at=now_iso(),
                stale_after_s=stale_after_s,
                provenance=PROVENANCE_OBSERVED,
            )
        # An Arm returned something that is not a dict at all: an upstream
        # contract break. Report it as an error rather than coercing it into
        # a false success.
        return cls(
            status="error",
            arm_id=arm_id,
            capability=capability,
            data=None,
            error="Arm returned %s, expected dict" % type(raw).__name__,
            produced_at=now_iso(),
            provenance=PROVENANCE_OBSERVED,
        )


def check_result(result: ArmResult, at: Optional[datetime] = None) -> List[str]:
    """Return the contract violations in an envelope. Never raises.

    Each violation is a short machine-checkable string so callers can count
    and group them; human-facing wording lives in the log line.
    """
    violations: List[str] = []

    if result.status not in KNOWN_STATUSES:
        violations.append("unknown_status:%s" % result.status)

    produced = parse_timestamp(result.produced_at)
    if produced is None:
        violations.append("produced_at_unparseable")
    else:
        # A naive timestamp on the wire usually means someone wrote
        # datetime.now() on a machine in another timezone; it is worth
        # knowing about explicitly rather than absorbing silently.
        if produced - (at or now_local()) > timedelta(seconds=FUTURE_TOLERANCE_S):
            violations.append("produced_at_in_future")

    if result.stale_after_s is not None:
        try:
            value = float(result.stale_after_s)
            if value <= 0 or value != value or value == float("inf"):
                violations.append("stale_after_s_not_positive")
        except (TypeError, ValueError):
            violations.append("stale_after_s_not_numeric")
    elif result.status == "ok" and result.data is not None:
        # A datum handed back with no declared lifetime is the original gap.
        # Only a violation when there IS data to age; an "ok" carrying None
        # makes no freshness claim and is left alone.
        violations.append("stale_after_s_missing")

    return violations


class ContractReport:
    """Thread-safe, bounded counter of envelope contract violations.

    Mirrors the callback-error accounting already used by ``EventBus`` so the
    two surfaces report defects the same way. Bounded, because an unbounded
    violation log on a hot routing path is itself a leak.
    """

    def __init__(self, max_kept: int = 100):
        self._lock = threading.Lock()
        self._counts: Dict[str, int] = {}
        self._recent: List[Dict[str, Any]] = []
        self._total = 0
        self._checked = 0
        self._max_kept = max_kept

    def record(self, arm_id: str, capability: str, result: ArmResult,
               violations: List[str]) -> None:
        if not violations:
            with self._lock:
                self._checked += 1
            return
        entry = {
            "at": now_iso(),
            "arm_id": arm_id,
            "capability": capability,
            "violations": list(violations),
            "provenance": result.provenance,
        }
        with self._lock:
            self._checked += 1
            self._total += 1
            for name in violations:
                self._counts[name] = self._counts.get(name, 0) + 1
            self._recent.append(entry)
            if len(self._recent) > self._max_kept:
                self._recent = self._recent[-self._max_kept:]
        # Warn-only: logged, never raised. The whole point of this phase is
        # to learn the violation rate before anything depends on it.
        log.warning(
            "AOA contract violation: arm=%s capability=%s violations=%s "
            "provenance=%s",
            arm_id, capability, ",".join(violations), result.provenance)

    @property
    def total(self) -> int:
        with self._lock:
            return self._total

    @property
    def checked(self) -> int:
        with self._lock:
            return self._checked

    def counts(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._counts)

    def recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._recent[-limit:])

    def snapshot(self) -> Dict[str, Any]:
        """Summary for monitors. ``clean`` is the promotion criterion: while
        it is False, forcing a hard failure would break working arms."""
        with self._lock:
            checked = self._checked
            total = self._total
            counts = dict(self._counts)
            recent = list(self._recent[-5:])
        return {
            "checked": checked,
            "violations": total,
            "violation_rate": round(total / checked, 4) if checked else 0.0,
            "by_kind": counts,
            "clean": total == 0,
            "recent": recent,
        }

    def reset(self) -> None:
        with self._lock:
            self._counts.clear()
            self._recent.clear()
            self._total = 0
            self._checked = 0


_CONTRACT_REPORT = ContractReport()


def get_contract_report() -> ContractReport:
    """Process-wide contract report, so monitors see every layer's results."""
    return _CONTRACT_REPORT


def validate_result(result: ArmResult, arm_id: str = "",
                    capability: str = "",
                    report: Optional[ContractReport] = None) -> List[str]:
    """Check an envelope, count any violations, and return them.

    Warn-only by construction: this function cannot raise, so it is safe to
    call on the routing path before the migration completes.
    """
    violations = check_result(result)
    (report or _CONTRACT_REPORT).record(
        arm_id or result.arm_id, capability or result.capability,
        result, violations)
    return violations
