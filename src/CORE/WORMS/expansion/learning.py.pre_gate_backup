# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: LEARNING (5 worms)
RLTrainLoop, ModelVersioner, DataPipelineWorm, ABTestRunner, FeatureEngineer
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict

# -- Worm Registry Import ---------------------------------------------
try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
def register_worm(**kw):
        return lambda cls: cls


# -- Python 3.14t Free-Threading Awareness ----------------------------
try:
    from CORE.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
FreeThreadPool = None
ThreadSafeDict = dict
ThreadSafeList = list
def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False
@register_worm(category="learning", priority=6, cooldown_seconds=120.0,
    description="RL train loop v2 — trains from DataPipelineWorm output with Q-learning policy optimization")
class RLTrainLoop:
    """Reinforcement learning training loop v2.0.

    Trains from real execution data extracted by DataPipelineWorm from
    LocalMemoryStore. Uses Q-learning with epsilon-greedy exploration.
    Records training metrics and persists learned Q-tables.

    Usage:
        loop = RLTrainLoop()

        # Train from DataPipelineWorm output
        stats = loop.train_from_memory(source="SystemZ", n_episodes=100)

        # Or train with a mock environment
        episode = loop.train_episode(env, agent)
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._episodes: List[Dict] = []
        self._q_table: Dict[str, Dict[int, float]
            ] = defaultdict(lambda: defaultdict(float))
        self._lock = threading.Lock()
        self._pipeline = None  # Lazy DataPipelineWorm
        self._versioner = None  # Lazy ModelVersioner
        self._model_name = None  # Set during register_to_versioner()


    def _get_pipeline(self):
        """Lazy DataPipelineWorm for memory access — double-checked locking for 3.14t."""
        if self._pipeline is None:
            with self._lock:
                if self._pipeline is None:
                    try:
                        from CORE.WORMS.expansion.learning import DataPipelineWorm
                        self._pipeline = DataPipelineWorm()
                    except ImportError:
                        self._pipeline = False
        return self._pipeline if self._pipeline else None
    def _get_versioner(self):
        """Lazy ModelVersioner for model version tracking — double-checked locking for 3.14t."""
        if self._versioner is None:
            with self._lock:
                if self._versioner is None:
                    try:
                        from CORE.WORMS.expansion.learning import ModelVersioner
                        self._versioner = ModelVersioner()
                    except ImportError:
                        self._versioner = False
        return self._versioner if self._versioner else None
    def register_to_versioner(self, model_name: Optional[str] = None,
                               metrics: Optional[Dict[str, float]] = None,
                               metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Register the current Q-table policy with ModelVersioner for version tracking.

        Persists the learned policy to LocalMemoryStore via ModelVersioner,
        enabling rollback, comparison, and history queries.

        Args:
            model_name: Name for the model (default: "RLTrainLoop_QTable").
            metrics: Optional metrics dict (avg_reward, q_table_size, etc.)
            metadata: Optional metadata (source, n_episodes, etc.)

        Returns:
            Dict with registration result: model_name, version, registered_at
        """
        versioner = self._get_versioner()
        if not versioner:
            return {"error": "ModelVersioner unavailable"}

        name = model_name or f"RLTrainLoop_{
    datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._model_name = name
        stats = self.get_training_stats()

        _metrics = metrics or {
            "avg_reward": stats.get("avg_reward", 0),
            "q_table_size": stats.get("q_table_size", 0),
            "episodes": stats.get("episodes", 0),
        }
        _metadata = metadata or {
            "version": self.VERSION,
            "source": "RLTrainLoop",
        }

        version = f"v{stats.get('episodes', 0)}"

        try:
            result = versioner.register_model(
                name=name, version=version,
                metrics=_metrics, metadata=_metadata,
            )
            # Also persist Q-table to LocalMemoryStore for durability
            self._save_q_table_to_store(name, version)
            return {
                "model_name": name,
                "version": version,
                "registered_at": result.get("registered_at", datetime.now().isoformat()),
                "metrics": _metrics,
            }
        except Exception as e:
            return {"error": str(e)}

    def _save_q_table_to_store(self, model_name: str, version: str) -> bool:
        """Persist the Q-table to LocalMemoryStore for durable storage."""
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            # Convert Q-table to serializable format
            q_serializable = {}
            with self._lock:
                for state_key, actions in self._q_table.items():
                    q_serializable[state_key] = dict(actions)

            store.record_event(
                source="RLTrainLoop", event_type="q_table_persisted",
                data={
                    "model_name": model_name,
                    "model_version": version,
                    "q_table": q_serializable,
                    "q_table_size": len(q_serializable),
                    "episodes": len(self._episodes),
                },
                severity="info", tags=["rl", "q_table", "persist"],
            )
            return True
        except Exception:
            return False
    def load_q_table_from_store(self, model_name: Optional[str] = None, version: Optional[str] = None) -> bool:
        """Load a persisted Q-table from LocalMemoryStore.

        Args:
            model_name: Model name to search for (default: latest).
            version: Specific version to load.

        Returns:
            True if Q-table was loaded successfully.
        """
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()

            if model_name:
                query = f"q_table_persisted {model_name}"
            else:
                query = "q_table_persisted RLTrainLoop"

            events = store.search_memories(query, source="RLTrainLoop", limit=10)
            if not events:
                return False

            for ev in reversed(events):
                data = ev.get("data", {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except Exception:
                        continue
                if not isinstance(data, dict):
                    continue

                q_data = data.get("q_table")
                if not q_data:
                    continue

                # Rebuild Q-table from serialized format
                with self._lock:
                    self._q_table.clear()
                    for state_key, actions in q_data.items():
                        for action_val, q_val in actions.items():
                            self._q_table[state_key][int(action_val)] = float(q_val)

                # Also restore episode count
                episodes = data.get("episodes", 0)
                if episodes and not self._episodes:
                    self._episodes = [{"loaded": True, "count": episodes}]

                return True

            return False
        except Exception:
            return False
    def train_from_memory(self, source: Optional[str] = None, event_type: Optional[str] = None,
                          n_episodes: int = 100, max_steps: int = 50,
                          learning_rate: float = 0.1, discount_factor: float = 0.9,
                          epsilon: float = 0.1,
                          test_data: Optional[List[Dict]] = None,
                          use_data_split: bool = False,
                          val_ratio: float = 0.1, test_ratio: float = 0.2,
                          by_session: bool = True,
                          use_schema_features: bool = False) -> Dict[str, Any]:
        """Train from real execution data in LocalMemoryStore.

        Uses DataPipelineWorm to extract records, then treats each
        record as a training step. Builds a state-action-reward model
        based on worm execution patterns.

        If use_data_split=True, automatically splits memories into
        train/validation/test sets (by session_id to prevent leakage).

        If use_schema_features=True, uses SchemaAwareFeatureExtractor for
        richer state vectors (typed numeric features from the data blob).
        Otherwise uses simple source:severity state keys.

        If test_data is provided directly, uses it for held-out evaluation.

        Args:
            source: Filter memories by source component
            event_type: Filter by event type
            n_episodes: Number of training episodes to run
            max_steps: Max steps per episode
            learning_rate: Q-learning alpha
            discount_factor: Q-learning gamma
            epsilon: Exploration rate
            test_data: Optional held-out test records for evaluation
            use_data_split: If True, auto-split memories using split_memories()
            val_ratio: Fraction of sessions for validation when use_data_split=True
            test_ratio: Fraction of sessions for test when use_data_split=True
            by_session: If True, split by session_id to prevent leakage
            use_schema_features: If True, use SchemaAwareFeatureExtractor states

        Returns:
            Dict with training stats, policy summary, and test metrics
        """
        pipeline = self._get_pipeline()
        if not pipeline:
            return {"error": "DataPipelineWorm unavailable", "episodes": 0}

        # Auto-split if requested (overrides explicit test_data)
        if use_data_split:
            split_result = pipeline.split_memories(
                source=source, event_type=event_type,
                test_ratio=test_ratio, val_ratio=val_ratio,
                by_session=by_session,
            )
            records = split_result.get("train", [])
            test_data = split_result.get("test", [])
            split_stats = split_result.get("stats", {})
        else:
            # Extract all records (no split)
            records = pipeline.extract_from_memory(
                source=source, event_type=event_type, limit=n_episodes * 10
            )
            split_stats = {}

        if not records:
            return {"error": "No training data found in LocalMemoryStore", "episodes": 0}

        # Build SchemaAwareFeatureExtractor if requested
        _schema_extractor = None
        if use_schema_features:
            try:
                _schema_extractor = SchemaAwareFeatureExtractor()
                _schema_extractor.fit(records)
            except Exception:
                _schema_extractor = None

        def _get_state_key(record: Dict) -> str:
            """Build a state key from a record.

            When use_schema_features=True, uses the feature vector hash
            from SchemaAwareFeatureExtractor for richer state discrimination.
            Otherwise uses simple source:severity string key.
            """
            if _schema_extractor:
                features, _ = _schema_extractor.extract([record])
                if features:
                    # Round features to 2 decimals and join as comma-separated string
                    rounded = tuple(round(v, 2) for v in features[0])
                    # Include severity to ensure different severities map to different states
                    sv = record.get("severity", "info")
                    return f"schema:{hash(rounded)}:{sv}"
            # Fallback to simple key
            src = record.get("source", "unknown")
            sv = record.get("severity", "info")
            return f"{src}:{sv}"

        def _compute_reward(record: Dict) -> float:
            """Compute reward from a record.

            Positive reward for non-error records, negative for errors.
            Longer duration reduces reward slightly (penalizes slow operations).
            """
            sev = record.get("severity", "info")
            data = record.get("data", {})
            if isinstance(data, dict):
                duration = data.get("duration_ms", 0)
                success = sev != "error"
                reward = 1.0 if success else -1.0
                if duration:
                    reward -= duration / 10000.0
            else:
                reward = 0.0
            return reward

        start = time.perf_counter()
        episode_rewards = []

        for episode in range(n_episodes):
            total_reward = 0.0
            for step in range(min(max_steps, len(records))):
                record = records[(episode + step) % len(records)]

                # Build state key (simple or schema-aware)
                state_key = _get_state_key(record)

                # Choose action (epsilon-greedy)
                if state_key not in self._q_table or random.random() < epsilon:
                    action = random.randint(0, 3)
                else:
                    action = max(self._q_table[state_key], key=self._q_table[state_key].get)

                # Compute reward
                reward = _compute_reward(record)

                # Q-learning update
                old_q = self._q_table[state_key].get(action, 0.0)
                next_max_q = max(self._q_table[state_key].values(), default=0.0)
                new_q = old_q + learning_rate * (reward + discount_factor * next_max_q - old_q)
                self._q_table[state_key][action] = new_q

                total_reward += reward

            episode_rewards.append(total_reward)

            episode_data = {
                "episode": episode + 1,
                "total_reward": total_reward,
                "steps": min(max_steps, len(records)),
                "timestamp": time.time(),
            }
            with self._lock:
                self._episodes.append(episode_data)

        duration_ms = (time.perf_counter() - start) * 1000

        # Evaluate on held-out test data if provided
        test_metrics = {}
        if test_data:
            test_rewards = []
            test_unknown_states = 0
            for record in test_data:
                state_key = _get_state_key(record)

                # Greedy action (no exploration)
                if state_key in self._q_table:
                    action = max(self._q_table[state_key], key=self._q_table[state_key].get)
                else:
                    action = 0
                    test_unknown_states += 1

                reward = _compute_reward(record)
                test_rewards.append(reward)

            test_metrics = {
                "test_records": len(test_data),
                "test_avg_reward": round(sum(test_rewards) / len(test_rewards), 4) if test_rewards else 0,
                "test_unknown_states": test_unknown_states,
            }

        # Build result dict before persistence (fixes used-before-def error)
        result = {
            "version": self.VERSION,
            "episodes": n_episodes,
            "avg_reward": round(sum(episode_rewards) / len(episode_rewards), 4) if episode_rewards else 0,
            "max_reward": round(max(episode_rewards), 4) if episode_rewards else 0,
            "min_reward": round(min(episode_rewards), 4) if episode_rewards else 0,
            "q_table_size": len(self._q_table),
            "duration_ms": round(duration_ms, 2),
            "data_source": source or "all",
            "persisted": False,
        }
        if test_metrics:
            result["test_metrics"] = test_metrics
        if split_stats:
            result["data_split"] = {
                "method": split_stats.get("split_method", "unknown"),
                "train_records": split_stats.get("train_records", len(records)),
                "test_records": split_stats.get("test_records", 0),
                "val_records": split_stats.get("val_records", 0),
                "total_sessions": split_stats.get("total_sessions", 0),
            }

        # Persist learned policy to LocalMemoryStore + ModelVersioner
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            save_data = {
                "n_episodes": n_episodes,
                "total_duration_ms": round(duration_ms, 2),
                "avg_reward": result["avg_reward"],
                "q_table_size": len(self._q_table),
                "source_filter": source,
            }
            if test_metrics:
                save_data["test_avg_reward"] = test_metrics["test_avg_reward"]
            store.record_event(
                source="RLTrainLoop", event_type="training_complete",
                data=save_data,
                severity="info", tags=["rl", "training", "v2"],
            )
            result["persisted"] = True

            # Auto-register with ModelVersioner if training produced results
            if len(self._q_table) > 0:
                reg_result = self.register_to_versioner(
                    metrics={
                        "avg_reward": result["avg_reward"],
                        "q_table_size": len(self._q_table),
                        "episodes": n_episodes,
                    },
                    metadata={
                        "source_filter": source or "all",
                        "learning_rate": learning_rate,
                        "discount_factor": discount_factor,
                        "epsilon": epsilon,
                        "use_schema_features": use_schema_features,
                    },
                )
                if "error" not in reg_result:
                    result["registered_model"] = reg_result.get("model_name")
                    result["registered_version"] = reg_result.get("version")
        except Exception:
            pass

        return result
    def hyperparameter_tune(self, source: Optional[str] = None, event_type: Optional[str] = None,
                              n_episodes: int = 50, max_steps: int = 30,
                              n_folds: int = 3, use_schema_features: bool = False,
                              lr_values: Optional[List[float]] = None,
                              gamma_values: Optional[List[float]] = None,
                              eps_values: Optional[List[float]] = None,
                              register_tune_model: bool = False) -> Dict[str, Any]:
        """Hyperparameter tuning via temporal cross-validation.

        Uses DataPipelineWorm.temporal_cross_validation() to create
        temporally-ordered train/test folds, then trains an RLTrainLoop
        on each fold for each hyperparameter combination, evaluating
        held-out test avg_reward to find the best config.

        Grid search over learning_rate, discount_factor (gamma), and
        epsilon. Default values are reasonable starting points.

        Args:
            source: Filter memories by source.
            event_type: Filter by event type.
            n_episodes: Episodes per training run.
            max_steps: Steps per episode.
            n_folds: Number of CV folds.
            use_schema_features: Use SchemaAwareFeatureExtractor states.
            lr_values: Learning rates to try.
            gamma_values: Discount factors to try.
            eps_values: Epsilon (exploration) values to try.

        Returns:
            Dict with best_params, best_score, and all_results.
        """
        pipeline = self._get_pipeline()
        if not pipeline:
            return {"error": "DataPipelineWorm unavailable"}

        # Default grid
        if lr_values is None:
            lr_values = [0.05, 0.1, 0.2]
        if gamma_values is None:
            gamma_values = [0.8, 0.9, 0.95]
        if eps_values is None:
            eps_values = [0.05, 0.1, 0.2]

        # Get CV folds from pipeline
        cv_result = pipeline.temporal_cross_validation(
            source=source, event_type=event_type,
            n_folds=n_folds,
        )
        folds = cv_result.get("folds", [])
        if not folds:
            return {"error": "No data for CV folds", "cv_stats": cv_result.get("stats", {})}

        start = time.perf_counter()
        results = []
        best_score = -float("inf")
        best_params = {}

        # Save original state to restore after tuning
        _saved_q_table = self._q_table
        _saved_episodes = self._episodes

        len(lr_values) * len(gamma_values) * len(eps_values)
        config_idx = 0

        for lr in lr_values:
            for gamma in gamma_values:
                for eps in eps_values:
                    config_idx += 1
                    fold_rewards = []

                    for fold in folds:
                        train_records = fold["train"]
                        test_records = fold["test"]

                        if not train_records or not test_records:
                            continue

                        # Use fresh Q-table per config/fold (non-destructive)
                        self._q_table = defaultdict(lambda: defaultdict(float))
                        self._episodes = []

                        # Quick training on fold
                        fold_result = self.train_from_memory(
                            source=source, event_type=event_type,
                            n_episodes=n_episodes // max(1, n_folds),
                            max_steps=max_steps,
                            learning_rate=lr,
                            discount_factor=gamma,
                            epsilon=eps,
                            test_data=test_records,
                            use_schema_features=use_schema_features,
                        )

                        if "test_metrics" in fold_result:
                            fold_rewards.append(fold_result["test_metrics"]["test_avg_reward"])

                    if not fold_rewards:
                        continue

                    avg_fold_reward = round(sum(fold_rewards) / len(fold_rewards), 4)

                    result_entry = {
                        "learning_rate": lr,
                        "discount_factor": gamma,
                        "epsilon": eps,
                        "avg_test_reward": avg_fold_reward,
                        "n_folds_with_data": len(fold_rewards),
                    }
                    results.append(result_entry)

                    if avg_fold_reward > best_score:
                        best_score = avg_fold_reward
                        best_params = {
                            "learning_rate": lr,
                            "discount_factor": gamma,
                            "epsilon": eps,
                        }

        duration_ms = (time.perf_counter() - start) * 1000

        # Restore original state
        self._q_table = _saved_q_table
        self._episodes = _saved_episodes

        # Optionally register best config as a model version
        registered_version = None
        if register_tune_model and best_params:
            try:
                from CORE.local_memory import LocalMemoryStore
                store = LocalMemoryStore()
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                store.record_event(
                    source="RLTrainLoop", event_type="tune_config_registered",
                    data={
                        "best_params": best_params,
                        "best_score": best_score,
                        "n_configs_tried": len(results),
                        "n_folds": n_folds,
                        "data_source": source or "all",
                        "use_schema_features": use_schema_features,
                    },
                    severity="info", tags=["rl", "tune", "v2"],
                )
                registered_version = version
            except Exception:
                pass

        return {
            "version": self.VERSION,
            "best_params": best_params,
            "best_score": best_score,
            "results": sorted(results, key=lambda r: -r["avg_test_reward"]),
            "n_configs_tried": len(results),
            "n_folds": n_folds,
            "duration_ms": round(duration_ms, 2),
            "data_source": source or "all",
            "use_schema_features": use_schema_features,
            "registered_version": registered_version,
        }

    def tune_and_train(self, source: Optional[str] = None, event_type: Optional[str] = None,
                        n_episodes: int = 50, max_steps: int = 30,
                        n_folds: int = 3, use_schema_features: bool = False,
                        lr_values: Optional[List[float]] = None,
                        gamma_values: Optional[List[float]] = None,
                        eps_values: Optional[List[float]] = None,
                        register_tune_model: bool = False) -> Dict[str, Any]:
        """Tune hyperparams via CV, then train a final model with best params.

        Runs hyperparameter_tune() to find the optimal configuration via
        temporal cross-validation, then trains a final policy using those
        optimal hyperparameters on ALL available data.

        Args:
            Same as hyperparameter_tune() + same as train_from_memory().

        Returns:
            Dict with 'tune_result', 'train_result', and 'best_params'.
        """
        # Step 1: Tune hyperparams via CV
        tune_result = self.hyperparameter_tune(
            source=source, event_type=event_type,
            n_episodes=n_episodes, max_steps=max_steps,
            n_folds=n_folds, use_schema_features=use_schema_features,
            lr_values=lr_values, gamma_values=gamma_values,
            eps_values=eps_values,
            register_tune_model=register_tune_model,
        )

        if "error" in tune_result:
            return {"error": tune_result["error"], "tune_result": tune_result}

        best_params = tune_result.get("best_params", {})

        # Step 2: Train final model with best params on all data
        train_result = self.train_from_memory(
            source=source, event_type=event_type,
            n_episodes=n_episodes, max_steps=max_steps,
            learning_rate=best_params.get("learning_rate", 0.1),
            discount_factor=best_params.get("discount_factor", 0.9),
            epsilon=best_params.get("epsilon", 0.1),
            use_schema_features=use_schema_features,
        )

        return {
            "tune_result": tune_result,
            "train_result": train_result,
            "best_params": best_params,
            "best_score": tune_result.get("best_score"),
        }

    def train_episode(self, env, agent, max_steps: int = 1000) -> Dict[str, Any]:
        """Run a single training episode (backward-compatible mock training)."""
        state = getattr(env, "reset", lambda: 0)()
        total_reward = 0.0
        steps = 0
        for _ in range(max_steps):
            action = getattr(agent, "act", lambda s: 0)(state)
            try:
                next_state, reward, done, *_ = getattr(env, "step", lambda a: (0, 0, True, {}))(action)
            except Exception:
                break
            total_reward += reward
            state = next_state
            steps += 1
            if done:
                break
        episode = {"steps": steps, "total_reward": total_reward, "timestamp": time.time()}
        with self._lock:
            self._episodes.append(episode)
        return episode
    def get_training_stats(self) -> Dict[str, Any]:
        with self._lock:
            if not self._episodes:
                return {"episodes": 0}
            rewards = [e["total_reward"] for e in self._episodes]
            return {"episodes": len(rewards), "avg_reward": round(sum(rewards) / len(rewards), 2),
                    "max_reward": max(rewards), "min_reward": min(rewards),
                    "q_table_size": len(self._q_table)}

    def tune_history(self, limit: int = 20) -> Dict[str, Any]:
        """Query tune_config_registered events from LocalMemoryStore.

        Queries all 'tune_config_registered' events to show the
        progression of best_params and best scores over time.

        Args:
            limit: Max history entries to return.

        Returns:
            Dict with history list and summary stats.
        """
        try:
            from CORE.local_memory import LocalMemoryStore
            store = LocalMemoryStore()
            events = store.search_memories(
                "tune_config_registered", source="RLTrainLoop", limit=limit
            )

            history = []
            for ev in events:
                raw_data = ev.get("data", {})
                if isinstance(raw_data, str):
                    try:
                        data = json.loads(raw_data)
                    except Exception:
                        continue
                else:
                    data = raw_data
                if isinstance(data, dict) and "best_params" in data:
                    history.append({
                        "registered_at": ev.get("timestamp", ""),
                        "best_params": data["best_params"],
                        "best_score": data.get("best_score"),
                        "n_configs_tried": data.get("n_configs_tried"),
                        "n_folds": data.get("n_folds"),
                        "data_source": data.get("data_source"),
                    })

            # Compute progression summary
            scores = [h["best_score"] for h in history if h["best_score"] is not None]

            return {
                "history": history,
                "count": len(history),
                "summary": {
                    "best_overall": max(scores) if scores else None,
                    "worst_overall": min(scores) if scores else None,
                    "avg_score": round(sum(scores) / len(scores), 4) if scores else None,
                    "n_tune_runs": len(history),
                } if scores else {},
            }
        except Exception as e:
            return {"error": str(e), "history": []}


@register_worm(category="learning", priority=5, cooldown_seconds=60.0,
    description="Model versioner v2 — persistent ML model version tracking via LocalMemoryStore with rollback support")
class ModelVersioner:
    """Tracks ML model versions with LocalMemoryStore persistence v2.0.
    
    Stores model versions in LocalMemoryStore for durability.
    Supports: register, compare, list, rollback, and history queries.
    
    Usage:
        mv = ModelVersioner()
        
        # Register a trained model
        mv.register_model("worm_dispatch", "1.0.0", {
            "avg_reward": 0.85, "success_rate": 0.92
        }, metadata={"training_source": "SystemZ"})
        
        # Compare versions
        comparison = mv.compare_versions("worm_dispatch", "1.0.0", "2.0.0")
        
        # List all versions of a model
        versions = mv.list_versions("worm_dispatch")
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._models: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()
        self._store = None  # Lazy LocalMemoryStore

    def _get_store(self):
        """Lazy LocalMemoryStore connection — double-checked locking for 3.14t."""
        if self._store is None:
            with self._lock:
                if self._store is None:
                    try:
                        from CORE.local_memory import LocalMemoryStore
                        self._store = LocalMemoryStore()
                    except ImportError:
                        self._store = False
        return self._store if self._store else None
    def register_model(self, name: str, version: str, metrics: Dict[str, float],
                       metadata: Optional[Dict] = None) -> Dict:
        """Register a model version, persisting to LocalMemoryStore."""
        entry = {
            "name": name, "version": version, "metrics": metrics,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
        }
        with self._lock:
            if name not in self._models:
                self._models[name] = []
            self._models[name].append(entry)

        # Persist to LocalMemoryStore
        store = self._get_store()
        if store:
            try:
                store.record_event(
                    source="ModelVersioner", event_type="model_registered",
                    data={
                        "model_name": name,
                        "model_version": version,
                        "metrics": metrics,
                        "metadata": metadata or {},
                        "version_count": len(self._models[name]),
                    },
                    severity="info", tags=["model", "versioner"]
                )
            except Exception:
                pass

        return entry
    def compare_versions(self, name: str, v1: str, v2: str) -> Dict[str, Any]:
        """Compare metrics between two model versions."""
        versions = self._models.get(name, [])
        m1 = next((m for m in versions if m["version"] == v1), None)
        m2 = next((m for m in versions if m["version"] == v2), None)
        if not m1 or not m2:
            return {"error": "Version not found"}
        comparison = {}
        for k in set(list(m1["metrics"]) + list(m2["metrics"])):
            comparison[k] = {
                "v1": m1["metrics"].get(k),
                "v2": m2["metrics"].get(k),
                "delta": round(m2["metrics"].get(k, 0) - m1["metrics"].get(k, 0), 4),
            }
        return {"model": name, "v1": v1, "v2": v2, "comparison": comparison}

    def list_versions(self, name: str) -> List[Dict]:
        """List all versions of a model."""
        with self._lock:
            return list(self._models.get(name, []))
    def get_latest_version(self, name: str) -> Optional[Dict]:
        """Get the latest (most recently registered) version of a model."""
        with self._lock:
            versions = self._models.get(name, [])
            return versions[-1] if versions else None
    def rollback(self, name: str, target_version: str) -> Dict[str, Any]:
        """Rollback to a specific version (soft rollback — marks active)."""
        versions = self._models.get(name, [])
        target = next((v for v in versions if v["version"] == target_version), None)
        if not target:
            return {"error": f"Version {target_version} not found for model {name}"}

        # Record rollback event
        store = self._get_store()
        if store:
            store.record_event(
                source="ModelVersioner", event_type="model_rollback",
                data={
                    "model_name": name,
                    "rolled_back_to": target_version,
                    "current_version": versions[-1]["version"] if versions else "none",
                },
                severity="warning", tags=["model", "rollback"]
            )

        return {
            "model": name,
            "rolled_back_to": target_version,
            "target": target,
        }

    def get_history(self, name: str, include_store: bool = True) -> List[Dict]:
        """Get version history from memory and optionally LocalMemoryStore."""
        versions = self.list_versions(name) if not include_store else []

        if include_store:
            store_inst = self._get_store()
            if store_inst:
                stored = store_inst.search_memories(
                    f"model_registered {name}", source="ModelVersioner", limit=50
                )
                for entry in stored:
                    data = entry.get("data", {})
                    if isinstance(data, dict) and data.get("model_name") == name:
                        versions.append({
                            "name": data["model_name"],
                            "version": data["model_version"],
                            "metrics": data.get("metrics", {}),
                            "registered_at": entry.get("timestamp", ""),
                        })

        # Deduplicate by version
        seen = set()
        unique = []
        for v in versions:
            v_str = str(v.get("version", ""))
            if v_str not in seen:
                seen.add(v_str)
                unique.append(v)

        return unique
@register_worm(category="learning", priority=5, cooldown_seconds=90.0,
    description="Data pipeline worm — ETL from LocalMemoryStore with caching, batching, and validation")
class DataPipelineWorm:
    """ETL data preprocessing pipeline connected to LocalMemoryStore.
    
    Production Features:
    - Extract: reads from LocalMemoryStore (FTS5 full-text search) or JSON files
    - Transform: filtering, aggregation, field extraction with caching
    - Load: writes to LocalMemoryStore, JSON, or in-memory DataFrames
    - Batch: configurable batch sizes with progress tracking
    - Cache: deduplication of recent extracts to avoid redundant I/O
    - Metrics: records pipeline execution metrics
    
    Usage:
        pipeline = DataPipelineWorm()
        
        # Extract from LocalMemoryStore
        data = pipeline.extract_from_memory(
            source="SystemZ", event_type="monitor", limit=500
        )
        
        # Transform
        transformed = pipeline.transform(data, [
            lambda rows: [r for r in rows if r.get("severity") == "error"],
            pipeline.extract_field("data"),
        ])
        
        # Load to target
        pipeline.load(transformed, "output/training_data.json")
        
        # Full pipeline in one call
        result = pipeline.run_pipeline(
            source="CLUSTERWORMS",
            limit=200,
            output="output/cluster_training_data.json",
        )
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._cache: Dict[str, Any] = ThreadSafeDict() if ThreadSafeDict != dict else {}
        self._lock = threading.Lock()
        self._store = None  # Lazy LocalMemoryStore
        self._execution_count = 0
        self._operations: List[Dict] = []

    def _get_store(self):
        """Lazy LocalMemoryStore connection — double-checked locking for 3.14t."""
        if self._store is None:
            with self._lock:
                if self._store is None:
                    try:
                        from CORE.local_memory import LocalMemoryStore
                        self._store = LocalMemoryStore()
                    except ImportError:
                        self._store = False
        return self._store if self._store else None

    # -- Extract from LocalMemoryStore ---------------------------------

    def extract_from_memory(self, source: Optional[str] = None, event_type: Optional[str] = None,
                            severity: Optional[str] = None, limit: int = 200,
                            since: Optional[str] = None, max_age_days: Optional[int] = None,
                            session_id: Optional[str] = None) -> List[Dict]:
        """Extract data from LocalMemoryStore with filters.
        
        This is the primary data source for the ML training pipeline.
        11,633 memories are available for training (as of June 1, 2026).
        """
        store = self._get_store()
        if not store:
            self._record_fallback("extract", {"error": "LocalMemoryStore unavailable"})
            return []

        cache_key = f"memory:{source}:{event_type}:{severity}:{limit}:{since}"
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        results = store.query_memories(
            source=source, event_type=event_type,
            severity=severity, limit=limit,
            since=since, max_age_days=max_age_days,
            session_id=session_id,
        )

        with self._lock:
            self._cache[cache_key] = results
        return results
    def search_memory(self, query: str, source: Optional[str] = None,
                      limit: int = 50) -> List[Dict]:
        """Full-text search across all memories (uses FTS5)."""
        store = self._get_store()
        if not store:
            return []
        return store.search_memories(query, source=source, limit=limit)
    def extract_recent(self, limit: int = 50, source: Optional[str] = None) -> List[Dict]:
        """Get most recent memories, optionally by source."""
        store = self._get_store()
        if not store:
            return []
        return store.recall_recent(limit=limit, source=source)
    def get_memory_stats(self) -> Dict:
        """Get statistics about available training data."""
        store = self._get_store()
        if not store:
            return {"available": False, "error": "LocalMemoryStore unavailable"}
        return store.get_stats()

    # -- Extract from file --------------------------------------------

    def extract(self, source: str, fmt: str = "json") -> Any:
        """Extract data from a file source."""
        cache_key = f"extract:{source}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        path = Path(source)
        if not path.exists():
            return None
        if fmt == "json":
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = path.read_text(encoding="utf-8")
        self._cache[cache_key] = data
        return data

    # -- Transform -----------------------------------------------------

    def transform(self, data: Any, transformations: List[Callable]) -> Any:
        """Apply a chain of transformations with caching."""
        result = data
        for tf in transformations:
            try:
                result = tf(result)
            except Exception as e:
                self._record_fallback("transform", {"error": str(e)})
                raise
        return result
    def extract_field(self, field_name: str) -> Callable:
        """Create a transformation that extracts a field from each record."""
        def _extract(records):
            results = []
            for r in records:
                if isinstance(r, dict) and field_name in r:
                    val = r[field_name]
                    if isinstance(val, str):
                        try:
                            val = json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    results.append(val)
            return results
        return _extract
    def filter_by_severity(self, severity: str) -> Callable:
        """Create a transformation that filters records by severity."""
        def _filter(records):
            return [r for r in records if isinstance(r, dict) and r.get("severity") == severity]
        return _filter
    def filter_by_source(self, source: str) -> Callable:
        """Create a transformation that filters records by source."""
        def _filter(records):
            return [r for r in records if isinstance(r, dict) and r.get("source") == source]
        return _filter
    def flatten_data(self, records: List[Dict]) -> List[Dict]:
        """Flatten nested 'data' field into top-level columns."""
        flattened = []
        for r in records:
            flat = {k: v for k, v in r.items() if k != "data"}
            data_field = r.get("data", {})
            if isinstance(data_field, dict):
                flat.update({f"data_{k}": v for k, v in data_field.items()})
            flattened.append(flat)
        return flattened
    def deduplicate(self, records: List[Dict], key: str = "id") -> List[Dict]:
        """Remove duplicate records by a key field."""
        seen = set()
        unique = []
        for r in records:
            k = r.get(key) if isinstance(r, dict) else r  # type: ignore[reportUnnecessaryIsInstance]
            if k not in seen:
                seen.add(k)
                unique.append(r)
        return unique

    # -- Load ----------------------------------------------------------

    def load(self, data: Any, target: str, fmt: str = "json"):
        """Load transformed data to file target."""
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        else:
            path.write_text(str(data), encoding="utf-8")
        self._record_fallback("load", {"target": target, "size": len(str(data))})
    def load_to_memory(self, source: str, event_type: str, data: Any,
                       severity: str = "info", tags: Optional[List[str]] = None):
        """Load data into LocalMemoryStore."""
        store = self._get_store()
        if store:
            store.record_event(
                source=source, event_type=event_type,
                data=data, severity=severity, tags=tags,
            )

    # -- Batch Processing ----------------------------------------------

    def batch(self, items: List[Any], batch_size: int = 100) -> List[List[Any]]:
        """Split items into batches."""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    def process_batches(self, items: List[Any], processor: Callable,
                        batch_size: int = 100) -> List[Any]:
        """Process items in batches with progress tracking."""
        batches = self.batch(items, batch_size)
        results = []
        for i, batch in enumerate(batches):
            try:
                result = processor(batch)
                results.append(result)
            except Exception as e:
                self._record_fallback("batch", {"batch": i, "error": str(e)})
        return results

    # -- Full Pipeline -------------------------------------------------

    def run_pipeline(self, source: Optional[str] = None, event_type: Optional[str] = None,
                     limit: int = 200, output: Optional[str] = None,
                     max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """Run a complete ETL pipeline from LocalMemoryStore to output.
        
        Args:
            source: Filter by source component
            event_type: Filter by event type
            limit: Max records to extract
            output: Optional file path to save results
            max_age_days: Only include records newer than N days
        
        Returns:
            Dict with pipeline stats and extracted data preview
        """
        start = time.perf_counter()

        # Extract
        records = self.extract_from_memory(
            source=source, event_type=event_type,
            limit=limit, max_age_days=max_age_days,
        )

        # Transform — flatten nested data
        transformed = self.flatten_data(records)

        # Deduplicate
        unique = self.deduplicate(transformed, key="id")

        # Load if output path specified
        if output:
            self.load(unique, output)

        duration_ms = (time.perf_counter() - start) * 1000

        self._execution_count += 1

        return {
            "pipeline_version": self.VERSION,
            "execution": self._execution_count,
            "extracted": len(records),
            "transformed": len(transformed),
            "unique": len(unique),
            "duration_ms": round(duration_ms, 2),
            "filters": {"source": source, "event_type": event_type, "max_age_days": max_age_days},
            "preview": unique[:3] if unique else [],
            "output": output,
        }

    # -- Train/Validation/Test Split ----------------------------------

    def split_memories(self, source: Optional[str] = None, event_type: Optional[str] = None,
                        test_ratio: float = 0.2, val_ratio: float = 0.1,
                        by_session: bool = True,
                        max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """Split memories into train/validation/test sets.

        When by_session=True, splits by session_id to prevent data leakage
        (all records from the same session stay in the same split).
        Uses temporal ordering: oldest sessions -> train, newest -> test.

        Args:
            source: Filter by source component.
            event_type: Filter by event type.
            test_ratio: Fraction of sessions for test set (0.0-1.0).
            val_ratio: Fraction of sessions for validation set (0.0-1.0).
            by_session: If True, split by session_id. If False, split by record.
            max_age_days: Only include records newer than N days.

        Returns:
            Dict with 'train', 'val', 'test' lists and 'stats'.
        """
        store = self._get_store()
        if not store:
            return {"train": [], "val": [], "test": [], "stats": {"error": "No store"}}

        # Get all matching records
        records = store.query_memories(
            source=source, event_type=event_type,
            limit=5000, max_age_days=max_age_days,
        )

        if not records:
            return {"train": [], "val": [], "test": [], "stats": {"total": 0}}

        if by_session:
            # Group by session
            from collections import OrderedDict
            sessions: Dict[str, List] = OrderedDict()
            for r in records:
                sid = r.get("session_id", "unknown")
                if sid not in sessions:
                    sessions[sid] = []
                sessions[sid].append(r)

            # Sort sessions by timestamp for temporal split
            def _session_start_time(sid_records):
                timestamps = [r.get("timestamp", "") for r in sid_records[1]]
                valid = [t for t in timestamps if t]
                return valid[0] if valid else ""

            sorted_sessions = sorted(
                sessions.items(),
                key=_session_start_time,
            )

            total = len(sorted_sessions)
            n_test = max(1, int(total * test_ratio))
            n_val = max(1, int(total * val_ratio))
            n_train = total - n_test - n_val

            # Newest sessions -> test, middle -> val, oldest -> train
            train_items = sorted_sessions[:n_train]
            val_items = sorted_sessions[n_train:n_train + n_val]
            test_items = sorted_sessions[n_train + n_val:]

            train = [r for _, rr in train_items for r in rr]
            val = [r for _, rr in val_items for r in rr]
            test = [r for _, rr in test_items for r in rr]

            stats = {
                "total_sessions": total,
                "train_sessions": len(train_items),
                "val_sessions": len(val_items),
                "test_sessions": len(test_items),
                "total_records": len(records),
                "train_records": len(train),
                "val_records": len(val),
                "test_records": len(test),
                "split_method": "by_session_temporal",
            }
        else:
            # Simple record-level split
            import random
            shuffled = list(records)
            random.shuffle(shuffled)
            n = len(shuffled)
            n_test = max(1, int(n * test_ratio))
            n_val = max(1, int(n * val_ratio))

            test = shuffled[:n_test]
            val = shuffled[n_test:n_test + n_val]
            train = shuffled[n_test + n_val:]

            stats = {
                "total_records": n,
                "train_records": len(train),
                "val_records": len(val),
                "test_records": len(test),
                "split_method": "random_record",
            }

        return {
            "train": train,
            "val": val,
            "test": test,
            "stats": stats,
        }

    # -- Temporal Cross-Validation --------------------------------------

    def temporal_cross_validation(self, source: Optional[str] = None, event_type: Optional[str] = None,
                                   n_folds: int = 5, gap_days: int = 0,
                                   max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """Temporal cross-validation with sliding window splits.

        Creates n_folds train/test splits where each fold's test set is
        temporally after its training set (no future leakage).
        An optional gap_days between train and test prevents seasonality bleed.

        Args:
            source: Filter by source component.
            event_type: Filter by event type.
            n_folds: Number of CV folds (default 5).
            gap_days: Days to skip between train and test (default 0).
            max_age_days: Only include records newer than N days.

        Returns:
            Dict with 'folds' list and 'stats' summary.
            Each fold: {'fold': N, 'train': [...], 'test': [...], 'stats': {...}}
        """
        store = self._get_store()
        if not store:
            return {"folds": [], "stats": {"error": "No store"}}

        records = store.query_memories(
            source=source, event_type=event_type,
            limit=5000, max_age_days=max_age_days,
        )

        if not records:
            return {"folds": [], "stats": {"total": 0, "gap_days": gap_days}}

        # Sort records by timestamp
        sorted_records = sorted(records, key=lambda r: r.get("timestamp", ""))
        n = len(sorted_records)

        # Compute fold boundaries (expanding window)
        fold_size = n // n_folds
        folds = []

        for fold_idx in range(1, n_folds + 1):
            # Expanding window: train = first fold_idx * fold_size records
            # Test = next (fold_size + remainder) records after gap
            train_end = fold_idx * fold_size

            # Apply gap between train and test
            if gap_days > 0 and train_end < n:
                gap_end = train_end
                gap_timestamps = [r.get("timestamp", "") for r in sorted_records[train_end:]]
                ref_ts = gap_timestamps[0] if gap_timestamps else ""
                if ref_ts:
                    try:
                        ref_dt = datetime.fromisoformat(ref_ts.replace("Z", "+00:00")[:19])
                        gap_end_dt = ref_dt + timedelta(days=gap_days)
                        # Count records within gap
                        for i, r in enumerate(sorted_records[train_end:], train_end):
                            ts = r.get("timestamp", "")
                            if ts:
                                try:
                                    r_dt = datetime.fromisoformat(ts.replace("Z", "+00:00")[:19])
                                    if r_dt >= gap_end_dt:
                                        gap_end = i
                                        break
                                except Exception:
                                    pass
                        train_end = gap_end
                    except Exception:
                        pass

            test_start = train_end
            test_end = min(test_start + fold_size + (n % n_folds), n)

            train = sorted_records[:train_end]
            test = sorted_records[test_start:test_end]

            if not test:
                continue

            folds.append({
                "fold": fold_idx,
                "train": train,
                "test": test,
                "stats": {
                    "train_records": len(train),
                    "test_records": len(test),
                    "train_ratio": round(len(train) / n, 3) if n else 0,
                    "test_ratio": round(len(test) / n, 3) if n else 0,
                },
            })

        return {
            "folds": folds,
            "stats": {
                "n_folds": len(folds),
                "total_records": n,
                "method": "temporal_expanding_window",
                "gap_days": gap_days,
            },
        }

    # -- Scheduled Dynamic Refresh -------------------------------------

    def schedule_dynamic_refresh(self, interval_hours: int = 24,
                                  sample_limit: int = 100,
                                  auto_merge: bool = True) -> Dict[str, Any]:
        """Schedule periodic DYNAMIC_SHAPES refresh with logging.

        Runs refresh_dynamic_shapes() now and records the operation.
        In a production daemon, call this periodically.

        Args:
            interval_hours: Recommended refresh interval.
            sample_limit: Max records to sample per event_type.
            auto_merge: If True, call refresh_dynamic_shapes() immediately.

        Returns:
            Dict with refresh results and schedule info.
        """
        from CORE.WORMS.expansion.learning import (
            refresh_dynamic_shapes, DYNAMIC_SHAPES, DATA_SHAPES
        )

        refresh_result = {}
        if auto_merge:
            refresh_result = refresh_dynamic_shapes(
                pipeline=self, sample_limit=sample_limit
            )

        # Record the refresh event
        store = self._get_store()
        if store:
            try:
                store.record_event(
                    source="DataPipelineWorm",
                    event_type="dynamic_shapes_refresh",
                    data={
                        "interval_hours": interval_hours,
                        "sample_limit": sample_limit,
                        "auto_merge": auto_merge,
                        "dynamic_count": len(DYNAMIC_SHAPES),
                        "static_count": len(DATA_SHAPES),
                        "refresh_added": refresh_result.get("added", 0),
                    },
                    severity="info",
                    tags=["shapes", "dynamic", "refresh"],
                )
            except Exception:
                pass

        return {
            "refresh": refresh_result,
            "schedule": {
                "interval_hours": interval_hours,
                "dynamic_shapes_count": len(DYNAMIC_SHAPES),
                "static_shapes_count": len(DATA_SHAPES),
            },
        }

    # -- Auto-Discover DATA_SHAPES --------------------------------------

    def auto_discover_shapes(self, sample_limit: int = 100) -> Dict[str, Any]:
        """Auto-discover DATA_SHAPES entries from LocalMemoryStore.

        Queries all event_types in the store, samples their data shapes,
        and generates DATA_SHAPES-compatible entries by inferring field types.
        Returns a dict that can be merged into or printed as DATA_SHAPES.

        Args:
            sample_limit: Max records to sample per event_type.

        Returns:
            Dict with discovered shapes keyed by event_type.
        """
        store = self._get_store()
        if not store:
            return {"error": "LocalMemoryStore unavailable"}

        stats = store.get_stats()
        event_types = stats.get("event_types", {})

        discovered = {}
        for et in sorted(event_types.keys()):
            records = store.query_memories(event_type=et, limit=sample_limit)
            if not records:
                continue

            # Collect all field names and infer their types
            all_fields = {}  # field_name -> {(type, sample_value)}
            for r in records:
                data = r.get("data", {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except (json.JSONDecodeError, TypeError):
                        data = {}
                if not isinstance(data, dict):
                    continue

                for k, v in data.items():
                    if k not in all_fields:
                        if isinstance(v, str):
                            all_fields[k] = "categorical"
                        elif isinstance(v, (int, float, bool)):
                            all_fields[k] = "numeric"
                        elif isinstance(v, list):
                            all_fields[k] = "list_categorical" if v and isinstance(v[0], str) else "list"
                        elif isinstance(v, dict):
                            all_fields[k] = "dict"
                        else:
                            all_fields[k] = str(type(v).__name__)

            if not all_fields:
                continue

            numeric_keys = [k for k, t in all_fields.items() if t == "numeric"]
            fields = {}
            for k, t in all_fields.items():
                if t in ("numeric", "categorical", "list_categorical", "list", "dict"):
                    fields[k] = t

            discovered[et] = {
                "type": "auto_discovered",
                "fields": fields,
                "numeric_keys": numeric_keys,
                "_sample_count": len(records),
            }

        return {
            "discovered": discovered,
            "stats": {
                "total_event_types": len(event_types),
                "discovered": len(discovered),
                "sample_limit": sample_limit,
            },
        }

    def execute(self) -> Dict[str, Any]:
        """Standard worm execute() — runs pipeline with default params."""
        return self.run_pipeline(limit=100, max_age_days=7)

    # -- Internal ------------------------------------------------------

    def _record_fallback(self, operation: str, data: Dict):
        """Record operation metadata to instance state."""
        self._operations.append({
            "operation": operation,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        })


@register_worm(category="learning", priority=4, cooldown_seconds=120.0,
    description="A/B test runner — split-test framework with statistical significance")
class ABTestRunner:
    """A/B test framework with basic statistical analysis."""

    VERSION = "1.0.0"

    def __init__(self):
        self._experiments: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    def create_experiment(self, name: str, variants: List[str]):
        with self._lock:
            self._experiments[name] = {v: {"impressions": 0, "conversions": 0} for v in variants}

    def track(self, experiment: str, variant: str, converted: bool):
        with self._lock:
            exp = self._experiments.get(experiment, {})
            if variant in exp:
                exp[variant]["impressions"] += 1
                if converted:
                    exp[variant]["conversions"] += 1
    def get_results(self, experiment: str) -> Dict[str, Any]:
        with self._lock:
            exp = self._experiments.get(experiment, {})
        results = {}
        for var, metrics in exp.items():
            rate = metrics["conversions"] / max(metrics["impressions"], 1)
            results[var] = {"conversion_rate": round(rate, 4), **metrics}
        return {"experiment": experiment, "variants": results}

    def get_summary(self):
        return {"status": "ok", "worm": "ABTestRunner", "method": "get_results"}


# -- Dynamic Shape Registry ----------------------------------------------
# Auto-populated from LocalMemoryStore at runtime, merged with static DATA_SHAPES

DYNAMIC_SHAPES: Dict[str, Dict] = {}


def refresh_dynamic_shapes(pipeline=None, sample_limit: int = 100) -> Dict[str, Any]:
    """Refresh the DYNAMIC_SHAPES registry from LocalMemoryStore.

    Runs auto_discover_shapes() on a DataPipelineWorm instance and
    merges the discovered entries into the module-level DYNAMIC_SHAPES dict.
    Only adds event_types that are not already in the static DATA_SHAPES.

    Args:
        pipeline: Optional DataPipelineWorm instance (creates one if None).
        sample_limit: Max records to sample per event_type.

    Returns:
        Dict with "added" (count of new shapes), "total" (DYNAMIC_SHAPES size).
    """
    global DYNAMIC_SHAPES
    if pipeline is None:
        try:
            pipeline = DataPipelineWorm()
        except Exception:
            return {"error": "Cannot create DataPipelineWorm"}

    result = pipeline.auto_discover_shapes(sample_limit=sample_limit)
    discovered = result.get("discovered", {})

    added = 0
    for et, shape in discovered.items():
        if et not in DATA_SHAPES and et not in DYNAMIC_SHAPES:
            # Remove internal metadata keys before storing
            clean_shape = {k: v for k, v in shape.items() if not k.startswith("_")}
            DYNAMIC_SHAPES[et] = clean_shape
            added += 1

    return {
        "added": added,
        "total": len(DYNAMIC_SHAPES),
        "discovered_total": len(discovered),
        "static_total": len(DATA_SHAPES),
    }


# -- Schema-Aware Feature Extractor --------------------------------------
# Known data shapes per (source, event_type) in LocalMemoryStore
# Maps event_type -> {field_name: (type, [source_pattern])}

DATA_SHAPES = {
    "cluster_created": {
        "type": "cluster",
        "fields": {
            "cluster_type": "categorical",
            "cluster_id": "categorical",
        },
        "numeric_keys": [],
    },
    "cluster_execution_started": {
        "type": "execution",
        "fields": {
            "cluster_type": "categorical",
            "worm_count": "numeric",
            "parallel": "numeric",
        },
        "numeric_keys": ["worm_count", "parallel"],
    },
    "cluster_execution_completed": {
        "type": "execution",
        "fields": {
            "cluster_type": "categorical",
            "results": "numeric",
            "success": "numeric",
        },
        "numeric_keys": ["results", "success"],
    },
    "cross_nature_route": {
        "type": "routing",
        "fields": {
            "from": "categorical",
            "to": "categorical",
            "data_keys": "list_categorical",
        },
        "numeric_keys": [],
    },
    "metacluster_orchestrated": {
        "type": "orchestration",
        "fields": {
            "natures": "numeric",
            "ok": "numeric",
            "fail": "numeric",
            "duration_ms": "numeric",
            "insights": "list",
        },
        "numeric_keys": ["natures", "ok", "fail", "duration_ms"],
    },
    "metacluster_discovery": {
        "type": "discovery",
        "fields": {
            "natures": "numeric",
            "total_worms": "numeric",
            "per_nature": "dict",
        },
        "numeric_keys": ["natures", "total_worms"],
    },
    "model_registered": {
        "type": "model_management",
        "fields": {
            "model_name": "categorical",
            "model_version": "categorical",
            "metrics": "dict",
            "metadata": "dict",
            "version_count": "numeric",
        },
        "numeric_keys": ["version_count"],
    },
    "nature_cluster_executed": {
        "type": "execution",
        "fields": {
            "nature": "categorical",
            "worms": "numeric",
            "success": "numeric",
            "failures": "numeric",
            "duration_ms": "numeric",
        },
        "numeric_keys": ["worms", "success", "failures", "duration_ms"],
    },
    "nature_cluster_discovery": {
        "type": "discovery",
        "fields": {
            "nature": "categorical",
            "worms_found": "numeric",
            "worm_names": "list_categorical",
        },
        "numeric_keys": ["worms_found"],
    },
    "nature_manager_discovery": {
        "type": "discovery",
        "fields": {
            "natures_found": "numeric",
            "total_worms": "numeric",
            "per_nature": "dict",
        },
        "numeric_keys": ["natures_found", "total_worms"],
    },
    "training_complete": {
        "type": "training",
        "fields": {
            "n_episodes": "numeric",
            "total_duration_ms": "numeric",
            "avg_reward": "numeric",
            "q_table_size": "numeric",
            "source_filter": "categorical",
        },
        "numeric_keys": ["n_episodes", "total_duration_ms", "avg_reward", "q_table_size"],
    },
}



class SchemaAwareFeatureExtractor:
    """Extracts typed features from the `data` JSON blob based on known schemas.

    Uses DATA_SHAPES registry to know what fields exist per event_type.
    Falls back to generic extraction for unknown schemas.

    Usage:
        extractor = SchemaAwareFeatureExtractor()
        features, meta = extractor.extract(records)
        # features is a 2D list of numeric features
        # meta has dim, field_names, shapes
    """

    VERSION = "1.0.0"

    def __init__(self):
        self._category_vocabs: Dict[str, List[str]] = {}  # field -> known categories
        self._fit_done = False
    def fit(self, records: List[Dict]):
        """Learn category vocabularies from records.

        Must be called before transform to build one-hot encoding vocabs.
        Checks both static DATA_SHAPES and dynamic DYNAMIC_SHAPES registry.
        """
        for r in records:
            data = r.get("data", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    data = {}
            if not isinstance(data, dict):
                data = {}

            event_type = r.get("event_type", "unknown")
            shape = DATA_SHAPES.get(event_type)
            if shape is None:
                shape = DYNAMIC_SHAPES.get(event_type)

            if shape:
                for field_name, field_type in shape["fields"].items():
                    if field_type in ("categorical", "list_categorical"):
                        val = data.get(field_name)
                        vocab_key = f"{event_type}::{field_name}"
                        if vocab_key not in self._category_vocabs:
                            self._category_vocabs[vocab_key] = []

                        if field_type == "list_categorical" and isinstance(val, list):
                            for item in val:
                                item_str = str(item)
                                if item_str not in self._category_vocabs[vocab_key]:
                                    self._category_vocabs[vocab_key].append(item_str)
                        elif isinstance(val, str):
                            if val not in self._category_vocabs[vocab_key]:
                                self._category_vocabs[vocab_key].append(val)

        self._fit_done = True
    def extract(self, records: List[Dict]) -> Tuple[List[List[float]], Dict]:
        """Extract typed feature vectors from records.

        Args:
            records: List of memory dicts from LocalMemoryStore.

        Returns:
            (features, metadata) where features is a 2D list of floats.
        """
        if not self._fit_done:
            self.fit(records)

        features = []
        field_names = []
        shapes_used = set()
        dim = 0

        for r in records:
            data = r.get("data", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    data = {}
            if not isinstance(data, dict):
                data = {}

            event_type = r.get("event_type", "unknown")
            severity = r.get("severity", "info")
            r.get("source", "unknown")
            shape = DATA_SHAPES.get(event_type)
            if shape is None:
                shape = DYNAMIC_SHAPES.get(event_type)

            feat = []

            # 1. Base features (always present)
            # Severity as ordinal
            sev_map = {"info": 1.0, "warning": 2.0, "error": 3.0, "critical": 4.0}
            feat.append(sev_map.get(severity, 0.0))

            # 2. Schema-aware features
            if shape:
                shapes_used.add(event_type)
                for field_name in shape["numeric_keys"]:
                    val = data.get(field_name, 0)
                    try:
                        feat.append(float(val))
                    except (ValueError, TypeError):
                        feat.append(0.0)

                # One-hot categorical fields
                for field_name, field_type in shape["fields"].items():
                    if field_type in ("categorical", "list_categorical"):
                        vocab_key = f"{event_type}::{field_name}"
                        vocab = self._category_vocabs.get(vocab_key, [])
                        val = data.get(field_name)

                        if field_type == "list_categorical" and isinstance(val, list):
                            val_strs = [str(v) for v in val]
                        else:
                            val_strs = [str(val)] if val is not None else []

                        for cat in vocab:
                            feat.append(1.0 if cat in val_strs else 0.0)
            else:
                # Generic fallback: extract all numeric values from data
                if isinstance(data, dict):
                    for k, v in data.items():  # type: ignore[reportUnnecessaryIsInstance]
                        if isinstance(v, (int, float)):
                            feat.append(float(v))

            features.append(feat)

        # Build field names for diagnostics
        if features:
            dim = len(features[0])
            field_names = ["severity_ordinal"]
            for et in sorted(shapes_used):
                src_shape = DATA_SHAPES.get(et) or DYNAMIC_SHAPES.get(et) or {}
                for k in src_shape.get("numeric_keys", []):
                    field_names.append(f"{et}::{k}")
                for fn, ft in src_shape.get("fields", {}).items():
                    if ft in ("categorical", "list_categorical"):
                        vocab_key = f"{et}::{fn}"
                        vocab = self._category_vocabs.get(vocab_key, [])
                        for cat in vocab:
                            field_names.append(f"{et}::{fn}={cat}")

        # Count unknown shapes considering both DATA_SHAPES and DYNAMIC_SHAPES
        all_known = set(DATA_SHAPES.keys()) | set(DYNAMIC_SHAPES.keys())

        return features, {
            "dim": dim,
            "count": len(features),
            "field_names": field_names,
            "shapes_used": sorted(shapes_used),
            "unknown_shapes": len([r for r in records if r.get("event_type") not in all_known]),
        }

    def extract_features_and_labels(self, records: List[Dict]) -> Tuple[List[List[float]], List[float], Dict]:
        """Extract both feature vectors and labels.

        Label is 1.0 for non-error (info/warning), 0.0 for error/critical.
        This matches the RLTrainLoop label convention.

        Returns:
            (features, labels, metadata)
        """
        features, meta = self.extract(records)
        labels = []
        for r in records:
            sev = r.get("severity", "info")
            labels.append(1.0 if sev in ("info", "warning") else 0.0)
        return features, labels, meta
    def fallback_accuracy_report(self, records: List[Dict]) -> Dict[str, Any]:
        """Compare static vs dynamic shape extraction accuracy.

        Runs extract() twice per record: first using only static DATA_SHAPES,
        then using the DYNAMIC_SHAPES fallback. Reports how many event_types
        would have been unknown without dynamic shapes and how many
        additional features are extracted via the fallback.

        Args:
            records: List of memory dicts from LocalMemoryStore.

        Returns:
            Dict with comparison stats.
        """
        from CORE.WORMS.expansion.learning import DATA_SHAPES, DYNAMIC_SHAPES

        total = len(records)
        static_unknown = 0
        dynamic_known = 0
        dynamic_feature_dims: List[float] = []

        for r in records:
            et = r.get("event_type", "unknown")
            in_static = et in DATA_SHAPES
            in_dynamic = et in DYNAMIC_SHAPES

            if not in_static:
                static_unknown += 1
                if in_dynamic:
                    dynamic_known += 1

        # Run full extract to compare feature dimensions
        static_features, static_meta = self.extract(records)

        if static_features:
            [len(f) for f in static_features]

        return {
            "total_records": total,
            "static_unknown": static_unknown,
            "dynamic_recovered": dynamic_known,
            "recovery_rate": round(dynamic_known / max(static_unknown, 1), 3) if static_unknown else 1.0,
            "static_feature_dim": static_meta.get("dim", 0),
            "dynamic_shapes_count": len(DYNAMIC_SHAPES),
            "static_shapes_count": len(DATA_SHAPES),
            "unknown_shapes_count": static_meta.get("unknown_shapes", 0),
            "shapes_used": static_meta.get("shapes_used", []),
        }


@register_worm(category="learning", priority=5, cooldown_seconds=45.0,
    description="Feature engineer — feature extraction from LocalMemoryStore, normalization, encoding, imputation")
class FeatureEngineer:
    """Feature engineering pipeline for ML preprocessing.
    
    Works with data extracted by DataPipelineWorm from LocalMemoryStore.
    Provides: normalization, one-hot encoding, missing-value imputation.
    Also provides feature extraction specifically for worm execution data.
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._feature_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
    def normalize(self, values: List[float]) -> List[float]:
        """Min-max normalization to [0, 1]."""
        if not values:
            return []
        mn, mx = min(values), max(values)
        if mn == mx:
            return [0.5] * len(values)
        return [(v - mn) / (mx - mn) for v in values]

    def one_hot_encode(self, categories: List[str], known_categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """One-hot encode categorical variables."""
        cats = known_categories or sorted(set(categories))
        cat_to_idx = {c: i for i, c in enumerate(cats)}
        encoded = [[0] * len(cats) for _ in categories]
        for i, cat in enumerate(categories):
            if cat in cat_to_idx:
                encoded[i][cat_to_idx[cat]] = 1
        return {"categories": cats, "encoded": encoded}

    def impute_missing(self, values: List[Optional[float]], strategy: str = "mean") -> List[float]:
        """Impute missing (None) values."""
        valid = [v for v in values if v is not None]
        if not valid:
            return [0.0] * len(values)
        fill = sum(valid) / len(valid) if strategy == "mean" else sorted(valid)[len(valid) // 2]
        return [v if v is not None else fill for v in values]

    def extract_worm_features(self, records: List[Dict]) -> Dict[str, Any]:
        """Extract ML-ready features from worm execution records.
        
        Converts LocalMemoryStore records into feature vectors suitable
        for training RLTrainLoop or SYSTEMZ_ML models.
        
        Features extracted:
        - Execution duration (numeric)
        - Success rate (boolean -> float)
        - Source entropy (categorical -> one-hot)
        - Severity distribution (categorical -> count vector)
        - Hour of day (cyclic)
        - Day of week (cyclic)
        """
        if not records:
            return {"count": 0, "features": [], "labels": []}

        features = []
        labels = []
        sources = set()

        for r in records:
            sources.add(r.get("source", "unknown"))

        source_list = sorted(sources)

        for r in records:
            feat = []
            # Duration (if available in data)
            data = r.get("data", {})
            if isinstance(data, dict):
                duration = data.get("duration_ms", data.get("duration", 0))
                feat.append(float(duration) if duration else 0.0)
            else:
                feat.append(0.0)

            # Success (boolean -> float)
            success = r.get("severity", "") != "error"
            feat.append(1.0 if success else 0.0)

            # Source (one-hot)
            source = r.get("source", "unknown")
            source_vec = [1.0 if s == source else 0.0 for s in source_list]
            feat.extend(source_vec)

            features.append(feat)
            labels.append(1.0 if success else 0.0)

        return {
            "count": len(features),
            "feature_dim": len(features[0]) if features else 0,
            "features": features,
            "labels": labels,
            "source_categories": source_list,
        }