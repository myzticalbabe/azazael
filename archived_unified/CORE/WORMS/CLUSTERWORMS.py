# coding: utf-8
"""
CLUSTERWORMS - Coordinated Worm Collectives

Tier 2: Coordinated groups of worms working in unison.

Features:
- Worm coordination with shared state
- Inter-worm messaging
- Cluster lifecycle management
- Result aggregation
- Cluster persistence

Usage:
    >>> import clusterworms
    >>> cluster = clusterworms.ClusterWORMZ("system")
    >>> cluster.add_worm("SYSTEMZ", config={})
    >>> cluster.add_worm("PROCESSZ", config={})
    >>> results = cluster.execute_all()
    >>> aggregated = cluster.aggregate_results()
"""

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, scrolledtext


@dataclass
class ClusterResult:
    """Result from cluster execution."""

    cluster_id: str
    worm_results: Dict[str, Any]
    aggregated_metrics: Dict[str, float]
    duration_ms: float
    success_count: int
    failure_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WormConfig:
    """Configuration for a worm in cluster."""

    name: str
    module: str
    enabled: bool = True
    priority: int = 0
    timeout: int = 30
    retry: int = 1
    params: Dict = field(default_factory=dict)


CLUSTER_REGISTRY = {
    "bibl": {
        "description": "BIBL crawling and trimming",
        "worms": ["WORMZ", "TRIMZ"],
    },
    "system": {
        "description": "Full system monitoring",
        "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ"],
    },
    "network": {
        "description": "Network and time management",
        "worms": ["NETWORXZ", "CLOCKZ", "DISKZ"],
    },
    "security": {
        "description": "Security auditing",
        "worms": ["PROCESSZ", "NETWORXZ", "SYSTEMZ"],
    },
    "analysis": {
        "description": "Code analysis and metrics",
        "worms": ["METAZ", "METRICZ", "DEPENDZ"],
    },
    "validation": {
        "description": "Code validation and error checking",
        "worms": ["VALIDZ", "DEADZ", "ERRORZ"],
    },
    "health": {
        "description": "System health monitoring",
        "worms": ["HEALTHZ", "OPTIMIZ", "SYSTEMZ"],
    },
    "full": {
        "description": "Complete ecosystem scan",
        "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ", "NETWORXZ", "WORMZ"],
    },
}


