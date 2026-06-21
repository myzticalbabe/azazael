# coding: utf-8
"""Unit tests for CORE/config.py — AzazaelConfig loading and validation."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Python 3.14t Free-Threading Guard (module level — before imports) ──
from _env_314t import setup_314t
setup_314t(mock_pams=True)

try:
    import pytest
except BaseException:
    import types
    pytest = types.ModuleType("pytest")
    pytest.skip = lambda reason=None: exec("raise type('Skip', (BaseException,), {})(reason or '')")
    pytest.mark = types.ModuleType("mark")
    pytest.mark.skip = lambda *a, **kw: lambda f: f

# ── Module Under Test ──────────────────────────────────────────────
from CORE.config import (
    AzazaelConfig,
    PathsConfig,
    PamsConfig,
    CircuitBreakerConfig,
    ClustersConfig,
    NatureConfig,
    ObservabilityConfig,
    LoggingConfig,
    MetricsConfig,
    FreeThreadingConfig,
    SecurityConfig,
    BackupConfig,
    BuildConfig,
    get_config,
    reset_config,
    get_warnings,
    _find_config_file,
)


# ═══════════════════════════════════════════════════════════════════
# PathsConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestPathsConfig:
    """Verify PathsConfig section."""

    def test_defaults(self):
        cfg = PathsConfig()
        assert cfg.project_root is None
        assert cfg.output_dir is None
        assert cfg.archive_dir is None
        assert cfg.desktop_dir is None

    def test_from_dict(self):
        cfg = PathsConfig.from_dict({
            "project_root": "/custom/root",
            "output_dir": "/custom/output",
        })
        assert cfg.project_root == "/custom/root"
        assert cfg.output_dir == "/custom/output"

    def test_env_var_override(self):
        """Environment variable should override YAML value."""
        os.environ["AZAZAEL_ROOT"] = "/env/root"
        try:
            cfg = PathsConfig.from_dict({"project_root": "/yaml/root"})
            assert cfg.project_root == "/env/root"
        finally:
            del os.environ["AZAZAEL_ROOT"]


# ═══════════════════════════════════════════════════════════════════
# PamsConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestPamsConfig:
    """Verify PamsConfig section."""

    def test_defaults(self):
        cfg = PamsConfig()
        assert cfg.url == "http://localhost:8420"
        assert cfg.session_prefix == "azazael"
        assert cfg.poll_interval_sec == 1.0
        assert cfg.use_local_fallback is True

    def test_from_dict(self):
        cfg = PamsConfig.from_dict({
            "url": "http://custom:9999",
            "session_prefix": "custom",
            "poll_interval_sec": 2.5,
            "use_local_fallback": False,
        })
        assert cfg.url == "http://custom:9999"
        assert cfg.session_prefix == "custom"
        assert cfg.poll_interval_sec == 2.5
        assert cfg.use_local_fallback is False

    def test_env_var_override(self):
        os.environ["PAMS_URL"] = "http://env:1234"
        try:
            cfg = PamsConfig.from_dict({"url": "http://yaml:5678"})
            assert cfg.url == "http://env:1234"
        finally:
            del os.environ["PAMS_URL"]


# ═══════════════════════════════════════════════════════════════════
# CircuitBreakerConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestCircuitBreakerConfig:
    """Verify CircuitBreakerConfig section."""

    def test_defaults(self):
        cfg = CircuitBreakerConfig()
        assert cfg.failure_threshold == 5
        assert cfg.recovery_timeout == 30.0
        assert cfg.half_open_max_requests == 3
        assert cfg.retry_base_delay == 0.1
        assert cfg.retry_max_delay == 60.0
        assert cfg.retry_backoff == 2.0
        assert cfg.dead_letter_max == 1000
        assert cfg.enabled is True

    def test_from_dict_partial(self):
        """Only provided fields should be overridden."""
        cfg = CircuitBreakerConfig.from_dict({
            "failure_threshold": 10,
            "recovery_timeout": 15.0,
        })
        assert cfg.failure_threshold == 10
        assert cfg.recovery_timeout == 15.0
        assert cfg.half_open_max_requests == 3  # default

    def test_to_circuit_config(self):
        """Should convert to CORE.circuit_breaker.CircuitConfig."""
        cfg = CircuitBreakerConfig(
            failure_threshold=7,
            recovery_timeout=45.0,
            half_open_max_requests=5,
            retry_base_delay=0.2,
            retry_max_delay=90.0,
            retry_backoff=3.0,
            dead_letter_max=500,
        )
        cc = cfg.to_circuit_config()
        assert cc.failure_threshold == 7
        assert cc.recovery_timeout == 45.0
        assert cc.half_open_max_requests == 5
        assert cc.retry_base_delay == 0.2
        assert cc.retry_max_delay == 90.0
        assert cc.retry_backoff == 3.0
        assert cc.dead_letter_max == 500


# ═══════════════════════════════════════════════════════════════════
# ClustersConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestClustersConfig:
    """Verify ClustersConfig section."""

    def test_defaults(self):
        cfg = ClustersConfig()
        assert cfg.default_timeout == 60
        assert cfg.max_parallel_worms == 8
        assert cfg.retry_enabled is True
        assert cfg.max_retries == 3
        assert cfg.record_to_pams is True


# ═══════════════════════════════════════════════════════════════════
# Other Config Sections
# ═══════════════════════════════════════════════════════════════════


class TestFreeThreadingConfig:
    def test_defaults(self):
        cfg = FreeThreadingConfig()
        assert cfg.enabled == "auto"
        assert cfg.max_workers is None


class TestLoggingConfig:
    def test_defaults(self):
        cfg = LoggingConfig()
        assert cfg.level == "INFO"

    def test_env_var_override(self):
        os.environ["AZAZAEL_LOG_LEVEL"] = "DEBUG"
        try:
            cfg = LoggingConfig.from_dict({})
            assert cfg.level == "DEBUG"
        finally:
            del os.environ["AZAZAEL_LOG_LEVEL"]


class TestSecurityConfig:
    def test_defaults(self):
        cfg = SecurityConfig()
        assert cfg.secret_rotation_days == 30
        assert cfg.audit_enabled is True


class TestBackupConfig:
    def test_defaults(self):
        cfg = BackupConfig()
        assert cfg.interval_hours == 24
        assert cfg.keep_count == 7
        assert cfg.target_dir is None


class TestBuildConfig:
    def test_defaults(self):
        cfg = BuildConfig()
        assert cfg.python_version == "3.14"
        assert cfg.output_dir == "G:/AZAZAEL_Standalone"
        assert "torch" in cfg.nofollow_imports
        assert "optree" in cfg.nofollow_imports


# ═══════════════════════════════════════════════════════════════════
# AzazaelConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestAzazaelConfig:
    """Verify top-level AzazaelConfig."""

    def test_default_construction(self):
        """Default config should have all sections initialized."""
        cfg = AzazaelConfig()
        assert cfg.version == "1.0.0"
        assert isinstance(cfg.paths, PathsConfig)
        assert isinstance(cfg.pams, PamsConfig)
        assert isinstance(cfg.circuit_breaker, CircuitBreakerConfig)
        assert isinstance(cfg.clusters, ClustersConfig)
        assert isinstance(cfg.free_threading, FreeThreadingConfig)
        assert isinstance(cfg.observability, ObservabilityConfig)
        assert isinstance(cfg.security, SecurityConfig)
        assert isinstance(cfg.backup, BackupConfig)
        assert isinstance(cfg.build, BuildConfig)

    def test_from_dict(self):
        """Full dict should populate all sections."""
        cfg = AzazaelConfig.from_dict({
            "version": "2.0.0",
            "pams": {"url": "http://test:1234"},
            "circuit_breaker": {"failure_threshold": 99},
            "clusters": {"default_timeout": 120},
        })
        assert cfg.version == "2.0.0"
        assert cfg.pams.url == "http://test:1234"
        assert cfg.circuit_breaker.failure_threshold == 99
        assert cfg.clusters.default_timeout == 120

    def test_validate_defaults(self):
        """Default config should validate clean."""
        cfg = AzazaelConfig()
        warnings = cfg.validate()
        assert len(warnings) == 0

    def test_validate_bad_values(self):
        """Invalid values should produce warnings."""
        cfg = AzazaelConfig()
        cfg.clusters.default_timeout = 0
        cfg.circuit_breaker.failure_threshold = -1
        warnings = cfg.validate()
        assert len(warnings) == 2
        assert any("timeout" in w.lower() for w in warnings)
        assert any("failure_threshold" in w.lower() for w in warnings)

    def test_validate_zero_recovery_timeout(self):
        """Zero recovery timeout should warn."""
        cfg = AzazaelConfig()
        cfg.circuit_breaker.recovery_timeout = 0
        warnings = cfg.validate()
        assert len(warnings) == 1
        assert "recovery_timeout" in warnings[0]


# ═══════════════════════════════════════════════════════════════════
# Config Singleton Tests
# ═══════════════════════════════════════════════════════════════════


class TestConfigSingleton:
    """Verify get_config singleton behavior."""

    def test_get_config_returns_instance(self):
        reset_config()
        cfg = get_config()
        assert isinstance(cfg, AzazaelConfig)

    def test_get_config_is_cached(self):
        reset_config()
        cfg1 = get_config()
        cfg2 = get_config()
        assert cfg1 is cfg2

    def test_get_config_reload(self):
        reset_config()
        cfg1 = get_config()
        cfg2 = get_config(reload=True)
        # Both should be AzazaelConfig instances
        assert isinstance(cfg2, AzazaelConfig)

    def test_get_warnings(self):
        reset_config()
        cfg = get_config()
        warnings = get_warnings()
        assert isinstance(warnings, list)

    def test_reset_config(self):
        reset_config()
        cfg1 = get_config()
        reset_config()
        cfg2 = get_config()
        assert isinstance(cfg2, AzazaelConfig)


class TestFindConfigFile:
    """Verify config file discovery."""

    def test_find_config_returns_path_or_none(self):
        result = _find_config_file()
        # Either finds the file or returns None
        if result is not None:
            assert result.exists()
            assert result.name == "azazael.yaml"


# ═══════════════════════════════════════════════════════════════════
# NatureConfig Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureConfig:
    """Verify NatureConfig section."""

    def test_defaults(self):
        """Default NatureConfig should have safe defaults."""
        cfg = NatureConfig()
        assert cfg.enabled is True
        assert cfg.timeout is None
        assert cfg.max_retries is None
        assert cfg.parallel is None
        assert cfg.feeds_into == []

    def test_from_dict_full(self):
        """Full dict should override all fields."""
        cfg = NatureConfig.from_dict({
            "enabled": False,
            "timeout": 120,
            "max_retries": 2,
            "parallel": True,
            "feeds_into": ["defense", "telemetry"],
        })
        assert cfg.enabled is False
        assert cfg.timeout == 120
        assert cfg.max_retries == 2
        assert cfg.parallel is True
        assert cfg.feeds_into == ["defense", "telemetry"]

    def test_from_dict_partial(self):
        """Partial dict should leave unspecified fields as None/default."""
        cfg = NatureConfig.from_dict({"timeout": 90})
        assert cfg.timeout == 90
        assert cfg.max_retries is None
        assert cfg.parallel is None
        assert cfg.enabled is True  # default

    def test_merge_with_cluster_timeout(self):
        """merge_with_cluster should use nature timeout when set."""
        nature = NatureConfig(timeout=45)
        cluster = ClustersConfig(default_timeout=60, max_retries=3)
        merged = nature.merge_with_cluster(cluster)
        assert merged["timeout"] == 45  # nature overrides cluster
        assert merged["max_retries"] == 3  # falls through to cluster
        assert merged["parallel"] is False  # default

    def test_merge_with_cluster_fallback(self):
        """merge_with_cluster should use cluster defaults when nature has None."""
        nature = NatureConfig()  # all None
        cluster = ClustersConfig(default_timeout=60, max_retries=3)
        merged = nature.merge_with_cluster(cluster)
        assert merged["timeout"] == 60
        assert merged["max_retries"] == 3
        assert merged["parallel"] is False

    def test_merge_with_cluster_parallel(self):
        """merge_with_cluster should use nature parallel when set."""
        nature = NatureConfig(parallel=True)
        cluster = ClustersConfig()
        merged = nature.merge_with_cluster(cluster)
        assert merged["parallel"] is True

    def test_merge_with_cluster_falsy_timeout(self):
        """merge_with_cluster should treat falsy timeout (0/None) as cluster default."""
        for falsy_value in (0, None):
            nature = NatureConfig(timeout=falsy_value)
            cluster = ClustersConfig(default_timeout=60)
            merged = nature.merge_with_cluster(cluster)
            assert merged["timeout"] == 60, \
                f"timeout={falsy_value!r} should fall through to cluster default 60, got {merged['timeout']}"


class TestAzazaelConfigNatures:
    """Verify AzazaelConfig nature integration."""

    def test_get_nature_config_default(self):
        """get_nature_config for unknown nature returns defaults."""
        cfg = AzazaelConfig()
        nature = cfg.get_nature_config("nonexistent")
        assert isinstance(nature, NatureConfig)
        assert nature.timeout is None
        assert nature.max_retries is None

    def test_get_nature_config_from_yaml(self):
        """get_nature_config from loaded YAML should have overrides."""
        reset_config()
        cfg = get_config()
        monitor = cfg.get_nature_config("monitor")
        # Values come from azazael.yaml:
        #   monitor.timeout: 30, monitor.max_retries: 2
        #   monitor.parallel: true, feeds_into: ["orchestration"]
        assert monitor.timeout == 30
        assert monitor.max_retries == 2
        assert monitor.parallel is True
        assert "orchestration" in monitor.feeds_into

    def test_natures_from_dict(self):
        """AzazaelConfig.from_dict should parse natures."""
        cfg = AzazaelConfig.from_dict({
            "natures": {
                "test": {"timeout": 99, "parallel": False},
            },
        })
        test_nature = cfg.get_nature_config("test")
        assert test_nature.timeout == 99
        assert test_nature.parallel is False


# ═══════════════════════════════════════════════════════════════════
# Circuit Breaker Integration Tests (CLUSTERWORMS)
# ═══════════════════════════════════════════════════════════════════


class TestCircuitBreakerIntegration:
    """Verify circuit breaker integration in CLUSTERWORMS."""

    def test_cluster_status_has_breaker_info(self):
        """Cluster status should report breaker availability."""
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
        cluster = ClusterWORMZ("system")
        status = cluster.get_status()
        assert "breaker_ok" in status

    def test_execute_with_breaker_does_not_crash(self):
        """Execution with breaker enabled should not crash."""
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
        cluster = ClusterWORMZ("system")
        results = cluster.execute_all()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_breaker_registry_accumulates_stats(self):
        """After execution, breaker stats should be available."""
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ, _breaker_registry, _get_breaker_registry
        if not _get_breaker_registry() or not _breaker_registry:
            pytest.skip("Circuit breaker not available")
        cluster = ClusterWORMZ("system")
        cluster.execute_all()
        stats = _breaker_registry.all_stats()
        assert len(stats) > 0


# ═══════════════════════════════════════════════════════════════════
# Circuit Breaker Integration Tests (NATURE_CLUSTERS)
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterBreakerIntegration:
    """Verify circuit breaker integration in NATURE_CLUSTERS."""

    def test_nature_cluster_status_has_breaker_info(self):
        """Nature cluster status should report breaker info."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
        cluster = NatureCluster("security")
        status = cluster.get_status()
        assert "breaker_ok" in status

    def test_execute_with_breaker_does_not_crash(self):
        """Nature cluster execution with breaker should not crash."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
        cluster = NatureCluster("security")
        cluster.discover_worms()
        result = cluster.execute()
        assert result is not None


# ═══════════════════════════════════════════════════════════════════
# NATURE_CLUSTERS Discovery Edge Cases
# ═══════════════════════════════════════════════════════════════════


class TestNatureDiscoveryEdgeCases:
    """Verify Nature discovery handles edge cases."""

    def test_discover_all_natures_repeatable(self):
        """Calling discover_all_natures twice should not error."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
        ncm = NatureClusterManager()
        first = ncm.discover_all_natures()
        second = ncm.discover_all_natures()
        assert first == second  # Should be idempotent

    def test_get_cluster_nonexistent(self):
        """Getting a non-existent cluster should return None or empty."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        # Clusters dict may or may not have already been discovered for unknown natures
        cluster = ncm.get_cluster("__nonexistent_999__")
        if cluster is not None:
            assert cluster.worms == {}  # No worms discovered for unknown nature

    def test_execute_nonexistent_nature_returns_none(self):
        """Executing non-existent nature should return None."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
        ncm = NatureClusterManager()
        result = ncm.execute_nature("__nonexistent_nature__")
        assert result is None

    def test_manager_status_after_execution(self):
        """Status should reflect execution history."""
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        result = ncm.execute_nature("security")
        status = ncm.get_status()
        assert status["execution_history_count"] >= 1


