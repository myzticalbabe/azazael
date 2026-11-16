#!/usr/bin/env python3
"""Convert yggdrasil_census.py output to shard_intake.py expected atlas format."""

import json
import sys
from pathlib import Path


def convert_atlas(census_path: str, output_path: str):
    """Convert yggdrasil census to shard_intake atlas format."""
    with open(census_path, 'r') as f:
        census = json.load(f)

    # Build modules dict from python graph
    modules = {}
    python_graph = census.get('graphs', {}).get('python', {})

    # The python_graph has modules with their metadata
    for module_name, meta in python_graph.items():
        # Skip non-source modules (tests, vendored, etc.)
        if module_name.startswith('test_') or 'test/' in module_name:
            continue
        if 'vendor' in module_name or 'archived' in module_name:
            continue
        if 'generated' in module_name:
            continue

        # Extract class info from the module's class list
        # The census doesn't directly list top_classes per module, but we can
        # get it from the python_graph if it has class info

        tree = meta.get('tree', '(root)')
        lines = meta.get('lines', 0)
        public_api = meta.get('public_api', 0)
        classes = meta.get('classes', 0)

        # Get top classes from the module's class list
        # The census might not have per-module class names, so we'll use what we have
        top_classes = meta.get('top_classes', [])

        modules[module_name] = {
            'tree': tree,
            'lines': lines,
            'public_api': public_api,
            'classes': classes,
            'top_classes': top_classes
        }

    # Build the atlas in the format shard_intake.py expects
    atlas = {
        'schema': 2,
        'generated_at': census.get('generated_at', ''),
        'root': census.get('root', '/mnt/c/Azazael/azazael'),
        'modules': modules,
        'totals': {
            'trees': census.get('totals', {}).get('trees', 0),
            'modules': len(modules),
            'lines': sum(m.get('lines', 0) for m in modules.values()),
            'classes': sum(m.get('classes', 0) for m in modules.values()),
        }
    }

    with open(output_path, 'w') as f:
        json.dump(atlas, f, indent=2)

    print(f"Converted {len(modules)} modules to {output_path}")
    print(f"Total classes: {sum(m.get('classes', 0) for m in modules.values())}")
    print(f"Total lines: {sum(m.get('lines', 0) for m in modules.values())}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_atlas.py <census.json> <output_atlas.json>")
        sys.exit(1)

    convert_atlas(sys.argv[1], sys.argv[2])