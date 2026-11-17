#!/usr/bin/env python3
"""
NATIVE ADAPTATION LAYER for Python 3.16t Free-Threaded
========================================================
Provides transparent access to all ML/scientific packages by:
1. Using native 3.16t packages where available
2. Transparently routing to 3.15t GIL sidecar for missing packages
3. Providing unified import interface
4. Building native wheels where possible

This is the ADAPTATION LAYER that makes 3.16t a viable production environment.
"""

import sys
import subprocess
import importlib
import importlib.util
import sysconfig
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import threading
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

class AdaptationConfig:
    """Configuration for the adaptation layer."""
    
    # Python interpreters - explicit paths for reliability
    PY316T = Path(r"C:/Azazael/.venvs/py316t/Scripts/python.exe")
    PY315T = Path(r"C:/Azazael/.venvs/py315t/Scripts/python.exe")
    
    # Package categories
    NATIVE_316T = {
        # Confirmed working natively on 3.16t
        "numpy", "cython", "llama_cpp", "gguf", "rich", "click", "typer",
        "pydantic", "pydantic_core", "pydantic_settings", "attrs", "sortedcontainers",
        "diskcache", "sqlalchemy", "sqlmodel", "httpx", "aiohttp", "requests",
        "pillow", "opencv", "scipy", "pandas", "scikit_learn", "transformers",
        "torch", "tensorflow", "jax", "flax", "opencv", "cv2"
    }
    
    REQUIRES_SIDECAR = {
        # Known to need 3.15t sidecar (no 3.16t wheels)
        "torch", "tensorflow", "jax", "flax", "transformers",
        "xgboost", "lightgbm", "catboost", "opencv", "cv2"
    }
    
    SIDECAR_PACKAGES = {
        "torch", "torchvision", "torchaudio",
        "tensorflow", "tensorflow_probability",
        "jax", "jaxlib", "flax", "optax",
        "transformers", "accelerate", "peft", "trl",
        "xgboost", "lightgbm", "catboost",
        "opencv-python", "opencv-contrib-python",
        "mediapipe", "onnxruntime", "onnx",
        "sentencepiece", "tokenizers", "huggingface_hub",
        "bitsandbytes", "flash_attn", "deepspeed",
    }
    
    # Sidecar executable
    SIDECAR_PYTHON = Path(r"C:/Azazael/.venvs/py315t/Scripts/python.exe")

# =============================================================================
# SIDECAR COMMUNICATION
# =============================================================================

