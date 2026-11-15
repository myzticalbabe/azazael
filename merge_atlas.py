#!/usr/bin/env python3
# coding: utf-8
"""Merge yggdrasil census (cleave ledger) with module inventory (shard_intake format)."""

import json
import sys
from pathlib import Path


def merge_atlases(census_path: str, modules_path: str, output_path: str):
    """Merge cleave ledger census with module inventory."""
    print("Loading census...", file=sys.stderr)
    with open(census_path, 'r') as f:
        census = json.load(f)

    print("Loading modules...", file=sys.stderr)
    with open(modules_path, 'r') as f:
        modules_atlas = json.load(f)

    # Start with census (cleave ledger)
    merged = dict(census)

    # Add modules dict from module inventory
    merged['modules'] = modules_atlas.get('modules', {})

    # Update totals with module inventory data
    modules = modules_atlas.get('modules', {})
    if modules:
        merged['totals']['modules'] = len(modules)
        merged['totals']['lines'] = sum(m.get('lines', 0) for m in modules.values())
        merged['totals']['classes'] = sum(m.get('classes', 0) for m in modules.values())
        # Keep trees from census (more accurate for cleave)
        # merged['totals']['trees'] = len(set(m.get('tree') for m in modules.values()))

    # Write merged atlas
    Path(output_path).write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"Wrote merged atlas to {output_path}", file=sys.stderr)
    print(f"  trees: {merged['totals'].get('trees', 0)}", file=sys.stderr)
    print(f"  modules: {merged['totals'].get('modules', 0)}", file=sys.stderr)
    print(f"  lines: {merged['totals'].get('lines', 0)}", file=sys.stderr)
    print(f"  classes: {merged['totals'].get('classes', 0)}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python merge_atlas.py <census.json> <modules_atlas.json> <output.json>")
        sys.exit(1)
    sys.exit(merge_atlases(sys.argv[1], sys.argv[2], sys.argv[3]))