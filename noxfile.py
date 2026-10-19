"""noxfile.py — Multi-Python test sessions for Azazael.

3.14 RETIREMENT (2026-10-19): the 3.14t free-threaded venv is archived and is
no longer a session target. Production is the free-threaded 3.15 build; the
GIL 3.15 build is the same version with the GIL on, so a session pair isolates
threading rather than version drift. The only sanctioned 3.14 runtime is the
3.14m GIL venv, and it is not a test target — it exists for a dependency that
has no 3.15 build.

Usage:
    nox                          # Run default sessions (tests-315, tests-315t)
    nox -s tests-315             # Standard Python 3.15 only
    nox -s tests-315t            # Free-threaded Python 3.15t only
    nox -s quick-315             # Quick smoke test under standard 3.15
    nox -s quick-315t            # Quick smoke test under free-threaded 3.15t
    nox --list                   # List available sessions

Requires:
    python3.15  — Standard CPython 3.15 (on PATH)
    python3.15t — Free-threaded CPython 3.15t (on PATH)
"""

import nox

nox.options.sessions = ["tests-315", "tests-315t"]
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


@nox.session(python="3.15", name="tests-315")
def tests_315(session: nox.Session) -> None:
    """Full test suite under standard Python 3.15 (non-free-threaded)."""
    _run_tests(session)


@nox.session(python="3.15t", name="tests-315t")
def tests_315t(session: nox.Session) -> None:
    """Full test suite under free-threaded Python 3.15t.

    Note: This is the PRIMARY test target — Azazael runs on the GIL-disabled
    3.15t build. Standard 3.15 will also work but with degraded parallel
    performance (CLUSTERWORMS, CONCURRENCY).
    """
    _run_tests(session)


@nox.session(python="3.15", name="quick-315")
def quick_315(session: nox.Session) -> None:
    """Quick smoke test (predefined files, ``--quick`` mode) under standard 3.15."""
    _run_quick_tests(session)


@nox.session(python="3.15t", name="quick-315t")
def quick_315t(session: nox.Session) -> None:
    """Quick smoke test (predefined files, ``--quick`` mode) under free-threaded 3.15t."""
    _run_quick_tests(session)


# ═══════════════════════════════════════════════════════════════════
# Lint & Typecheck Sessions
# ═══════════════════════════════════════════════════════════════════


@nox.session(python="3.15t", name="lint")
def lint(session: nox.Session) -> None:
    """Run ruff linter on the src/ directory."""
    session.install("ruff")
    session.run(
        "ruff", "check", "src/",
        env={"PYTHONPATH": "src"},
    )


@nox.session(python="3.15t", name="format-check")
def format_check(session: nox.Session) -> None:
    """Check formatting with ruff (no changes made)."""
    session.install("ruff")
    session.run(
        "ruff", "format", "--check", "src/",
        env={"PYTHONPATH": "src"},
    )


@nox.session(python="3.15t", name="typecheck")
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


@nox.session(python="3.15t", name="lint-all")
def lint_all(session: nox.Session) -> None:
    """Run all linters and typecheck in sequence (lint, format-check, typecheck)."""
    lint(session)
    format_check(session)
    typecheck(session)
