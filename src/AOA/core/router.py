"""AOA Cross-Arm Router — DAG-based workflow orchestration across Arms."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime
from collections import deque
import uuid

from .arm_registry import ArmRegistry, BaseArm
from .event_bus import EventBus, AOEvent, AOEventType, EventPriority, get_event_bus


class StepStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    step_id: str
    arm_id: str
    capability: str
    payload: dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class WorkflowDAG:
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)

    def add_step(self, step: WorkflowStep):
        self.steps[step.step_id] = step
        self.edges[step.step_id] = list(step.depends_on)

    def get_ready_steps(self) -> List[WorkflowStep]:
        ready = []
        for step in self.steps.values():
            if step.status != StepStatus.PENDING:
                continue
            deps_satisfied = all(
                self.steps[dep].status == StepStatus.COMPLETED
                for dep in step.depends_on if dep in self.steps)
            if deps_satisfied:
                ready.append(step)
        return ready

    def get_topological_order(self) -> List[str]:
        in_degree = {sid: 0 for sid in self.steps}
        for sid, deps in self.edges.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[sid] += 1
        queue = deque([sid for sid, deg in in_degree.items() if deg == 0])
        order = []
        while queue:
            sid = queue.popleft()
            order.append(sid)
            for other_sid, deps in self.edges.items():
                if sid in deps:
                    in_degree[other_sid] -= 1
                    if in_degree[other_sid] == 0:
                        queue.append(other_sid)
        return order if len(order) == len(self.steps) else list(self.steps.keys())

    def is_complete(self) -> bool:
        return all(s.status in (StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED)
                   for s in self.steps.values())

    def get_status_summary(self) -> dict:
        counts = {s: 0 for s in StepStatus}
        for step in self.steps.values():
            counts[step.status] += 1
        return {
            "workflow_id": self.workflow_id, "name": self.name,
            "total_steps": len(self.steps), "completed": counts[StepStatus.COMPLETED],
            "failed": counts[StepStatus.FAILED], "pending": counts[StepStatus.PENDING],
            "running": counts[StepStatus.RUNNING], "skipped": counts[StepStatus.SKIPPED],
        }


class CrossArmRouter:
    def __init__(self, registry: ArmRegistry = None, bus: EventBus = None):
        self.registry = registry or ArmRegistry()
        self.bus = bus or get_event_bus()
        self._workflows: Dict[str, WorkflowDAG] = {}
        self._execution_history: List[dict] = []

    def route_task(self, arm_id: str, capability: str, payload: dict = None) -> dict:
        arm = self.registry.get_arm(arm_id)
        if arm is None:
            return {"status": "error", "error": f"Arm '{arm_id}' not found"}
        if not arm.is_initialized:
            arm.initialize()
        self.bus.publish(AOEvent(
            event_type=f"{arm_id}.execute.started",
            source_arm="aoa.router", target_arm=arm_id,
            payload={"capability": capability, "payload": payload or {}}))
        try:
            result = arm.execute(capability, payload or {})
            result["routed_by"] = "aoa.router"
            result["arm_id"] = arm_id
            self.bus.publish(AOEvent(
                event_type=f"{arm_id}.execute.complete", source_arm=arm_id,
                payload={"capability": capability, "result": result}))
            return result
        except Exception as e:
            error_result = {"status": "error", "error": str(e), "arm_id": arm_id}
            self.bus.publish(AOEvent(
                event_type=AOEventType.ARM_ERROR, source_arm=arm_id,
                payload={"capability": capability, "error": str(e)},
                priority=EventPriority.HIGH))
            return error_result

    def create_workflow(self, name: str, description: str = "") -> WorkflowDAG:
        workflow = WorkflowDAG(name=name, description=description)
        self._workflows[workflow.workflow_id] = workflow
        return workflow

    def execute_workflow(self, workflow_id: str) -> List[dict]:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return [{"error": f"Workflow '{workflow_id}' not found"}]
        results = []
        self.bus.publish(AOEvent(
            event_type=AOEventType.WORKFLOW_STARTED, source_arm="aoa.router",
            payload={"workflow_id": workflow_id, "name": workflow.name},
            correlation_id=workflow_id))
        while not workflow.is_complete():
            ready = workflow.get_ready_steps()
            if not ready:
                break
            for step in ready:
                step.status = StepStatus.RUNNING
                step.started_at = datetime.now().isoformat()
                result = self.route_task(step.arm_id, step.capability, step.payload)
                step.result = result
                step.completed_at = datetime.now().isoformat()
                if result.get("status") == "ok":
                    step.status = StepStatus.COMPLETED
                else:
                    step.status = StepStatus.FAILED
                    step.error = result.get("error", "Unknown error")
                results.append({
                    "step_id": step.step_id, "arm_id": step.arm_id,
                    "capability": step.capability, "status": step.status.value,
                    "result": result})
                self.bus.publish(AOEvent(
                    event_type=AOEventType.WORKFLOW_STEP_COMPLETE,
                    source_arm="aoa.router",
                    payload={"step_id": step.step_id, "status": step.status.value},
                    correlation_id=workflow_id))
        self.bus.publish(AOEvent(
            event_type=AOEventType.WORKFLOW_COMPLETE, source_arm="aoa.router",
            payload=workflow.get_status_summary(), correlation_id=workflow_id))
        return results

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDAG]:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[dict]:
        return [w.get_status_summary() for w in self._workflows.values()]

    def get_cross_arm_routes(self) -> List[dict]:
        routes = []
        arms = self.registry.list_arms()
        for source in arms:
            for target in arms:
                if source["arm_id"] != target["arm_id"]:
                    routes.append({
                        "source": source["arm_id"], "target": target["arm_id"],
                        "source_category": source["category"],
                        "target_category": target["category"]})
        return routes
