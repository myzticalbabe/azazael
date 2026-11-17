#!/usr/bin/env python3
# coding: utf-8
"""native_tools -- build the tools no distro packages, from source.

Declarative recipes, one per tool: where the source comes from, which system
libraries it links, the exact argv that builds it, and how to prove the result
runs. Nothing is inferred at build time and nothing is fetched behind your
back -- ``--build`` refuses when a system dependency is missing and prints the
single zypper command that fixes it.

Trust model, stated because it is a compromise: the first successful fetch
records the source's identity (tarball sha256, or a git commit sha) in
``NATIVE_ROOT/SOURCES.lock``. Every later build compares against that record
and refuses on a mismatch. That is trust-on-first-use -- it cannot prove the
first fetch was honest, but it makes a *silent* substitution impossible, which
is the failure that matters when an upstream re-tags a release under the same
URL.

Usage:
    python tools/native_tools.py --list
    python tools/native_tools.py --doctor
    python tools/native_tools.py --build pixiewps
    python tools/native_tools.py --build-all --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PREFIX = os.environ.get("NATIVE_PREFIX", "/usr/local")
ROOT = Path(os.environ.get("NATIVE_ROOT", "/srv/mb/native"))
# The interpreter that builds Python-extension recipes. sys.executable, never
# a bare "python": inside the 3.16t lane a bare name resolves to the distro's
# GIL build, which produces a module that imports fine and silently re-enables
# the GIL.
PYTHON = os.environ.get("NATIVE_PYTHON", sys.executable)
LOCK = ROOT / "SOURCES.lock"
JOBS = str(os.cpu_count() or 4)
BUILD_TIMEOUT = int(os.environ.get("NATIVE_BUILD_TIMEOUT", "1800"))


class BuildError(RuntimeError):
    """A build step refused or failed; the message names the step."""


@dataclass(frozen=True)
class Recipe:
    """One tool: where it comes from, what it needs, how to build and prove it."""

    name: str
    summary: str
    url: str
    kind: str = "git"                      # "git" | "tarball"
    ref: str = ""                          # git branch/tag; empty = default
    deps: tuple[str, ...] = ()             # rpm packages the link needs
    build: tuple[tuple[str, ...], ...] = ()  # argv lists, run in the source dir
    sub: str = ""                           # build entry point inside the tree
    # (relpath, old, new) applied to the extracted source, once. Declarative on
    # purpose: a patch that lives in this file is reviewable, and a patch
    # applied by hand inside /srv is a fix the next machine cannot reproduce.
    # The old text must occur exactly once or the build refuses.
    patch: tuple[tuple[str, str, str], ...] = ()
    verify: tuple[str, ...] = ()           # argv proving the binary executes
    # None = "it ran": any rc except 126 (not executable) / 127 (not found).
    # Usage printers are upstream-specific -- pixiewps --help exits 3 -- so a
    # guessed allowed-set reports a healthy install as a failure, which is a
    # reading error dressed as a build error.
    verify_rc: tuple[int, ...] | None = None


# Only recipes whose upstream URL and build entry point are known are listed.
# A guessed recipe is worse than an absent one: it fails halfway and leaves a
# half-installed tool that reads as present.
RECIPES: dict[str, Recipe] = {
    "pixiewps": Recipe(
        name="pixiewps",
        summary="offline WPS PIN recovery (pixie dust); no deps, single make",
        url="https://github.com/wiire-a/pixiewps",
        build=(("make", "-j{jobs}"), ("make", "install", "PREFIX={prefix}")),
        verify=("pixiewps", "--help"),
    ),
    "cowpatty": Recipe(
        name="cowpatty",
        summary="WPA-PSK handshake cracker",
        url="https://github.com/joswr1ght/cowpatty",
        deps=("libpcap-devel",),
        # upstream hardcodes CC=clang (not on this box) and writes K&R-style
        # `void cleanup()` as a signal handler, which gnu17 reads as taking no
        # args and rejects against __sighandler_t; gnu89 restores the meaning
        # the source was written for, without patching upstream.
        build=(("make", "CC=gcc -std=gnu89"), ("make", "install")),
        verify=("cowpatty", "-h"),
    ),
    "mdk4": Recipe(
        name="mdk4",
        summary="802.11 denial-of-service test suite",
        url="https://github.com/aircrack-ng/mdk4",
        deps=("libpcap-devel",),
        build=(("make", "-j{jobs}"), ("make", "install", "PREFIX={prefix}")),
        verify=("mdk4", "--help"),
    ),
    "reaver": Recipe(
        name="reaver",
        summary="WPS brute-force / pixie-dust attack (t6x fork)",
        url="https://github.com/t6x/reaver-wps-fork-t6x",
        deps=("libpcap-devel",),
        # repo root holds docs/tools; configure lives in src/, and `sh` runs it
        # even when the exec bit did not survive the clone
        sub="src",
        build=(("sh", "./configure", "--prefix={prefix}"),
               ("make", "-j{jobs}"),
               ("make", "install")),
        verify=("reaver", "-h"),
    ),
    "hcxtools": Recipe(
        name="hcxtools",
        summary="capture conversion to hashcat formats (hcxpcapngtool etc.)",
        url="https://github.com/ZerBea/hcxtools",
        deps=("libcurl-devel", "libopenssl-devel"),
        build=(("make", "-j{jobs}"), ("make", "install", "PREFIX={prefix}")),
        verify=("hcxpcapngtool", "--version"),
    ),
    "hcxdumptool": Recipe(
        name="hcxdumptool",
        summary="capture WLAN packets for hashcat/pmkid workflows",
        url="https://github.com/ZerBea/hcxdumptool",
        deps=("libcurl-devel",),
        build=(("make", "-j{jobs}"), ("make", "install", "PREFIX={prefix}")),
        verify=("hcxdumptool", "--version"),
    ),
    "cffi": Recipe(
        name="cffi",
        summary="Python C-extension FFI backend; 3.16 removed an API it calls",
        url="https://files.pythonhosted.org/packages/source/c/cffi/cffi-2.1.1.tar.gz",
        kind="tarball",
        # CPython 3.16 removed Py_FileSystemDefaultEncoding outright -- it is
        # not merely gone from the headers, `nm -D` finds no such symbol in
        # libpython3.16t.so, so a header shim cannot link. cffi passes it as the
        # encoding argument of PyArg_ParseTuple's "et" format, where NULL means
        # precisely the same thing: the default filesystem encoding.
        patch=(("src/c/_cffi_backend.c",
                "Py_FileSystemDefaultEncoding, &filename_or_null",
                "NULL, &filename_or_null"),),
        # --no-deps both times: pycparser is pure Python and installs normally;
        # the point of this recipe is the compiled backend, not dependency walk.
        build=(("{python}", "-m", "pip", "wheel", ".", "--no-deps",
                "-w", "{root}/wheels"),
               ("{python}", "-m", "pip", "install", ".", "--no-deps",
                "--force-reinstall")),
        # Proves both halves: the ABI loads AND the GIL is still off afterwards.
        verify=("{python}", "-c",
                "import cffi,sys;print(cffi.__version__,sys._is_gil_enabled())"),
        verify_rc=(0,),
    ),
    "bully": Recipe(
        name="bully",
        summary="WPS brute-force with a different state machine than reaver",
        url="https://github.com/aanarchyy/bully",
        deps=("libpcap-devel", "libnl3-devel", "ncurses-devel"),
        # the repo root is a buildroot package stub; the real Makefile is in src/
        sub="src",
        build=(("make", "-j{jobs}", "prefix={prefix}"),
               ("make", "install", "prefix={prefix}")),
        verify=("bully", "--help"),
    ),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(argv: tuple[str, ...] | list[str], cwd: Path,
         timeout: int = BUILD_TIMEOUT) -> subprocess.CompletedProcess[str]:
    """Run one step, echo its tail, and fail loudly naming the step."""
    shown = " ".join(argv)
    print("+ " + shown, flush=True)
    proc = subprocess.run([str(a) for a in argv], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)
    for line in (proc.stdout or "").strip().splitlines()[-6:]:
        print("  " + line)
    if proc.returncode != 0:
        for line in (proc.stderr or "").strip().splitlines()[-12:]:
            print("  ! " + line)
        raise BuildError("step failed rc=%d: %s" % (proc.returncode, shown))
    return proc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_lock() -> dict:
    if not LOCK.exists():
        return {}
    return json.loads(LOCK.read_text(encoding="utf-8"))


def _write_lock(data: dict) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = LOCK.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(LOCK)


def _guard(lock: dict, name: str, identity: str) -> None:
    """Pin a source on first sight; refuse a later change (trust-on-first-use)."""
    known = (lock.get(name) or {}).get("identity")
    if known is None:
        lock[name] = {"identity": identity, "recorded": _now()}
        _write_lock(lock)
        print("lock: recorded first identity for %s: %s" % (name, identity))
        return
    if known != identity:
        raise BuildError(
            "%s: source identity changed\n  recorded: %s\n  fetched:  %s\n"
            "refusing to build a source that no longer matches the lock"
            % (name, known, identity))


def _missing_deps(recipe: Recipe) -> list[str]:
    missing: list[str] = []
    for dep in recipe.deps:
        probe = subprocess.run(["rpm", "-q", dep], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120)
        if probe.returncode != 0:
            missing.append(dep)
    return missing


def _fetch(recipe: Recipe, work: Path, lock: dict) -> Path:
    """Materialise the source into work/src and pin its identity."""
    src = work / "src"
    work.mkdir(parents=True, exist_ok=True)
    if recipe.kind == "git":
        if not (src / ".git").exists():
            clone = ["git", "clone", "--depth", "1"]
            if recipe.ref:
                clone += ["--branch", recipe.ref]
            clone += [recipe.url, str(src)]
            _run(tuple(clone), work)
        head = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)
        if head.returncode != 0:
            raise BuildError("cannot read HEAD of %s" % src)
        _guard(lock, recipe.name, "git:" + head.stdout.strip())
        return src
    tarball = work / "source.tar.gz"
    if not tarball.exists():
        _run(("curl", "-fsSL", "--retry", "3", "-o", str(tarball), recipe.url), work)
    _guard(lock, recipe.name, "sha256:" + _sha256(tarball))
    if not (src / ".fetched").exists():
        src.mkdir(parents=True, exist_ok=True)
        _run(("tar", "-xf", str(tarball), "-C", str(src), "--strip-components=1"), work)
        _apply_patches(recipe, src)
        (src / ".fetched").write_text(_now() + "\n", encoding="utf-8")
    elif recipe.patch:
        print("  patch: source already extracted; patches were applied at fetch")
    return src


def _fmt(step: tuple[str, ...]) -> tuple[str, ...]:
    """Expand the declared placeholders in one argv step."""
    return tuple(part.replace("{jobs}", JOBS)
                 .replace("{prefix}", PREFIX)
                 .replace("{root}", str(ROOT))
                 .replace("{python}", PYTHON)
                 for part in step)


def _steps(recipe: Recipe) -> list[tuple[str, ...]]:
    return [_fmt(step) for step in recipe.build]


def _apply_patches(recipe: Recipe, src: Path) -> None:
    """Apply declared patches once, refusing anything but an exact single hit."""
    for relpath, old, new in recipe.patch:
        target = src / relpath
        text = target.read_text(encoding="utf-8")
        hits = text.count(old)
        if hits != 1:
            raise BuildError(
                "%s: patch anchor found %d times in %s (expected 1); the source "
                "changed shape and the patch no longer describes it"
                % (recipe.name, hits, relpath))
        target.write_text(text.replace(old, new), encoding="utf-8")
        print("  patch: %s (%d chars -> %d chars)" % (relpath, len(old), len(new)))


def _verify(recipe: Recipe) -> str:
    if not recipe.verify:
        return "no verify command declared"
    argv = _fmt(recipe.verify)
    proc = subprocess.run([str(a) for a in argv], capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=120, cwd="/")
    banner = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
    first = banner[0] if banner else "(no output)"
    if recipe.verify_rc is None:
        if proc.returncode in (126, 127):
            raise BuildError("verify could not execute (rc=%d): %s"
                             % (proc.returncode, " ".join(argv)))
    elif proc.returncode not in recipe.verify_rc:
        raise BuildError("verify failed rc=%d: %s -- %s"
                         % (proc.returncode, " ".join(argv), first))
    return "rc=%d %s" % (proc.returncode, first[:90])


def cmd_list(_: argparse.Namespace) -> int:
    print("%-14s %-9s %-28s %s" % ("name", "kind", "deps", "summary"))
    for name in sorted(RECIPES):
        rec = RECIPES[name]
        print("%-14s %-9s %-28s %s"
              % (name, rec.kind, ",".join(rec.deps) or "-", rec.summary))
    print("\n%d recipes; root=%s prefix=%s" % (len(RECIPES), ROOT, PREFIX))
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    if sys.platform == "win32":
        print("doctor: these recipes are POSIX-only; run inside the Linux lane")
        return 2
    bad = 0
    for name in sorted(RECIPES):
        rec = RECIPES[name]
        missing = _missing_deps(rec)
        state = "READY" if not missing else "MISSING " + " ".join(missing)
        if missing:
            bad += 1
        print("%-14s %s" % (name, state))
    print("\n%d of %d recipes ready" % (len(RECIPES) - bad, len(RECIPES)))
    return 0 if bad == 0 else 1


def cmd_build(ns: argparse.Namespace) -> int:
    names = sorted(RECIPES) if ns.build_all else [ns.build]
    if sys.platform == "win32":
        print("build: these recipes are POSIX-only; run inside the Linux lane")
        return 2
    lock = _read_lock()
    failures: list[str] = []
    for name in names:
        rec = RECIPES.get(name)
        if rec is None:
            print("%s: no such recipe (see --list)" % name)
            return 2
        missing = _missing_deps(rec)
        if missing and not ns.dry_run:
            print("%s: missing system deps: %s" % (name, " ".join(missing)))
            print("  fix: zypper in -y %s" % " ".join(missing))
            failures.append(name)
            continue
        print("\n=== %s (%s) ===" % (name, rec.summary))
        if ns.dry_run:
            for step in _steps(rec):
                print("  would run: " + " ".join(step))
            print("  would verify: " + " ".join(rec.verify))
            continue
        try:
            src = _fetch(rec, ROOT / name, lock)
            build_dir = src / rec.sub if rec.sub else src
            for step in _steps(rec):
                _run(step, build_dir)
            print("  verify: " + _verify(rec))
            print("  BUILT %s" % name)
        # OSError: a step's program does not exist (missing autotools, a
        # configure that upstream never shipped). Named, not a traceback.
        except (BuildError, subprocess.TimeoutExpired, OSError) as exc:
            print("  FAILED %s: %s" % (name, exc))
            failures.append(name)
    if failures:
        print("\n%d of %d failed: %s" % (len(failures), len(names), " ".join(failures)))
        return 1
    print("\nall %d ok" % len(names))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="native_tools",
        description="Build security tools no distro packages, from pinned sources.")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="show recipes")
    group.add_argument("--doctor", action="store_true", help="check system deps")
    group.add_argument("--build", metavar="NAME", help="fetch, build, install, verify")
    group.add_argument("--build-all", action="store_true", help="every recipe, in order")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, fetch nothing")
    ns = ap.parse_args(argv)
    if ns.list:
        return cmd_list(ns)
    if ns.doctor:
        return cmd_doctor(ns)
    return cmd_build(ns)


if __name__ == "__main__":
    raise SystemExit(main())
