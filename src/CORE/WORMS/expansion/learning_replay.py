# coding: utf-8
"""
learning_replay.py — PrioritizedReplayBuffer (fast-loading focused module)

Extracted from learning.py (103K monolith) to avoid loading the entire
module when only the replay buffer is needed. This module is ~250 lines
and loads in milliseconds vs 300s+ for the full learning.py.

Used by:
- scheduling.py (PrioritizedReplayBuffer for scheduled training)
- learning.py (re-exported for backward compatibility)
"""

import random
import threading
from typing import Any


class PrioritizedReplayBuffer:
    """Prioritized experience replay for RL training.

    Stores (state, action, reward, next_state, done) tuples with
    priorities based on TD-error. High-error experiences are replayed
    more often, improving sample efficiency.

    Uses proportional prioritization: P(i) = p_i^alpha / sum(p_k^alpha).
    Importance sampling (IS) weights correct for the bias.

    Usage:
        buffer = PrioritizedReplayBuffer(capacity=10000)

        # Add experiences
        buffer.add(state_key, action, reward, next_state_key, done=False)

        # Sample a batch (priority-weighted)
        batch, indices, weights = buffer.sample(batch_size=32)

        # Update priorities after training step
        buffer.update_priorities(indices, td_errors)
    """

    VERSION = "1.0.0"

    def __init__(self, capacity: int = 10000, alpha: float = 0.6,
                 beta_start: float = 0.4, beta_frames: int = 100000):
        """
        Args:
            capacity: Maximum buffer size.
            alpha: Prioritization exponent (0 = uniform, 1 = full priority).
            beta_start: Initial IS weight correction.
            beta_frames: Frames to anneal beta to 1.0.
        """
        self._capacity = capacity
        self._alpha = alpha
        self._beta_start = beta_start
        self._beta_frames = beta_frames
        self._frame = 0

        self._buffer: list[tuple] = []  # (state, action, reward, next_state, done)
        self._priorities: list[float] = []
        self._position = 0
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        """Current buffer size."""
        return len(self._buffer)

    def add(self, state: str, action: int, reward: float,
            next_state: str, done: bool = False):
        """Add an experience with maximum priority (will be sampled soon)."""
        max_priority = max(self._priorities) if self._priorities else 1.0
        experience = (state, action, reward, next_state, done)

        with self._lock:
            if len(self._buffer) < self._capacity:
                self._buffer.append(experience)
                self._priorities.append(max_priority)
            else:
                self._buffer[self._position] = experience
                self._priorities[self._position] = max_priority
            self._position = (self._position + 1) % self._capacity

    def sample(self, batch_size: int) -> tuple[list[tuple], list[int], list[float]]:
        """Sample a batch with priority-weighted probability.

        Returns:
            (batch, indices, is_weights) where batch is a list of
            (state, action, reward, next_state, done) tuples.
        """
        with self._lock:
            n = len(self._buffer)
            if n == 0:
                return [], [], []
            batch_size = min(batch_size, n)

            # Compute sampling probabilities
            priorities = self._priorities[:n]
            powered = [p ** self._alpha for p in priorities]
            total = sum(powered)
            if total <= 0:
                probs = [1.0 / n] * n
            else:
                probs = [p / total for p in powered]

            # Sample indices without replacement
            indices = []
            available = set(range(n))
            for _ in range(batch_size):
                if not available:
                    break
                # Weighted random choice from available
                avail_list = sorted(available)
                avail_probs = [probs[i] for i in avail_list]
                avail_total = sum(avail_probs)
                if avail_total <= 0:
                    chosen_idx = avail_list[0]
                else:
                    r = random.random() * avail_total
                    cumsum = 0.0
                    chosen_idx = avail_list[0]
                    for idx, p in zip(avail_list, avail_probs):
                        cumsum += p
                        if cumsum >= r:
                            chosen_idx = idx
                            break
                indices.append(chosen_idx)
                available.discard(chosen_idx)

            # Compute IS weights: w_i = (1/N * 1/P(i))^beta
            self._frame += 1
            beta = min(1.0, self._beta_start +
                       (1.0 - self._beta_start) * self._frame / max(self._beta_frames, 1))

            weights = []
            max_weight = 0.0
            for idx in indices:
                w = (n * probs[idx]) ** (-beta)
                weights.append(w)
                if w > max_weight:
                    max_weight = w

            # Normalize weights
            if max_weight > 0:
                weights = [w / max_weight for w in weights]

            batch = [self._buffer[i] for i in indices]

        return batch, indices, weights

    def update_priorities(self, indices: list[int], td_errors: list[float]):
        """Update priorities based on new TD-errors.

        Args:
            indices: Buffer indices of the experiences.
            td_errors: Absolute TD-errors for each experience.
        """
        with self._lock:
            for idx, td_error in zip(indices, td_errors):
                if 0 <= idx < len(self._priorities):
                    self._priorities[idx] = abs(td_error) + 1e-6

    def add_from_memories(self, records: list[dict],
                          q_table: dict[str, dict[int, float]] = None) -> int:
        """Bulk-add experiences from LocalMemoryStore records.

        Converts memory records into (state, action, reward, next_state, done)
        tuples using the same state/reward logic as RLTrainLoop.

        Args:
            records: list of memory dicts from DataPipelineWorm.
            q_table: Optional Q-table for computing TD-errors as initial priorities.

        Returns:
            Number of experiences added.
        """
        count = 0
        for i, record in enumerate(records):
            src = record.get("source", "unknown")
            sev = record.get("severity", "info")
            state = f"{src}:{sev}"

            # Next state from next record (wraps around)
            next_record = records[(i + 1) % len(records)]
            next_src = next_record.get("source", "unknown")
            next_sev = next_record.get("severity", "info")
            next_state = f"{next_src}:{next_sev}"

            # Reward: same as RLTrainLoop
            data = record.get("data", {})
            if isinstance(data, dict):
                duration = data.get("duration_ms", 0)
                success = sev != "error"
                reward = 1.0 if success else -1.0
                if duration:
                    reward -= duration / 10000.0
            else:
                reward = 0.0

            # Action: epsilon-greedy from Q-table or random
            if q_table and state in q_table:
                action = max(q_table[state], key=q_table[state].get)
            else:
                action = random.randint(0, 3)

            # Compute initial priority from TD-error if Q-table available
            if q_table and state in q_table:
                old_q = q_table[state].get(action, 0.0)
                next_max_q = max(q_table[next_state].values(), default=0.0) if next_state in q_table else 0.0
                td_error = abs(reward + 0.9 * next_max_q - old_q)
            else:
                td_error = 1.0  # Unknown state = high priority

            experience = (state, action, reward, next_state,
                          (i == len(records) - 1))
            with self._lock:
                if len(self._buffer) < self._capacity:
                    self._buffer.append(experience)
                    self._priorities.append(td_error + 1e-6)
                else:
                    self._buffer[self._position] = experience
                    self._priorities[self._position] = td_error + 1e-6
                self._position = (self._position + 1) % self._capacity
            count += 1

        return count

    def get_stats(self) -> dict[str, Any]:
        """Get buffer statistics."""
        with self._lock:
            n = len(self._buffer)
            if n == 0:
                return {"size": 0, "capacity": self._capacity}
            avg_priority = sum(self._priorities[:n]) / n
            max_priority = max(self._priorities[:n])
            min_priority = min(self._priorities[:n])
        return {
            "size": n,
            "capacity": self._capacity,
            "alpha": self._alpha,
            "avg_priority": round(avg_priority, 4),
            "max_priority": round(max_priority, 4),
            "min_priority": round(min_priority, 4),
            "fill_pct": round(n / self._capacity * 100, 1),
            "frame": self._frame,
        }

    def get_summary(self) -> dict[str, Any]:
        """Worm contract: return a summary dict (see BaseWormMixin).

        `PrioritizedReplayBuffer` was split out of the `learning.py` monolith
        without a `get_summary()`, so the smoke test that instantiates every
        registered worm saw `None` here. `get_stats()` already computes the
        buffer telemetry; this only adds the `success` envelope the registry
        executors expect.
        """
        return {"success": True, "method": "get_stats", "result": self.get_stats()}
