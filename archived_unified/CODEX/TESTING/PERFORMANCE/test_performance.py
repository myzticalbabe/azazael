import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))

# coding: utf-8
#!/usr/bin/env python3
"""
Performance Benchmarks for Azazael Ecosystem
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, "C:/Users/clint/Desktop")


class PerformanceBenchmarks:
    """Performance benchmarks for ecosystem components."""

    BENCHMARKS = {
        "wormz_crawl_1000_files": {"target": "< 30s", "threshold": "60s"},
        "metaworms_analysis": {"target": "< 60s", "threshold": "120s"},
        "hydra_pipeline": {"target": "< 120s", "threshold": "300s"},
        "memory_usage_peak": {"target": "< 500MB", "threshold": "1GB"},
        "klink_response": {"target": "< 1s", "threshold": "5s"},
    }

    def __init__(self):
        self.results = []

    def benchmark_wormz_crawl(
        self, path: str = "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION"
    ):
        """Benchmark WORMZ crawl performance."""
        start = time.time()
        try:
            from WORMZ.WORMZ import WORMZ

            wormz = WORMZ()
            result = wormz.crawl(path)
            elapsed = time.time() - start
            self.results.append(
                {
                    "test": "wormz_crawl",
                    "elapsed_ms": elapsed * 1000,
                    "files": result.files_scanned
                    if hasattr(result, "files_scanned")
                    else 0,
                }
            )
            return elapsed
        except Exception as e:
            return None

    def benchmark_metaworms(self):
        """Benchmark METAWORMS analysis performance."""
        start = time.time()
        try:
            from METAWORMS.METAWORMS import METAWORMS

            mw = METAWORMS()
            results = mw.run_all()
            elapsed = time.time() - start
            self.results.append(
                {
                    "test": "metaworms_analysis",
                    "elapsed_ms": elapsed * 1000,
                    "metaworms_run": len(results),
                }
            )
            return elapsed
        except Exception as e:
            return None

    def benchmark_hydra_pipeline(self):
        """Benchmark HYDRA pipeline performance."""
        start = time.time()
        try:
            from HYDRA.HYDRA import HYDRACluster

            hydra = HYDRACluster()
            result = hydra.run_all()
            elapsed = time.time() - start
            self.results.append(
                {"test": "hydra_pipeline", "elapsed_ms": elapsed * 1000}
            )
            return elapsed
        except Exception as e:
            return None

    def run_all_benchmarks(self) -> dict:
        """Run all benchmarks."""
        print("Running performance benchmarks...")
        print("-" * 50)

        benchmarks = [
            ("WORMZ crawl", self.benchmark_wormz_crawl),
            ("METAWORMS analysis", self.benchmark_metaworms),
            ("HYDRA pipeline", self.benchmark_hydra_pipeline),
        ]

        for name, func in benchmarks:
            print(f"Running {name}...", end=" ")
            result = func()
            if result is not None:
                print(f"OK ({result:.2f}s)")
            else:
                print("SKIPPED")

        print("-" * 50)
        return {"benchmarks": self.results}

    def generate_report(self) -> str:
        """Generate benchmark report."""
        lines = ["# Performance Benchmark Report", ""]
        lines.append(f"Generated: time.strftime('%Y-%m-%d %H:%M:%S')")
        lines.append("")
        lines.append("## Results")
        lines.append("")
        lines.append("| Test | Elapsed | Status |")
        lines.append("|------|---------|--------|")

        for r in self.results:
            elapsed_ms = r.get("elapsed_ms", 0)
            elapsed = elapsed_ms / 1000
            status = "PASS" if elapsed < 60 else "WARN"
            lines.append(f"| {r['test']} | {elapsed:.2f}s | {status} |")

        return "\n".join(lines)


if __name__ == "__main__":
    bench = PerformanceBenchmarks()
    bench.run_all_benchmarks()
    print("\n" + bench.generate_report())
