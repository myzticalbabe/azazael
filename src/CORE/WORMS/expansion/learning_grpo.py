# coding: utf-8
"""
learning_grpo.py — GRPOTrainer + ABTestRunner (fast-loading focused module)

Extracted from learning.py (103K monolith) to avoid loading the entire
module when only GRPO or A/B testing is needed. This module is ~600 lines
and loads in milliseconds vs 300s+ for the full learning.py.

Used by:
- WORM_SELECTOR.py (GRPO policy for worm selection)
- scheduling.py (GRPO for scheduled training pipeline)
"""

import json
import math
import time
import random
import threading
from typing import Any, Callable

# -- Worm Registry Import ---------------------------------------------
try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls


# -- GRPO Trainer -----------------------------------------------------------


class GRPOTrainer:
    """Group Relative Policy Optimization for worm selection.

    For each task, generates a group of candidate worms, scores them
    relative to each other, and updates the policy using group-normalized
    advantages. No separate critic model needed (unlike PPO).

    Based on DeepSeek-R1's GRPO approach: normalize rewards within
    each group to compute advantages, then apply policy gradient.

    Usage:
        trainer = GRPOTrainer()

        # Generate candidates for a task
        candidates = trainer.generate_group(task_context, group_size=8)

        # Run each candidate and record rewards
        rewards = trainer.compute_group_rewards(candidates, task_context)

        # Update policy
        trainer.update_policy(candidates, rewards)

        # Get recommended worm for a task
        best = trainer.select_best(task_context)
    """

    VERSION = "1.0.0"

    def __init__(self, beta: float = 0.04, lr: float = 0.01, load_policy: bool = True):
        """
        Args:
            beta: KL penalty coefficient (higher = more conservative).
            lr: Policy learning rate.
            load_policy: If True, auto-load persisted policy from LocalMemoryStore
                          on init. set to False for testing with clean state.
        """
        self._beta = beta
        self._lr = lr
        self._policy: dict[str, dict[str, float]] = {}  # context -> {worm: score}
        self._history: list[dict] = []
        self._lock = threading.Lock()
        # Auto-load persisted policy from LocalMemoryStore
        if load_policy:
            self.load_policy()

    def generate_group(self, task_context: dict, group_size: int = 8) -> list[str]:
        """Generate a group of candidate worms for a task.

        Selects candidates from WORM_REGISTRY using SpawnDiversityEngine
        weighted selection, with some random exploration.

        Args:
            task_context: dict with task_type, category, etc.
            group_size: Number of candidates to generate.

        Returns:
            list of worm names.
        """
        try:
            from CORE.worm_registry import WORM_REGISTRY
        except ImportError:
            return []

        registry = WORM_REGISTRY
        if not registry:
            return []

        # Get all worm names, prefer matching category
        preferred_category = task_context.get("category", "")
        all_worms = list(registry)

        # Split into preferred (matching category) and others
        preferred = [w for w in all_worms
                     if registry[w].get("category") == preferred_category]
        others = [w for w in all_worms if w not in preferred]

        # Shuffle both lists
        random.shuffle(preferred)
        random.shuffle(others)

        # Fill group: preferred first, then others
        candidates = []
        for w in preferred:
            if len(candidates) >= group_size:
                break
            candidates.append(w)
        for w in others:
            if len(candidates) >= group_size:
                break
            if w not in candidates:
                candidates.append(w)

        return candidates[:group_size]

    def compute_group_rewards(self, group: list[str], task_context: dict,
                              evaluator: Callable = None) -> list[float]:
        """Compute rewards for each candidate in the group.

        Args:
            group: list of worm names.
            task_context: Task context dict.
            evaluator: Optional callable(worm_name, context) -> reward.
                      If None, uses historical performance from LocalMemoryStore.

        Returns:
            list of reward floats (one per candidate, same order).
        """
        if evaluator:
            return [evaluator(w, task_context) for w in group]

        # Default: score from REAL execution history. The old default queried
        # event_type="worm_execution" — a legacy event NO producer records, so
        # every worm scored a flat 0.0 and the GRPO policy update was a no-op
        # (fix, 2026-09-08). Real signal streams, in preference order:
        #   1. cluster_execution_completed / nature_cluster_executed
        #      (modern cluster events, recorded by NATURE_CLUSTERS/CLUSTERWORMS)
        #   2. any recent events from that worm source (fallback), minus
        #      self-recorded training bookkeeping
        # Reward = success_rate - duration penalty (success = severity != error).
        rewards = []
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            event_prefs = ("cluster_execution_completed", "nature_cluster_executed")
            for worm_name in group:
                records = []
                for et in event_prefs:
                    records = store.query_memories(
                        source=worm_name, event_type=et, limit=20)
                    if records:
                        break
                if not records:
                    records = store.query_memories(source=worm_name, limit=20)
                if records:
                    success_count = sum(1 for r in records if r.get("severity") != "error")
                    success_rate = success_count / len(records)
                    avg_duration = 0.0
                    for r in records:
                        data = r.get("data", {})
                        if isinstance(data, dict):
                            avg_duration += data.get("duration_ms", 0)
                    avg_duration /= max(len(records), 1)
                    reward = success_rate - avg_duration / 10000.0
                else:
                    reward = 0.0  # No execution history yet: neutral reward
                rewards.append(reward)
        except Exception:
            rewards = [0.0] * len(group)

        return rewards

    def compute_advantages(self, rewards: list[float],
                             global_stats: tuple | None = None) -> list[float]:
        """Group-normalized advantages + REINFORCE++ global-norm fallback.

        DAPO: if std_r < 1e-4 (zero-variance group) return [] to signal skip.
        REINFORCE++: if global_stats (mean, std) given, use global std.
        """
        if not rewards:
            return []
        mean_r = sum(rewards) / len(rewards)
        variance = sum((r - mean_r) ** 2 for r in rewards) / len(rewards)
        std_r = variance ** 0.5
        if std_r < 1e-4:
            return []  # DAPO: drop zero-gradient group, resample task
        if global_stats is not None:
            _, gstd = global_stats
            if gstd and gstd > 1e-8:
                std_r = gstd  # REINFORCE++ unbiased global norm
        return [(r - mean_r) / std_r for r in rewards]

    def update_policy(self, group: list[str], rewards: list[float],
                      context_key: str = "default"):
        """Update the policy using GRPO.

        Applies policy gradient with group-normalized advantages:
        policy[worm] += lr * advantage * (1 - beta * kl_penalty)

        Args:
            group: list of worm names.
            rewards: list of rewards (same order as group).
            context_key: Key for the policy context (e.g., task_type).
        """
        advantages = self.compute_advantages(rewards)

        # DAPO: skip no-signal groups instead of no-op update. The group still
        # ran in this context, so register it (with neutral scores) before
        # returning -- get_policy() must report every evaluated context, even
        # ones that produced no gradient.
        if not advantages:
            with self._lock:
                policy = self._policy.setdefault(context_key, {})
                for worm in group:
                    policy.setdefault(worm, 0.0)
            return {"skipped": True, "reason": "zero-variance"}

        with self._lock:
            if context_key not in self._policy:
                self._policy[context_key] = {}

            policy = self._policy[context_key]

            # Initialize new worms with neutral score
            for worm in group:
                if worm not in policy:
                    policy[worm] = 0.0

            # TR-GRPO token-regulate analogue: downweight fluke winners.
            # w = clip(1.5*sigmoid((p-0.3)/0.1), 0.5, 1.5) on softmax scores.
            import math
            exps = {w: math.exp(policy[w]) for w in group}
            denom = sum(exps.values()) or 1.0
            probs = {w: exps[w] / denom for w in group}

            def tr_w(p):
                return min(1.5, max(0.5, 1.5 / (1.0 + math.exp(-(p - 0.3) / 0.1))))

            # Policy gradient update with KL penalty (k2 form: 0.5*(s-ref)^2)
            ref = getattr(self, "_ref_policy", {}).get(context_key, {})
            for worm, advantage in zip(group, advantages):
                old_score = policy[worm]
                # KL penalty: penalize large changes from old policy
                kl_penalty = self._beta * old_score
                w = tr_w(probs[worm])
                # Update: move in direction of advantage, penalized by KL
                policy[worm] += self._lr * (w * advantage - kl_penalty)

            # Normalize scores to prevent drift
            scores = list(policy.values())
            if scores:
                max_abs = max(abs(s) for s in scores) if scores else 1.0
                if max_abs > 10.0:
                    scale = 10.0 / max_abs
                    for w in policy:
                        policy[w] *= scale

        # Record history
        entry = {
            "group": group,
            "rewards": rewards,
            "advantages": advantages,
            "context_key": context_key,
            "timestamp": time.time(),
        }
        with self._lock:
            self._history.append(entry)
            if len(self._history) > 500:
                self._history = self._history[-500:]

        # Persist to LocalMemoryStore
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            best_idx = rewards.index(max(rewards))
            store.record_event(
                source="GRPOTrainer", event_type="policy_update",
                data={
                    "context_key": context_key,
                    "group_size": len(group),
                    "best_worm": group[best_idx],
                    "best_reward": round(max(rewards), 4),
                    "avg_reward": round(sum(rewards) / len(rewards), 4),
                },
                severity="info", tags=["grpo", "policy", context_key],
            )
        except Exception:
            pass

        # Auto-save full policy snapshot after every update
        self.save_policy()

    def select_best(self, context_key: str = "default") -> (str | None):
        """Select the best worm for a given context based on learned policy.

        Args:
            context_key: Policy context key.

        Returns:
            Best worm name, or None if no policy exists.
        """
        with self._lock:
            policy = self._policy.get(context_key, {})
        if not policy:
            return None
        best = max(policy, key=policy.get)
        # Evolution joint: blend metacognition confidence into selection.
        # Unknown worms score neutral (0.5x2 = unchanged order). Any failure
        # keeps GRPO order. See MetaCognitionWorm.get_confidence.
        try:
            from CORE.WORMS.expansion.meta_cognition import MetaCognitionWorm
            mc = MetaCognitionWorm()

            def _blended(w):
                try:
                    conf = mc.get_confidence(w)
                except Exception:
                    conf = 0.5
                return policy[w] * (0.5 + conf)

            ranked = sorted(policy, key=_blended, reverse=True)
            if ranked:
                return ranked[0]
        except Exception:
            pass
        return best

    def get_policy(self, context_key: str = None) -> dict[str, Any]:
        """Get the current policy.

        Args:
            context_key: If provided, return only this context's policy.

        Returns:
            dict with policy scores.
        """
        with self._lock:
            if context_key:
                return dict(self._policy.get(context_key, {}))
            return {k: dict(v) for k, v in self._policy.items()}

    def save_policy(self) -> bool:
        """Persist learned policy to LocalMemoryStore as JSON.

        Stores the full policy dict and recent history so the policy
        survives across sessions. Called automatically after updates.

        Returns:
            True if persisted successfully.
        """
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            with self._lock:
                policy_data = {
                    k: dict(v) for k, v in self._policy.items()
                }
            store.record_event(
                source="GRPOTrainer", event_type="policy_snapshot",
                data={
                    "policy": policy_data,
                    "beta": self._beta,
                    "lr": self._lr,
                    "n_contexts": len(policy_data),
                    "total_worms": sum(len(v) for v in policy_data.values()),
                },
                severity="info", tags=["grpo", "policy", "snapshot"],
            )
            # Cleanup: delete old policy_snapshot events (keep only latest 3)
            try:
                old = store.query_memories(
                    source="GRPOTrainer", event_type="policy_snapshot", limit=50
                )
                if len(old) > 3:
                    ids_to_delete = [r["id"] for r in old[3:]]
                    # (2026-09-10, A6: routed through the public tombstone
                    # API — no more private connections.)
                    marked = store.tombstone(ids_to_delete)
                    if marked != len(ids_to_delete):
                        print("GRPO tombstone cleanup partial: %d/%d" % (
                            marked, len(ids_to_delete)), flush=True)
            except Exception as e:  # noqa: BLE001 — logged, never silent
                print("GRPO tombstone cleanup failed: %s" % str(e)[:160], flush=True)
            return True
        except Exception:
            return False

    def load_policy(self) -> bool:
        """Load persisted policy from LocalMemoryStore.

        Queries the most recent policy_snapshot event and restores
        the learned policy. Called automatically on init.

        Returns:
            True if policy was loaded successfully.
        """
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            events = store.query_memories(
                source="GRPOTrainer", event_type="policy_snapshot", limit=1
            )
            if not events:
                return False
            data = events[0].get("data", {})
            if isinstance(data, str):
                data = json.loads(data)
            if not isinstance(data, dict) or "policy" not in data:
                return False
            with self._lock:
                for ctx, worms in data["policy"].items():
                    if isinstance(worms, dict):
                        self._policy[ctx] = {
                            w: float(s) for w, s in worms.items()
                        }
            return bool(self._policy)
        except Exception:
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get trainer statistics."""
        with self._lock:
            n_updates = len(self._history)
            n_contexts = len(self._policy)
            total_worms = sum(len(p) for p in self._policy.values())
            recent_rewards = []
            for entry in self._history[-10:]:
                recent_rewards.extend(entry["rewards"])
        return {
            "version": self.VERSION,
            "n_updates": n_updates,
            "n_contexts": n_contexts,
            "total_worms_scored": total_worms,
            "beta": self._beta,
            "lr": self._lr,
            "recent_avg_reward": round(
                sum(recent_rewards) / max(len(recent_rewards), 1), 4
            ) if recent_rewards else None,
        }

    def get_summary(self) -> dict[str, Any]:
        """Worm contract: return a summary dict (see BaseWormMixin).

        `GRPOTrainer` was split out of the `learning.py` monolith without a
        `get_summary()`, so the smoke test that instantiates every registered
        worm saw `None` here. `get_stats()` already computes the policy
        telemetry; this only adds the `success` envelope the registry executors
        expect.
        """
        return {"success": True, "method": "get_stats", "result": self.get_stats()}


# -- A/B Test Runner with DPO ----------------------------------------------


@register_worm(category="learning", priority=4, cooldown_seconds=120.0,
    description="A/B test runner \u2014 split-test framework with DPO preference learning")
class ABTestRunner:
    """A/B test framework with statistical analysis and DPO preference learning.

    Supports:
    - Traditional A/B tracking (impressions, conversions)
    - DPO-style pairwise preference recording (chosen vs rejected)
    - Preference score computation per variant
    - Export of preference pairs for offline DPO training

    Usage:
        runner = ABTestRunner()
        runner.create_experiment("worm_selection", ["SystemZ", "ProcessZ", "VulnScanner"])

        # Traditional tracking
        runner.track("worm_selection", "SystemZ", converted=True)

        # DPO preference recording
        runner.record_preference("worm_selection",
            chosen="SystemZ", rejected="ProcessZ",
            context={"task_type": "monitor"},
            chosen_reward=0.9, rejected_reward=0.3)

        # Get preference pairs for training
        pairs = runner.get_preference_pairs("worm_selection")
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._experiments: dict[str, dict] = {}
        self._preferences: dict[str, list[dict]] = {}  # experiment -> preference pairs
        self._lock = threading.Lock()

    def load_pairs(self, experiment: str, limit: int = 1000) -> int:
        """Hydrate in-memory pairs from persisted preference_recorded rows.

        (2026-09-10 fix: each DPO run is a fresh process, so the learner
        only ever saw that run's pairs — loss over 1 pair, history
        accumulating unread in the store. Loading first makes the loss
        cumulative. Idempotent per instance: skips already-loaded
        (chosen, rejected, timestamp) triples.)
        """
        try:
            from CORE.local_memory import get_memory_store
            store = get_memory_store()
            rows = store.query_memories(event_type="preference_recorded",
                                        limit=limit)
        except Exception:
            return 0
        import json as _json
        loaded = 0
        with self._lock:
            cur = self._preferences.setdefault(experiment, [])
            seen = {(p.get("chosen"), p.get("rejected"), p.get("timestamp"))
                    for p in cur}
            for r in reversed(rows):  # oldest first keeps chronological order
                d = r.get("data", {})
                if isinstance(d, str):
                    try:
                        d = _json.loads(d)
                    except Exception:
                        continue
                if not isinstance(d, dict) or d.get("experiment") != experiment:
                    continue
                key = (d.get("chosen"), d.get("rejected"),
                       r.get("timestamp", ""))
                if key in seen:
                    continue
                seen.add(key)
                cur.append({
                    "chosen": d.get("chosen"),
                    "rejected": d.get("rejected"),
                    "context": d.get("context") or {},
                    "chosen_reward": float(d.get("chosen_reward", 0.0)),
                    "rejected_reward": float(d.get("rejected_reward", 0.0)),
                    "reward_margin": round(float(d.get("chosen_reward", 0.0))
                                           - float(d.get("rejected_reward", 0.0)), 4),
                    "timestamp": r.get("timestamp", ""),
                })
                loaded += 1
        return loaded

    def create_experiment(self, name: str, variants: list[str]):
        with self._lock:
            self._experiments[name] = {v: {"impressions": 0, "conversions": 0} for v in variants}
            if name not in self._preferences:
                self._preferences[name] = []

    def track(self, experiment: str, variant: str, converted: bool):
        with self._lock:
            exp = self._experiments.get(experiment, {})
            if variant in exp:
                exp[variant]["impressions"] += 1
                if converted:
                    exp[variant]["conversions"] += 1

    def record_preference(self, experiment: str, chosen: str, rejected: str,
                          context: dict = None, chosen_reward: float = 0.0,
                          rejected_reward: float = 0.0) -> dict[str, Any]:
        """Record a DPO-style pairwise preference.

        When two variants are evaluated on the same task, record which
        one performed better. This builds a preference dataset for
        Direct Preference Optimization training.

        Args:
            experiment: Experiment name.
            chosen: The better-performing variant.
            rejected: The worse-performing variant.
            context: Task context (task_type, source, etc.).
            chosen_reward: Reward for chosen variant.
            rejected_reward: Reward for rejected variant.

        Returns:
            The recorded preference entry.
        """
        entry = {
            "chosen": chosen,
            "rejected": rejected,
            "context": context or {},
            "chosen_reward": chosen_reward,
            "rejected_reward": rejected_reward,
            "reward_margin": round(chosen_reward - rejected_reward, 4),
            "timestamp": time.time(),
        }
        with self._lock:
            if experiment not in self._preferences:
                self._preferences[experiment] = []
            self._preferences[experiment].append(entry)

        # Persist to LocalMemoryStore
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            store.record_event(
                source="ABTestRunner", event_type="preference_recorded",
                data={
                    "experiment": experiment,
                    "chosen": chosen,
                    "rejected": rejected,
                    "context": context or {},
                    "chosen_reward": chosen_reward,
                    "rejected_reward": rejected_reward,
                },
                severity="info", tags=["dpo", "preference", experiment],
            )
        except Exception:
            pass

        return entry

    def get_preference_pairs(self, experiment: str,
                             limit: int = 1000) -> list[dict[str, Any]]:
        """Get recorded preference pairs for DPO training.

        Args:
            experiment: Experiment name.
            limit: Max pairs to return.

        Returns:
            list of preference pair dicts.
        """
        with self._lock:
            pairs = list(self._preferences.get(experiment, []))
        return pairs[-limit:]

    def compute_preference_scores(self, experiment: str) -> dict[str, dict[str, Any]]:
        """Compute preference scores for each variant.

        A variant's preference score is the fraction of pairwise
        comparisons where it was chosen over the other variant.

        Args:
            experiment: Experiment name.

        Returns:
            dict mapping variant -> {chosen_count, rejected_count, preference_score}.
        """
        with self._lock:
            pairs = list(self._preferences.get(experiment, []))

        scores: dict[str, dict[str, int]] = {}
        for pair in pairs:
            chosen = pair["chosen"]
            rejected = pair["rejected"]
            if chosen not in scores:
                scores[chosen] = {"chosen_count": 0, "rejected_count": 0}
            if rejected not in scores:
                scores[rejected] = {"chosen_count": 0, "rejected_count": 0}
            scores[chosen]["chosen_count"] += 1
            scores[rejected]["rejected_count"] += 1

        result = {}
        for variant, counts in scores.items():
            total = counts["chosen_count"] + counts["rejected_count"]
            result[variant] = {
                "chosen_count": counts["chosen_count"],
                "rejected_count": counts["rejected_count"],
                "total_comparisons": total,
                "preference_score": round(
                    counts["chosen_count"] / max(total, 1), 4
                ),
            }
        return result

    def compute_dpo_loss(self, experiment: str, beta: float = 0.1) -> dict[str, Any]:
        """Compute DPO loss from preference pairs.

        DPO loss = -mean(log(sigmoid(beta * (r_chosen - r_rejected)))).
        A lower loss means the reward model better explains the preferences.

        Args:
            experiment: Experiment name.
            beta: Temperature parameter (higher = more conservative).

        Returns:
            dict with loss value and diagnostics.
        """
        with self._lock:
            pairs = list(self._preferences.get(experiment, []))

        if not pairs:
            return {"loss": None, "n_pairs": 0, "error": "No preference pairs"}

        losses = []
        for pair in pairs:
            margin = pair["chosen_reward"] - pair["rejected_reward"]
            x = beta * margin
            loss_val = math.log(1.0 + math.exp(-x))
            losses.append(loss_val)

        avg_loss = sum(losses) / len(losses)
        return {
            "loss": round(avg_loss, 6),
            "n_pairs": len(pairs),
            "beta": beta,
            "avg_margin": round(
                sum(p["chosen_reward"] - p["rejected_reward"] for p in pairs) / len(pairs), 4
            ),
        }

    def get_results(self, experiment: str) -> dict[str, Any]:
        with self._lock:
            exp = self._experiments.get(experiment, {})
        results = {}
        for var, metrics in exp.items():
            rate = metrics["conversions"] / max(metrics["impressions"], 1)
            results[var] = {"conversion_rate": round(rate, 4), **metrics}

        # Include preference scores if available
        pref_scores = self.compute_preference_scores(experiment)
        for var, pref in pref_scores.items():
            if var in results:
                results[var]["preference_score"] = pref["preference_score"]
                results[var]["preference_count"] = pref["total_comparisons"]
            else:
                results[var] = pref

        return {"experiment": experiment, "variants": results}

    def get_summary(self):
        return {"status":"ok","worm":"ABTestRunner"}
