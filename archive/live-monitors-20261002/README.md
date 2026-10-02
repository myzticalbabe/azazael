# Live monitors — archived 2026-10-02, pending reengineering.

WHY: the codebase evolved past them. `live_monitor.py` carried a stale
rotation table (GRPOTUNE present, ALLPAR missing vs the `track_registry`
authority) and its dependents assumed the pre-migration layout.
`test_track_registry_consumers.py` pinned that exact drift and is archived
with its subject.

CONTENTS:
- `live_monitor.py` — the live monitor (was scripts/).
- `test_track_registry_consumers.py` — its consumer-integrity suite.
- `test_exmachina_monitor_split.py`, `test_monitor_verdict_accuracy.py` —
  suites importing the module (archived with subject).

REENGINEER NEXT: rebuild the monitor against `track_registry.ROTATION` as
the single rotation authority (see `scripts/track_registry.py`, tracked),
with the archive's tests as the acceptance bar (minus GRPOTUNE).
Do NOT resurrect GRPOTUNE without a runner behind it.
