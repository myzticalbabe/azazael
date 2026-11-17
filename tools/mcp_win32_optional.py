#!/usr/bin/env python3
"""Let ``mcp`` import on a free-threaded 3.16 interpreter where pywin32 cannot exist.

The problem, measured 2026-11-16 in ``.venvs/py316t``:

* ``mcp`` declares ``pywin32>=311; sys_platform == 'win32'`` from 1.15 through
  2.3.0, and ``pip index versions pywin32`` returns ``from versions: none`` for
  this interpreter -- pywin32 ships no cp316 wheel at all, so the dependency is
  unsatisfiable, not merely uninstalled.
* Every ``mcp`` old enough to skip pywin32 imports
  ``pydantic._internal._typing_extra.eval_type_backport``, which pydantic 2.14.3
  no longer exports. There is no release in between: 1.28 already needs pywin32,
  1.20 still needs the pydantic internal.
* ``mcp/os/win32/utilities.py`` uses the win32 modules only for Windows Job
  Objects, and it already sets all four to ``None`` on non-Windows platforms,
  with every job-object call guarded by ``if not win32job``. The import is a
  hard failure for a capability the module is written to do without.

So this applies upstream's own non-Windows degradation on Windows: a guarded
import that leaves the four names ``None`` when pywin32 is absent. Process-tree
termination then falls back to ``process.terminate()``, which the module already
does when a job object cannot be created.

The edit lands in the installed package, which ``pip install --upgrade mcp``
replaces wholesale. Re-run ``--apply`` after any mcp upgrade; ``--check`` is the
gate that notices when it is needed.

    python tools/mcp_win32_optional.py --check     # exit 0 imports, exit 1 does not
    python tools/mcp_win32_optional.py --apply     # patch if absent (idempotent)
    python tools/mcp_win32_optional.py --revert    # restore the original block
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import sys
from pathlib import Path

TARGET_REL = "mcp/os/win32/utilities.py"

ORIGINAL = '''\
# Windows-specific imports for Job Objects
if sys.platform == "win32":
    import pywintypes
    import win32api
    import win32con
    import win32job
else:
    # Type stubs for non-Windows platforms
    win32api = None
    win32con = None
    win32job = None
    pywintypes = None
'''

PATCHED = '''\
# Windows-specific imports for Job Objects
#
# pywin32 ships no wheel for free-threaded 3.16 (pip index versions pywin32 ->
# "from versions: none"), and every mcp release from 1.15 to 2.3.0 declares it
# on win32, so the requirement is unsatisfiable there rather than missing.
# The four modules are used only by the Job Object helpers below, each of which
# is guarded by `if not win32job` and returns cleanly -- the same degradation
# this module already applies on non-Windows platforms. Applied by
# azazael/tools/mcp_win32_optional.py; re-apply after upgrading mcp.
try:
    import pywintypes
    import win32api
    import win32con
    import win32job
except ImportError:
    win32api = None
    win32con = None
    win32job = None
    pywintypes = None
'''


def target_path() -> Path:
    try:
        dist = importlib.metadata.distribution("mcp")
    except importlib.metadata.PackageNotFoundError:
        raise SystemExit("mcp is not installed in " + sys.executable)
    return Path(dist.locate_file(TARGET_REL))


def state(text: str) -> str:
    if PATCHED in text:
        return "patched"
    if ORIGINAL in text:
        return "original"
    return "unknown"


def check() -> int:
    """Import the module the servers actually need, and say what happened."""
    try:
        importlib.import_module("mcp.client.stdio")
    except Exception as exc:  # noqa: BLE001 - the exception type is the finding
        print("mcp.client.stdio FAILED: %s: %s" % (type(exc).__name__, exc))
        return 1
    print("mcp.client.stdio imports")
    return 0


def apply_patch(revert: bool) -> int:
    path = target_path()
    text = path.read_text(encoding="utf-8")
    now = state(text)
    want, replacement = ("original", ORIGINAL) if revert else ("patched", PATCHED)
    source, dest = (PATCHED, ORIGINAL) if revert else (ORIGINAL, PATCHED)

    if now == want:
        print("%s: already %s" % (path, want))
        return 0
    if now != ("original" if not revert else "patched"):
        print("%s: unrecognised import block -- mcp changed shape; handle by hand" % path)
        return 1

    path.write_text(text.replace(source, dest, 1), encoding="utf-8")
    print("%s: %s applied; re-checking" % (path, "revert" if revert else "patch"))
    return check() if not revert else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="exit 0 when mcp imports")
    g.add_argument("--apply", action="store_true", help="apply the optional import")
    g.add_argument("--revert", action="store_true", help="restore upstream's block")
    g.add_argument("--status", action="store_true", help="print the block's state only")
    args = ap.parse_args(argv)

    if args.status:
        path = target_path()
        print("%s: %s" % (path, state(path.read_text(encoding="utf-8"))))
        return 0
    if args.apply:
        return apply_patch(revert=False)
    if args.revert:
        return apply_patch(revert=True)
    # --check is the default: a bare run is a gate, not a mutation.
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
