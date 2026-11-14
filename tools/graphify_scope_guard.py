#!/usr/bin/env python3
# coding: utf-8
"""graphify scope guard — refuse a graph write that no lane reads.

Why this exists (2026-11-14)
----------------------------
The codegraph store every lane configures is::

    <repo>/src/graphify-out/graph.json

That single path is what ``mcp_startup_gate.py``'s ``codegraph-staleness``
check certifies, and what kilo / freebuff / opencode all pass as ``--graph``.

graphify, however, writes the graph beside whatever it is pointed at::

    out = watch_path / GRAPHIFY_OUT          # watch.py:1451
    out = (out_dir or target) / GRAPHIFY_OUT  # cli.py:3431 (extract)

and ``graphify update`` with no path recovers its scan root from
``<cwd>/graphify-out/.graphify_root``, falling back to ``"."`` (cli.py:2437).
So a run started at the repo root — ``cd repo && graphify update``, or plain
``graphify .`` — writes ``<repo>/graphify-out/graph.json``. Nothing reads that
file. The write succeeds, exit 0, and the canonical store stays stale: the
exact silent drift the read-side gate was built to detect, produced on the
write side by an ordinary command.

The read side is already loud (``codegraph-staleness``). This makes the write
side refuse instead of producing the orphan.

What is guarded
---------------
The three commands that build/write a graph, plus the bare-path form:

* ``update [path]``   — cli.py:2407
* ``extract <path> [--out DIR|--output DIR]`` — cli.py:3227, out at cli.py:3431
* ``watch [path]``    — cli.py:1982
* ``graphify <path>`` — rewritten to ``extract <path>`` at cli.py:4859

``label`` / ``cluster-only`` are deliberately NOT guarded: they read
``watch_path / GRAPHIFY_OUT / "graph.json"`` and exit 1 with "no graph found"
when it is absent (cli.py:3452), so they cannot create an orphan graph
silently. Reading commands (``query``, ``god-nodes``, ``explain``, ...) are
untouched — the guard exits 0 without output.

The rule
--------
Compute the out dir exactly as graphify will, then:

* ``out == <repo>/src/graphify-out``            -> allow (the read store)
* ``out`` is outside this repo                  -> allow (other repos,
  ``graphify_refresh_all.sh`` targets; drift is only a defect inside the tree
  whose lanes disagree about where the store is)
* anything else inside this repo                -> refuse, exit 3

Usage (normally invoked by ``scripts/graphify_bin.sh``, which passes the same
argv it is about to exec)::

    graphify_scope_guard.py --repo-root <root> [--] <graphify argv...>

Escape hatch
------------
``GRAPHIFY_ALLOW_SCOPE_DRIFT=1`` permits the write and says so on stderr.
It is a notice, never a silent pass: an operator sees the line, and a later
reader of the transcript can see the choice was made.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_DRIFT = 3

# Commands that write a graph. Anything else passes through untouched.
WRITE_COMMANDS = frozenset({"update", "extract", "watch"})

# The only out dir codegraph reads, relative to the repo root.
CANONICAL_PARTS = ("src", "graphify-out")

ESCALATION_VAR = "GRAPHIFY_ALLOW_SCOPE_DRIFT"
TRUTHY = {"1", "true", "yes", "on"}


def graphify_out_name() -> str:
    """``GRAPHIFY_OUT`` as paths.py:26 reads it — absolute wins, else a name."""
    return os.environ.get("GRAPHIFY_OUT", "graphify-out")


def _looks_like_path(token: str) -> bool:
    """Mirror cli.py:4859's bare-path test (``graphify <path>``).

    ``Path.exists()`` answers False for a NUL byte, an unrepresentable name and
    an absent drive rather than raising, so there is no failure to trap here.
    """
    if Path(token).exists():
        return True
    return token in (".", "..") or token.startswith(("./", "../", "/", "~"))


def _cwd_base() -> Path:
    """Cwd the rebuild will actually use.

    watch.py:1302 ``_stabilize_rebuild_cwd`` chdirs to ``GRAPHIFY_REPO_ROOT``
    when the watch path is relative and that directory exists, so a relative
    ``out`` resolves against it rather than against the shell's cwd.
    """
    declared = os.environ.get("GRAPHIFY_REPO_ROOT", "").strip()
    if declared and Path(declared).is_dir():
        return Path(declared)
    return Path.cwd()


def _extract_out_override(args: list[str]) -> Path | None:
    """``--out DIR`` / ``--output DIR`` / ``--out=DIR`` (cli.py:3328-3335)."""
    out_dir: Path | None = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--out", "--output") and i + 1 < len(args):
            out_dir = Path(args[i + 1])
            i += 2
            continue
        if arg.startswith(("--out=", "--output=")):
            out_dir = Path(arg.split("=", 1)[1])
        i += 1
    return out_dir


def _update_watch_path(args: list[str]) -> Path | None:
    """Watch path ``update`` will use, or None when it will error out first."""
    watch_arg: str | None = None
    for arg in args:
        if arg in ("--force", "--no-cluster"):
            continue
        if arg.startswith("-"):
            continue
        watch_arg = arg
        break
    if watch_arg is not None:
        return Path(watch_arg)
    # cli.py:2437 — recover the root saved by the last full build, else ".".
    saved = Path(graphify_out_name()) / ".graphify_root"
    if saved.is_file():
        try:
            return Path(saved.read_text(encoding="utf-8-sig").strip())
        except (OSError, UnicodeDecodeError) as exc:
            # Two statements, not a bare pass: read_text is only reached once
            # is_file() is true, so a failure here is anomalous. Falling through
            # to "." in silence would turn an unreadable marker into a refusal
            # with no stated reason; say it, then take the safe direction.
            print(
                f"graphify scope guard: unreadable {saved} ({exc}); assuming '.'",
                file=sys.stderr,
            )
            return Path(".")
    return Path(".")


def resolve_out_dir(command: str, args: list[str]) -> Path | None:
    """The directory graphify will write ``graph.json`` into.

    Returns None when the invocation cannot write anything (graphify exits on
    its own usage/path error first), so the guard never replaces a precise
    graphify error with a scope error.
    """
    name = graphify_out_name()

    if command == "extract":
        has_path = bool(args) and not args[0].startswith("-")
        if not has_path and "--postgres" not in args and not any(
            a.startswith("--postgres=") for a in args
        ):
            # cli.py:3406 — "must specify a path to scan or a --postgres DSN".
            return None
        target = Path(args[0]).resolve() if has_path else Path(".").resolve()
        out_root = _extract_out_override(args)
        root = out_root.resolve() if out_root is not None else target
        return (root / name).resolve()

    if command == "update":
        watch = _update_watch_path(args)
    else:  # watch
        watch = Path(args[0]) if args and not args[0].startswith("-") else Path(".")

    if watch is None:
        return None
    if not watch.exists():
        # graphify prints "error: path not found" and exits 1 — no write.
        return None

    out = watch / name
    if not out.is_absolute():
        out = _cwd_base() / out
    return out.resolve()


def _is_within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def decide(out: Path, repo_root: Path) -> tuple[bool, str]:
    """(allowed, reason) for a computed out dir."""
    canonical = (repo_root / "src" / "graphify-out").resolve()
    if out == canonical:
        return True, "canonical store"
    if not _is_within(out, repo_root):
        return True, "outside this repo"
    return False, "inside this repo but not the store codegraph reads"


def _refuse(out: Path, canonical: Path, argv: list[str]) -> str:
    joined = " ".join(argv) if argv else "<graphify args>"
    return (
        "graphify scope guard: REFUSED — nothing was written.\n"
        f"\n"
        f"  this run would write : {out}\n"
        f"  codegraph reads      : {canonical}\n"
        f"\n"
        f"Every lane (kilo, freebuff, opencode) passes the second path as\n"
        f"--graph, and tools/mcp_startup_gate.py certifies that one. A graph at\n"
        f"the first path is invisible: the write succeeds, the store stays\n"
        f"stale, and nothing reports it.\n"
        f"\n"
        f"Fix — name the read store explicitly (any one of these):\n"
        f"\n"
        f"  graphify update src\n"
        f"  cd src && graphify update\n"
        f"  GRAPHIFY_OUT={canonical} graphify {joined}\n"
        f"\n"
        f"Deliberate override (states itself in the transcript):\n"
        f"\n"
        f"  {ESCALATION_VAR}=1 graphify {joined}\n"
    )


def parse_args(argv: list[str]) -> tuple[Path | None, list[str]]:
    """Split ``--repo-root`` from the graphify argv after ``--``."""
    repo_root: Path | None = None
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--":
            rest = argv[i + 1:]
            break
        if arg == "--repo-root" and i + 1 < len(argv):
            repo_root = Path(argv[i + 1])
            i += 2
            continue
        if arg.startswith("--repo-root="):
            repo_root = Path(arg.split("=", 1)[1])
            i += 1
            continue
        rest.append(arg)
        i += 1
    return repo_root, rest


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    repo_root, rest = parse_args(raw)
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    try:
        repo_root = repo_root.resolve()
    except OSError as exc:
        print(f"graphify scope guard: cannot resolve repo root: {exc}", file=sys.stderr)
        return EXIT_USAGE

    if not rest:
        return EXIT_OK

    command = rest[0]
    if command in WRITE_COMMANDS:
        args = rest[1:]
    elif _looks_like_path(command):
        # cli.py:4859 — `graphify <path>` becomes `graphify extract <path>`.
        command, args = "extract", rest
    else:
        return EXIT_OK  # read command, help, version, unknown: not our business

    out = resolve_out_dir(command, args)
    if out is None:
        return EXIT_OK

    allowed, reason = decide(out, repo_root)
    if allowed:
        return EXIT_OK

    if os.environ.get(ESCALATION_VAR, "").strip().lower() in TRUTHY:
        print(
            f"graphify scope guard: ALLOWED by {ESCALATION_VAR} — writing {out}, "
            f"which codegraph does not read ({reason}).",
            file=sys.stderr,
        )
        return EXIT_OK

    print(_refuse(out, (repo_root / "src" / "graphify-out").resolve(), rest), file=sys.stderr)
    return EXIT_DRIFT


if __name__ == "__main__":
    sys.exit(main())
