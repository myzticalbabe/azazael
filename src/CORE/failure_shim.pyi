# failure_shim.pyi — Type stubs for failure_shim module
# This file provides @overload signatures for type checkers (mypy, basedpyright, pyright).
# The actual implementation is in failure_shim.py

from typing import Optional, Dict, Any, List, overload
from BaseException import BaseException

from .failure_shim import FailureRecord

@overload
def note_failure(where: str, exc: Optional[BaseException] = None) -> None:
    """Legacy signature: note_failure(where, exc=None). Never raises."""
    ...

@overload
def note_failure(where: str, exc: Optional[BaseException] = None,
                 *, context: Optional[Dict[str, Any]] = None,
                 severity: str = "medium",
                 tags: Optional[List[str]] = None) -> None:
    """Enhanced signature with structured metadata (keyword-only).
    
    Args:
        where: Location identifier (e.g., "module:function" or "file:line")
        exc: Exception that was caught and swallowed, or None
        context: Optional dict of contextual data for debugging
        severity: One of "low", "medium", "high", "critical"
        tags: Optional list of categorization tags
    """
    ...

@overload
def note_failure(record: FailureRecord) -> None:
    """Structured record signature: note_failure(FailureRecord(...)).
    
    Args:
        record: FailureRecord with where, exc, context, severity, tags
    """
    ...

def note_failure(where: str, exc: Optional[BaseException] = None,
                 *, context: Optional[Dict[str, Any]] = None,
                 severity: str = "medium",
                 tags: Optional[List[str]] = None) -> None: ...

def note_failure_v2(record: FailureRecord) -> None: ...

# Re-exported from failure_ledger
def failure_notes() -> Dict[str, int]: ...
def reset_notes() -> None: ...

class FailureRecord:
    where: str
    exc: Optional[BaseException]
    context: Dict[str, Any]
    severity: str
    tags: List[str]
    timestamp: str
    
    def __init__(self, where: str, exc: Optional[BaseException] = None,
                 context: Optional[Dict[str, Any]] = None,
                 severity: str = "medium",
                 tags: Optional[List[str]] = None,
                 timestamp: Optional[str] = None) -> None: ...
    def to_ledger_key(self) -> str: ...

failure_notes: Dict[str, int]
reset_notes: Any
FailureRecord: Any
note_failure_v2: Any