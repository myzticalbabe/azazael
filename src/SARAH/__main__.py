"""
SARAH CLI Entry Point — Headless Run (Build Instructions B9)

Usage:
    python -m SARAH --profile demo --steps 20 --json /tmp/sarah_run.json
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

from SARAH.profile import SarahProfile
from SARAH.clinical import ClinicalCrosswalk
from SARAH.exit import request as request_exit
from SARAH.telemetry import (
    emit_profile_set,
    emit_demand_change,
    emit_exit_requested,
    emit_pause,
    emit_resume,
    emit_affirmation,
    emit_session_end,
    emit_clinical_seed,
    get_session_events,
)


def run_demo(steps: int = 20, profile: str = "demo", output: str | None = None) -> list[dict]:
    """Run a headless demo session, emitting telemetry events."""
    events = []
    
    # Create demo profile
    if profile == "demo":
        p = SarahProfile.from_signals({
            "sensory_gain": 0.7,
            "processing_speed": 0.5,
            "attention_span": 0.6,
            "recovery_latency": 0.4,
        }, source="probe")
    else:
        p = SarahProfile()
    
    # Emit profile_set events
    for axis in ["sensory_gain", "processing_speed", "attention_span", "recovery_latency"]:
        val = getattr(p, axis)
        if val is not None:
            src = p._sources.get(axis, "probe")
            emit_profile_set(axis, val, src)
    
    # Simulate clinical seed (M16)
    crosswalk = ClinicalCrosswalk()
    seed = crosswalk.seed_profile("F84.0", "DSM-5-TR")
    if seed:
        axes_seeded = len(seed)
        source_versions = {prov["source"]: prov["version"] for prov in seed.values()}
        emit_clinical_seed("F84.0", "DSM-5-TR", axes_seeded, source_versions)
    
    # Simulate steps
    start_time = time.time()
    for step in range(steps):
        # Simulate demand changes (never up unless user requested)
        if step % 5 == 0:
            emit_demand_change("pacing", "down", 0.05)
        if step % 7 == 0:
            emit_pause(time.time() - start_time, 0.1)
            emit_resume(time.time() - start_time)
    
    # Affirmation: the demo supplies no user-authored evidence, so nothing is
    # drafted. Emitting the fail-closed path is the point — a fabricated
    # affirmation is the backfire case B3 exists to prevent.
    emit_affirmation(drafted=False, evidence_present=False)

    # Exit: one action, never scored, always reachable.
    ticket = request_exit("demo complete")
    emit_exit_requested(time.time() - start_time, ticket.reason)

    # Session end
    emit_session_end(time.time() - start_time, load_peak=0.7, stopped_by="user")
    
    # Collect events
    events = get_session_events()
    
    if output:
        Path(output).write_text(json.dumps({"events": [e.__dict__ for e in events]}, indent=2))
    
    return events


def main():
    parser = argparse.ArgumentParser(description="SARAH headless demo runner")
    parser.add_argument("--profile", default="demo", help="Profile name (demo)")
    parser.add_argument("--steps", type=int, default=20, help="Number of simulation steps")
    parser.add_argument("--json", dest="output", help="Output JSON file path")
    args = parser.parse_args()
    
    events = run_demo(steps=args.steps, profile=args.profile, output=args.output)
    
    # Print event types for verification
    event_types = sorted({e.event for e in events})
    print("Event types:", event_types)
    
    # Verify no unrequested demand increase
    up_events = [e for e in events if e.event == "demand_change" and e.direction == "up"]
    if up_events:
        print(f"WARNING: {len(up_events)} unrequested demand increases", file=sys.stderr)
        sys.exit(1)
    
    print(f"Completed {len(events)} events, {args.steps} steps")


if __name__ == "__main__":
    main()