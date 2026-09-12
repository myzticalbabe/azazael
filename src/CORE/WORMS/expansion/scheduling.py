# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: SCHEDULING (1 worm)
ScheduledTrainingWorm — runs DataPipelineWorm -> RLTrainLoop -> ModelVersioner on schedule

Records training results to LocalMemoryStore for observability.
Supports daily, hourly, or interval-based scheduling with configurable max duration.
"""

import time
import random
import threading
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass

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
    from CORE.freethreading import is_free_threaded
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False


# G-3 (2026-09-11): single tuning/deployment horizon. Evolution evaluated
# candidates at N_EPISODES=80 while production trained at n_episodes=50 —
# horizon-sensitive genes (discount, epsilon_decay) were tuned on one
# horizon and deployed on another. Both now share EVAL_EPISODES.
EVAL_EPISODES = 80


@dataclass
class ScheduleConfig:
    """Configuration for a scheduled training run."""
    interval_hours: float = 24.0        # How often to run
    max_duration_minutes: float = 30.0   # Max training duration
    n_episodes: int = EVAL_EPISODES      # RL episodes per run (= tuning horizon)
    data_limit: int = 200                # Records to extract
    learning_rate: float = 0.29      # Evolved 2026-09-07 (was 0.1)
    discount_factor: float = 0.91    # Evolved 2026-09-07 (was 0.9)
    epsilon: float = 0.11            # Evolved 2026-09-07 (was 0.2)
    epsilon_decay: float = 0.0       # Evolved gene (2026-09-08): annealing speed
    source_filter: (str | None) = None  # None = all sources
    record_to_memory: bool = True        # Persist results
    exclude_sources: (list[str] | None) = None  # Skip self-generated bookkeeping sources

    def apply_evolved_overrides(self) -> bool:
        """Load champion genes promoted by evolution_cycle.py, if present.

        Reads state/evolved_rl_params.json (written after 3 consecutive
        wins over the production baseline). Range-validates before
        applying; falls back to built-in defaults on any problem.
        Rollback = delete the JSON file. Returns True if overrides applied.
        """
        try:
            import json as _json
            from pathlib import Path as _Path
            # Resolve to <project-root>/state/evolved_rl_params.json — the
            # same location evolution_cycle.py writes to. This file sits
            # 5 dirs below the root (src/CORE/WORMS/expansion/), so five
            # .parent hops, not four (path mismatch bug, 2026-09-08).
            p = (_Path(__file__).resolve().parent.parent.parent.parent.parent
                 / "state" / "evolved_rl_params.json")
            # EV-1 (EVOLUTION_PROCESS_AUDIT_20260910, D-1): prefer the untracked
            # runtime location and only fall back to the legacy tracked
            # config/ path for reading, so a repo git restore/checkout can no
            # longer silently revert production hyperparameters.
            if not p.exists():
                _legacy = (_Path(__file__).resolve()
                           .parent.parent.parent.parent.parent
                           / "config" / "evolved_rl_params.json")
                if _legacy.exists():
                    p = _legacy
            if not p.exists():
                return False
            data = _json.loads(p.read_text(encoding="utf-8"))
            g = {k: float(data["genes"][k])
                 for k in ("learning_rate", "epsilon", "discount")}
            if not (0.01 <= g["learning_rate"] <= 0.5
                    and 0.0 <= g["epsilon"] <= 0.5
                    and 0.8 <= g["discount"] <= 0.999):
                return False
            self.learning_rate = g["learning_rate"]
            self.epsilon = g["epsilon"]
            self.discount_factor = g["discount"]
            # Evolved gene (2026-09-08): exploration-annealing speed.
            # Absent from older promotion files -> keep built-in default.
            if "epsilon_decay" in data.get("genes", {}):
                dec = float(data["genes"]["epsilon_decay"])
                self.epsilon_decay = max(0.0, min(dec, 0.2))
            return True
        except Exception:
            return False


@dataclass
class TrainingRun:
    """Record of a single training run.

    Honesty protocol (2026-09-11 audit): a run that did no training must
    never look like a successful one. Plateau/data skips set
    skipped=True (and success=False); synthetic-fallback runs set
    synthetic=True so ledgers and dashboards can exclude them.
    """
    run_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    records_extracted: int
    n_episodes: int
    avg_reward: float
    q_table_size: int
    model_version: str
    success: bool
    error: (str | None) = None
    skipped: bool = False
    skip_reason: (str | None) = None
    synthetic: bool = False


class ScheduledTrainingWorm:
    """Runs the full ML training pipeline on a configurable schedule.

    Orchestrates: DataPipelineWorm -> FeatureEngineer -> RLTrainLoop -> ModelVersioner
    Records all results to LocalMemoryStore for dashboard visibility.

    Usage:
        trainer = ScheduledTrainingWorm()
        result = trainer.execute()  # Run once
        trainer.start_scheduler()   # Run on a schedule (daemon thread)
    """

    VERSION = "1.0.0"

    def __init__(self, config: (ScheduleConfig | None) = None):
        self.config = config or ScheduleConfig()
        # Champion promotion: use evolved hyperparameters when a champion
        # has been promoted (rollback = delete evolved_rl_params.json).
        try:
            if self.config.apply_evolved_overrides():
                print(f"[train] using evolved params: lr={self.config.learning_rate} "
                      f"eps={self.config.epsilon} disc={self.config.discount_factor}",
                      flush=True)
        except Exception:
            pass
        self._lock = threading.Lock()
        self._run_history: list[TrainingRun] = []
        self._scheduler_thread: (threading.Thread | None) = None
        self._stop_event = threading.Event()
        self._last_model_version = "0.0.0"

    # -- Lazy Component Loaders --------------------------------------

    def _get_pipeline(self):
        try:
            from CORE.WORMS.expansion.learning import DataPipelineWorm
            return DataPipelineWorm()
        except ImportError:
            return None

    def _get_engineer(self):
        try:
            from CORE.WORMS.expansion.learning import FeatureEngineer
            return FeatureEngineer()
        except ImportError:
            return None

    def _get_rl(self):
        try:
            from CORE.WORMS.expansion.learning import RLTrainLoop
            return RLTrainLoop()
        except ImportError:
            return None

    def _get_versioner(self):
        try:
            from CORE.WORMS.expansion.learning import ModelVersioner
            return ModelVersioner()
        except ImportError:
            return None

    def _get_ab(self):
        try:
            from CORE.WORMS.expansion.learning import ABTestRunner
            return ABTestRunner()
        except ImportError:
            return None

    def _get_store(self):
        try:
            from CORE.local_memory import get_memory_store
            return get_memory_store()
        except ImportError:
            return None

    def _get_logger(self):
        try:
            from CORE.azazael_logging import get_logger
            return get_logger("scheduling")
        except ImportError:
            return None

    # -- Main Execution ----------------------------------------------

    def _plateau_skip_reason(self) -> Optional[str]:
        """Skip retraining when converged on unchanged data (learned knowledge).

        Compares the last two scheduled runs: identical record counts and
        reward within 2% means nothing left to learn. Returns reason or None.
        Read-only; fails open (None) on any error.
        """
        try:
            import json as _json
            store = self._get_store()
            if store is None:
                return None
            recent = store.query_memories(event_type="training_run_complete", limit=2)
            if len(recent) < 2:
                return None
            datas = []
            for r in recent:
                d = r.get("data", {})
                if isinstance(d, str):
                    try:
                        d = _json.loads(d)
                    except (ValueError, TypeError):
                        return None
                datas.append(d if isinstance(d, dict) else {})
            a, b = datas[0], datas[1]
            if a.get("records") != b.get("records"):
                return None
            ra, rb = float(a.get("avg_reward", 0) or 0), float(b.get("avg_reward", 0) or 0)
            if rb and abs(ra - rb) / abs(rb) < 0.02:
                return f"plateaued: reward {ra} vs {rb} on {a.get('records')} records"
            return None
        except Exception:
            return None

    def execute(self) -> TrainingRun:
        """Execute one full training pipeline run.

        Pipeline: DataPipelineWorm -> FeatureEngineer -> RLTrainLoop -> ModelVersioner
        Returns a TrainingRun with all metrics.
        """
        start = time.perf_counter()
        run_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        started_at = datetime.now().isoformat()
        error = None

        # Knowledge application: skip converged retraining on unchanged data.
        # Honesty protocol: a skip is skipped=True + success=False, never a
        # zero-record "success" (2026-09-11 audit — the 0-record SUCCESSFUL).
        skip_reason = self._plateau_skip_reason()
        if skip_reason:
            print(f"[train] {run_id} SKIPPED ({skip_reason})", flush=True)
            return TrainingRun(
                run_id=run_id, started_at=started_at,
                completed_at=datetime.now().isoformat(),
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
                records_extracted=0, n_episodes=0, avg_reward=0.0,
                q_table_size=0, model_version=self._last_model_version,
                success=False, error=None,
                skipped=True, skip_reason=skip_reason,
            )

        _synthetic = False  # bound before try: exception paths below read it
        try:
            # Stage 1: DataPipelineWorm — extract data
            pipeline = self._get_pipeline()
            if not pipeline:
                raise RuntimeError("DataPipelineWorm unavailable")
            records = pipeline.extract_from_memory(
                source=self.config.source_filter,
                limit=self.config.data_limit,
                exclude_sources=self.config.exclude_sources,
            )
            n_records = len(records)

            # Fallback to mock data if no records (2026-09-10 honesty
            # fix): fakes used to be counted as real records and the run
            # reported success on invented data. Now flagged synthetic
            # end-to-end and real count kept at zero.
            if n_records == 0:
                records = [
                    {"source": "SystemZ", "severity": "info", "data": {"duration_ms": 150, "synthetic": True}},
                    {"source": "ProcessZ", "severity": "info", "data": {"duration_ms": 200, "synthetic": True}},
                    {"source": "VulnScanner", "severity": "error", "data": {"duration_ms": 5000, "synthetic": True}},
                ]
                _synthetic = True

            # Stage 2: FeatureEngineer — extract features
            engineer = self._get_engineer()
            if engineer:
                features = engineer.extract_worm_features(records)
            else:
                features = {"count": 0, "feature_dim": 0}

            # Stage 3: RLTrainLoop — train. Resume persisted Q-knowledge
            # first (2026-09-10 fix): every run started tabula-rasa while
            # q_table_persisted rows piled up write-only. Load failure
            # falls back to fresh (logged, never fatal).
            rl = self._get_rl()
            if rl:
                try:
                    _resumed = bool(rl.load_q_table_from_store())
                except Exception as e:
                    _resumed = False
                    print(f"[train] {run_id} Q-resume failed, fresh start: {e}", flush=True)
                if _resumed:
                    print(f"[train] {run_id} resumed persisted Q-table", flush=True)
                training_result = rl.train_from_memory(
                    source=self.config.source_filter,
                    n_episodes=self.config.n_episodes,
                    max_steps=min(50, max(10, n_records // 2)),
                    learning_rate=self.config.learning_rate,
                    discount_factor=self.config.discount_factor,
                    epsilon=self.config.epsilon,
                )
                avg_reward = training_result.get("avg_reward", 0)
                q_table_size = training_result.get("q_table_size", 0)
            else:
                avg_reward = 0.0
                q_table_size = 0

            # Stage 4: ModelVersioner — register model
            versioner = self._get_versioner()
            if versioner:
                # Increment version
                parts = self._last_model_version.split(".")
                major = int(parts[0])
                minor = int(parts[1]) + 1 if len(parts) > 1 else 1
                new_version = f"{major}.{minor}.0"
                self._last_model_version = new_version

                versioner.register_model(
                    name="scheduled_training",
                    version=new_version,
                    metrics={
                        "avg_reward": avg_reward,
                        "q_table_size": q_table_size,
                        "records": n_records,
                        "episodes": self.config.n_episodes,
                    },
                    metadata={
                        "source_filter": self.config.source_filter,
                        "run_id": run_id,
                        "pipeline_version": self.VERSION,
                    },
                )
            else:
                new_version = "0.0.0"

            # Record to LocalMemoryStore
            store = self._get_store()
            if store and self.config.record_to_memory:
                store.record_event(
                    source="ScheduledTrainingWorm",
                    event_type="training_run_complete",
                    data={
                        "algo": "RL",
                        "run_id": run_id,
                        "records": n_records,
                        "synthetic": _synthetic,
                        "episodes": self.config.n_episodes,
                        "avg_reward": avg_reward,
                        "q_table_size": q_table_size,
                        "model_version": new_version,
                    },
                    severity="info",
                    tags=["training", "scheduled", "pipeline"],
                )

        except Exception as e:
            error = str(e)
            avg_reward = 0.0
            q_table_size = 0
            n_records = 0
            new_version = "0.0.0"

        duration_ms = (time.perf_counter() - start) * 1000

        run = TrainingRun(
            run_id=run_id,
            started_at=started_at,
            completed_at=datetime.now().isoformat(),
            duration_ms=round(duration_ms, 2),
            records_extracted=n_records,
            n_episodes=self.config.n_episodes,
            avg_reward=avg_reward,
            q_table_size=q_table_size,
            model_version=new_version,
            success=error is None,
            error=error,
            synthetic=_synthetic,
        )

        with self._lock:
            self._run_history.append(run)
            # Keep last 50 runs
            if len(self._run_history) > 50:
                self._run_history = self._run_history[-50:]

        print(f"[train] {run_id} done: success={run.success} "
              f"episodes={run.n_episodes} reward={round(run.avg_reward, 2)} "
              f"q={run.q_table_size} version={run.model_version} "
              f"ms={round(run.duration_ms, 1)}", flush=True)

        return run

    # -- Scheduler ---------------------------------------------------

    def start_scheduler(self, interval_hours: (float | None) = None):
        """Start the scheduler in a background daemon thread.

        Args:
            interval_hours: Override the default interval
        """
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        if interval_hours:
            self.config.interval_hours = interval_hours

        self._stop_event.clear()

        def _scheduler_loop():
            while not self._stop_event.is_set():
                run = self.execute()
                # Log run summary via structured logging
                status = "ok" if run.success else "fail"
                log = self._get_logger()
                if log:
                    log.info("scheduled_training_run_complete", {
                        "status": status,
                        "run_id": run.run_id,
                        "avg_reward": round(run.avg_reward, 2),
                        "duration_ms": round(run.duration_ms, 2),
                    })
                # Sleep for interval (check stop event periodically)
                deadline = time.time() + self.config.interval_hours * 3600
                while time.time() < deadline:
                    if self._stop_event.wait(timeout=5):
                        return

        self._scheduler_thread = threading.Thread(
            target=_scheduler_loop, daemon=True
        )
        self._scheduler_thread.start()

    def stop_scheduler(self):
        """Stop the scheduler gracefully."""
        self._stop_event.set()

    # -- Status ------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Get scheduler status and run history."""
        with self._lock:
            recent_runs = self._run_history[-5:]
            return {
                "version": self.VERSION,
                "scheduler_running": (
                    self._scheduler_thread is not None
                    and self._scheduler_thread.is_alive()
                ),
                "interval_hours": self.config.interval_hours,
                "source_filter": self.config.source_filter,
                "total_runs": len(self._run_history),
                "last_model_version": self._last_model_version,
                "recent_runs": [
                    {
                        "run_id": r.run_id,
                        "success": r.success,
                        "avg_reward": r.avg_reward,
                        "records": r.records_extracted,
                        "duration_ms": r.duration_ms,
                    }
                    for r in recent_runs
                ],
                "free_threaded": is_free_threaded(),
            }


