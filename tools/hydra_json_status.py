"""HYDRA --json status output. Run: python3 hydra_json_status.py

Adds --json flag for machine-readable cluster status.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Desktop/azazael-project-e"))

from HYDRA import HYDRACluster

cluster = HYDRACluster()
cluster.load_nodes()

if '--json' in sys.argv:
    print(json.dumps(cluster.get_cluster_status(), indent=2))
else:
    s = cluster.get_cluster_status()
    print(f"Nodes: {s['total_nodes']} | Success: {s['successful']} | Failed: {s['failed']} | Pending: {s.get('pending', 0)}")
