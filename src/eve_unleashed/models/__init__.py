"""
Eve Unleashed — Model Architectures
====================================
Custom PyTorch model definitions for Eve Unleashed.
"""

from .qwen35_ssm import (
    Qwen35ForCausalLM,
    Qwen35SSMConfig,
    create_qwen35_model,
)
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

__all__ = [
    "Qwen35ForCausalLM",
    "Qwen35SSMConfig",
    "create_qwen35_model",
]