# =======================================================================
# SCHEDULED DB MONITOR
# =======================================================================

@dataclass
class DbMonitorScheduleConfig:
    """Configuration for scheduled database monitoring."""
    interval_hours: float = 1.0               # How often to check (default: hourly)
    warn_db_size_mb: float = 100.0             # Warning threshold
    critical_db_size_mb: float = 500.0         # Critical threshold
    record_to_memory: bool = True               # Persist results to LocalMemoryStore
    use_postgres: bool = False                  # Use PostgreSQL backend


@dataclass
class DbMonitorRun:
    """Record of a single database monitoring run."""
    run_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    healthy: bool
    db_size_mb: float
    total_memories: int
    total_sessions: int
    growth_24h: int
    errors_7d: int
    warnings_7d: int
    alerts_generated: int
    success: bool
    error: (str | None) = None


class ScheduledDbMonitorWorm:
    """Runs DatabaseMonitorWorm on a configurable schedule.

    Performs periodic database health checks and records results
    to LocalMemoryStore for dashboard visibility. Works alongside
    ScheduledTrainingWorm in the scheduled pipeline.

    Usage:
        monitor = ScheduledDbMonitorWorm()
        result = monitor.execute()  # Run once
        monitor.start_scheduler()   # Run on a schedule (daemon thread)
    """

    VERSION = "1.0.0"

    def __init__(self, config: (DbMonitorScheduleConfig | None) = None, store: Any = None):
        self.config = config or DbMonitorScheduleConfig()
        self._injected_store = store
        self._lock = threading.Lock()
        self._run_history: list[DbMonitorRun] = []
        self._scheduler_thread: (threading.Thread | None) = None
        self._stop_event = threading.Event()

    def _get_monitor(self):
        """Lazy DatabaseMonitorWorm loader."""
        try:
            from CORE.WORMS.expansion.db_monitor import DatabaseMonitorWorm
            return DatabaseMonitorWorm(use_postgres=self.config.use_postgres, store=self._injected_store)
        except ImportError:
            return None

    def _get_store(self):
        """Lazy LocalMemoryStore loader."""
        try:
            from CORE.local_memory import get_memory_store
            return get_memory_store()
        except ImportError:
            return None

    def _get_logger(self):
        """Lazy logger loader."""
        try:
            from CORE.azazael_logging import get_logger
            return get_logger("db_monitor_scheduler")
        except ImportError:
            return None

    def execute(self) -> DbMonitorRun:
        """Execute one database monitoring run.

        Runs DatabaseMonitorWorm.check_health() and records results.

        Returns:
            DbMonitorRun with all health metrics.
        """
        start = time.perf_counter()
        run_id = f"dbmon_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        started_at = datetime.now().isoformat()
        error = None

        try:
            monitor = self._get_monitor()
            if not monitor:
                raise RuntimeError("DatabaseMonitorWorm unavailable")

            result = monitor.execute()
            healthy = result.get("healthy", False)
            db_size = result.get("db_size_mb", 0.0)
            memories = result.get("total_memories", 0)
            sessions = result.get("total_sessions", 0)
            growth = result.get("memory_growth_24h", 0)
            errors = result.get("error_count_7d", 0)
            warnings = result.get("warning_count_7d", 0)
            alerts = result.get("total_alerts", 0)

        except Exception as e:
            error = str(e)
            healthy = False
            db_size = 0.0
            memories = 0
            sessions = 0
            growth = 0
            errors = 0
            warnings = 0
            alerts = 0

        duration_ms = (time.perf_counter() - start) * 1000

        run = DbMonitorRun(
            run_id=run_id,
            started_at=started_at,
            completed_at=datetime.now().isoformat(),
            duration_ms=round(duration_ms, 2),
            healthy=healthy,
            db_size_mb=db_size,
            total_memories=memories,
            total_sessions=sessions,
            growth_24h=growth,
            errors_7d=errors,
            warnings_7d=warnings,
            alerts_generated=alerts,
            success=error is None,
            error=error,
        )

        with self._lock:
            self._run_history.append(run)
            if len(self._run_history) > 100:
                self._run_history = self._run_history[-100:]

        return run

    # -- Scheduler ---------------------------------------------------

    def start_scheduler(self, interval_hours: (float | None) = None):
        """Start the scheduler in a background daemon thread.

        Args:
            interval_hours: Override the default interval
        """
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        if interval_hours:
            self.config.interval_hours = interval_hours

        self._stop_event.clear()

        def _scheduler_loop():
            while not self._stop_event.is_set():
                run = self.execute()
                status = "ok" if run.success and run.healthy else "fail"
                log = self._get_logger()
                if log:
                    log.info("scheduled_db_monitor_complete", {
                        "status": status,
                        "run_id": run.run_id,
                        "db_size_mb": round(run.db_size_mb, 1),
                        "memories": run.total_memories,
                        "alerts": run.alerts_generated,
                    })
                deadline = time.time() + self.config.interval_hours * 3600
                while time.time() < deadline:
                    if self._stop_event.wait(timeout=5):
                        return

        self._scheduler_thread = threading.Thread(
            target=_scheduler_loop, daemon=True, name="azazael-db-monitor-scheduler"
        )
        self._scheduler_thread.start()

    def stop_scheduler(self):
        """Stop the scheduler gracefully."""
        self._stop_event.set()

    # -- Status ------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Get scheduler status and run history."""
        with self._lock:
            recent_runs = self._run_history[-5:]
            healthy_count = sum(1 for r in self._run_history if r.healthy)
            return {
                "version": self.VERSION,
                "scheduler_running": (
                    self._scheduler_thread is not None
                    and self._scheduler_thread.is_alive()
                ),
                "interval_hours": self.config.interval_hours,
                "total_runs": len(self._run_history),
                "healthy_runs": healthy_count,
                "success_rate": round(healthy_count / max(len(self._run_history), 1) * 100, 1),
                "recent_runs": [
                    {
                        "run_id": r.run_id,
                        "success": r.success,
                        "healthy": r.healthy,
                        "db_size_mb": r.db_size_mb,
                        "memories": r.total_memories,
                        "alerts": r.alerts_generated,
                        "duration_ms": r.duration_ms,
                    }
                    for r in recent_runs
                ],
                "free_threaded": is_free_threaded(),
            }


