#!/usr/bin/env python3
"""
run_training_orchestrator.py — Run TrainingOrchestrator once (for Task Scheduler).

Called by Windows Task Scheduler to execute one SB3 training run.
Records results to LocalMemoryStore and prints a summary.

Usage:
    python scripts/run_training_orchestrator.py
    python scripts/run_training_orchestrator.py --algo DQN --timesteps 2000 --source SystemZ
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add src/ to path
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


def main():
    parser = argparse.ArgumentParser(
        description="Run TrainingOrchestrator once (for Task Scheduler)",
    )
    parser.add_argument("--algo", default="PPO", choices=["PPO", "DQN", "A2C"],
                        help="SB3 algorithm")
    parser.add_argument("--timesteps", type=int, default=5000,
                        help="Total training timesteps")
    parser.add_argument("--source", default=None,
                        help="Data source filter (default: all)")
    parser.add_argument("--interval", type=float, default=24.0,
                        help="Scheduling interval in hours (default: 24)")

    args = parser.parse_args()

    # Warm registry for accurate data
    print("Warming worm registry...", flush=True)
    try:
        from CORE.worm_registry import discover_worms
        n = discover_worms()
        print(f"  {n} worms registered", flush=True)
    except Exception as e:
        print(f"  [WARN] Registry warm failed: {e}", flush=True)

    print(f"Starting TrainingOrchestrator (algo={args.algo}, "
          f"timesteps={args.timesteps}, source={args.source or 'all'})...",
          flush=True)

    try:
        from CORE.WORMS.expansion.scheduling import TrainingOrchestrator, OrchestratorConfig

        config = OrchestratorConfig(
            algo=args.algo,
            total_timesteps=args.timesteps,
            source_filter=args.source,
            interval_hours=args.interval,
            record_to_memory=True,
            register_model=True,
        )
        orch = TrainingOrchestrator(config)

        t0 = time.time()
        result = orch.execute()
        elapsed = time.time() - t0

        print("=" * 60)
        print(f"  TrainingOrchestrator — Run Complete")
        print("=" * 60)
        print(f"  Run ID:       {result.run_id}")
        print(f"  Algorithm:    {result.algo}")
        print(f"  Trained:      {result.trained}")
        print(f"  Timesteps:    {result.total_timesteps}")
        print(f"  Records used: {result.records_used}")
        print(f"  Data source:  {result.data_source}")
        print(f"  Model ver:    {result.model_version or 'N/A'}")
        print(f"  Duration:     {result.duration_ms:.0f}ms ({elapsed:.1f}s)")
        if result.error:
            print(f"  Error:        {result.error}")
        print("=" * 60)

        # Return exit code based on success
        if result.trained:
            print("STATUS: TRAINING SUCCESSFUL", flush=True)
            return 0
        elif result.error:
            print(f"STATUS: TRAINING FAILED — {result.error}", flush=True)
            return 2
        else:
            print("STATUS: TRAINING SKIPPED (no data or SB3 not available)", flush=True)
            return 1

    except Exception as e:
        print(f"STATUS: CRITICAL ERROR — {e}", flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