class ClusterState:
    """Shared state for cluster execution."""

    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        self.results: Dict[str, Any] = {}
        self.metrics = defaultdict(list)
        self.messages: List[Dict] = []
        self.last_sync = datetime.now()
        self.lock = threading.Lock()

    def add_result(self, worm_name: str, result: Any):
        """Add result from worm."""
        with self.lock:
            self.results[worm_name] = result
            self.last_sync = datetime.now()

    def send_message(self, from_worm: str, to_worm: str, data: Any):
        """Send message between worms."""
        with self.lock:
            self.messages.append(
                {
                    "from": from_worm,
                    "to": to_worm,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def broadcast(self, data: Any, exclude: List[str] = None):
        """Broadcast message to all worms."""
        with self.lock:
            for worm in self.results.keys():
                if exclude and worm in exclude:
                    continue
                self.messages.append(
                    {
                        "from": "BROADCAST",
                        "to": worm,
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def get_messages(self, worm_name: str) -> List[Dict]:
        """Get messages for worm."""
        with self.lock:
            return [
                m
                for m in self.messages
                if m["to"] == worm_name or m["to"] == "BROADCAST"
            ]

    def clear_messages(self, worm_name: str = None):
        """Clear processed messages."""
        with self.lock:
            if worm_name:
                self.messages = [m for m in self.messages if m["to"] != worm_name]
            else:
                self.messages = []


class WormExecutor:
    """Executes a single worm in cluster context."""

    def __init__(self, name: str, config: WormConfig, state: ClusterState):
        self.name = name
        self.config = config
        self.state = state

    def execute(self, timeout: int = None) -> Dict[str, Any]:
        """Execute worm with configuration."""
        start = time.time()
        success = False
        result = None
        error = None

        try:
            timeout = timeout or self.config.timeout

            if self.config.module == "SYSTEMZ":
                import SYSTEMZ

                worm = SYSTEMZ.SYSTEMZ()
                result = worm.get_status().__dict__

            elif self.config.module == "PROCESSZ":
                import PROCESSZ

                worm = PROCESSZ.PROCESSZ()
                result = worm.get_summary()

            elif self.config.module == "DISKZ":
                import DISKZ

                worm = DISKZ.DISKZ()
                result = worm.get_summary()

            elif self.config.module == "NETWORXZ":
                import NETWORXZ

                worm = NETWORXZ.NETWORXZ()
                result = worm.get_summary()

            elif self.config.module == "CLOCKZ":
                import CLOCKZ

                worm = CLOCKZ.CLOCKZ()
                result = worm.get_uptime()

            elif self.config.module == "METAZ":
                import METAZ

                worm = METAZ()
                result = worm.run().__dict__

            elif self.config.module == "METRICZ":
                import METRICZ

                worm = METRICZ()
                result = worm.run().__dict__

            elif self.config.module == "DEPENDZ":
                import DEPENDZ

                worm = DEPENDZ()
                result = worm.run().__dict__

            elif self.config.module == "VALIDZ":
                import VALIDZ

                worm = VALIDZ()
                result = worm.run().__dict__

            elif self.config.module == "DEADZ":
                import DEADZ

                worm = DEADZ()
                result = worm.run().__dict__

            elif self.config.module == "ERRORZ":
                import ERRORZ

                worm = ERRORZ()
                result = worm.run().__dict__

            elif self.config.module == "TRIMZ":
                import TRIMZ

                worm = TRIMZ.TRIMZ()
                worm.scan_all(show_progress=False)
                result = {"files_scanned": len(worm.results)}

            elif self.config.module == "OPTIMIZ":
                import OPTIMIZ

                worm = OPTIMIZ.OPTIMIZ()
                result = worm.analyze().__dict__

            elif self.config.module == "HEALTHZ":
                import HEALTHZ

                worm = HEALTHZ.HEALTHZ()
                result = worm.check().__dict__

            else:
                result = {"error": f"Unknown module: {self.config.module}"}

            success = True

        except Exception as e:
            error = str(e)
            result = {"error": error}
            success = False

        duration = (time.time() - start) * 1000

        output = {
            "name": self.name,
            "success": success,
            "duration_ms": duration,
            "result": result,
            "error": error,
        }

        self.state.add_result(self.name, output)
        return output


class ClusterWORMZ:
    """Main cluster worm coordinator."""

    VERSION = "1.0.0"

    def __init__(self, cluster_type: str = "system"):
        self.cluster_type = cluster_type
        self.cluster_id = f"cluster_{int(time.time())}"
        self.configs: List[WormConfig] = []
        self.state = ClusterState(self.cluster_id)
        self.parallel = False
        self.timeout = 60

        self._load_cluster_config(cluster_type)

    def _load_cluster_config(self, cluster_type: str):
        """Load predefined cluster configuration."""
        if cluster_type in CLUSTER_REGISTRY:
            for worm_name in CLUSTER_REGISTRY[cluster_type]["worms"]:
                self.add_worm(worm_name, worm_name)

    def add_worm(self, name: str, module: str, config: Dict = None):
        """Add worm to cluster."""
        worm_config = WormConfig(
            name=name,
            module=module,
            enabled=config.get("enabled", True) if config else True,
            priority=config.get("priority", 0) if config else 0,
            timeout=config.get("timeout", 30) if config else 30,
            retry=config.get("retry", 1) if config else 1,
            params=config.get("params", {}) if config else {},
        )
        self.configs.append(worm_config)

    def remove_worm(self, name: str):
        """Remove worm from cluster."""
        self.configs = [c for c in self.configs if c.name != name]

    def set_parallel(self, parallel: bool):
        """Set parallel or sequential execution."""
        self.parallel = parallel

    def set_timeout(self, timeout: int):
        """Set execution timeout."""
        self.timeout = timeout

    def execute_all(self) -> List[Dict[str, Any]]:
        """Execute all worms in cluster."""
        results = []
        enabled_configs = [c for c in self.configs if c.enabled]
        enabled_configs.sort(key=lambda x: x.priority, reverse=True)

        if self.parallel:
            threads = []
            for config in enabled_configs:
                executor = WormExecutor(config.name, config, self.state)
                t = threading.Thread(target=lambda: results.append(executor.execute()))
                threads.append(t)
                t.start()
            for t in threads:
                t.join(timeout=self.timeout)
        else:
            for config in enabled_configs:
                executor = WormExecutor(config.name, config, self.state)
                result = executor.execute(timeout=self.timeout)
                results.append(result)

        return results

    def execute_worm(self, name: str) -> Optional[Dict]:
        """Execute single worm by name."""
        for config in self.configs:
            if config.name == name:
                executor = WormExecutor(config.name, config, self.state)
                return executor.execute()
        return None

    def aggregate_results(self) -> ClusterResult:
        """Aggregate results from all worms."""
        results = self.state.results

        metrics = {
            "total_duration_ms": 0,
            "success_rate": 0,
            "avg_duration_ms": 0,
        }

        success_count = 0
        total_duration = 0

        for worm_name, result in results.items():
            if isinstance(result, dict) and "duration_ms" in result:
                total_duration += result["duration_ms"]
                if result.get("success", False):
                    success_count += 1

        metrics["total_duration_ms"] = total_duration
        metrics["success_rate"] = success_count / len(results) if results else 0
        metrics["avg_duration_ms"] = total_duration / len(results) if results else 0

        return ClusterResult(
            cluster_id=self.cluster_id,
            worm_results=results,
            aggregated_metrics=metrics,
            duration_ms=total_duration,
            success_count=success_count,
            failure_count=len(results) - success_count,
        )

    def get_status(self) -> Dict:
        """Get cluster status."""
        return {
            "cluster_id": self.cluster_id,
            "cluster_type": self.cluster_type,
            "worm_count": len(self.configs),
            "enabled_count": len([c for c in self.configs if c.enabled]),
            "parallel": self.parallel,
            "timeout": self.timeout,
            "last_sync": self.state.last_sync.isoformat(),
        }


def run_popup():
    """Run cluster worms with popup window."""
    root = tk.Tk()
    root.title("CLUSTERWORMS - Coordinated Worm Collectives")
    root.geometry("1000x750")
    root.configure(bg="#1a1a2e")

    def log(msg, level="INFO"):
        colors = {
            "OK": "#00ff88",
            "FAIL": "#ff4444",
            "INFO": "#00aaff",
            "CLUSTER": "#ff00ff",
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        text_area.insert("end", f"[{timestamp}] [{level}] {msg}\n")
        text_area.see("end")
        root.update_idletasks()

    header = tk.Frame(root, bg="#16213e", pady=15)
    header.pack(fill="x")

    tk.Label(
        header,
        text="CLUSTERWORMS",
        font=("Consolas", 28, "bold"),
        bg="#16213e",
        fg="#00d4ff",
    ).pack()

    tk.Label(
        header,
        text="Tier 2: Coordinated Worm Collectives",
        font=("Consolas", 12),
        bg="#16213e",
        fg="#7c3aed",
    ).pack()

    status_label = tk.Label(
        root,
        text="Ready",
        font=("Consolas", 14),
        bg="#1a1a2e",
        fg="#00ff88",
    )
    status_label.pack(pady=5)

    control_frame = tk.Frame(root, bg="#1a1a2e", pady=10)
    control_frame.pack(fill="x", padx=20)

    tk.Label(
        control_frame,
        text="Cluster:",
        bg="#1a1a2e",
        fg="#00d4ff",
        font=("Consolas", 11),
    ).pack(side="left")

    cluster_var = tk.StringVar(value="system")
    cluster_combo = ttk.Combobox(
        control_frame,
        textvariable=cluster_var,
        values=list(CLUSTER_REGISTRY.keys()),
        width=15,
        font=("Consolas", 10),
    )
    cluster_combo.pack(side="left", padx=10)

    parallel_var = tk.BooleanVar(value=False)
    parallel_check = tk.Checkbutton(
        control_frame,
        text="Parallel Execution",
        variable=parallel_var,
        font=("Consolas", 11),
        bg="#1a1a2e",
        fg="#00ff88",
        selectcolor="#16213e",
    )
    parallel_check.pack(side="left", padx=20)

    progress_frame = tk.Frame(root, bg="#1a1a2e", pady=10)
    progress_frame.pack(fill="x", padx=20)

    progress = ttk.Progressbar(progress_frame, mode="determinate", length=950)
    progress.pack(fill="x")

    progress_label = tk.Label(
        progress_frame,
        text="0 / 0 worms",
        font=("Consolas", 12),
        bg="#1a1a2e",
        fg="#00ff88",
    )
    progress_label.pack()

    stats_frame = tk.Frame(root, bg="#1a1a2e", pady=5)
    stats_frame.pack(fill="x", padx=20)

    stats_label = tk.Label(
        stats_frame,
        text="Worms: 0 | Success: 0 | Duration: 0ms",
        font=("Consolas", 12),
        bg="#1a1a2e",
        fg="#00d4ff",
    )
    stats_label.pack()

    text_area = scrolledtext.ScrolledText(
        root, wrap="word", font=("Consolas", 10), bg="#0f0f1a", fg="#00ff88", height=35
    )
    text_area.pack(fill="both", expand=True, padx=20, pady=10)

    button_frame = tk.Frame(root, bg="#1a1a2e", pady=15)
    button_frame.pack(fill="x", padx=20)

    def run_cluster():
        status_label.config(text="Executing...")
        progress["value"] = 0
        text_area.delete("1.0", "end")

        cluster_type = cluster_var.get()
        parallel = parallel_var.get()

        log("=" * 60, "CLUSTER")
        log(f"CLUSTERWORMS - {cluster_type.upper()} Cluster", "CLUSTER")
        log("=" * 60, "CLUSTER")

        cluster = ClusterWORMZ(cluster_type)
        cluster.set_parallel(parallel)

        status = cluster.get_status()
        log(f"Cluster: {status['cluster_id']}", "INFO")
        log(f"Worms: {status['worm_count']} | Parallel: {parallel}", "INFO")
        log("-" * 60, "INFO")

        progress["value"] = 20
        progress_label.config(text=f"Executing worms...")
        root.update()

        results = cluster.execute_all()

        progress["value"] = 80
        log(f"\nExecution Results:", "INFO")
        for r in results:
            status_icon = "OK" if r.get("success") else "FAIL"
            log(
                f"  [{status_icon}] {r['name']}: {r.get('duration_ms', 0):.0f}ms",
                status_icon if r.get("success") else "FAIL",
            )

        agg = cluster.aggregate_results()

        log(f"\nAggregation:", "INFO")
        log(
            f"  Success Rate: {agg.success_count}/{len(results)} ({agg.success_count / len(results) * 100:.0f}%)",
            "INFO",
        )
        log(f"  Total Duration: {agg.duration_ms:.0f}ms", "INFO")

        progress["value"] = 100
        stats_label.config(
            text=f"Worms: {len(results)} | Success: {agg.success_count} | Duration: {agg.duration_ms:.0f}ms"
        )
        status_label.config(text="Complete!")

    def show_clusters():
        text_area.delete("1.0", "end")
        log("=" * 60, "CLUSTER")
        log("Available Clusters", "CLUSTER")
        log("=" * 60, "CLUSTER")
        for name, info in CLUSTER_REGISTRY.items():
            log(f"\n{name.upper()}:", "INFO")
            log(f"  Description: {info['description']}", "INFO")
            log(f"  Worms: {', '.join(info['worms'])}", "INFO")

    btn_run = tk.Button(
        button_frame,
        text="EXECUTE",
        command=run_cluster,
        font=("Consolas", 13, "bold"),
        bg="#16213e",
        fg="#00ff88",
        width=12,
    )
    btn_run.pack(side="left", padx=10)

    btn_show = tk.Button(
        button_frame,
        text="CLUSTERS",
        command=show_clusters,
        font=("Consolas", 13, "bold"),
        bg="#16213e",
        fg="#ff00ff",
        width=10,
    )
    btn_show.pack(side="left", padx=10)

    close_btn = tk.Button(
        button_frame,
        text="CLOSE",
        command=root.destroy,
        font=("Consolas", 13, "bold"),
        bg="#ff4444",
        fg="#ffffff",
        width=10,
    )
    close_btn.pack(side="right", padx=10)

    log("CLUSTERWORMS Ready", "INFO")
    log("Select cluster type and click EXECUTE", "INFO")

    root.mainloop()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CLUSTERWORMS - Coordinated Worm Collectives"
    )
    parser.add_argument(
        "--type", type=str, help="Cluster type (system, network, bibl, etc.)"
    )
    parser.add_argument("--list", action="store_true", help="List available clusters")
    parser.add_argument("--execute", action="store_true", help="Execute cluster")
    parser.add_argument("--parallel", action="store_true", help="Parallel execution")
    parser.add_argument("--popup", action="store_true", help="Show popup window")

    args = parser.parse_args()

    if args.popup:
        run_popup()
    elif args.list:
        print("Available Clusters:")
        for name, info in CLUSTER_REGISTRY.items():
            print(f"  {name}: {info['description']}")
            print(f"    Worms: {', '.join(info['worms'])}")
    elif args.execute:
        cluster_type = args.type or "system"
        cluster = ClusterWORMZ(cluster_type)
        cluster.set_parallel(args.parallel)
        results = cluster.execute_all()
        agg = cluster.aggregate_results()
        print(f"Cluster: {cluster_type}")
        print(f"Success: {agg.success_count}/{len(results)}")
        print(f"Duration: {agg.duration_ms:.0f}ms")
    else:
        print("CLUSTERWORMS - Coordinated Worm Collectives")
        print()
        print("Usage:")
        print("  python ClusterWORMZ.py --type system --execute")
        print("  python ClusterWORMZ.py --list")
        print("  python ClusterWORMZ.py --type bibl --parallel --execute")
        print("  python ClusterWORMZ.py --popup")


if __name__ == "__main__":
    main()
