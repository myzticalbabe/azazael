"""AOA Arm Registry — Registration and discovery of all neural architecture Arms.

Analogous to Azazael's worm_registry.py, this module provides the central
registry for all sub-system Arms (Azazael, Libra, CODEX, EveUnleashed, etc.).

Architecture:
    BaseArm (ABC) — Standard interface all Arms must implement
    ArmRegistry   — Central registry with discovery and lifecycle management
    register_arm  — Decorator for declarative Arm registration
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from pathlib import Path


@dataclass
class ArmCapability:
    """Describes a single capability an Arm exposes."""
    name: str
    description: str
    input_schema: Optional[dict] = None
    output_schema: Optional[dict] = None
    category: str = "general"


@dataclass
class ArmMetadata:
    """Metadata for a registered Arm."""
    arm_id: str
    name: str
    version: str
    description: str
    category: str = "quartet"  # quartet, support, infrastructure
    priority: int = 5          # 1-10, higher = more critical
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[ArmCapability] = field(default_factory=list)
    status: str = "uninitialized"
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseArm(ABC):
    """Abstract base class for all AOA Arms.
    
    Every sub-system (Azazael, Libra, CODEX, EveUnleashed, etc.) must
    implement this interface to participate in AOA orchestration.
    
    Required methods:
        initialize()    — Boot the sub-system, return success/failure
        execute()       — Run a capability, return results
        get_capabilities() — Report available capabilities
        shutdown()      — Graceful teardown
    """

    def __init__(self):
        self._initialized = False
        self._metadata: Optional[ArmMetadata] = None

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the Arm. Return True on success."""
        ...

    @abstractmethod
    def execute(self, capability: str, payload: dict = None) -> dict:
        """Execute a named capability with optional payload.
        
        Returns: {"status": "ok"|"error", "data": ..., "arm_id": str}
        """
        ...

    @abstractmethod
    def get_capabilities(self) -> List[ArmCapability]:
        """Return list of capabilities this Arm exposes."""
        ...

    @abstractmethod
    def shutdown(self) -> bool:
        """Graceful shutdown. Return True on success."""
        ...

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    @property
    def metadata(self) -> Optional[ArmMetadata]:
        return self._metadata

    def get_status(self) -> dict:
        """Return current status of this Arm."""
        return {
            "arm_id": self._metadata.arm_id if self._metadata else "unknown",
            "initialized": self._initialized,
            "capabilities_count": len(self.get_capabilities()),
        }


# Global Arm Registry
ARM_REGISTRY: Dict[str, BaseArm] = {}


def register_arm(
    arm_id: str,
    name: str,
    version: str = "1.0.0",
    description: str = "",
    category: str = "quartet",
    priority: int = 5,
    dependencies: List[str] = None,
):
    """Decorator to register an Arm class in the ARM_REGISTRY.
    
    Usage:
        @register_arm("azazael", "Azazael Neural Mesh", priority=10)
        class AzazaelArm(BaseArm):
            ...
    """
    def decorator(cls):
        if not issubclass(cls, BaseArm):
            raise TypeError(
                f"{cls.__name__} must subclass BaseArm to use @register_arm"
            )
        instance = cls()
        instance._metadata = ArmMetadata(
            arm_id=arm_id,
            name=name,
            version=version,
            description=description,
            category=category,
            priority=priority,
            dependencies=dependencies or [],
        )
        ARM_REGISTRY[arm_id] = instance
        return cls
    return decorator


class ArmRegistry:
    """Central registry for all AOA Arms.
    
    Provides discovery, lifecycle management, and status reporting
    across all registered sub-systems.
    """

    def __init__(self):
        self._arms: Dict[str, BaseArm] = dict(ARM_REGISTRY)
        self._initialized_arms: set = set()

    def register(self, arm_id: str, arm: BaseArm):
        """Register an Arm instance directly."""
        if not isinstance(arm, BaseArm):
            raise TypeError(f"{type(arm).__name__} must be a BaseArm")
        self._arms[arm_id] = arm

    def get_arm(self, arm_id: str) -> Optional[BaseArm]:
        """Get an Arm by ID."""
        return self._arms.get(arm_id)

    def list_arms(self, category: str = None) -> List[dict]:
        """List all registered Arms with metadata."""
        result = []
        for arm_id, arm in self._arms.items():
            meta = arm.metadata
            if meta is None:
                continue
            if category and meta.category != category:
                continue
            result.append({
                "arm_id": meta.arm_id,
                "name": meta.name,
                "version": meta.version,
                "category": meta.category,
                "priority": meta.priority,
                "status": meta.status,
                "initialized": arm.is_initialized,
                "capabilities": len(arm.get_capabilities()),
                "dependencies": meta.dependencies,
            })
        return sorted(result, key=lambda x: (-x["priority"], x["name"]))

    def get_categories(self) -> List[str]:
        """Get all unique Arm categories."""
        cats = set()
        for arm in self._arms.values():
            if arm.metadata:
                cats.add(arm.metadata.category)
        return sorted(cats)

    def initialize_all(self, category: str = None) -> Dict[str, bool]:
        """Initialize all Arms (optionally filtered by category).
        
        Returns: {arm_id: success}
        """
        results = {}
        for arm_id, arm in self._arms.items():
            if arm.metadata is None:
                continue
            if category and arm.metadata.category != category:
                continue
            try:
                success = arm.initialize()
                results[arm_id] = success
                if success:
                    self._initialized_arms.add(arm_id)
                    arm.metadata.status = "initialized"
                else:
                    arm.metadata.status = "init_failed"
            except Exception as e:
                results[arm_id] = False
                if arm.metadata:
                    arm.metadata.status = f"error: {e}"
        return results

    def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all initialized Arms."""
        results = {}
        for arm_id in self._initialized_arms.copy():
            arm = self._arms.get(arm_id)
            if arm:
                try:
                    success = arm.shutdown()
                    results[arm_id] = success
                    if arm.metadata:
                        arm.metadata.status = "shutdown"
                except Exception as e:
                    results[arm_id] = False
                self._initialized_arms.discard(arm_id)
        return results

    def get_status_report(self) -> dict:
        """Generate a full status report of all Arms."""
        arms_list = self.list_arms()
        return {
            "total_arms": len(self._arms),
            "initialized": len(self._initialized_arms),
            "categories": self.get_categories(),
            "arms": arms_list,
            "timestamp": datetime.now().isoformat(),
        }

    @property
    def arms(self) -> Dict[str, BaseArm]:
        return self._arms
