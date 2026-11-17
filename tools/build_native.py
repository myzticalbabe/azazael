"""build_native -- compile one .pyx into a GIL-free extension on this box.

Two lanes, chosen by ``sys.platform``, because the load-bearing facts differ.
Neither is a copy of the other: a flag that is essential under cl is merely
belt-and-braces under gcc, and a library that must be found by hand on Windows
is never linked at all on POSIX.

Windows / MSVC (this box: MSVC 14.51, SDK 10.0.26100.0, the self-built
3.16.0a1t tree at C:\\Azazael\\.py316t, Cython 3.3.1 in the py316t venv):

1. cl needs //DPy_GIL_DISABLED=1 on the command line. The define comes from
   the build system, never from pyconfig.h (which only *tests* it). Without
   it the pragma in pyconfig.h pulls python316.lib -- which does not exist
   -- and a module that somehow still links refuses to import with
   ``SystemError: invalid PyModuleDef`` on a free-threaded interpreter.
2. Flags are single-slash (/I, /D, /OUT:) with backslash values (C:\\...).
   The double-slash form only survives when bash mangles it first; passed
   straight from subprocess, cl rejects it (D9002). Forward slashes in the
   *values* also die under MSYS path conversion; backslashes never do.

3. A module that compiles and imports can still be the wrong module: Cython's
   default module init is *legacy*, and importing a legacy-init extension on a
   free-threaded interpreter sets the GIL back ON -- silently, with a normal
   import and no warning. ``-X freethreading_compatible=True`` is what emits the
   ``Py_MOD_GIL_NOT_USED`` slot, so BOTH lanes pass it and the build refuses a
   translation that does not carry the slot. Measured: without the directive
   ``sys._is_gil_enabled()`` read True after a successful import; with it, False.

Linux / gcc (this box: gcc 16.2.1, CPython 3.16.0a1 built --disable-gil into
/usr/local, ext suffix .cpython-316t-x86_64-linux-gnu.so):

1. Extensions never link libpython; the running interpreter resolves their
   symbols. So there is no analogue of the missing python316.lib trap, and
   the -D is insurance rather than the fix.
2. The include directory is asked of the interpreter itself
   (``sysconfig.get_paths()["include"]``) and the suffix from
   ``sysconfig.get_config_var("EXT_SUFFIX")``, so a differently-built
   interpreter needs no edit here.

Override the Windows paths with env vars for other boxes; fail loudly when a
path is missing instead of emitting a half-linked binary.

Usage:
    python tools/build_native.py src/eve_unleashed/_replay_cy.pyx
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import sysconfig

MSVC = os.environ.get("AZAZAEL_MSVC",
                      r"C:\Program Files\Microsoft Visual Studio\18"
                      r"\Community\VC\Tools\MSVC\14.51.36231")
SDK = os.environ.get("AZAZAEL_SDK", r"C:\Program Files (x86)\Windows Kits\10")
SDK_VER = os.environ.get("AZAZAEL_SDK_VER", "10.0.26100.0")
PYT = os.environ.get("AZAZAEL_PYT", r"C:\Azazael\.py316t")


def run(cmd, cwd):
    print("+ " + " ".join(cmd))
    # Bounded: a wedged compiler must fail loudly, never hang the caller.
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", timeout=600)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.returncode != 0:
        if proc.stderr.strip():
            print(proc.stderr.strip())
        raise SystemExit("build step failed rc=%d: %s"
                         % (proc.returncode, cmd[0]))
    elif proc.stderr.strip():
        print(proc.stderr.strip())


def _cython(pyx, here, c_file):
    """Translate .pyx, then require the free-threaded module slot to exist."""
    run([sys.executable, "-m", "cython", "-3",
         "-X", "freethreading_compatible=True", pyx], here)
    with open(c_file, encoding="utf-8", errors="replace") as handle:
        generated = handle.read()
    if "Py_MOD_GIL_NOT_USED" not in generated:
        raise SystemExit(
            "generated C carries no free-threading slot (Py_MOD_GIL_NOT_USED); "
            "importing this module would re-enable the GIL: " + c_file)


def build_posix(pyx):
    """cython -> one shared object, in the .pyx's own directory."""
    here = os.path.dirname(pyx)
    base = os.path.basename(pyx)[:-4]
    tag = (os.environ.get("AZAZAEL_EXT_SUFFIX")
           or sysconfig.get_config_var("EXT_SUFFIX") or ".so")
    c_file = os.path.join(here, base + ".c")
    so = os.path.join(here, base + tag)
    inc = sysconfig.get_paths()["include"]
    cc = os.environ.get("CC", "gcc")
    _cython(pyx, here, c_file)
    run([cc, "-shared", "-fPIC", "-O2", "-DPy_GIL_DISABLED=1",
         "-I" + inc, c_file, "-o", so], here)
    size = os.path.getsize(so)
    if size == 0:
        raise SystemExit("compiler wrote an empty module: " + so)
    print("built %s (%d bytes)" % (so, size))


def build_windows(pyx):
    here = os.path.dirname(pyx)
    base = os.path.basename(pyx)[:-4]
    tag = os.environ.get("AZAZAEL_EXT_SUFFIX", ".cp316t-win_amd64.pyd")
    for path in (MSVC, SDK, PYT, pyx):
        if not os.path.exists(path):
            raise SystemExit("missing (set AZAZAEL_* override): " + path)
    c_file = os.path.join(here, base + ".c")
    obj = os.path.join(here, base + ".obj")
    pyd = os.path.join(here, base + tag)
    _cython(pyx, here, c_file)
    cl = os.path.join(MSVC, "bin", "Hostx64", "x64", "cl.exe")
    run([cl, "/nologo", "/c", c_file, "/Fo" + obj, "/DPy_GIL_DISABLED=1",
         "/I" + PYT + r"\Include",
         "/I" + MSVC + r"\include",
         "/I" + SDK + r"\Include\%s\ucrt" % SDK_VER,
         "/I" + SDK + r"\Include\%s\um" % SDK_VER,
         "/I" + SDK + r"\Include\%s\shared" % SDK_VER], here)
    link = os.path.join(MSVC, "bin", "Hostx64", "x64", "link.exe")
    run([link, "/nologo", "/DLL", "/OUT:" + pyd, obj,
         "/LIBPATH:" + PYT + r"\libs",
         "/LIBPATH:" + MSVC + r"\lib\x64",
         "/LIBPATH:" + SDK + r"\Lib\%s\um\x64" % SDK_VER,
         "/LIBPATH:" + SDK + r"\Lib\%s\ucrt\x64" % SDK_VER,
         "kernel32.lib"], here)
    size = os.path.getsize(pyd)
    if size == 0:
        raise SystemExit("linker wrote an empty module: " + pyd)
    print("built %s (%d bytes)" % (pyd, size))


def main(argv=None):
    # argparse, not sys.argv slicing: mellifluous.py forwards a bare argument
    # list, so `native-build mod.pyx` and `build_native.py mod.pyx` must agree.
    ap = argparse.ArgumentParser(
        prog="build_native",
        description="compile one .pyx into a GIL-free extension (MSVC or gcc)")
    ap.add_argument("pyx", help="path to the .pyx module")
    ns = ap.parse_args(argv)
    if not ns.pyx.endswith(".pyx"):
        raise SystemExit("usage: build_native.py <module>.pyx")
    pyx = os.path.abspath(ns.pyx)
    if not os.path.exists(pyx):
        raise SystemExit("missing: " + pyx)
    if sys.platform == "win32":
        build_windows(pyx)
    else:
        build_posix(pyx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
