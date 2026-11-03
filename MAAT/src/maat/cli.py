"""Command line: maat weigh [--raw PATH] [--sizes 3,5,7,9,11]
                maat rules --text 'some 2d content' [--ref SRC] [--version YYYY-MM-DD]
                maat mutate --rules RS.json [--seed TEXT] [--frames N]
                maat arena --rules RS.json [--seed TEXT] [--frames N]
"""
from __future__ import annotations

import argparse
import json
import sys

from . import PANEL_SIZES
from .panel import compare
from .rules import validate

DEFAULT_RAW = "C:/Users/clint/Documents/ai_panel_opinions_raw.json"


def load_ruleset(path: str):
    """Load and validate a ruleset file; raises on the first violation."""
    from .rules import load

    return load(path)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="maat",
        description="MAAT — the Scales of Ma'at: AI panel weighing (opinion record only, not legally binding)",
    )
    sub = p.add_subparsers(dest="cmd")
    w = sub.add_parser("weigh", help="compute nested panels from an opinions raw file")
    w.add_argument("--raw", default=DEFAULT_RAW, help="path to ai_panel_*_raw.json")
    w.add_argument("--sizes", default=",".join(str(s) for s in PANEL_SIZES))
    r = sub.add_parser("rules", help="extract a Q1R1 ruleset from 2d content text")
    r.add_argument("--text", required=True, help="content text to extract rules from")
    r.add_argument("--ref", default="inline", help="source reference (url / path / id)")
    r.add_argument("--media", default="2d", choices=("2d", "3d", "text"))
    r.add_argument("--version", default=None, help="ruleset version date YYYY-MM-DD")
    m = sub.add_parser("mutate", help="run a mesh through the Q1R1 ruleset (Q2 kernel)")
    m.add_argument("--rules", required=True, help="path to a Q1R1 ruleset JSON file")
    m.add_argument("--seed", default="maat-default-seed", help="mesh seed text")
    m.add_argument("--frames", type=int, default=4, help="frames of the render loop")
    m.add_argument("--version", default=None, help="mesh version date YYYY-MM-DD")
    a = sub.add_parser("arena", help="run candidate branches through the Q1R1 ruleset (Q3 kernel)")
    a.add_argument("--rules", required=True, help="path to a Q1R1 ruleset JSON file")
    a.add_argument("--seed", default="maat-default-seed", help="arena seed text")
    a.add_argument("--frames", type=int, default=4, help="frames the tree runs")
    a.add_argument("--version", default=None, help="arena version date YYYY-MM-DD")
    args = p.parse_args(argv)

    if args.cmd == "rules":
        from .rules import extract as extract_rules

        rs = extract_rules(args.text, ref=args.ref, media=args.media, version=args.version)
        errs = validate(rs)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        print(json.dumps(rs, indent=2, sort_keys=True))
        return 0
    if args.cmd == "mutate":
        try:
            rs = load_ruleset(args.rules)
        except FileNotFoundError:
            print(f"ruleset not found: {args.rules}", file=sys.stderr)
            return 2
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        from .mutate import apply, new_mesh

        try:
            out = apply(rs, new_mesh(args.seed, version=args.version), frames=args.frames)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    if args.cmd == "arena":
        try:
            rs = load_ruleset(args.rules)
        except FileNotFoundError:
            print(f"ruleset not found: {args.rules}", file=sys.stderr)
            return 2
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        from .arena import apply as arena_apply, new_arena

        try:
            out = arena_apply(rs, new_arena(args.seed, version=args.version), frames=args.frames)
        except ValueError as e:
            print(e, file=sys.stderr)
            return 1
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
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
