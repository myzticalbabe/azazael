#!/usr/bin/env python3
r"""SOULFORGE -- the Vulcan-salute cursor swarm as one Windows program.

Double-click it and it prints what is built, what is installed, what is live and
what is wrong, then offers the verbs. Give it a flag for a scripted one-shot.

  SOULFORGE.exe                 status, then the menu
  SOULFORGE.exe --build         rasterise the masters into out\cursors
  SOULFORGE.exe --apply         build, install, switch the pointers, go live
  SOULFORGE.exe --check         read every artefact and live pointer back
  SOULFORGE.exe --restore       put the saved scheme back
  SOULFORGE.exe --defaults      Windows Aero back, backup or not
  SOULFORGE.exe --uninstall     remove the files, the scheme and the pointers
  SOULFORGE.exe --selftest      run build, install, check and uninstall on a
                               throwaway key, proving the binary without
                               moving the pointers you are using
  SOULFORGE.exe --preview       open the built preview.png

Exit codes: 0 nothing wrong, 1 a defect named, 2 nothing to read, 3 refused.
Every verb delegates to make_cursors, so the binary and the script cannot
diverge: there is one build, one install and one check, and this file only
chooses between them.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import winreg

import make_cursors as mc

VERBS = (
    ("1", "--build      rasterise the masters into the output folder"),
    ("2", "--apply      build it, install it, switch the pointers, go live"),
    ("3", "--check      read everything back and name every defect"),
    ("4", "--restore    put the pre-install scheme back"),
    ("5", "--defaults   write Windows Aero back, backup or not"),
    ("6", "--uninstall  remove the files, the scheme and the pointers"),
    ("7", "--preview    open the actual pixels"),
    ("8", "--selftest   prove it on a throwaway key, live scheme untouched"),
    ("q", "quit"),
)


def _count(directory, suffixes):
    if not os.path.isdir(directory):
        return 0
    return sum(1 for name in os.listdir(directory) if name.endswith(suffixes))


def _values(root):
    """{name: (value, kind)} under one HKCU key, or {} when it is not there."""
    values = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, root) as key:
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, value, kind = winreg.EnumValue(key, i)
                values[name] = (value, kind)
    except FileNotFoundError as exc:
        print("selftest    %s does not exist yet (%s)" % (root, exc.strerror))
    return values


def _drop_tree(root):
    """Delete one HKCU key and everything below it, leaf first."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, root, 0,
                            winreg.KEY_READ) as key:
            names = [winreg.EnumKey(key, i)
                     for i in range(winreg.QueryInfoKey(key)[0])]
    except FileNotFoundError as exc:
        print("cleanup     nothing to remove at %s (%s)" % (root, exc.strerror))
        return
    for name in names:
        _drop_tree(root + "\\" + name)
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, root)
        print("cleanup     %s removed" % root)
    except FileNotFoundError as exc:
        print("cleanup     %s already gone (%s)" % (root, exc.strerror))


def _image_of(pid):
    """The full image path of a live process, or None when it cannot be read."""
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFO
    if not handle:
        return None
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer,
                                               ctypes.byref(size)):
            return buffer.value
        return None
    finally:
        kernel32.CloseHandle(handle)


def self_command():
    """The argv prefix that runs this program again as a child process.

    A source run is the interpreter plus this file. A compiled onefile is the
    exe itself, and Nuitka's bootstrap leaves sys.executable pointing inside
    its extraction folder at a path that does not exist (measured 2026-11-14:
    ...\\onefile_21916_...\\python.exe, FileNotFoundError WinError 2), so the
    exe is resolved through SOULFORGE_SELF, the bootstrap parent named by
    NUITKA_ONEFILE_PARENT, argv[0] and finally sys.executable. An empty list
    means no candidate is a real file, and the caller must say so rather than
    report a pass it did not have.
    """
    if not mc.COMPILED:
        return [sys.executable, os.path.abspath(__file__)]
    parent = os.environ.get("NUITKA_ONEFILE_PARENT", "")
    candidates = [os.environ.get("SOULFORGE_SELF"),
                  _image_of(int(parent)) if parent.isdigit() else None,
                  sys.argv[0],
                  sys.executable]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return [candidate]
    return []


