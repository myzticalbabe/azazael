"""AOA — Armorie-of-Anubis Umbrella Orchestrator.

Master orchestrator for the Quartet Architecture and all neural agent systems.
Registers and coordinates Azazael, Libra, CODEX, EveUnleashed, and support Arms
through a unified event bus, session manager, and cross-arm routing engine.

Quick Start:
    from aoa.core import ArmRegistry, EventBus, SessionManager, CrossArmRouter

    registry = ArmRegistry()
    registry.initialize_all()
    print(registry.get_status_report())
"""

from .core import (
    ArmRegistry, BaseArm, register_arm,
    EventBus, AOEvent, AOEventType, EventPipeline, get_event_bus,
    SessionManager, Milestone, SessionState, get_session_manager,
    CrossArmRouter, WorkflowDAG,
)

__version__ = "1.0.0"
__all__ = [
    "ArmRegistry", "BaseArm", "register_arm",
    "EventBus", "AOEvent", "AOEventType", "EventPipeline", "get_event_bus",
    "SessionManager", "Milestone", "SessionState", "get_session_manager",
    "CrossArmRouter", "WorkflowDAG",
]
