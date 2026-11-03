"""Command line: maat weigh [--raw PATH] [--sizes 3,5,7,9,11]"""
from __future__ import annotations

import argparse
import sys

from . import PANEL_SIZES
from .panel import compare

DEFAULT_RAW = "C:/Users/clint/Documents/ai_panel_opinions_raw.json"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="maat",
        description="MAAT — the Scales of Ma'at: AI panel weighing (opinion record only, not legally binding)",
    )
    sub = p.add_subparsers(dest="cmd")
    w = sub.add_parser("weigh", help="compute nested panels from an opinions raw file")
    w.add_argument("--raw", default=DEFAULT_RAW, help="path to ai_panel_*_raw.json")
    w.add_argument("--sizes", default=",".join(str(s) for s in PANEL_SIZES))
    args = p.parse_args(argv)
    if args.cmd != "weigh":
        p.print_help()
        return 0

    sizes = tuple(int(s) for s in str(args.sizes).split(",") if s.strip())
    try:
        panels, n = compare(args.raw, sizes)
    except FileNotFoundError:
        print(f"raw file not found: {args.raw}", file=sys.stderr)
        return 2

    print(f"reachable judges: {n}")
    for pan in panels:
        print(f"\n== panel-{pan['size']} ({pan['judges']} judges) ==")
        for h, t in pan["tally"].items():
            a, rv = t["AFFIRM"], t["REVERSE"]
            print(f"  {h}: AFFIRM {a} / REVERSE {rv}")
        print(f"  named dissent: {pan['dissent_named']}")
    print("\nAI panel opinions are not legally binding - opinion record with provenance only.")
    return 0
