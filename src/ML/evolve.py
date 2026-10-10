# coding: utf-8
"""DEPRECATED shim — ML.evolve was renamed to ML.nsga_tuner (2026-10-10).

Reason: the old name shadowed CORE's evolution mechanics (population-based
worm optimization); this module is the NSGA-II hyperparameter tuner for EffGen
agents. Same implementation, clearer name. Import from ML.nsga_tuner.
"""
import warnings as _warnings

_warnings.warn("ML.evolve is renamed to ML.nsga_tuner; import from there",
               FutureWarning, stacklevel=2)

from ML.nsga_tuner import (  # noqa: F401
    CALCULATOR_TASKS,
    TIME_BUDGET_S,
    AgentGenome,
    NSGA2,
    RunAgent,
    Task,
    decode,
    live_run_agent,
    make_objectives,
    tune,
)

__all__ = [
    "CALCULATOR_TASKS",
    "TIME_BUDGET_S",
    "AgentGenome",
    "NSGA2",
    "RunAgent",
    "Task",
    "decode",
    "live_run_agent",
    "make_objectives",
    "tune",
]
