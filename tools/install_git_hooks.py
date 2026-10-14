#!/usr/bin/env python3
# coding: utf-8
"""Install this repo's tracked git hooks so they actually run.

The gap this closes
-------------------
`.githooks/pre-commit` has existed since 2026-09-28 and has never run. Its own
header says how it is meant to be activated --

    Installed by: git config core.hooksPath .githooks

-- and `git config --get core.hooksPath` returned nothing, so git was reading
the default `.git/hooks/`, which contains only `*.sample`. The compliance
scanner, the bulk-diff gate and the catch-all guard were all built and none of
them was connected. `reports/ERROR_LESSON_AUDIT_2026-10-03.md` names this as
Lesson #86 in its purest form: a check that is built and wired to nothing that
blocks.

Why `core.hooksPath` and not copying into `.git/hooks/`
-------------------------------------------------------
`.git/hooks/` is not tracked, so a copy there drifts from `.githooks/` the
moment either is edited, and a fresh clone has no hook at all. Pointing
`core.hooksPath` at the tracked `.githooks/` makes the tracked file the one that
runs, so the hook is versioned with the code it guards.

This is a per-clone action (the setting lives in `.git/config`, which git does
not version). Run this script once per clone.

Usage
-----
    python tools/install_git_hooks.py            # install (idempotent)
    python tools/install_git_hooks.py --check    # report status, change nothing
    python tools/install_git_hooks.py --uninstall
"""
from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIRNAME = ".githooks"
REQUIRED_HOOKS = ("pre-commit",)


def _git(*args: str) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=str(ROOT),
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "").rstrip("\n") + (r.stderr or "").rstrip("\n")


def current_hookspath() -> str:
    rc, out = _git("config", "--get", "core.hooksPath")
    return out if rc == 0 else ""


def hooks_dir() -> Path:
    return ROOT / HOOKS_DIRNAME


def hook_paths() -> list[Path]:
    return [hooks_dir() / name for name in REQUIRED_HOOKS]


def _make_executable(path: Path) -> bool:
    """Set the executable bit where the filesystem has one (POSIX)."""
    try:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except OSError:
        return False


def install() -> int:
    missing = [p for p in hook_paths() if not p.exists()]
    if missing:
        print("FAIL: tracked hook(s) missing: %s"
              % ", ".join(str(p.relative_to(ROOT)) for p in missing),
              file=sys.stderr)
        return 1

    for p in hook_paths():
        _make_executable(p)

    rc, out = _git("config", "core.hooksPath", HOOKS_DIRNAME)
    if rc != 0:
        print("FAIL: could not set core.hooksPath: %s" % out, file=sys.stderr)
        return 1

    print("core.hooksPath = %s" % current_hookspath())
    for p in hook_paths():
        print("  active: %s" % p.relative_to(ROOT))
    print("\nHooks are installed. Bypass a single commit with "
          "`git commit --no-verify`.")
    return 0


def check() -> int:
    hp = current_hookspath()
    ok = True
    print("core.hooksPath : %s" % (hp or "(unset -- .git/hooks/ is in use)"))
    if hp != HOOKS_DIRNAME:
        print("  FAIL: not pointing at %s" % HOOKS_DIRNAME)
        ok = False
    for p in hook_paths():
        exists = p.exists()
        executable = bool(p.exists() and (os.stat(p).st_mode & stat.S_IXUSR))
        print("  %-24s exists=%s executable=%s"
              % (p.relative_to(ROOT), exists, executable))
        if not exists:
            ok = False
    print("STATUS: %s" % ("INSTALLED" if ok else "NOT INSTALLED"))
    return 0 if ok else 1


def uninstall() -> int:
    rc, out = _git("config", "--unset", "core.hooksPath")
    if rc != 0 and "not found" not in out.lower() and out:
        print("FAIL: could not unset core.hooksPath: %s" % out, file=sys.stderr)
        return 1
    print("core.hooksPath unset; .git/hooks/ (samples only) is in use again.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="report install status, change nothing")
    group.add_argument("--uninstall", action="store_true",
                       help="unset core.hooksPath")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    if args.uninstall:
        return uninstall()
    return install()


if __name__ == "__main__":
    sys.exit(main())
