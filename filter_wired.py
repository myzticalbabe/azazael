#!/usr/bin/env python3
# coding: utf-8
"""Filter WIRED.json to only include entries that exist in the current atlas."""

import json
import sys
from pathlib import Path


def filter_wired(atlas_path: str, wired_path: str, output_path: str):
    """Filter WIRED.json to only include shards that exist in atlas."""
    print("Loading atlas...", file=sys.stderr)
    with open(atlas_path, 'r') as f:
        atlas = json.load(f)

    print("Loading WIRED...", file=sys.stderr)
    with open(wired_path, 'r') as f:
        wired = json.load(f)

    # Generate expected shard IDs from atlas
    from Project_ELIZA.tools.shard_intake import units as intake_units
    expected_shards = {entry["shard_id"] for entry in intake_units(atlas)}
    print(f"Expected shards in atlas: {len(expected_shards)}", file=sys.stderr)

    # Filter wired entries
    wired_dict = wired.get('wired', {})
    print(f"Original wired entries: {len(wired_dict)}", file=sys.stderr)

    filtered = {k: v for k, v in wired_dict.items() if k in expected_shards}
    print(f"Filtered wired entries: {len(filtered)}", file=sys.stderr)
    print(f"Removed: {len(wired_dict) - len(filtered)}", file=sys.stderr)

    # Write filtered WIRED.json
    filtered_wired = dict(wired)
    filtered_wired['wired'] = filtered
    Path(output_path).write_text(json.dumps(filtered_wired, indent=1), encoding="utf-8")
    print(f"Wrote filtered WIRED to {output_path}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python filter_wired.py <atlas.json> <WIRED.json> <output.json>")
        sys.exit(1)
    sys.exit(filter_wired(sys.argv[1], sys.argv[2], sys.argv[3]))