"""noxfile.py — Multi-Python test sessions for Azazael.

Usage:
    nox                          # Run default sessions (tests-314, tests-314t)
    nox -s tests-314             # Standard Python 3.14 only
    nox -s tests-314t            # Free-threaded Python 3.14t only
    nox -s quick-314             # Quick smoke test under standard 3.14
    nox -s quick-314t            # Quick smoke test under free-threaded 3.14t
    nox --list                   # List available sessions

Requires:
    python3.14  — Standard CPython 3.14 (on PATH)
    python3.14t — Free-threaded CPython 3.14t (on PATH)
"""

import nox

nox.options.sessions = ["tests-314", "tests-314t"]
nox.options.reuse_existing_virtualenvs = True


def _run_tests(session: nox.Session) -> None:
    """Run all Azazael tests via unittest discovery."""
    session.install("psutil")
    session.run(
        "python", "-c",
        "import sys; print(f'Python {sys.version_info[0]}.{sys.version_info[1]}"
        ".{sys.version_info[2]} on {sys.platform}')",
    )
    session.run(
        "python", "-m", "unittest", "discover", "-s", "tests", "-v",
        env={"PYTHONPATH": "src"},
    )


def _run_quick_tests(session: nox.Session) -> None:
    """Run predefined test files (faster, no discovery overhead).

    Uses ``--quick`` flag to skip longer integration tests.
    """
    session.install("psutil")
    session.run(
        "python", "-c",
        "import sys; print(f'Python {sys.version_info[0]}.{sys.version_info[1]}"
        ".{sys.version_info[2]} on {sys.platform}')",
    )
    quick_files = [
        ("tests/test_clusterworms_unit.py", ["--quick"]),
        ("tests/test_config_and_breaker.py", ["--quick"]),
        ("tests/test_nature_clusters_unit.py", []),
    ]
    for test_file, extra_args in quick_files:
        session.run(
            "python", test_file, *extra_args,
            env={"PYTHONPATH": "src"},
        )


@nox.session(python="3.14", name="tests-314")
def tests_314(session: nox.Session) -> None:
    """Full test suite under standard Python 3.14 (non-free-threaded)."""
    _run_tests(session)


@nox.session(python="3.14t", name="tests-314t")
def tests_314t(session: nox.Session) -> None:
    """Full test suite under free-threaded Python 3.14t.

    Note: This is the PRIMARY test target — Azazael is designed for
    the GIL-disabled 3.14t build. Standard 3.14 will also work but
    with degraded parallel performance (CLUSTERWORMS, CONCURRENCY).
    """
    _run_tests(session)


@nox.session(python="3.14", name="quick-314")
def quick_314(session: nox.Session) -> None:
    """Quick smoke test (predefined files, ``--quick`` mode) under standard 3.14."""
    _run_quick_tests(session)


@nox.session(python="3.14t", name="quick-314t")
def quick_314t(session: nox.Session) -> None:
    """Quick smoke test (predefined files, ``--quick`` mode) under free-threaded 3.14t."""
    _run_quick_tests(session)


# ═══════════════════════════════════════════════════════════════════
# Lint & Typecheck Sessions
# ═══════════════════════════════════════════════════════════════════


@nox.session(python="3.14t", name="lint")
def lint(session: nox.Session) -> None:
    """Run ruff linter on the src/ directory."""
    session.install("ruff")
    session.run(
        "ruff", "check", "src/",
        env={"PYTHONPATH": "src"},
    )


@nox.session(python="3.14t", name="format-check")
def format_check(session: nox.Session) -> None:
    """Check formatting with ruff (no changes made)."""
    session.install("ruff")
    session.run(
        "ruff", "format", "--check", "src/",
        env={"PYTHONPATH": "src"},
    )


@nox.session(python="3.14t", name="typecheck")
def typecheck(session: nox.Session) -> None:
    """Run mypy type checker on the src/ directory.

    Uses the existing [tool.mypy] config from pyproject.toml.
    Excluded files are those listed in pyproject.toml's exclude list.
    """
    session.install("mypy")
    session.run(
        "python", "-m", "mypy", "src/",
        env={"PYTHONPATH": "src"},
    )


@nox.session(python="3.14t", name="lint-all")
def lint_all(session: nox.Session) -> None:
    """Run all linters and typecheck in sequence (lint, format-check, typecheck)."""
    lint(session)
    format_check(session)
    typecheck(session)
