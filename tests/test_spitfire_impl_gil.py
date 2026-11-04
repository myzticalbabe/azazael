# coding: utf-8
"""Tests for spitfire.compat.impl_gil — GIL implementation."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pytest

import spitfire.compat.impl_gil as impl_gil


def test_module_imports():
    """GIL implementation module imports without error."""
    assert hasattr(impl_gil, "census")
    assert hasattr(impl_gil, "fix")
    assert hasattr(impl_gil, "run")


def test_classify_returns_dict():
    """classify returns expected dict structure."""
    # Uses actual repo paths - may be untracked
    result = impl_gil.classify("src/spitfire/compat/impl_gil.py", "modified")
    assert isinstance(result, dict)
    assert "path" in result
    assert "status" in result
    assert "category" in result


def test_sh_returns_tuple():
    """sh helper returns (code, stdout, stderr)."""
    code, out, err = impl_gil.sh("echo", "test")
    assert isinstance(code, int)
    assert isinstance(out, str)
    assert isinstance(err, str)
    assert code == 0
    assert "test" in out


def test_run_dispatches():
    """run dispatches to census/fix/all."""
    # Just verify the function exists and handles unknown cmd
    class Args:
        cmd = "unknown"
        max_workers = 1
        save = None

    rc = impl_gil.run(Args(), None)
    assert rc == 2