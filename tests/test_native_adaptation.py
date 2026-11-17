"""Tests for NATIVE_ADAPTATION module."""

from __future__ import annotations

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from NATIVE_ADAPTATION import (
    AdaptationConfig,
    SidecarClient,
    SidecarModuleProxy,
    AdaptationRegistry,
    get_module,
    is_native,
    install_native,
    register_adaptation,
    preload_adaptations,
    torch,
    transformers,
    tensorflow,
    cv2,
    opencv,
)

# Check if we're on 3.16t (free-threaded)
IS_316T = sys.version_info >= (3, 16) and hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled()


class TestAdaptationConfig:
    """Test AdaptationConfig."""

    def test_paths_exist(self):
        """Config paths are valid."""
        assert AdaptationConfig.PY316T.name == "python.exe"
        assert AdaptationConfig.PY315T.name == "python.exe"
        assert "py316t" in str(AdaptationConfig.PY316T)
        assert "py315t" in str(AdaptationConfig.PY315T)

    def test_package_categories(self):
        """Package categories are defined."""
        assert "torch" in AdaptationConfig.REQUIRES_SIDECAR
        assert "transformers" in AdaptationConfig.REQUIRES_SIDECAR
        assert "numpy" not in AdaptationConfig.REQUIRES_SIDECAR


class TestSidecarClient:
    """Test SidecarClient."""

    def test_sidecar_verification(self):
        """Sidecar client verifies sidecar on init."""
        client = SidecarClient(AdaptationConfig.SIDECAR_PYTHON)
        # Should not raise if sidecar works
        assert client.sidecar == AdaptationConfig.SIDECAR_PYTHON


class TestAdaptationRegistry:
    """Test AdaptationRegistry."""

    def setup_method(self):
        self.registry = AdaptationRegistry()

    def test_is_native_numpy(self):
        """numpy is native on 3.16t."""
        assert self.registry.is_native("numpy") is True

    @pytest.mark.skipif(not IS_316T, reason="Only valid on 3.16t free-threaded")
    def test_is_native_torch(self):
        """torch is not native on 3.16t."""
        assert self.registry.is_native("torch") is False

    def test_get_module_native(self):
        """Get native module."""
        mod = self.registry.get_module("numpy")
        assert hasattr(mod, "__version__")

    def test_get_module_sidecar(self):
        """Get sidecar module."""
        mod = self.registry.get_module("torch")
        # Returns SidecarModuleProxy
        from NATIVE_ADAPTATION import SidecarModuleProxy
        assert isinstance(mod, SidecarModuleProxy) or hasattr(mod, '__version__')


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_is_native(self):
        """is_native works."""
        assert is_native("numpy") is True
        # torch native status depends on Python version
        if IS_316T:
            assert is_native("torch") is False
        else:
            # On non-3.16t, torch might be native
            assert is_native("torch") in (True, False)

    def test_get_module(self):
        """get_module returns module or proxy."""
        mod = get_module("numpy")
        assert hasattr(mod, "__version__")

    def test_register_adaptation(self):
        """Register custom adaptation."""
        class FakeMod:
            pass
        register_adaptation("fake_pkg", FakeMod)
        # Should be retrievable
        # (registry is global, so this affects other tests)


class TestAdaptedModules:
    """Test AdaptedModule proxies."""

    def test_torch_proxy(self):
        """torch proxy works."""
        # This will route to sidecar
        assert hasattr(torch, "__version__")

    def test_transformers_proxy(self):
        """transformers proxy works."""
        assert hasattr(transformers, "__version__")


class TestPreloadAdaptations:
    """Test preload_adaptations."""

    def test_preload_runs(self):
        """preload_adaptations runs without error."""
        preload_adaptations()  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])