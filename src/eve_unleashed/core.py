"""
Eve Unleashed Core
==================
Model loading, inference result types, and framework detection.
"""

import os
import subprocess
import sys
import time
from typing import Any
from pathlib import Path

# Cached XPU availability check (subprocess-based to survive segfaults)
_XPU_AVAILABLE: (bool | None) = None


def _check_xpu_available() -> bool:
    """Check Intel XPU GPU availability via a subprocess sandbox.

    torch.xpu.is_available() can segfault or hang on systems without
    Intel GPU hardware (e.g. WSL2 without GPU-PV passthrough). Running
    the check in a child process isolates the crash from the parent.

    Result is cached globally — first call takes up to 5 seconds,
    subsequent calls return instantly.
    """
    global _XPU_AVAILABLE
    if _XPU_AVAILABLE is not None:
        return _XPU_AVAILABLE

    try:
        code = (
            "import torch; "
            "print(getattr(torch, 'xpu', None) is not None "
            "and torch.xpu.is_available())"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            env=os.environ.copy(),
        )
        _XPU_AVAILABLE = (
            result.returncode == 0 and result.stdout.strip() == "True"
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception):
        _XPU_AVAILABLE = False

    return _XPU_AVAILABLE

# PIL / image support detection
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None  # type: ignore

# Re-export shared data models (single source of truth across all projects)
try:
    from shared.models import InferenceResult, BatchResult
except ImportError:
    # Fallback: define locally if shared module not available
    from dataclasses import dataclass, field

    @dataclass
    class InferenceResult:
        model_name: str = ""
        framework: str = ""
        input_shape: tuple = ()
        output_shape: tuple = ()
        latency_ms: float = 0.0
        predictions: list[Any] = field(default_factory=list)
        probabilities: (list[float] | None) = None
        metadata: dict[str, Any] = field(default_factory=dict)

    @dataclass
    class BatchResult:
        results: list[Any] = field(default_factory=list)
        total_time_ms: float = 0.0
        avg_latency_ms: float = 0.0
        throughput_per_sec: float = 0.0

# Ensure shared is importable from the library
try:
    pass
except ImportError:
    _shared_path = Path(__file__).resolve().parents[4] / "workspace" / "projects"
    if str(_shared_path) not in sys.path:
        sys.path.insert(0, str(_shared_path))


