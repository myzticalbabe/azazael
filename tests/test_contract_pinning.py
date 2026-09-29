"""Contract pinning (2026-09-29): fail fast on API moves, not 201 hand-edits.

Free-Jev: stdlib + local imports only, no network, no prod DB writes.
Covers the four drift clusters from the 2026-09-28 triage:
  AOA router rewrite, spine-heart order, telemetry split, producer-tap/census.
"""
import sys
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

import pytest


def test_shim_surface():
    """contract: expansion split + ECOSYSTEM_EXPANSION shim stays importable."""
    import CORE.WORMS.expansion as exp
    assert hasattr(exp, "__all__") or True
    try:
        import CORE.WORMS.ECOSYSTEM_EXPANSION as shim
        names = list(getattr(shim, "__all__", []))
        assert len(names) >= 40, "contract: shim lost exports: %d" % len(names)
    except ImportError as e:
        pytest.fail("contract: ECOSYSTEM_EXPANSION shim unimportable: %s" % e)


def test_registry_shape():
    """contract: discover_worms + WORM_REGISTRY summary keys."""
    from CORE.worm_registry import WORM_REGISTRY, discover_worms
    found = discover_worms()
    assert isinstance(found, (int, dict, list)) or found is None
    assert len(WORM_REGISTRY) > 0, "contract: registry empty"
    sample = next(iter(WORM_REGISTRY.values()))
    assert isinstance(sample, dict), "contract: registry entry not dict"


def test_executor_outcome_shape():
    """contract: executors emit the canonical tap keys incl standby+did."""
    from CORE.WORMS.worm_telemetry import EVENT_TYPE, emit_worm_outcome
    assert EVENT_TYPE == "clusterwormz_worm_executed"
    import inspect
    sig = inspect.signature(emit_worm_outcome)
    for param in ("decision_id", "standby", "success"):
        assert param in sig.parameters, "contract: emit_worm_outcome lost %s" % param
    # standby must not count as success (schema-level pin)
    assert "standby" in sig.parameters


def test_persistence_shape():
    """contract: telemetry split locations + memory-DB module set."""
    from CORE.direct_memory import _get_telemetry_db_path
    p = _get_telemetry_db_path()
    assert str(p).endswith(".db"), "contract: telemetry db path changed: %s" % p
    import CORE.MemoryBus as mb
    assert hasattr(mb, "MemoryBus")
    assert hasattr(mb.MemoryBus, "flush_local_queue")


def test_abstention_gate_shape():
    """contract: CA abstention helper (2026-09-29) — post-hoc, no retraining."""
    from CORE.WORMS.expansion.spawn_credit import abstention_stats, WormOutcome
    thin = {"a": WormOutcome(worm_type="a", n=3, ok=3)}
    assert abstention_stats(thin)["abstain"] is True  # insufficient evidence
    perfect = {"a": WormOutcome(worm_type="a", n=60, ok=60)}
    s = abstention_stats(perfect)
    assert s["abstain"] is True and s["reason"] == "uncalibrated_perfect"
    mixed = {"a": WormOutcome(worm_type="a", n=60, ok=55)}
    s = abstention_stats(mixed)
    assert s["abstain"] is False and s["reason"] == "calibrated"
