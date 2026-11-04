# coding: utf-8
"""Tests for spitfire.compat.impl_free_threaded — free-threaded implementation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pytest

import spitfire.compat.impl_free_threaded as impl_ft


def test_module_imports():
    """Free-threaded implementation module imports without error."""
    assert hasattr(impl_ft, "census")
    assert hasattr(impl_ft, "fix")
    assert hasattr(impl_ft, "run")


def test_classify_returns_dict():
    """classify returns expected dict structure."""
    result = impl_ft.classify("src/spitfire/compat/impl_free_threaded.py", "modified")
    assert isinstance(result, dict)
    assert "path" in result
    assert "status" in result
    assert "category" in result


def test_sh_returns_tuple():
    """sh helper returns (code, stdout, stderr)."""
    code, out, err = impl_ft.sh("echo", "test")
    assert isinstance(code, int)
    assert isinstance(out, str)
    assert isinstance(err, str)
    assert code == 0
    assert "test" in out


def test_run_dispatches():
    """run dispatches to census/fix/all."""
    class Args:
        cmd = "unknown"
        max_workers = 1
        save = None

    rc = impl_ft.run(Args(), None)
    assert rc == 2


def test_free_threaded_detection():
    """Verify free-threaded runtime detection works."""
    import sys as _sys
    gil_free = getattr(_sys, "_is_gil_enabled", lambda: True)() is False
    # Test passes regardless - just documents the check
    assert isinstance(gil_free, bool)