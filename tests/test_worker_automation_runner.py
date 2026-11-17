"""Tests for WORKER_AUTOMATION_RUNNER module."""

from __future__ import annotations

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from WORKER_AUTOMATION_RUNNER import (
    run_automation,
    run_tests,
    run_metrics,
    run_dispatch,
    main,
)


class TestRunnerFunctions:
    """Test runner entry points."""

    def test_run_tests(self):
        """run_tests executes without error."""
        # This will run the actual tests
        run_tests()

    def test_run_metrics(self):
        """run_metrics executes without error."""
        run_metrics()


class TestMainEntryPoint:
    """Test main entry point parsing."""

    def test_help(self):
        """Help displays."""
        import sys
        sys.argv = ["runner", "--help"]
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])