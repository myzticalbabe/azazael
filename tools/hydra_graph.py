"""HYDRA Node Dependency Graph — Generates Graphviz DOT output.

Usage:  python3 hydra_graph.py | dot -Tpng -o hydra_graph.png
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "Desktop/azazael-project-e"))

from HYDRA import HYDRACluster

cluster = HYDRACluster()
cluster.load_nodes()

if not cluster.nodes:
    print("// No nodes registered. Run --discover first.", file=sys.stderr)
    sys.exit(1)

# Color mapping by group
GROUP_COLORS = {
    "Core": "#4CAF50",
    "Analysis": "#2196F3",
    "Q-Learning": "#FF9800",
    "Integration": "#9C27B0",
    "Monitoring": "#00BCD4",
    "LM Studio": "#E91E63",
    "Installation": "#795548",
    "Conversion": "#607D8B",
    "Autoload": "#3F51B5",
    "Improvements": "#009688",
}

print("digraph HYDRA {")
print("  rankdir=LR;")
print("  splines=ortho;")
print('  node [style=filled, shape=box, fontname="monospace"];')
print("  ranksep=1.5;")
print()

# Create subgraphs by group
groups = {}
for name, node in cluster.nodes.items():
    groups.setdefault(node.group, []).append(name)

for group, members in groups.items():
    color = GROUP_COLORS.get(group, "#cccccc")
    print(f"  subgraph cluster_{group.lower().replace('-', '_')} {{")
    print(f'    label="{group} ({len(members)} nodes)";')
    print(f'    style=filled;')
    print(f'    color="{color}22";')
    print(f'    fontname="monospace";')
    for m in members:
        status_color = "palegreen" if cluster.nodes[m].status == "success" else "lightyellow"
        print(f'    "{m}" [fillcolor="{status_color}"];')
    print("  }")
    print()

# Draw dependency edges
for name, node in cluster.nodes.items():
    for dep in node.dependencies:
        print(f'  "{dep}" -> "{name}";')

print("}")
