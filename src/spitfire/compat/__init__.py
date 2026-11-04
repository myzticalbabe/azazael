# coding: utf-8
"""SpitFire compatibility layer — GIL-sidecar pattern.

Exports:
  - dispatch: main entry point that detects OS and routes to implementation
  - detect_target: OS detection function
  - Target, TargetInfo: target enumeration and metadata
"""

from .launcher import (
    Target,
    TargetInfo,
    TARGET_MATRIX,
    detect_target,
    dispatch,
    get_target_info,
)

__all__ = [
    "Target",
    "TargetInfo",
    "TARGET_MATRIX",
    "detect_target",
    "dispatch",
    "get_target_info",
]