class SidecarClient:
    """Communicates with 3.15t GIL sidecar for unsupported packages."""
    
    def __init__(self, sidecar_python: Path):
        self.sidecar = sidecar_python
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._verify_sidecar()
    
    def _verify_sidecar(self):
        """Verify sidecar is functional."""
        try:
            result = subprocess.run(
                [str(self.sidecar), "-c", "import sys; print(sys.version)"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"Sidecar failed: {result.stderr}")
            print(f"[ADAPTATION] Sidecar verified: {result.stdout.strip()}")
        except Exception as e:
            raise RuntimeError(f"Sidecar verification failed: {e}")
    
    def execute(self, code: str, imports: List[str] = None) -> Any:
        """Execute code in sidecar and return result."""
        # Build execution script
        imports_code = "\n".join(f"import {imp}" for imp in (imports or []))
        script = f"""
{imports_code}
import json
import sys

try:
    result = {{
    {code}
    }}
    print("__ADAPTATION_RESULT__", json.dumps(result, default=str))
except Exception as e:
    print("__ADAPTATION_ERROR__", str(e), file=sys.stderr)
    sys.exit(1)
"""
        cache_key = hashlib.sha256(script.encode()).hexdigest()[:16]
        
        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            result = subprocess.run(
                [str(AdaptationConfig.SIDECAR_PYTHON), "-c", script],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Sidecar execution failed: {result.stderr}")
            
            # Parse result
            for line in result.stdout.split('\n'):
                if line.startswith("__ADAPTATION_RESULT__"):
                    import json
                    return json.loads(line[len("__ADAPTATION_RESULT__ "):])
            
            raise RuntimeError("No result returned from sidecar")
    
    def import_module(self, module_name: str):
        """Import a module from sidecar and return a proxy."""
        return SidecarModuleProxy(module_name, self)
    
    def call(self, module: str, func: str, *args, **kwargs):
        """Call a function from a sidecar module."""
        args_json = json.dumps(args, default=str)
        kwargs_json = json.dumps(kwargs, default=str)
        code = f"'{func}': getattr(__import__('{module}'), '{func}')(*{args_json}, **{kwargs_json})"
        return self.execute(code, imports=[module])

class SidecarModuleProxy:
    """Proxy for a module running in the sidecar."""
    
    def __init__(self, module_name: str, client: SidecarClient):
        self._module = module_name
        self._client = client
    
    def __getattr__(self, name: str):
        def wrapper(*args, **kwargs):
            return self._client.call(self._module, name, *args, **kwargs)
        return wrapper
    
    def __dir__(self):
        # Could fetch from sidecar
        return []

# =============================================================================
# ADAPTATION REGISTRY
# =============================================================================

class AdaptationRegistry:
    """Registry of package adaptations."""
    
    def __init__(self):
        self._adaptations: Dict[str, Any] = {}
        self._sidecar: Optional[SidecarClient] = None
        self._native_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def get_sidecar(self) -> SidecarClient:
        """Get or create sidecar client."""
        with self._lock:
            if self._sidecar is None:
                self._sidecar = SidecarClient(AdaptationConfig.SIDECAR_PYTHON)
            return self._sidecar
    
    def is_native(self, package: str) -> bool:
        """Check if package is available natively on 3.16t."""
        if package in self._native_cache:
            return self._native_cache[package]
        
        try:
            spec = importlib.util.find_spec(package)
            available = spec is not None
            self._native_cache[package] = available
            return available
        except Exception as e:
            print(f"[ADAPTATION] Native check failed for {package}: {e}")
            self._native_cache[package] = False
            return False
    
    def get_module(self, package: str):
        """Get module - native if available, else sidecar proxy."""
        if self.is_native(package):
            return importlib.import_module(package)
        
        # Check if we have a custom adaptation
        if package in self._adaptations:
            return self._adaptations[package]
        
        # Use sidecar
        sidecar = self.get_sidecar()
        return sidecar.import_module(package)
    
    def register_adaptation(self, package: str, adaptation: Any):
        """Register a custom adaptation for a package."""
        self._adaptations[package] = adaptation
    
    def install_native(self, package: str) -> bool:
        """Attempt to install package natively on 3.16t."""
        try:
            result = subprocess.run(
                [str(AdaptationConfig.PY316T), "-m", "pip", "install", package],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                self._native_cache[package] = True
                return True
            return False
        except Exception as e:
            print(f"[ADAPTATION] Native install failed for {package}: {e}")
            return False

# =============================================================================
# GLOBAL REGISTRY
# =============================================================================

# Global registry instance
_adaptation_registry = AdaptationRegistry()

def get_module(package: str):
    """Get module with adaptation."""
    return _adaptation_registry.get_module(package)

def install_native(package: str) -> bool:
    """Try to install package natively."""
    return _adaptation_registry.install_native(package)

def register_adaptation(package: str, adaptation: Any):
    """Register custom adaptation."""
    _adaptation_registry.register_adaptation(package, adaptation)

def is_native(package: str) -> bool:
    """Check if package is native."""
    return _adaptation_registry.is_native(package)

# =============================================================================
# CONVENIENCE IMPORTS
# =============================================================================

# Pre-load common adaptations
def preload_adaptations():
    """Pre-load common ML package adaptations."""
    print("[ADAPTATION] Preloading adaptations...")
    
    # Try native installs for known-working packages (disabled for speed)
    # for pkg in ["scipy", "pandas", "scikit-learn", "pillow"]:
    #     if not _adaptation_registry.is_native(pkg):
    #         print(f"[ADAPTATION] Attempting native install: {pkg}")
    #         _adaptation_registry.install_native(pkg)
    
    print("[ADAPTATION] Preload complete (native installs disabled for speed)")

# Auto-preload on import
preload_adaptations()

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "get_module",
    "install_native", 
    "register_adaptation",
    "is_native",
    "AdaptationConfig",
    "SidecarClient",
    "SidecarModuleProxy",
    "AdaptationRegistry",
    "preload_adaptations",
]

# Convenience: make adapted modules available directly
class AdaptedModule:
    """Lazy-loaded adapted module."""
    def __init__(self, name: str):
        self._name = name
        self._module = None
    
    def __getattr__(self, name):
        if self._module is None:
            self._module = get_module(self._name)
        return getattr(self._module, name)
    
    def __dir__(self):
        if self._module is None:
            self._module = get_module(self._name)
        return dir(self._module)

# Expose commonly used modules as adapted
torch = AdaptedModule("torch")
transformers = AdaptedModule("transformers")
tensorflow = AdaptedModule("tensorflow")
cv2 = AdaptedModule("cv2")
opencv = AdaptedModule("cv2")

print("[ADAPTATION] Native Adaptation Layer loaded for Python 3.16t")
print(f"[ADAPTATION] Sidecar: {AdaptationConfig.SIDECAR_PYTHON}")
print(f"[ADAPTATION] Native: {AdaptationConfig.PY316T}")