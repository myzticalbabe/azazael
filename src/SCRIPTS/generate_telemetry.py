#!/usr/bin/env python
"""generate_telemetry.py — Export PreActionGate telemetry to JSON for dashboard.

Generates azazael/src/scripts/telemetry.json with RULE 0Z-F counters:
  - parallel_batches: Number of compliant parallel spawn_agents calls
  - sequential_violations: Number of sequential spawn violations
  - edit_count: Total successful edits through the gate
  - compliance_ratio: parallel / (parallel + sequential) as percentage
  - timestamp: ISO-8601 timestamp

Usage:
    python azazael/src/scripts/generate_telemetry.py
    python azazael/src/scripts/generate_telemetry.py --output /path/to/telemetry.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    # Resolve output path
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir / "telemetry.json"

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    # Import PreActionGate
    src_dir = script_dir.parent  # azazael/src/
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from CORE.compliance.pre_action_gate import get_pre_action_gate
        gate = get_pre_action_gate()
    except ImportError as e:
        # Fallback: write baseline telemetry if gate unavailable
        data = {
            "parallel_batches": 0,
            "sequential_violations": 0,
            "edit_count": 0,
            "compliance_ratio": 100.0,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "gate_unavailable",
            "error": str(e),
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[telemetry] Gate unavailable — wrote baseline to {output_path}")
        return 0

    parallel = gate.parallel_batch_count
    sequential = gate.sequential_spawn_count
    total = parallel + sequential
    ratio = round((parallel / max(total, 1)) * 100, 1)

    data = {
        "parallel_batches": parallel,
        "sequential_violations": sequential,
        "edit_count": gate.edit_count,
        "compliance_ratio": ratio,
        "total_spawns": total,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "ok",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[telemetry] Wrote telemetry to {output_path}")
    print(f"  parallel_batches={parallel}, sequential_violations={sequential}, ratio={ratio}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
