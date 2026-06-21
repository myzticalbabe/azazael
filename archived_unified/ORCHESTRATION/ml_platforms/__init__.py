import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))

# coding: utf-8
"""
Azazael ML Platform Harness
Unified interface for ML development with LM Studio.
"""

__version__ = "2.0.0"
__path__ = ["C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION/ml_platforms"]


def _setup_path():
    """Ensure correct path is in sys.path."""
    import sys
    import os

    correct_path = "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION/ml_platforms"

    # Remove wrong paths
    wrong_paths = [
        "%PYTHONPATH%",
        "C:\\Users\\clint\\Desktop\\New folder\\ml_platforms",
        "C:\\Users\\clint\\Desktop\\New folder\\ml_platforms\\",
    ]

    sys.path = [
        p
        for p in sys.path
        if p not in wrong_paths and not p.endswith("\\ml_platforms\\")
    ]

    # Add correct path if not present
    if correct_path not in sys.path:
        sys.path.insert(0, correct_path)

    return correct_path


_correct_path = _setup_path()


def list_platforms():
    """List available ML platforms."""
    print("\n" + "=" * 60)
    print("AVAILABLE ML PLATFORMS")
    print("=" * 60)
    print("  [OK] PyTorch       - Deep learning framework")
    print("  [OK] TensorFlow    - Deep learning framework")
    print("  [OK] NumPy         - Array computing")
    print("  [OK] scikit-learn  - Classical ML")
    print("  [OK] ONNX          - Model interchange")
    print("  [OK] MLflow        - Experiment tracking")
    print("  [OK] Ray           - Distributed computing")
    print("=" * 60 + "\n")


def debug(error_msg):
    """Debug ML errors and suggest fixes."""
    print("\n" + "=" * 60)
    print("DEBUG ANALYSIS")
    print("=" * 60)
    print(f"Error: {error_msg}\n")

    fixes = {
        "cuda out of memory": "REDUCE BATCH SIZE or use gradient accumulation",
        "module not found": "RUN: pip install the-missing-package",
        "shape mismatch": "Use tensor.reshape() or tensor.view()",
        "dtype error": "Convert: tensor.float() or tensor.long()",
        "nan loss": "Check data normalization, add gradient clipping",
    }

    found = False
    for key, fix in fixes.items():
        if key in error_msg.lower():
            print(f"[ISSUE] {key}")
            print(f"[FIX] {fix}")
            found = True

    if not found:
        print("[SUGGESTION] Check framework documentation")

    print("=" * 60 + "\n")


def get_recommendation(task, gpu_available=True):
    """Get framework recommendation for task."""
    from improvements.qlearning_table import AdaptivePlatformSelector, TaskType

    task_map = {
        "cv": TaskType.COMPUTER_VISION,
        "nlp": TaskType.NLP,
        "tabular": TaskType.TABULAR,
        "rl": TaskType.REINFORCEMENT,
        "generative": TaskType.GENERATIVE,
    }

    selector = AdaptivePlatformSelector()
    task_type = task_map.get(task, TaskType.COMPUTER_VISION)
    return selector.get_recommendations(task_type)


def monitor_health():
    """Run health monitoring."""
    from health_monitor import PlatformHealthMonitor

    monitor = PlatformHealthMonitor()
    monitor.print_status()


if __name__ == "__main__":
    print("Azazael ML Platform")
    print("=" * 60)
    list_platforms()
    print("Path fixed:", _correct_path)


