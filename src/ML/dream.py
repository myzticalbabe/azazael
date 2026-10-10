# coding: utf-8
"""DEPRECATED shim — ML.dream was renamed to ML.trace_consolidator (2026-10-10).

Reason: the old name shadowed CORE's DreamingModule (offline scenario replay /
synthesis engine); this module consolidates session traces into a durable
patterns digest. Same implementation, clearer name. Import from
ML.trace_consolidator.
"""
import warnings as _warnings

_warnings.warn("ML.dream is renamed to ML.trace_consolidator; import from there",
               FutureWarning, stacklevel=2)

from ML.trace_consolidator import (  # noqa: F401
    SessionSignature,
    consolidate,
    dream,
    load_report_verdicts,
    render_markdown,
    summarize_snapshot,
)

__all__ = [
    "SessionSignature",
    "consolidate",
    "dream",
    "load_report_verdicts",
    "render_markdown",
    "summarize_snapshot",
]
