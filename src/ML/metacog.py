# coding: utf-8
"""DEPRECATED shim — ML.metacog was renamed to ML.step_monitor (2026-10-10).

Reason: the old name shadowed CORE's MetaCognitionWorm (the full reflection /
error-learning engine); this module is the online step-stream stall/loop
monitor. Same implementation, clearer name. Import from ML.step_monitor.
"""
import warnings as _warnings

_warnings.warn("ML.metacog is renamed to ML.step_monitor; import from there",
               FutureWarning, stacklevel=2)

from ML.step_monitor import StepEvent, StepMonitor, Verdict  # noqa: F401

__all__ = ["StepEvent", "StepMonitor", "Verdict"]
