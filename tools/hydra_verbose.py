"""HYDRA Verbose Mode — Monkey-patch to add --verbose to HYDRA.py.

Usage:  python3 hydra_verbose.py --discover --run --verbose
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Desktop/azazael-project-e"))
os.chdir(str(Path.home() / "Desktop/azazael-project-e"))

# Patch HYDRA before importing
import HYDRA

original_execute = HYDRA.HYDRACluster._execute_stage

def verbose_execute(self, step):
    results = original_execute(self, step)
    verbose = '--verbose' in sys.argv
    if verbose:
        print(f"\n  📊 Stage: {step.stage.value}")
        print(f"  📋 Nodes: {step.nodes}")
        print(f"  🔄 Conditions: {step.conditions}")
        for node_name, node_result in results.items():
            print(f"     {'✅' if node_result['status'] == 'success' else '❌'} {node_name}: {node_result['status']} ({node_result['duration']:.2f}s)")
    return results

HYDRA.HYDRACluster._execute_stage = verbose_execute

# Run HYDRA with verbose flag
if __name__ == "__main__":
    # Remove --verbose from args for argparse
    sys.argv = [a for a in sys.argv if a != '--verbose']
    from HYDRA import HYDRACluster
    # Re-parse with argparse
    # Just run the cluster directly
    cluster = HYDRACluster()
    cluster.load_nodes()
    
    if '--discover' in sys.argv:
        groups = cluster.auto_discover_ml_groups()
        print(f"Discovered {len(groups)} groups:")
        for g, m in groups.items():
            print(f"  {g}: {len(m)} modules")
    
    if '--run' in sys.argv:
        cluster.build_sequence()
        results = cluster.run_sequential()
        print(f"\nCompleted {len(results['stages'])} stages")
    
    if '--status' in sys.argv:
        s = cluster.get_cluster_status()
        print(f"Nodes: {s['total_nodes']} | Success: {s['successful']} | Failed: {s['failed']}")