def selftest():
    """Prove build, install, check and uninstall without touching the desktop.

    Every step is this same binary run as a child with a throwaway Cursors key
    and install folder, so the code path is the shipped one and the only
    difference is where it writes. The live key is snapshotted before and after
    and must be identical: a selftest that quietly moved the user's pointers is
    a failure, not a pass with a caveat.
    """
    if mc.CURSORS_KEY != mc.LIVE_CURSORS_KEY:
        print("refused     already under %s; run it with no "
              "SOULFORGE_CURSOR_KEY set" % mc.CURSORS_KEY)
        return 3
    root = tempfile.mkdtemp(prefix="soulforge-selftest-")
    scratch = "Software\\SOULFORGE\\selftest-%d" % os.getpid()
    scheme = os.path.join(root, "installed")
    env = dict(os.environ)
    env["SOULFORGE_CURSOR_KEY"] = scratch + "\\Cursors"
    env["SOULFORGE_SCHEME_DIR"] = scheme
    env["SOULFORGE_OUT"] = os.path.join(root, "out")
    base = self_command()
    if not base:
        _drop_tree(scratch)
        shutil.rmtree(root, ignore_errors=True)
        print("DEFECT      no runnable self: %s is not a file, no parent image "
              "was readable and SOULFORGE_SELF is unset" % sys.executable)
        return 1
    print("selftest    self %s" % base[-1])
    before = _values(mc.LIVE_CURSORS_KEY)
    failures = []

    def child(flag, budget):
        print("selftest    %s under %s" % (flag, scratch))
        got = subprocess.run(base + [flag], env=env, capture_output=True,
                             text=True, encoding="utf-8", errors="replace",
                             timeout=budget)
        for line in (got.stdout or "").strip().splitlines():
            print("  %s" % line)
        print("  %s exit %d" % (flag, got.returncode))
        if got.returncode != 0:
            tail = (got.stderr or "").strip().splitlines()[-1:]
            failures.append("%s exited %d %s" % (flag, got.returncode, tail))
        return got

    try:
        child("--apply", 600)
        staged = _values(scratch + "\\Cursors")
        want = len(mc.PROGRAMS) + 1  # one pointer per slot, plus the scheme name
        if len(staged) != want:
            failures.append("the throwaway key holds %d value(s), not %d"
                            % (len(staged), want))
        if staged.get("", (None, None))[0] != mc.SCHEME_NAME:
            failures.append("the throwaway scheme reads %r, not %r"
                            % (staged.get("", (None, None))[0], mc.SCHEME_NAME))
        files = _count(scheme, (".cur", ".ani"))
        if files != len(set(mc.PROGRAMS.values())):
            failures.append("the throwaway install holds %d file(s), not %d"
                            % (files, len(set(mc.PROGRAMS.values()))))
        checked = child("--check", 180)
        if "clean       0 defect(s)" not in (checked.stdout or ""):
            failures.append("--check did not report a clean scheme")
        child("--uninstall", 180)
        if os.path.isdir(scheme):
            failures.append("%s survived --uninstall" % scheme)
        aimed = [name for name, (value, _kind)
                 in _values(scratch + "\\Cursors").items()
                 if str(value).startswith(scheme)]
        if aimed:
            failures.append("%d value(s) still name a deleted file: %s"
                            % (len(aimed), ", ".join(sorted(aimed))))
        after = _values(mc.LIVE_CURSORS_KEY)
        moved = sorted(name for name in set(before) | set(after)
                       if before.get(name) != after.get(name))
        if moved:
            failures.append("the live Cursors key changed: %s"
                            % ", ".join(moved))
    finally:
        _drop_tree(scratch)
        shutil.rmtree(root, ignore_errors=True)
    if failures:
        for line in failures:
            print("DEFECT      %s" % line)
        return 1
    print("selftest    PASS  build, install, check and uninstall under %s; "
          "live key untouched (%d value(s))" % (scratch, len(before)))
    return 0


def status():
    """Print the four facts a person needs before choosing a verb."""
    live = mc.read_scheme()
    bound = [slot for slot, value in live.items() if mc.owns(str(value))]
    print("SOULFORGE   Vulcan-salute cursor swarm")
    print("  masters   %s" % mc.CURSORS)
    print("  built     %s  (%d artefact(s))"
          % (mc.OUT, _count(mc.OUT, (".cur", ".ani"))))
    print("  installed %s  (%d file(s))"
          % (mc.SCHEME_DIR, _count(mc.SCHEME_DIR, (".cur", ".ani"))))
    print("  live      %d slot(s) in %s; scheme %r"
          % (len(bound), os.path.basename(mc.SCHEME_DIR), live.get("", "")))
    if not os.path.isdir(mc.OUT):
        print("  note      nothing is built yet; 2 or --apply does that first")


def run(flag):
    """Run one make_cursors verb, translating its SystemExit into an exit code."""
    verb = {
        "--build": mc.do_build,
        "--apply": mc.do_apply,
        "--check": mc.do_check,
        "--restore": mc.do_restore,
        "--defaults": mc.do_defaults,
        "--uninstall": mc.do_uninstall,
    }[flag]
    try:
        result = verb(None)
    except SystemExit as exc:
        if exc.code not in (None, 0):
            print(exc.code if isinstance(exc.code, str) else
                  "SOULFORGE: %s exited %s" % (flag, exc.code))
            return 1
        return 0
    if flag == "--build":
        built, preview = result
        for path, label, _images in built:
            print("%-12s %6d B  %s" % (label, os.path.getsize(path), path))
        print("preview     %s" % preview)
    return 0


def preview():
    path = os.path.join(mc.OUT, "preview.png")
    if not os.path.exists(path):
        print("cannot open %s; build it first (2)" % path)
        return 2
    # A local artefact this program built, opened in the user's own viewer.
    os.startfile(path)
    print("opened      %s" % path)
    return 0


def menu():
    status()
    print()
    for key, text in VERBS:
        print("  %s  %s" % (key, text))
    while True:
        try:
            choice = input("\nchoose> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice in ("q", "", "quit", "exit"):
            return 0
        if choice == "7":
            preview()
            continue
        text = dict(VERBS).get(choice)
        if not text:
            print("not a choice: %r" % choice)
            continue
        run(text.split()[0])
        print()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag in ("--build", "--apply", "--check", "--restore", "--defaults",
                 "--uninstall", "--preview", "--selftest", "--status"):
        ap.add_argument(flag, action="store_true")
    args = ap.parse_args(argv)
    for flag in ("--build", "--apply", "--check", "--restore", "--defaults",
                 "--uninstall", "--preview", "--selftest"):
        if not getattr(args, flag[2:].replace("-", "_")):
            continue
        if flag == "--preview":
            return preview()
        if flag == "--selftest":
            return selftest()
        return run(flag)
    if args.status or not sys.stdin.isatty():
        status()
        return 0
    return menu()


if __name__ == "__main__":
    sys.exit(main())
