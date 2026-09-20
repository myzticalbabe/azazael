# coding: utf-8
"""Optional torch bridge.

torch is neither installed nor importable on this box (Windows: no torch in
3.14t; WSL Ubuntu: CUDA build without libcublas). Everything here is lazy:
importing this module never imports torch. Callers gate on
:func:`torch_available` and otherwise receive an informative error naming
the exact blocker instead of a bare ``ImportError``.
"""

from __future__ import annotations

from typing import Any

_TORCH_ERROR: str | None = None


def torch_available() -> bool:
    """True when torch imports and reports a working backend."""
    global _TORCH_ERROR
    try:
        import torch

        _ = torch.zeros(1)
        return True
    except Exception as exc:  # noqa: BLE001 - the message IS the API
        _TORCH_ERROR = f"{type(exc).__name__}: {exc}"
        return False


def require_torch() -> Any:
    """Import torch or raise with the recorded blocker and remediation."""
    try:
        import torch

        torch.zeros(1)
        return torch
    except Exception as exc:  # noqa: BLE001
        hint = _TORCH_ERROR or f"{type(exc).__name__}: {exc}"
        raise ImportError(
            "torch is unavailable on this box "
            f"({hint}). Install a CPU-only wheel "
            "(pip install torch --index-url https://download.pytorch.org/whl/cpu) "
            "or run inside an image with CUDA libraries present."
        ) from exc


def to_torch(array: Any) -> Any:
    """Convert a numpy array to a torch tensor (requires torch)."""
    torch = require_torch()
    import numpy as np

    return torch.as_tensor(np.asarray(array))


def to_numpy(tensor: Any) -> Any:
    """Convert a torch tensor to numpy (requires torch)."""
    require_torch()
    return tensor.detach().cpu().numpy()
