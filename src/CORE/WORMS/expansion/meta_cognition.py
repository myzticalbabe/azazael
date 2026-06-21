# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: NEURAL ADVANCEMENT (1 worm)
MetaCognitionWorm — Self-reflection, error learning, and strategy adaptation engine.

Enables the Azazael ecosystem to introspect on its own execution patterns,
learn from failures, and adapt strategies without human intervention.

Part of GOSP (Gossamer Oxford Semantical Parser) DoctoralThesisEngine —
Tier 5: DISTILLATION — Knowledge synthesis and pattern consolidation.

Features:
- Error pattern recognition across worm executions
- Strategy adaptation based on failure analysis  
- Confidence calibration for decision-making
- Introspective audit trails to PAMS/LocalMemoryStore
- Self-correction loops with CurativePool integration

Created: June 4, 2026 — Neural Advancement Realignment Session
"""

import json
import time
import threading
from datetime import datetime
from typing import Any
from collections import defaultdict

# -- Sentinel for disabled persistence (safer than string "none") --
_PERSISTENCE_DISABLED = object()

# -- Module-level imports for 3.14t thread safety (Lesson #29) --
# NEVER call importlib.import_module() from background threads — deadlocks under free-threading
try:
    from CORE.local_memory import get_memory_store as _get_memory_store_global
    _LOCAL_MEMORY_OK = True
except ImportError:
    _LOCAL_MEMORY_OK = False
    _get_memory_store_global = None

try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls


@register_worm(
    category="learning", priority=7, cooldown_seconds=90.0,
    description="MetaCognition engine — self-reflection, error pattern learning, strategy adaptation for autonomous improvement"
)
class MetaCognitionWorm:
    """Meta-cognitive engine for autonomous system improvement.

    Analyzes execution patterns across worm executions to:
    1. Detect recurring error patterns and failure modes
    2. Build confidence models for decision-making
    3. Adapt strategies based on historical performance
    4. Generate introspective audit trails

    The meta-cognition loop operates in 4 phases:
    OBSERVE -> ANALYZE -> ADAPT -> VALIDATE

    Usage:
        mc = MetaCognitionWorm()
        episode = mc.observe(worm_type="SystemZ", action="scan", outcome="error", context={...})
        patterns = mc.analyze_patterns()
        adaptation = mc.adapt_strategy(worm_type="SystemZ", current_strategy="default")
        report = mc.generate_introspection_report()
    """

    VERSION = "1.0.0"

    def __init__(self, memory_store=None):
        self._lock = threading.Lock()
        # memory_store: None=use global, LocalMemoryStore instance=injected, _PERSISTENCE_DISABLED=skip all I/O
        self._memory_store = memory_store
        self._persistence_enabled = memory_store is not _PERSISTENCE_DISABLED
        self._observations: list[dict[str, Any]] = []
        self._error_patterns: dict[str, list[dict]] = defaultdict(list)
        self._confidence_models: dict[str, dict[str, float]] = {}
        self._strategy_scores: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._adaptations: list[dict] = []
        self._episode_count = 0

        # Auto-restore state from previous session (fail-safe, never blocks)
        if self._persistence_enabled:
            self.load_state()

    # -- OBSERVE Phase --------------------------------------------------

    def observe(self, worm_type: str, action: str, outcome: str,
                context: (dict | None) = None, duration_ms: float = 0.0,
                error: (str | None) = None) -> dict[str, Any]:
        """Record an execution observation for pattern analysis.

        Args:
            worm_type: Type of worm that executed
            action: Action taken
            outcome: "success", "error", "timeout", "blocked"
            context: Additional execution context
            duration_ms: Execution duration
            error: Error message if outcome is "error"

        Returns:
            dict with observation_id and current pattern state
        """
        obs = {
            "id": f"mc_{self._episode_count}_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "worm_type": worm_type,
            "action": action,
            "outcome": outcome,
            "duration_ms": duration_ms,
            "error": error,
            "context": context or {},
            "free_threaded": True,
        }

        with self._lock:
            self._observations.append(obs)
            self._episode_count += 1
            if len(self._observations) > 1000:
                self._observations = self._observations[-1000:]

            # Update error patterns if this was an error
            if outcome == "error" and error:
                self._error_patterns[worm_type].append({
                    "timestamp": obs["timestamp"],
                    "action": action,
                    "error": error,
                    "duration_ms": duration_ms,
                })
                if len(self._error_patterns[worm_type]) > 50:
                    self._error_patterns[worm_type] = self._error_patterns[worm_type][-50:]

        # Persist to memory store
        self._persist_observation(obs)

        return {
            "observation_id": obs["id"],
            "total_observations": self._episode_count,
            "error_count": sum(len(v) for v in self._error_patterns.values()),
        }

    def _get_store(self):
        """Resolve memory store: injected -> global -> None.

        Thread-safe under 3.14t free-threading — all imports happen at module level.
        Uses sys.modules lookup pattern from Lesson #29 to avoid import deadlocks.
        """
        if not self._persistence_enabled:
            return None
        if self._memory_store is not None:
            return self._memory_store
        if _LOCAL_MEMORY_OK and _get_memory_store_global is not None:
            try:
                return _get_memory_store_global()
            except Exception:
                return None
        return None

    def _persist_observation(self, obs: dict) -> None:
        """Persist observation to LocalMemoryStore."""
        store = self._get_store()
        if store is None:
            return
        try:
            store.record_event(
                source="MetaCognitionWorm",
                event_type="meta_cognition_observation",
                data=obs,
                severity="error" if obs["outcome"] == "error" else "info",
                tags=["meta_cognition", obs["worm_type"], obs["outcome"]],
            )
        except Exception:
            pass

    # -- ANALYZE Phase --------------------------------------------------

    def analyze_patterns(self, worm_type: (str | None) = None,
                         limit: int = 50) -> dict[str, Any]:
        """Analyze error patterns and compute failure probabilities.

        Args:
            worm_type: Filter to specific worm type or None for all
            limit: Maximum observations to analyze

        Returns:
            dict with error patterns, failure rates, and recurrence analysis
        """
        with self._lock:
            if worm_type:
                obs_list = [o for o in self._observations[-limit:] if o["worm_type"] == worm_type]
                errors = self._error_patterns.get(worm_type, [])
            else:
                obs_list = self._observations[-limit:]
                errors = []
                for errs in self._error_patterns.values():
                    errors.extend(errs)

        if not obs_list:
            return {"total": 0, "error_rate": 0.0, "patterns": []}

        total = len(obs_list)
        error_count = sum(1 for o in obs_list if o["outcome"] == "error")
        error_rate = error_count / total if total > 0 else 0.0

        # Find recurring error patterns (same error message appearing >2 times)
        error_msgs: dict[str, int] = defaultdict(int)
        for err in errors[-limit:]:
            msg = err.get("error", "unknown")
            error_msgs[msg] += 1

        recurring = [
            {"error": msg, "count": count, "recurring": count > 2}
            for msg, count in sorted(error_msgs.items(), key=lambda x: -x[1])
        ]

        # Compute confidence per worm type
        confidence = self._compute_confidence(worm_type, obs_list)

        # Update confidence models
        if worm_type:
            self._confidence_models[worm_type] = confidence

        return {
            "total": total,
            "error_count": error_count,
            "error_rate": round(error_rate, 4),
            "recurring_errors": recurring[:10],
            "confidence": confidence,
            "worm_type": worm_type or "all",
        }

    def _compute_confidence(self, worm_type: (str | None),
                            observations: list[dict]) -> dict[str, float]:
        """Compute confidence scores based on historical performance."""
        if not observations:
            return {"overall": 0.5, "success_rate": 0.0, "stability": 0.5}

        total = len(observations)
        successes = sum(1 for o in observations if o["outcome"] == "success")
        errors = sum(1 for o in observations if o["outcome"] == "error")
        timeouts = sum(1 for o in observations if o["outcome"] == "timeout")

        success_rate = successes / total if total > 0 else 0.0

        # Stability: inversely proportional to error variance
        durations = [o["duration_ms"] for o in observations if o["duration_ms"] > 0]
        if durations:
            avg_dur = sum(durations) / len(durations)
            variance = sum((d - avg_dur) ** 2 for d in durations) / len(durations)
            stability = 1.0 / (1.0 + variance / 10000.0)
        else:
            stability = 0.5

        # Overall confidence: weighted blend
        overall = success_rate * 0.5 + stability * 0.3 + (1.0 - errors / max(total, 1)) * 0.2

        return {
            "overall": round(overall, 4),
            "success_rate": round(success_rate, 4),
            "stability": round(stability, 4),
            "error_ratio": round(errors / max(total, 1), 4),
        }

    # -- ADAPT Phase ----------------------------------------------------

    def adapt_strategy(self, worm_type: str, current_strategy: str,
                       available_strategies: (list[str] | None) = None) -> dict[str, Any]:
        """Adapt execution strategy based on historical performance.

        Uses confidence-weighted scoring to select optimal strategy.

        Args:
            worm_type: Worm type to adapt for
            current_strategy: Currently active strategy name
            available_strategies: list of alternative strategies

        Returns:
            dict with recommended_strategy and adaptation rationale
        """
        if available_strategies is None:
            available_strategies = ["default", "conservative", "aggressive", "defensive"]

        # Get confidence for current strategy
        confidence = self._confidence_models.get(worm_type, {})
        current_score = confidence.get("overall", 0.5)

        # Score each available strategy
        scores = {current_strategy: current_score}
        for alt in available_strategies:
            if alt == current_strategy:
                continue
            alt_score = self._strategy_scores[worm_type].get(alt, 0.5)
            scores[alt] = alt_score

        # Find best strategy
        best_strategy = max(scores, key=scores.get)
        best_score = scores[best_strategy]

        # Determine if adaptation is needed
        should_adapt = (
            best_strategy != current_strategy
            and best_score > current_score * 1.15  # 15% improvement threshold
        )

        adaptation = {
            "worm_type": worm_type,
            "current_strategy": current_strategy,
            "current_score": round(current_score, 4),
            "recommended_strategy": best_strategy,
            "recommended_score": round(best_score, 4),
            "should_adapt": should_adapt,
            "rationale": (
                f"Switch to {best_strategy}: score {best_score:.3f} > {current_score:.3f}"
                if should_adapt
                else f"Keep {current_strategy}: no better alternative (best: {best_strategy} at {best_score:.3f})"
            ),
            "all_scores": {k: round(v, 4) for k, v in scores.items()},
            "timestamp": datetime.now().isoformat(),
        }

        with self._lock:
            self._adaptations.append(adaptation)
            if len(self._adaptations) > 100:
                self._adaptations = self._adaptations[-100:]

            # Update strategy score
            if should_adapt:
                self._strategy_scores[worm_type][best_strategy] = best_score * 1.05

        # Persist adaptation
        self._persist_adaptation(adaptation)

        return adaptation

    def _persist_adaptation(self, adaptation: dict) -> None:
        """Persist strategy adaptation to LocalMemoryStore."""
        store = self._get_store()
        if store is None:
            return
        try:
            store.record_event(
                source="MetaCognitionWorm",
                event_type="strategy_adaptation",
                data=adaptation,
                severity="warning" if adaptation.get("should_adapt") else "info",
                tags=["meta_cognition", "adaptation", adaptation.get("worm_type", "unknown")],
            )
        except Exception:
            pass

    # -- VALIDATE Phase -------------------------------------------------

    def validate_adaptation(self, worm_type: str, strategy: str,
                            before_confidence: float, current_confidence: float) -> dict[str, Any]:
        """Validate whether a strategy adaptation improved performance.

        Args:
            worm_type: Worm type being validated
            strategy: The new strategy being validated
            before_confidence: Confidence score before adaptation
            current_confidence: Confidence score after adaptation

        Returns:
            dict with validation result and improvement metrics
        """
        improvement = current_confidence - before_confidence
        improved = improvement > 0.05

        validation = {
            "worm_type": worm_type,
            "strategy": strategy,
            "before_confidence": round(before_confidence, 4),
            "current_confidence": round(current_confidence, 4),
            "improvement": round(improvement, 4),
            "improved": improved,
            "verdict": "successful" if improved else "regression" if improvement < -0.05 else "neutral",
            "timestamp": datetime.now().isoformat(),
        }

        # Update strategy scores based on validation
        with self._lock:
            if improved:
                self._strategy_scores[worm_type][strategy] = (
                    self._strategy_scores[worm_type].get(strategy, 0.5) * 1.1
                )
            elif improvement < -0.05:
                self._strategy_scores[worm_type][strategy] = (
                    self._strategy_scores[worm_type].get(strategy, 0.5) * 0.9
                )

        return validation

    # -- Introspection Report -------------------------------------------

    def generate_introspection_report(self) -> dict[str, Any]:
        """Generate a comprehensive meta-cognition report.

        Includes: observation summary, error patterns, confidence models,
        strategy adaptations, and recommendations.
        """
        with self._lock:
            total_obs = len(self._observations)
            total_errors = sum(len(v) for v in self._error_patterns.values())
            total_adaptations = len(self._adaptations)

        # Compute global error rate
        error_rate = total_errors / max(total_obs, 1)

        # Find most error-prone worms
        worm_error_counts = {
            wt: len(errs) for wt, errs in self._error_patterns.items()
        }
        top_offenders = sorted(worm_error_counts.items(), key=lambda x: -x[1])[:5]

        # Strategy summary
        strategy_summary = {}
        for wt, strategies in self._strategy_scores.items():
            best = max(strategies, key=strategies.get)
            strategy_summary[wt] = {
                "best_strategy": best,
                "best_score": round(strategies[best], 4),
                "alternatives": len(strategies),
            }

        # Confidence summary
        confidence_summary = {}
        for wt, conf in self._confidence_models.items():
            confidence_summary[wt] = conf.get("overall", 0.5)

        # Generate recommendations
        recommendations = []
        if error_rate > 0.2:
            recommendations.append(
                f"High error rate ({error_rate:.1%}) — consider CurativePool scope tightening"
            )
        for worm, count in top_offenders:
            if count > 10:
                recommendations.append(
                    f"High error count for {worm} ({count} errors) — review strategy"
                )
        if total_adaptations == 0:
            recommendations.append(
                "No strategy adaptations yet — run adapt_strategy() for top offenders"
            )

        return {
            "version": self.VERSION,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_observations": total_obs,
                "total_errors": total_errors,
                "error_rate": round(error_rate, 4),
                "total_adaptations": total_adaptations,
                "worm_types_tracked": len(self._error_patterns),
            },
            "top_error_worms": [
                {"worm_type": wt, "errors": count}
                for wt, count in top_offenders
            ],
            "strategy_scores": strategy_summary,
            "confidence_models": confidence_summary,
            "recent_adaptations": self._adaptations[-5:] if self._adaptations else [],
            "recommendations": recommendations,
        }

    # -- Worm execute() -------------------------------------------------

    def execute(self) -> dict[str, Any]:
        """Standard worm execution — runs introspection report and auto-saves state."""
        report = self.generate_introspection_report()
        store = self._get_store()
        if store is not None:
            try:
                store.record_event(
                    source="MetaCognitionWorm",
                    event_type="introspection_report",
                    data=report,
                    severity="info",
                    tags=["meta_cognition", "report", "introspection"],
                )
            except Exception:
                pass
        # Auto-save state for session-to-session persistence
        if self._persistence_enabled:
            self.save_state()
        return report

    # -- Persistence -----------------------------------------------

    def save_state(self) -> dict[str, Any]:
        """Serialize all internal state and persist to LocalMemoryStore.

        Returns a dict with serialized observations, error patterns,
        confidence models, strategy scores, and adaptations.
        """
        with self._lock:
            state = {
                "version": self.VERSION,
                "episode_count": self._episode_count,
                "observations": self._observations[-200:],  # Keep last 200
                "error_patterns": dict(self._error_patterns),
                "confidence_models": dict(self._confidence_models),
                "strategy_scores": {k: dict(v) for k, v in self._strategy_scores.items()},
                "adaptations": self._adaptations[-50:],  # Keep last 50
                "saved_at": datetime.now().isoformat(),
                "free_threaded": True,
            }

        # Persist to LocalMemoryStore
        store = self._get_store()
        if store is not None:
            try:
                store.record_event(
                    source="MetaCognitionWorm",
                    event_type="state_saved",
                    data=state,
                    severity="info",
                    tags=["meta_cognition", "persistence", "save"],
                )
            except Exception:
                pass

        return state

    def load_state(self) -> bool:
        """Load the most recent saved state from LocalMemoryStore.

        Restores observations, error patterns, confidence models,
        strategy scores, and adaptations from the last save_state() call.

        Returns:
            True if state was loaded successfully, False otherwise.
        """
        store = self._get_store()
        if store is None:
            return False
        try:
            events = store.search_memories(
                "state_saved", source="MetaCognitionWorm", limit=5
            )
            if not events:
                return False

            # Find the most recent state_saved event
            for ev in reversed(events):
                data = ev.get("data", {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except (json.JSONDecodeError, TypeError):
                        continue
                if not isinstance(data, dict) or "episode_count" not in data:
                    continue

                # Restore state
                with self._lock:
                    self._episode_count = data.get("episode_count", 0)
                    self._observations = data.get("observations", [])
                    self._error_patterns = defaultdict(list, data.get("error_patterns", {}))
                    self._confidence_models = data.get("confidence_models", {})
                    self._strategy_scores = defaultdict(
                        lambda: defaultdict(float),
                        {k: defaultdict(float, v) for k, v in data.get("strategy_scores", {}).items()},
                    )
                    self._adaptations = data.get("adaptations", [])

                return True

            return False
        except Exception:
            return False

    # -- Anomaly Detection --------------------------------------------

    def detect_anomalies(self, worm_type: (str | None) = None,
                         limit: int = 100,
                         error_sigma: float = 2.0,
                         duration_sigma: float = 3.0) -> dict[str, Any]:
        """Detect behavioral anomalies in execution patterns.

        Uses rolling statistics to flag observations that deviate
        significantly from historical norms:
        - Error rate exceeding error_sigma standard deviations
        - Duration exceeding duration_sigma standard deviations

        Args:
            worm_type: Filter to specific worm or None for all
            limit: Recent observations to analyze
            error_sigma: Stddev threshold for error rate anomalies
            duration_sigma: Stddev threshold for duration anomalies

        Returns:
            dict with anomalous episodes and severity scores
        """
        with self._lock:
            if worm_type:
                observations = [o for o in self._observations[-limit:] if o["worm_type"] == worm_type]
            else:
                observations = self._observations[-limit:]

        if len(observations) < 10:
            return {"anomalies": [], "total_analyzed": len(observations), "message": "Insufficient data (need >=10)"}

        window_size = 10
        anomalies = []
        error_rates = []
        durations = []

        for i in range(window_size, len(observations)):
            window = observations[i - window_size:i]
            window_errors = sum(1 for o in window if o["outcome"] == "error")
            window_error_rate = window_errors / len(window)
            window_durations = [o["duration_ms"] for o in window if o["duration_ms"] > 0]
            sum(window_durations) / len(window_durations) if window_durations else 0.0
            current = observations[i]
            current_duration = current.get("duration_ms", 0.0)
            error_rates.append(window_error_rate)
            durations.append(current_duration)

        if not error_rates:
            return {"anomalies": [], "total_analyzed": len(observations)}

        mean_error_rate = sum(error_rates) / len(error_rates)
        mean_duration = sum(durations) / len(durations)
        error_variance = sum((r - mean_error_rate) ** 2 for r in error_rates) / len(error_rates)
        error_stddev = error_variance ** 0.5
        duration_variance = sum((d - mean_duration) ** 2 for d in durations) / len(durations)
        duration_stddev = duration_variance ** 0.5 if duration_variance > 0 else 0.0

        for i in range(window_size, len(observations)):
            window = observations[i - window_size:i]
            window_errors = sum(1 for o in window if o["outcome"] == "error")
            window_error_rate = window_errors / len(window)
            current = observations[i]
            current_duration = current.get("duration_ms", 0.0)

            error_anomaly = False
            error_severity = 0.0
            if error_stddev > 0 and window_error_rate > mean_error_rate + error_sigma * error_stddev:
                error_anomaly = True
                error_severity = (window_error_rate - mean_error_rate) / max(error_stddev, 0.001)

            duration_anomaly = False
            duration_severity = 0.0
            if duration_stddev > 0 and current_duration > mean_duration + duration_sigma * duration_stddev:
                duration_anomaly = True
                duration_severity = (current_duration - mean_duration) / max(duration_stddev, 0.001)

            if error_anomaly or duration_anomaly:
                severity = max(error_severity, duration_severity)
                severity_label = ("critical" if severity > 5.0 else "high" if severity > 3.0 else "medium")
                anomalies.append({
                    "observation_index": i,
                    "observation_id": current.get("id", f"obs_{i}"),
                    "worm_type": current.get("worm_type", "unknown"),
                    "outcome": current.get("outcome", "unknown"),
                    "duration_ms": current_duration,
                    "window_error_rate": round(window_error_rate, 4),
                    "mean_error_rate": round(mean_error_rate, 4),
                    "severity": severity_label,
                    "severity_score": round(severity, 2),
                    "trigger": ("error_rate" if error_anomaly else "") + ("+" if error_anomaly and duration_anomaly else "")
                                + ("duration" if duration_anomaly else ""),
                    "timestamp": current.get("timestamp", ""),
                })

        return {
            "anomalies": anomalies,
            "total_analyzed": len(observations),
            "window_size": window_size,
            "baseline": {
                "mean_error_rate": round(mean_error_rate, 4),
                "error_stddev": round(error_stddev, 4),
                "mean_duration_ms": round(mean_duration, 2),
                "duration_stddev_ms": round(duration_stddev, 2),
            },
            "error_sigma_threshold": error_sigma,
            "duration_sigma_threshold": duration_sigma,
            "timestamp": datetime.now().isoformat(),
        }

    # -- Cross-Worm Correlation --------------------------------------

    def compute_cross_worm_correlation(self, worm_types: (list[str] | None) = None,
                                       window_count: int = 20,
                                       min_correlation: float = 0.3) -> dict[str, Any]:
        """Compute error-rate correlation matrix across worm types.

        Detects if errors in one worm type predict errors in another.
        Uses rolling-window error rates and Pearson correlation.

        Args:
            worm_types: Specific worm types to compare, or None for all tracked
            window_count: Number of rolling windows to use for time series
            min_correlation: Minimum |r| to report as significant

        Returns:
            dict with correlation matrix, significant pairs, and recommendations
        """
        with self._lock:
            excluded = []
            if worm_types is None:
                worm_types = list(self._error_patterns.keys())
            else:
                excluded = [w for w in worm_types if w not in self._error_patterns]
                worm_types = [w for w in worm_types if w in self._error_patterns]

            if len(worm_types) < 2:
                return {
                    "correlations": [],
                    "message": "Need at least 2 worm types with error data",
                    "excluded_no_data": excluded,
                }

            # Build time-series of error rates for each worm type
            # Use the most recent observations to create rolling windows
            all_obs = self._observations[-500:]

        # Partition observations into time windows (include tail in last window)
        if len(all_obs) < window_count:
            return {"correlations": [], "total_analyzed": len(all_obs), "message": f"Insufficient data (need >= {window_count} windows)"}

        obs_per_window = max(1, len(all_obs) // window_count)
        windows = []
        for i in range(window_count - 1):
            windows.append(all_obs[i * obs_per_window: (i + 1) * obs_per_window])
        # Last window gets all remaining observations (avoids dropping tail)
        windows.append(all_obs[(window_count - 1) * obs_per_window:])

        # Compute error-rate time series per worm type
        worm_series: dict[str, list[float]] = {}
        for wt in worm_types:
            series = []
            for window in windows:
                wt_obs = [o for o in window if o["worm_type"] == wt]
                if wt_obs:
                    error_rate = sum(1 for o in wt_obs if o["outcome"] == "error") / len(wt_obs)
                else:
                    error_rate = 0.0
                series.append(error_rate)
            worm_series[wt] = series

        # Compute Pearson correlation for each pair
        def pearson_r(x: list[float], y: list[float]) -> float:
            n = len(x)
            if n < 3:
                return 0.0
            mean_x = sum(x) / n
            mean_y = sum(y) / n
            cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
            std_x = (sum((xi - mean_x) ** 2 for xi in x)) ** 0.5
            std_y = (sum((yi - mean_y) ** 2 for yi in y)) ** 0.5
            if std_x == 0 or std_y == 0:
                return 0.0
            return cov / (std_x * std_y)

        correlations = []
        for i, wt_a in enumerate(worm_types):
            for wt_b in worm_types[i + 1:]:
                r = pearson_r(worm_series[wt_a], worm_series[wt_b])
                if abs(r) >= min_correlation:
                    direction = "positive" if r > 0 else "negative"
                    strength = ("strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.5 else "weak")
                    correlations.append({
                        "worm_a": wt_a,
                        "worm_b": wt_b,
                        "correlation": round(r, 4),
                        "direction": direction,
                        "strength": strength,
                        "interpretation": (
                            f"{wt_a} errors {'co-occur with' if r > 0 else 'are inversely related to'} {wt_b} errors"
                        ),
                    })

        # Sort by correlation magnitude
        correlations.sort(key=lambda c: -abs(c["correlation"]))

        # Generate recommendations from strong correlations
        recommendations = []
        for corr in correlations:
            if abs(corr["correlation"]) > 0.5:
                if corr["direction"] == "positive":
                    recommendations.append(
                        f"Consider joint CurativePool governance for {corr['worm_a']} and {corr['worm_b']} "
                        f"(r={corr['correlation']:.2f}) — errors propagate together"
                    )
                else:
                    recommendations.append(
                        f"Investigate inverse relationship between {corr['worm_a']} and {corr['worm_b']} "
                        f"(r={corr['correlation']:.2f}) — may indicate resource contention"
                    )

        return {
            "correlations": correlations,
            "significant_pairs": len(correlations),
            "worm_types_analyzed": len(worm_types),
            "total_windows": window_count,
            "min_correlation_threshold": min_correlation,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
        }


# -- MetaCognitionAgent (FreeThreadedAgent wrapper) -------------------------

try:
    from CORE.Agent import FreeThreadedAgent, AgentConfig
    from CORE.agent_registry import register_agent

    @register_agent(category="rl", priority=9, description="Meta-cognitive agent with self-reflection and strategy adaptation")
    class MetaCognitionAgent(FreeThreadedAgent):
        """FreeThreadedAgent wrapper for MetaCognitionWorm.

        Provides persistent meta-cognitive capabilities to any agent
        in the ecosystem through standard agent interface.
        """

        VERSION = "1.0.0"

        def __init__(self, config=None):
            super().__init__(config or AgentConfig(agent_name="MetaCognition"))
            self._mc = MetaCognitionWorm()

        def _run(self, task, pool=None):
            action = task.get("action", "introspect")
            payload = task.get("payload", task)

            if action == "observe":
                return self._mc.observe(**payload)
            elif action == "analyze":
                return self._mc.analyze_patterns(**payload)
            elif action == "adapt":
                return self._mc.adapt_strategy(**payload)
            elif action == "validate":
                return self._mc.validate_adaptation(**payload)
            elif action == "introspect":
                return self._mc.generate_introspection_report()
            else:
                return {"error": f"Unknown meta-cognition action: {action}"}

except ImportError:
    pass
