"""Regression guard: production store must be unwritable from tests."""
import os
import pytest


def test_local_memory_store_refuses_default_under_pytest(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "guard")
    from CORE.local_memory import LocalMemoryStore
    with pytest.raises(RuntimeError):
        LocalMemoryStore()


def test_local_memory_store_allows_explicit_db_path(tmp_path):
    from CORE.local_memory import LocalMemoryStore
    s = LocalMemoryStore(db_path=str(tmp_path / "t.db"))
    assert s.db_path.endswith("t.db")