# =======================================================================
# TRAINING ORCHESTRATOR — SB3 Deep RL Pipeline
# =======================================================================

@dataclass
class OrchestratorConfig:
    """Configuration for TrainingOrchestrator runs."""
    algo: str = "PPO"                           # SB3 algorithm
    total_timesteps: int = 5000                  # Training timesteps per run
    policy: str = "MlpPolicy"                    # SB3 policy type
    device: str = "auto"                         # torch device
    learning_rate: (float | None) = None        # Override default LR
    max_age_days: int = 30                       # Data recency filter
    source_filter: (str | None) = None          # None = all sources
    interval_hours: float = 24.0                 # Schedule interval
    max_duration_minutes: float = 30.0           # Max run duration
    record_to_memory: bool = True                # Persist results to DB
    register_model: bool = True                  # Auto-register with ModelVersioner
    exclude_sources: (list[str] | None) = None   # Skip self-generated bookkeeping sources


@dataclass
class OrchestratorRun:
    """Record of a single SB3 training orchestration run."""
    run_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    algo: str
    total_timesteps: int
    records_used: int
    data_source: str
    trained: bool
    model_version: (str | None) = None
    eval_mean_reward: (float | None) = None
    eval_std_reward: (float | None) = None
    error: (str | None) = None


class TrainingOrchestrator:
    """
    Orchestrates the full SB3 deep RL training pipeline on a schedule.

    Pipeline:
        DataPipelineWorm (extract) -> SB3Agent (train) -> ModelVersioner (register)

    Unlike ScheduledTrainingWorm (which uses Q-learning via RLTrainLoop),
    this worm wraps SB3's PPO/DQN/A2C algorithms for true deep RL training
    from LocalMemoryStore data.

    Usage:
        orch = TrainingOrchestrator()
        result = orch.execute()  # Run once
        orch.start_scheduler()   # Daemon schedule
    """

    VERSION = "1.0.0"

    def __init__(self, config: (OrchestratorConfig | None) = None):
        self.config = config or OrchestratorConfig()
        self._lock = threading.Lock()
        self._run_history: list[OrchestratorRun] = []
        self._scheduler_thread: (threading.Thread | None) = None
        self._stop_event = threading.Event()
        self._last_model_version: (str | None) = None

    # -- Lazy Component Loaders --------------------------------------

    def _get_pipeline(self):
        """Lazy DataPipelineWorm for memory access."""
        try:
            from CORE.WORMS.expansion.learning import DataPipelineWorm
            return DataPipelineWorm()
        except ImportError:
            return None

    def _get_versioner(self):
        """Lazy ModelVersioner for version tracking."""
        try:
            from CORE.WORMS.expansion.learning import ModelVersioner
            return ModelVersioner()
        except ImportError:
            return None

    def _get_store(self):
        """Lazy LocalMemoryStore."""
        try:
            from CORE.local_memory import get_memory_store
            return get_memory_store()
        except ImportError:
            return None

    def _get_logger(self):
        """Lazy logger."""
        try:
            from CORE.azazael_logging import get_logger
            return get_logger("training_orchestrator")
        except ImportError:
            return None

    # -- Main Execution ----------------------------------------------

    def execute(self) -> OrchestratorRun:
        """
        Execute one full SB3 training orchestration run.

        Pipeline: DataPipelineWorm -> SB3Agent -> ModelVersioner
        Records results to LocalMemoryStore.
        """
        start = time.perf_counter()
        run_id = f"sb3train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        started_at = datetime.now().isoformat()
        error = None
        trained = False
        model_version = None
        records_used = 0
        total_timesteps = 0
        data_source = self.config.source_filter or "all"

        try:
            # Stage 1: Extract data via DataPipelineWorm
            pipeline = self._get_pipeline()
            if not pipeline:
                raise RuntimeError("DataPipelineWorm unavailable")

            records = pipeline.extract_from_memory(
                source=self.config.source_filter,
                limit=5000,
                max_age_days=self.config.max_age_days,
                exclude_sources=self.config.exclude_sources,
            )
            records_used = len(records)

            if records_used == 0:
                # Fallback: create SB3Agent with default env for dry-run
                pass

            # Stage 2: Create SB3Agent and train
            try:
                from CORE.sb3_agent import SB3Agent
            except ImportError:
                raise RuntimeError("SB3Agent unavailable")

            agent = SB3Agent(
                config=None,
                algo=self.config.algo,
                policy=self.config.policy,
                device=self.config.device,
                algo_kwargs={
                    "learning_rate": self.config.learning_rate,
                } if self.config.learning_rate else {},
            )

            train_result = agent.train(
                source=self.config.source_filter,
                total_timesteps=self.config.total_timesteps,
                register_model=self.config.register_model,
                max_age_days=self.config.max_age_days,
                exclude_sources=self.config.exclude_sources,
            )

            trained = train_result.get("trained", False)
            total_timesteps = train_result.get("total_timesteps", 0)

            if trained:
                # Stage 3: Get model version from ModelVersioner
                if self.config.register_model:
                    versioner = self._get_versioner()
                    if versioner:
                        latest = versioner.get_latest_version(
                            train_result.get("registered_model", f"SB3_{self.config.algo}")
                        )
                        if latest:
                            model_version = latest.get("version", "v1")
                            self._last_model_version = model_version

                # Record to LocalMemoryStore
                store = self._get_store()
                if store and self.config.record_to_memory:
                    store.record_event(
                        source="TrainingOrchestrator",
                        event_type="sb3_training_orchestrated",
                        data={
                            "run_id": run_id,
                            "algo": self.config.algo,
                            "total_timesteps": total_timesteps,
                            "records_used": records_used,
                            "data_source": data_source,
                            "model_version": model_version or "untracked",
                            "eval_mean_reward": train_result.get("eval_mean_reward"),
                            "eval_std_reward": train_result.get("eval_std_reward"),
                            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                        },
                        severity="info",
                        tags=["sb3", "training", "orchestrated"],
                    )

        except Exception as e:
            error = str(e)

        duration_ms = (time.perf_counter() - start) * 1000

        run = OrchestratorRun(
            run_id=run_id,
            started_at=started_at,
            completed_at=datetime.now().isoformat(),
            duration_ms=round(duration_ms, 2),
            algo=self.config.algo,
            total_timesteps=total_timesteps,
            records_used=records_used,
            data_source=data_source,
            trained=trained,
            model_version=model_version,
            eval_mean_reward=train_result.get("eval_mean_reward"),
            eval_std_reward=train_result.get("eval_std_reward"),
            error=error,
        )

        with self._lock:
            self._run_history.append(run)
            if len(self._run_history) > 50:
                self._run_history = self._run_history[-50:]

        return run

    # -- Scheduler ---------------------------------------------------

    def start_scheduler(self, interval_hours: (float | None) = None):
        """Start the scheduler in a background daemon thread.

        Calls execute() on the configured interval. Checks stop_event
        every 5 seconds for responsive shutdown.

        Args:
            interval_hours: Override the configured interval.
        """
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        if interval_hours:
            self.config.interval_hours = interval_hours

        self._stop_event.clear()

        def _scheduler_loop():
            while not self._stop_event.is_set():
                run = self.execute()
                status = "ok" if run.trained else ("fail" if run.error else "skip")
                log = self._get_logger()
                if log:
                    log.info("sb3_training_orchestration_complete", {
                        "status": status,
                        "run_id": run.run_id,
                        "algo": run.algo,
                        "timesteps": run.total_timesteps,
                        "records": run.records_used,
                        "duration_ms": round(run.duration_ms, 2),
                    })
                # Sleep for interval (check stop event periodically)
                deadline = time.time() + self.config.interval_hours * 3600
                while time.time() < deadline:
                    if self._stop_event.wait(timeout=5):
                        return

        self._scheduler_thread = threading.Thread(
            target=_scheduler_loop, daemon=True, name="azazael-sb3-orchestrator"
        )
        self._scheduler_thread.start()

    def stop_scheduler(self):
        """Stop the scheduler gracefully."""
        self._stop_event.set()

    # -- Status ------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status and run history."""
        with self._lock:
            recent_runs = self._run_history[-5:]
            trained_count = sum(1 for r in self._run_history if r.trained)
            return {
                "version": self.VERSION,
                "scheduler_running": (
                    self._scheduler_thread is not None
                    and self._scheduler_thread.is_alive()
                ),
                "config": {
                    "algo": self.config.algo,
                    "total_timesteps": self.config.total_timesteps,
                    "policy": self.config.policy,
                    "source_filter": self.config.source_filter,
                    "interval_hours": self.config.interval_hours,
                },
                "total_runs": len(self._run_history),
                "trained_runs": trained_count,
                "last_model_version": self._last_model_version,
                "recent_runs": [
                    {
                        "run_id": r.run_id,
                        "trained": r.trained,
                        "algo": r.algo,
                        "timesteps": r.total_timesteps,
                        "records": r.records_used,
                        "duration_ms": r.duration_ms,
                        "error": r.error,
                    }
                    for r in recent_runs
                ],
            }

    def get_run_history(self, limit: int = 10) -> list[dict]:
        """Get recent run history."""
        with self._lock:
            return [
                {
                    "run_id": r.run_id,
                    "started_at": r.started_at,
                    "completed_at": r.completed_at,
                    "duration_ms": r.duration_ms,
                    "algo": r.algo,
                    "timesteps": r.total_timesteps,
                    "records": r.records_used,
                    "trained": r.trained,
                    "model_version": r.model_version,
                    "error": r.error,
                }
                for r in self._run_history[-limit:]
            ]


# =======================================================================
# REGISTRATIONS
# =======================================================================

if _REGISTRY:
    ScheduledTrainingWorm = register_worm(
        category="learning", priority=4, cooldown_seconds=300.0,
        description="Scheduled ML training pipeline — runs DataPipelineWorm -> RLTrainLoop -> ModelVersioner on configurable interval"
    )(ScheduledTrainingWorm)

    ScheduledDbMonitorWorm = register_worm(
        category="monitor", priority=6, cooldown_seconds=120.0,
        description="Scheduled database monitor — runs DatabaseMonitorWorm health checks on configurable interval with alert thresholds"
    )(ScheduledDbMonitorWorm)

    TrainingOrchestrator = register_worm(
        category="learning", priority=5, cooldown_seconds=300.0,
        description="SB3 deep RL orchestrator — DataPipelineWorm -> SB3Agent (PPO/DQN/A2C) -> ModelVersioner on configurable schedule"
    )(TrainingOrchestrator)
