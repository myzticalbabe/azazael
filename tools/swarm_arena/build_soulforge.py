#!/usr/bin/env python3
r"""Build SOULFORGE.exe -- the cursor swarm as one Windows binary.

Nuitka compiles `soulforge.py` and `make_cursors.py` with the MSVC backend and
packs the cursor masters in as data, so the executable carries its own SVG
sources. The build is verified by running the thing it produced: a size on disk
is not evidence that an exe starts.

  python build_soulforge.py            # -> dist\SOULFORGE.exe
  python build_soulforge.py --keep     # keep Nuitka's intermediates

Onefile unpacks to a temp directory at start, so `make_cursors.OUT` moves to
%LOCALAPPDATA%\SOULFORGE\out\cursors in the compiled build (see the note at the
top of make_cursors.py); the masters are read from the unpacked copy.
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
EXE = os.path.join(DIST, "SOULFORGE.exe")
# Both children are bounded: a compiler that wedges must not take the build
# session with it, and a smoke run that hangs must not look like a slow pass.
BUILD_TIMEOUT = 1800
SMOKE_TIMEOUT = 120


def main(argv):
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile",
        "--assume-yes-for-downloads",
        "--output-dir=" + DIST,
        "--output-filename=SOULFORGE.exe",
        "--include-data-dir=cursors=cursors",
        "--windows-console-mode=force",
        "--product-name=SOULFORGE",
        "--file-version=1.0.0.0",
        "--product-version=1.0.0.0",
        "--copyright=Vulcan Swarm",
    ]
    if "--keep" not in argv:
        cmd.append("--remove-output")
    cmd.append("soulforge.py")
    print("building: %s" % " ".join(cmd[2:]))
    try:
        result = subprocess.run(cmd, cwd=HERE, timeout=BUILD_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise SystemExit("build_soulforge: Nuitka exceeded %d s" % BUILD_TIMEOUT)
    if result.returncode != 0:
        raise SystemExit("build_soulforge: Nuitka exited %d" % result.returncode)
    if not os.path.exists(EXE):
        raise SystemExit("build_soulforge: %s was not created" % EXE)
    size = os.path.getsize(EXE)
    if size == 0:
        raise SystemExit("build_soulforge: %s is 0 bytes" % EXE)
    print("\nbuilt %s  (%d bytes)" % (EXE, size))
    # Verify by running it: a file that exists is not a program that starts.
    try:
        probe = subprocess.run([EXE, "--status"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               timeout=SMOKE_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise SystemExit("build_soulforge: %s --status exceeded %d s"
                         % (EXE, SMOKE_TIMEOUT))
    print("smoke   SOULFORGE.exe --status -> exit %d" % probe.returncode)
    for line in probe.stdout.splitlines():
        print("        %s" % line)
    if probe.stderr.strip():
        print("        stderr: %s" % probe.stderr.strip()[:400])
    if probe.returncode != 0 or "SOULFORGE" not in probe.stdout:
        raise SystemExit("build_soulforge: the built exe did not report a status")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
