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
Every command that builds or writes a graph, plus the bare-path form:

* ``update [path]``   — cli.py:2407
* ``extract <path> [--out DIR|--output DIR]`` — cli.py:3227, out at cli.py:3431
* ``watch [path]``    — cli.py:1982
* ``graphify <path>`` — rewritten to ``extract <path>`` at cli.py:4859
* ``cluster-only [path] [--graph G]`` / ``label [path] [--graph G]``
  — cli.py:1995, out at cli.py:2132-2135

``cluster-only``/``label`` were left unguarded in the first version on the
theory that they only refresh a store that already exists. That theory is half
right, and the wrong half writes a store. Measured 2026-11-14 in a scratch tree
(graphify 0.9.72): with no ``--graph`` they do exit 1 with "no graph found"
when ``<watch_path>/graphify-out/graph.json`` is absent (cli.py:2063-2068) —
but when ``--graph`` names a graph.json whose parent is NOT a ``graphify-out``
dir, ``out`` falls back to ``watch_path / GRAPHIFY_OUT`` and is then
``mkdir(parents=True)``-ed (cli.py:2134-2135)::

    cd <repo>/src/CORE
    graphify cluster-only --graph /tmp/backup/graph.json --no-label --no-viz
    # rc=0, created <repo>/src/CORE/graphify-out/{graph.json,GRAPH_REPORT.md}

A run started in a subdirectory therefore rebuilt the exact orphan this
guard exists to prevent, one command over. Reading commands (``query``,
``god-nodes``, ``explain``, ...) are untouched — exit 0, no output.

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
WRITE_COMMANDS = frozenset({"update", "extract", "watch", "cluster-only", "label"})

# ``cluster-only`` / ``label`` write ``watch_path / GRAPHIFY_OUT`` (cli.py:2135)
# and read the graph beside it (cli.py:2063), so the guard needs that command's
# own positional/flag parse rather than the ``update`` one. These are the flags
# cli.py:2043-2060 consumes a value for; every other ``-``-leading token is a
# switch (``--no-viz``, ``--missing-only``, ``--timing``, ``--min-community-size=N``).
VALUE_FLAGS = frozenset({
    "--graph", "--backend", "--model", "--resolution",
    "--exclude-hubs", "--max-concurrency", "--batch-size",
})

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


def _label_scope(args: list[str]) -> tuple[Path, Path | None]:
    """``(watch_path, --graph override)`` as cli.py:2043-2062 parses them.

    ``watch_path`` defaults to ``.``; the first bare token wins and later bare
    tokens are ignored, exactly as the parser does. Only the separate-value
    form of ``--graph`` exists in graphify (``--graph=PATH`` would be consumed
    as an unknown switch), so accepting the ``=`` form here would let the guard
    allow a write graphify then ignores.
    """
    watch: Path | None = None
    graph: Path | None = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in VALUE_FLAGS:
            if arg == "--graph" and i + 1 < len(args):
                graph = Path(args[i + 1])
            i += 2
            continue
        if arg.startswith("-"):
            i += 1
            continue
        if watch is None:
            watch = Path(arg)
        i += 1
    return (watch if watch is not None else Path(".")), graph


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

    if command in ("cluster-only", "label"):
        watch, graph_override = _label_scope(args)
        out_name = Path(name).name  # cli.py:2131 compares on .name
        if graph_override is not None:
            if not graph_override.exists():
                # cli.py:2063-2068 — "no graph found at ...", exit 1, no write.
                return None
            if graph_override.parent.name == out_name:
                # cli.py:2132 — write beside the graph it read.
                return graph_override.parent.resolve()
        elif not (watch / name / "graph.json").exists():
            # Default read path is absent, so the same "no graph found" exit.
            return None
        out = watch / name
        if not out.is_absolute():
            # No _stabilize_rebuild_cwd on this path (watch.py:1448 only), so
            # ``out`` is relative to the process cwd, not GRAPHIFY_REPO_ROOT.
            out = Path.cwd() / out
        return out.resolve()

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


def _retarget_args(args: list[str]) -> str:
    """The caller's flags with the path and ``--graph`` removed.

    A remedy must not carry the refused ``--graph`` forward: graphify keeps the
    LAST one (cli.py:2043 walks argv in order), so appending the canonical path
    to the caller's argv would still name the wrong graph -- and the guard would
    refuse the fix it just printed.
    """
    kept: list[str] = []
    dropped_path = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--graph":
            i += 2  # flag + value
            continue
        if arg in VALUE_FLAGS:
            kept.extend(args[i:i + 2])
            i += 2
            continue
        if not arg.startswith("-") and not dropped_path:
            dropped_path = True  # first bare token is the path being replaced
            i += 1
            continue
        kept.append(arg)
        i += 1
    return (" " + " ".join(kept)) if kept else ""


def _refuse(
    out: Path, canonical: Path, argv: list[str], command: str
) -> str:
    joined = " ".join(argv) if argv else "<graphify args>"
    if command in ("cluster-only", "label"):
        rest = _retarget_args(argv[1:])
        fixes = (
            f"  graphify {command} src{rest}\n"
            f"  cd src && graphify {command}{rest}\n"
            f"  graphify {command} --graph {canonical / 'graph.json'}{rest}\n"
        )
        stake = (
            f"This command writes a whole store -- graph.json, GRAPH_REPORT.md and\n"
            f"the labels/analysis sidecars -- so a second one is a second graph to\n"
            f"keep in step, not a scratch file.\n"
        )
    else:
        fixes = (
            f"  graphify update src\n"
            f"  cd src && graphify update\n"
            f"  GRAPHIFY_OUT={canonical} graphify {joined}\n"
        )
        stake = ""
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
        f"{stake}"
        f"\n"
        f"Fix — point the run at the store codegraph reads (any one of these):\n"
        f"\n"
        f"{fixes}"
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

    canonical = (repo_root / "src" / "graphify-out").resolve()
    print(_refuse(out, canonical, rest, command), file=sys.stderr)
    return EXIT_DRIFT


if __name__ == "__main__":
    sys.exit(main())
