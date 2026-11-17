"""The mcp pywin32 patch: the gate must notice, and must never misclassify.

``pywin32`` ships no free-threaded wheel, and every ``mcp`` release from 1.15 to
2.3.0 declares it on win32, so in ``.venvs/py316t`` the requirement is
UNSATISFIABLE rather than merely uninstalled. ``tools/mcp_win32_optional.py``
applies upstream's own non-Windows degradation to Windows: a guarded import that
leaves the four names ``None``, which is what ``mcp/os/win32/utilities.py``
already assumes on every other platform.

The failure mode worth pinning is classification, not the write. The patch lands
in site-packages, which ``pip install --upgrade mcp`` replaces wholesale, so
``--check`` is the only thing standing between an upgrade and a stack whose every
MCP server dies at import. If ``state()`` ever calls a changed upstream block
"patched", that gate reports a healthy environment while the import is broken --
the same shape as a stale verdict reported as fresh.

Measured 2026-11-16 in ``.venvs/py316t`` (3.16.0a1, ``sys._is_gil_enabled()``
False): ``pywintypes``/``win32api``/``win32job``/``win32con`` all raise
ModuleNotFoundError, the site-packages block reads ``patched``, and
``mcp.client.stdio`` imports. ``src/win32_shim`` exists but is NOT on that
interpreter's path, so it does not resolve this import -- the patch is what is
in force.

Nothing here writes to site-packages: ``apply_patch`` is deliberately untested,
because a test that mutates the interpreter it runs under is not a test.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mcp_win32_optional as mwo  # noqa: E402


def test_original_block_is_the_upstream_shape():
    """ORIGINAL must be what upstream actually ships, or replace() never matches."""
    assert 'if sys.platform == "win32":' in mwo.ORIGINAL
    assert "import pywintypes" in mwo.ORIGINAL
    assert "import win32job" in mwo.ORIGINAL
    # Upstream's else-branch is the degradation this patch extends to Windows.
    assert "win32job = None" in mwo.ORIGINAL


def test_patched_block_degrades_instead_of_failing():
    """The patch must turn a hard import into a guarded one, all four names."""
    assert "try:" in mwo.PATCHED
    assert "except ImportError:" in mwo.PATCHED
    for name in ("win32api", "win32con", "win32job", "pywintypes"):
        assert "%s = None" % name in mwo.PATCHED, name
    # The patch must not drop the imports it is guarding.
    for name in ("win32api", "win32con", "win32job", "pywintypes"):
        assert "import %s" % name in mwo.PATCHED, name


def test_state_classifies_each_block():
    assert mwo.state(mwo.ORIGINAL) == "original"
    assert mwo.state(mwo.PATCHED) == "patched"


def test_state_says_unknown_for_a_changed_upstream_block():
    """The negative control: an unrecognised block is never called patched."""
    assert mwo.state("import pywin32  # some future mcp rewrote this") == "unknown"
    assert mwo.state("") == "unknown"


def test_patched_is_not_mistaken_for_original():
    """The two blocks must be distinguishable, or --apply would be a no-op loop."""
    assert mwo.PATCHED != mwo.ORIGINAL
    assert mwo.state(mwo.PATCHED) != mwo.state(mwo.ORIGINAL)


def test_check_reports_a_verdict_and_never_raises():
    """--check is a gate: it returns 0 or 1 and names the outcome either way."""
    rc = mwo.check()
    assert rc in (0, 1)


def test_status_exits_zero_and_names_the_path(capsys):
    """--status must be readable without mutating anything."""
    assert mwo.main(["--status"]) == 0
    out = capsys.readouterr().out
    assert "utilities.py" in out
    assert (
        "patched" in out or "original" in out or "unknown" in out
    ), out


def test_bare_invocation_is_a_check_not_a_mutation():
    """A bare run must judge, never patch -- the docstring promises this."""
    assert mwo.main([]) in (0, 1)
