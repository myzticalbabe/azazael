"""CORE — Azazael Core Package

Core infrastructure: DirectMemory, AuditTrail, InferencePool, FreeThreadPool.

Export:
    DirectMemory
    InferencePool, InferenceTask
    FreeThreadPool
    audit_session_start, verify_on_startup, close_session, verify_chain
    EVENT_VOCAB, EVENT_VOCAB_REVERSE
"""

from CORE.direct_memory import DirectMemory, get_dm, record, end
from CORE.freethreading import FreeThreadPool

# Backward-compat alias: formerly CORE/logging.py (renamed to _logging_shim.py
# so it no longer shadows stdlib 'logging' during package-tree script runs).
import CORE._logging_shim as logging  # noqa: E402  (package attribute, not stdlib)

from CORE.audit_trail import (
    verify_on_startup,
    audit_session_start,
    close_session,
    verify_chain,
    verify_head_hash,
    get_head_hash,
    audit_file_read,
    audit_file_edit,
    audit_file_create,
    audit_file_delete,
    audit_skill_loaded,
    audit_inference_spawn,
    audit_test_run,
    audit_code_review,
    audit_scan_run,
    audit_gate_passed,
    audit_sentinel_run,
    audit_sync_run,
    audit_tooling_verify,
    audit_error_occurrence,
    audit_expect_action,
    read_audit_lines,
    get_anchored_files,
    verify_completeness,
)
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

# EVENT_VOCAB / EVENT_VOCAB_REVERSE — not yet defined in audit_trail.py.
# Fall back to empty dicts to avoid blocking all CORE imports.
_EVENT_VOCAB: dict | None = None
_EVENT_VOCAB_REVERSE: dict | None = None
try:
    from CORE import audit_trail as _audit_trail_mod

    _EVENT_VOCAB = getattr(_audit_trail_mod, "EVENT_VOCAB", None)
    _EVENT_VOCAB_REVERSE = getattr(_audit_trail_mod, "EVENT_VOCAB_REVERSE", None)
    if _EVENT_VOCAB is None or _EVENT_VOCAB_REVERSE is None:
        raise ImportError("EVENT_VOCAB pair missing in CORE.audit_trail")
except ImportError as exc:
    note_failure("__init__:L51", exc)
    _EVENT_VOCAB = None
    _EVENT_VOCAB_REVERSE = None
EVENT_VOCAB: dict = _EVENT_VOCAB if _EVENT_VOCAB is not None else {}
EVENT_VOCAB_REVERSE: dict = _EVENT_VOCAB_REVERSE if _EVENT_VOCAB_REVERSE is not None else {}

# InferencePool is optional (requires CORE.freethreading)
try:
    from CORE.inference_pool import InferencePool
    _has_inference_pool = True
except ImportError as exc:
    note_failure("__init__:L59", exc)
    _has_inference_pool = False
    InferencePool = None  # type: ignore

__all__ = [
    "DirectMemory",
    "get_dm",
    "record",
    "end",
    "FreeThreadPool",
    "InferencePool",
    "EVENT_VOCAB",
    "EVENT_VOCAB_REVERSE",
    "verify_on_startup",
    "audit_session_start",
    "close_session",
    "verify_chain",
    "verify_head_hash",
    "get_head_hash",
    "audit_file_read",
    "audit_file_edit",
    "audit_file_create",
    "audit_file_delete",
    "audit_skill_loaded",
    "audit_inference_spawn",
    "audit_test_run",
    "audit_code_review",
    "audit_scan_run",
    "audit_gate_passed",
    "audit_sentinel_run",
    "audit_sync_run",
    "audit_tooling_verify",
    "audit_error_occurrence",
    "audit_expect_action",
    "read_audit_lines",
    "get_anchored_files",
    "verify_completeness",
    "_has_inference_pool",
]
