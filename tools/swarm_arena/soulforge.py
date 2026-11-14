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
  SOULFORGE.exe --preview       open the built preview.png

Exit codes: 0 nothing wrong, 1 a defect named, 2 nothing to read, 3 refused.
Every verb delegates to make_cursors, so the binary and the script cannot
diverge: there is one build, one install and one check, and this file only
chooses between them.
"""

from __future__ import annotations

import argparse
import os
import sys

import make_cursors as mc

VERBS = (
    ("1", "--build      rasterise the masters into the output folder"),
    ("2", "--apply      build it, install it, switch the pointers, go live"),
    ("3", "--check      read everything back and name every defect"),
    ("4", "--restore    put the pre-install scheme back"),
    ("5", "--defaults   write Windows Aero back, backup or not"),
    ("6", "--uninstall  remove the files, the scheme and the pointers"),
    ("7", "--preview    open the actual pixels"),
    ("q", "quit"),
)


def _count(directory, suffixes):
    if not os.path.isdir(directory):
        return 0
    return sum(1 for name in os.listdir(directory) if name.endswith(suffixes))


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
                 "--uninstall", "--preview", "--status"):
        ap.add_argument(flag, action="store_true")
    args = ap.parse_args(argv)
    for flag in ("--build", "--apply", "--check", "--restore", "--defaults",
                 "--uninstall", "--preview"):
        if getattr(args, flag[2:].replace("-", "_")):
            return preview() if flag == "--preview" else run(flag)
    if args.status or not sys.stdin.isatty():
        status()
        return 0
    return menu()


if __name__ == "__main__":
    sys.exit(main())
