#!/usr/bin/env python3
# coding: utf-8
"""mellifluous -- one native door into the memory + MCP tooling.

Phase 1 (dispatch): every live script in the migration map
(docs/MELLIFLUOUS_CONSOLIDATION.md) is a subcommand. Modules load lazily
so `--help` stays instant; entries run in-process; each run is timed and
`--json` wraps the envelope. No logic lives here -- that is phase 2+.

Usage:
    python tools/mellifluous.py --help
    python tools/mellifluous.py memory backup --dry-run
    python tools/mellifluous.py pmb e2e
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: name -> (module, mode, blurb). mode argv: entry(args); bare: entry()
#: with sys.argv patched (for mains that take none); phase per design doc.
COMMANDS: dict[str, tuple[str, str, str]] = {
    "memory-backup": ("memory_backup", "argv", "verified snapshots of the memory stores"),
    "pmb-capture": ("pmb_capture", "argv", "capture pmb working memory"),
    "pmb-pickup": ("pmb_outbox_pickup", "argv", "pick up pmb outbox records"),
    "pmb-transcript": ("pmb_observe_transcript", "argv", "observe transcript into pmb"),
    "pmb-session": ("pmb_session_observe", "argv", "observe a session into pmb"),
    "pams-capture": ("pams_capture", "argv", "capture into PAMS"),
    "pmb-e2e": ("pmb_e2e_check", "bare", "end-to-end pmb health check"),
    "pmb-client": ("pmb_client", "bare", "pmb client smoke"),
    "prune": ("prune_memory_debt", "bare", "prune memory debt"),
    "gate": ("mcp_startup_gate", "argv", "MCP startup gate"),
    "verify-engram": ("verify_engram_mcp", "bare", "verify engram MCP wiring"),
    "eight-verify": ("mcp_eight_verify", "argv", "eight-server MCP verification"),
    "proxy": ("pmb_floor_proxy", "bare", "floor proxy daemon (long-running)"),
    "supervisor": ("supervisor_mcp", "argv", "supervisor MCP (verdicts)"),
}


def run_command(name: str, args: list[str]) -> tuple[int, float]:
    mod_name, mode, _ = COMMANDS[name]
    mod = importlib.import_module(mod_name)
    entry = getattr(mod, "main", None)
    if entry is None:
        print(f"mellifluous: {mod_name} has no main() entry -- phase 3 work")
        return 2, 0.0
    t0 = time.perf_counter()
    if mode == "argv":
        rc = entry(args)
    else:
        saved, sys.argv = sys.argv, [mod_name, *args]
        try:
            rc = entry()
        finally:
            sys.argv = saved
    elapsed = time.perf_counter() - t0
    return (rc if isinstance(rc, int) else 0), elapsed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="mellifluous",
        description="One native door into the memory + MCP tooling (phase 1: dispatch).",
    )
    ap.add_argument("--json", action="store_true", help="wrap the result envelope as JSON")
    ap.add_argument("command", choices=sorted(COMMANDS), help="which tool to run")
    ap.add_argument("rest", nargs=argparse.REMAINDER, help="arguments forwarded to the tool")
    ns = ap.parse_args(argv)
    if ns.command in ("proxy", "supervisor"):
        print(f"note: {ns.command} is a long-running daemon -- it does not return promptly")
    rc, elapsed = run_command(ns.command, ns.rest)
    if ns.json:
        print(json.dumps({"command": ns.command, "exit": rc,
                          "seconds": round(elapsed, 1)}))
    else:
        print(f"mellifluous: {ns.command} exit={rc} {elapsed:.1f}s")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