class ModelLoader:
    """Load and manage ML models across frameworks."""

    @staticmethod
    def detect_frameworks() -> dict[str, bool]:
        """Detect which ML frameworks are available."""
        frameworks = {}
        for name, module in [
            ("torch", "torch"),
            ("tensorflow", "tensorflow"),
            ("sklearn", "sklearn"),
            ("transformers", "transformers"),
            ("onnx", "onnxruntime"),
            ("gguf", "llama_cpp"),
            ("vl", None),  # VL = transformers + PIL
        ]:
            if name == "vl":
                frameworks[name] = frameworks.get("transformers", False) and HAS_PIL
                continue
            try:
                __import__(module)
                frameworks[name] = True
            except ImportError:
                frameworks[name] = False

        # GPU acceleration detection
        if frameworks.get("torch"):
            try:
                import torch
                frameworks["cuda"] = torch.cuda.is_available()
                frameworks["metal"] = torch.backends.mps.is_available()
                # Intel XPU (Arc GPU via Level Zero / SYCL)
                # Uses subprocess sandbox to survive segfaults on headless systems
                frameworks["xpu"] = _check_xpu_available()
            except Exception:
                frameworks["cuda"] = False
                frameworks["metal"] = False
                frameworks["xpu"] = False

        # OpenCL detection (for Intel iGPU/dGPU, AMD GPUs)
        frameworks["opencl"] = False
        try:
            import pyopencl
            platforms = pyopencl.get_platforms()
            frameworks["opencl"] = len(platforms) > 0
        except ImportError:
            pass

        # Vulkan detection (cross-platform GPU compute)
        frameworks["vulkan"] = False
        try:
            # Check for Vulkan via torch backend or vulkan-compute library
            import torch
            frameworks["vulkan"] = (
                hasattr(torch, "vulkan") and torch.vulkan.is_available()
            )
        except Exception:
            pass

        return frameworks

    @staticmethod
    def load_torch(model_path: str, device: str = "cpu"):
        """Load a PyTorch model."""
        import torch

        model = torch.load(model_path, map_location=device, weights_only=False)
        model.eval()
        return model

    @staticmethod
    def load_sklearn(model_path: str):
        """Load a scikit-learn model."""
        import joblib

        return joblib.load(model_path)

    @staticmethod
    def get_model_info(model_path: str) -> dict[str, Any]:
        """Get metadata about a saved model."""
        path = Path(model_path)
        if not path.exists():
            return {"error": f"Model not found: {model_path}"}

        return {
            "path": str(path.absolute()),
            "size_bytes": path.stat().st_size,
            "framework": ModelLoader._guess_framework(path),
            "last_modified": path.stat().st_mtime,
        }

    @staticmethod
    def guess_framework(path: Path) -> str:
        """Guess the framework from file extension (public API)."""
        suffix = path.suffix.lower()
        name = path.name.lower()
        if suffix in (".pt", ".pth"):
            return "torch"
        elif suffix in (".joblib", ".pkl"):
            return "sklearn"
        elif suffix == ".onnx":
            return "onnx"
        elif suffix == ".gguf":
            return "gguf"
        elif suffix in (".h5", ".keras"):
            return "tensorflow"
        elif suffix in (".safetensors", ".bin"):
            for vl_keyword in ["llava", "blip", "clip", "vit", "detr", "yolo", "resnet"]:
                if vl_keyword in name:
                    return "vl"
            return "transformers"
        return "unknown"

    @staticmethod
    def get_gpu_info() -> dict[str, Any]:
        """Get detailed GPU hardware information."""
        info: dict[str, Any] = {
            "cuda_available": False,
            "cuda_devices": 0,
            "cuda_version": "",
            "metal_available": False,
            "xpu_available": False,
            "xpu_devices": 0,
            "opencl_available": False,
            "vulkan_available": False,
            "device_count": 0,
            "devices": [],
            "recommended_device": "cpu",
        }
        try:
            import torch
            info["cuda_available"] = torch.cuda.is_available()
            info["metal_available"] = torch.backends.mps.is_available()
            # Use crash-safe subprocess check — direct call can segfault
            info["xpu_available"] = _check_xpu_available()
            if info["cuda_available"]:
                info["cuda_devices"] = torch.cuda.device_count()
                info["cuda_version"] = torch.version.cuda or ""
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    info["devices"].append({
                        "index": i,
                        "name": props.name,
                        "total_memory_gb": round(props.total_memory / (1024**3), 2),
                        "compute_capability": f"{props.major}.{props.minor}",
                        "backend": "cuda",
                    })
            if info["xpu_available"]:
                info["xpu_devices"] = torch.xpu.device_count()
                for i in range(torch.xpu.device_count()):
                    try:
                        name = torch.xpu.get_device_name(i)
                        props = torch.xpu.get_device_properties(i)
                        info["devices"].append({
                            "index": i,
                            "name": name,
                            "total_memory_gb": round(props.total_memory / (1024**3), 2),
                            "backend": "xpu",
                        })
                    except Exception:
                        info["devices"].append({
                            "index": i,
                            "name": f"Intel XPU Device {i}",
                            "backend": "xpu",
                        })
            if info["metal_available"]:
                info["devices"].append({
                    "index": 0,
                    "name": "Apple Metal (MPS)",
                    "backend": "mps",
                })
        except ImportError:
            pass

        # OpenCL detection (independent of torch)
        try:
            import pyopencl
            platforms = pyopencl.get_platforms()
            info["opencl_available"] = len(platforms) > 0
            if info["opencl_available"]:
                for pi, plat in enumerate(platforms):
                    for di, dev in enumerate(plat.get_devices()):
                        info["devices"].append({
                            "index": di,
                            "name": dev.name,
                            "total_memory_gb": round(dev.global_mem_size / (1024**3), 2),
                            "backend": "opencl",
                            "platform": plat.name,
                        })
        except ImportError:
            pass

        # Vulkan detection (via torch backend)
        try:
            import torch
            info["vulkan_available"] = (
                hasattr(torch, "vulkan") and torch.vulkan.is_available()
            )
        except Exception:
            pass

        info["device_count"] = len(info["devices"])

        # Recommend best device (delegate to get_best_device)
        info["recommended_device"] = ModelLoader.get_best_device()

        return info

    @staticmethod
    def get_best_device() -> str:
        """Auto-detect the best available compute device.

        Priority: CUDA > Intel XPU > Apple Metal > CPU
        Returns a device string suitable for torch.device().
        """
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            if _check_xpu_available():
                return "xpu"
            if torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    @staticmethod
    def _guess_framework(path: Path) -> str:
        """Guess the framework from file extension (internal)."""
        return ModelLoader.guess_framework(path)


def timed_inference(fn):
    """Decorator to time inference calls."""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        if isinstance(result, InferenceResult):
            result.latency_ms = elapsed
        return result

    return wrapper
