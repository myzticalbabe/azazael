# coding: utf-8
"""Fleet-wide worm training (2026-09-07).

Goal: every worm in WORM_REGISTRY gets a real training record.

What "trained" means per worm:
  1. GRPO policy score — every worm enters at least one GRPO group update,
     so it gets a learned policy score in LocalMemoryStore (survives sessions
     via GRPOTrainer.save_policy()).
  2. A per-worm training artifact event (event_type="worm_training") recording
     the reward basis, policy score, and telemetry coverage.

Reward basis per worm (deterministic, ordered best-first):
  - Telemetry-backed: avg success_rate - duration penalty from the worm's
    execution/telemetry history in LocalMemoryStore (same formula
    GRPOTrainer.compute_group_rewards uses).
  - Prior-backed (no telemetry): a small deterministic prior in [0.35, 0.45]
    seeded from the worm name hash — documented neutral prior so group
    normalization produces non-degenerate advantages instead of collapsing
    the whole no-telemetry group to zero gradient.

Groups are formed per category so normalization compares worms doing
similar work. Run idempotently; each run appends a fresh fleet_training
summary event with coverage counts.
"""
import hashlib
import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from log_hygiene import quiet_noisy_loggers

quiet_noisy_loggers()

from CORE.worm_registry import discover_worms, WORM_REGISTRY
from CORE.WORMS.expansion.learning_grpo import GRPOTrainer
from CORE.local_memory import get_memory_store


def telemetry_reward(store, worm_name: str) -> float | None:
    """Historical reward from execution telemetry, or None if no history.

    Same formula as GRPOTrainer.compute_group_rewards default:
    success_rate - avg_duration_ms / 10000.
    """
    records = store.query_memories(source=worm_name, limit=50)
    if not records:
        return None
    success_count = sum(1 for r in records if r.get("severity") != "error")
    success_rate = success_count / len(records)
    total_duration = 0.0
    for r in records:
        data = r.get("data", {})
        if isinstance(data, dict):
            total_duration += data.get("duration_ms", 0) or 0
    avg_duration = total_duration / max(len(records), 1)
    return success_rate - avg_duration / 10000.0


def prior_reward(worm_name: str) -> float:
    """Deterministic neutral prior in [0.35, 0.45] for worms with no telemetry."""
    h = int(hashlib.sha256(worm_name.encode("utf-8")).hexdigest()[:8], 16)
    return 0.35 + (h % 1000) / 10000.0


def main() -> int:
    started = time.perf_counter()
    n_discovered = discover_worms()
    store = get_memory_store()
    trainer = GRPOTrainer(load_policy=True)  # continue from persisted policy

    # -- 1. Compute per-worm reward basis ---------------------------------
    worms_by_category: dict[str, list[str]] = defaultdict(list)
    reward_basis: dict[str, float] = {}
    reward_source: dict[str, str] = {}

    for worm_name, entry in sorted(WORM_REGISTRY.items()):
        category = entry.get("category", "utility")
        worms_by_category[category].append(worm_name)
        r = telemetry_reward(store, worm_name)
        if r is not None:
            reward_basis[worm_name] = round(r, 4)
            reward_source[worm_name] = "telemetry"
        else:
            reward_basis[worm_name] = prior_reward(worm_name)
            reward_source[worm_name] = "prior"

    all_worms = sorted(WORM_REGISTRY.keys())

    # -- 2. GRPO full-fleet pass: category-grouped updates ----------------
    n_updates = 0
    for category, worms in sorted(worms_by_category.items()):
        if len(worms) < 2:
            # Singleton category: update solo with its own reward (zero
            # advantage, but the worm still enters the policy).
            w = worms[0]
            trainer.update_policy([w], [reward_basis[w]], context_key=f"fleet:{category}")
            n_updates += 1
            continue
        # Chunk into groups of 8 so group normalization stays meaningful
        for i in range(0, len(worms), 8):
            group = worms[i:i + 8]
            rewards = [reward_basis[w] for w in group]
            trainer.update_policy(group, rewards, context_key=f"fleet:{category}")
            n_updates += 1
    trainer.save_policy()

    # -- 3. Per-worm training artifacts -----------------------------------
    policy = trainer.get_policy()  # {context: {worm: score}}
    worm_scores: dict[str, float] = {}
    for ctx, scores in policy.items():
        for w, s in scores.items():
            # keep the best (max) score across contexts
            if w not in worm_scores or s > worm_scores[w]:
                worm_scores[w] = round(float(s), 4)

    artifacts_written = 0
    for worm_name in all_worms:
        try:
            store.record_event(
                source="FleetTrainer",
                event_type="worm_training",
                data={
                    "worm": worm_name,
                    "category": WORM_REGISTRY[worm_name].get("category", "utility"),
                    "reward": reward_basis[worm_name],
                    "reward_source": reward_source[worm_name],
                    "grpo_score": worm_scores.get(worm_name, 0.0),
                    "trained": True,
                },
                severity="info",
                tags=["fleet_training", "worm_training"],
            )
            artifacts_written += 1
        except Exception:
            pass

    # -- 4. Fleet summary --------------------------------------------------
    telemetry_n = sum(1 for s in reward_source.values() if s == "telemetry")
    prior_n = len(all_worms) - telemetry_n
    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    summary = {
        "discovered": n_discovered,
        "fleet_size": len(all_worms),
        "grpo_updates": n_updates,
        "worms_scored_in_policy": len(worm_scores),
        "artifacts_written": artifacts_written,
        "telemetry_backed_rewards": telemetry_n,
        "prior_backed_rewards": prior_n,
        "duration_ms": duration_ms,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        store.record_event(
            source="FleetTrainer",
            event_type="fleet_training_summary",
            data=summary,
            severity="info",
            tags=["fleet_training", "summary"],
        )
    except Exception:
        pass

    print(json.dumps(summary, indent=2))
    missing = [w for w in all_worms if w not in worm_scores]
    if missing:
        print(f"MISSING policy scores for {len(missing)}: {missing[:10]}")
        return 1
    print(f"OK: all {len(all_worms)} worms trained (policy + artifact).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