if __name__ == "__main__":
    import subprocess
    sys.path.insert(0, os.path.dirname(__file__))
    from _timer_utils import run_class_with_timeout

    quick_mode = "--quick" in sys.argv

    # Slow integration test classes that run real worm execution
    slow_classes = {
        "TestCircuitBreakerIntegration",
        "TestNatureClusterBreakerIntegration",
        "TestNatureDiscoveryEdgeCases",
    }

    # Subprocess timeouts for slow classes (seconds)
    subprocess_timeouts = {
        "TestCircuitBreakerIntegration": 120,
        "TestNatureClusterBreakerIntegration": 120,
        "TestNatureDiscoveryEdgeCases": 60,
    }

    p = f = s = 0
    errors = []

    for name, obj in list(globals().items()):
        if isinstance(obj, type) and name.startswith("Test"):
            method_count = len([mn for mn in dir(obj) if mn.startswith("test_")])

            if quick_mode and name in slow_classes:
                print(f"  [SKIP] {name}.* ({method_count} tests skipped in --quick mode)")
                s += method_count
                continue

            if name in subprocess_timeouts:
                timeout = subprocess_timeouts[name]
                print(f"[{name}] (subprocess, timeout={timeout}s)")
                try:
                    sp, sf, sk = run_class_with_timeout(obj, timeout_sec=timeout)
                    p += sp; f += sf; s += sk
                except subprocess.TimeoutExpired:
                    print(f"  [FAIL] {name}.* — subprocess timed out after {timeout}s")
                    f += method_count
                    errors.append(f"{name}: TIMEOUT (subprocess killed at {timeout}s)")
                except Exception as e:
                    print(f"  [FAIL] {name}.* — subprocess error: {e}")
                    f += method_count
                    errors.append(f"{name}: SUBPROCESS ERROR: {e}")
            else:
                print(f"[{name}]")
                inst = obj()
                for mn in sorted(dir(inst)):
                    if mn.startswith("test_"):
                        try:
                            getattr(inst, mn)()
                            print(f"  [OK] {name}.{mn}")
                            p += 1
                        except BaseException as exc:
                            if type(exc).__name__ == 'Skip':
                                print(f"  [SKIP] {name}.{mn}: {exc}")
                                s += 1
                            elif isinstance(exc, (SystemExit, KeyboardInterrupt)):
                                raise
                            else:
                                print(f"  [FAIL] {name}.{mn}: {exc}")
                                f += 1
                                errors.append(f"{name}.{mn}: {exc}")

    print(f"  Passed: {p}, Failed: {f}, Skipped: {s}")
    if errors:
        print("  Errors:")
        for e in errors[:10]:
            print(f"    {e}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
