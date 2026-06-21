# coding: utf-8
"""


__all__ = [
    "BUILTIN_TEMPLATES",
    "ConditionalRouter",
    "DependencyGraph",
    "StepStatus",
    "Workflow",
    "WorkflowEngine",
    "WorkflowResult",
    "WorkflowStep",
    "WorkflowTemplate",
    "get_workflow_engine",
]

CORE/workflow.py — Workflow Engine for Azazael

Provides:
- WorkflowTemplate: reusable workflow blueprints with parameterized steps
- WorkflowDSL: simple JSON/YAML-based workflow definition language
- ConditionalRouter: route execution based on previous step results
- DependencyGraph: resolve worm execution order from dependencies

Usage:
    from CORE.workflow import WorkflowEngine, WorkflowTemplate, WorkflowDSL

    # Define a workflow from a template
    engine = WorkflowEngine()
    wf = engine.create_from_template("daily_training", {
        "n_episodes": 100,
        "source": "SystemZ",
    })
    result = engine.execute(wf)
"""

import time
import threading
from datetime import datetime, timezone
from typing import Any
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed  # TimeoutError is a builtin — no import needed

# -- Lazy Config (thread-safe) ------------------------------------
_cfg = None
_cfg_lock = threading.Lock()


def _get_config():
    """Lazy config — double-checked locking for Python 3.14t free-threading."""
    global _cfg
    if _cfg is None:
        with _cfg_lock:
            if _cfg is None:
                try:
                    from CORE.config import get_config
                    _cfg = get_config()
                except ImportError:
                    _cfg = False
    return _cfg if _cfg else None


# =======================================================================
# DATA TYPES
# =======================================================================

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    id: str
    action: str                      # e.g., "execute_worm", "run_pipeline", "condition"
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)  # Step IDs this depends on
    condition: (str | None) = None  # Optional condition expression (DSL)
    timeout: int = 300
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: (str | None) = None
    started_at: (str | None) = None
    completed_at: (str | None) = None
    duration_ms: float = 0.0


@dataclass
class Workflow:
    """A complete executable workflow."""
    id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)  # Template parameter overrides
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: list[str] = field(default_factory=list)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""
    workflow_id: str
    workflow_name: str
    started_at: str
    completed_at: str
    duration_ms: float
    step_results: dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0
    errors: list[str] = field(default_factory=list)
    outputs: dict[str, Any] = field(default_factory=dict)
    success: bool = True


# =======================================================================
# WORKFLOW TEMPLATES
# =======================================================================

@dataclass
class WorkflowTemplate:
    """A reusable workflow blueprint."""
    name: str
    description: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)  # {param_name: default_value}
    tags: list[str] = field(default_factory=list)


# Built-in templates
BUILTIN_TEMPLATES = {
    "daily_training": WorkflowTemplate(
        name="daily_training",
        description="Daily ML training pipeline: extract -> engineer -> train -> version",
        parameters={
            "n_episodes": 50,
            "source": None,
            "data_limit": 200,
            "register_model": True,
        },
        steps=[
            {
                "id": "extract",
                "action": "run_pipeline",
                "params": {
                    "pipeline": "DataPipelineWorm",
                    "method": "extract_from_memory",
                    "args": {"limit": "${data_limit}", "source": "${source}"},
                },
            },
            {
                "id": "engineer",
                "action": "execute_worm",
                "params": {
                    "worm": "FeatureEngineer",
                    "method": "extract_worm_features",
                    "args": {"records": "${extract.result}"},
                },
                "depends_on": ["extract"],
            },
            {
                "id": "train",
                "action": "execute_worm",
                "params": {
                    "worm": "RLTrainLoop",
                    "method": "train_from_memory",
                    "args": {
                        "n_episodes": "${n_episodes}",
                        "source": "${source}",
                    },
                },
                "depends_on": ["engineer"],
                "condition": "engineer.success == true",
            },
            {
                "id": "register",
                "action": "execute_worm",
                "params": {
                    "worm": "ModelVersioner",
                    "method": "register_model",
                    "args": {
                        "name": "daily_training",
                        "version": "auto",
                        "metrics": {"avg_reward": "${train.result.avg_reward}"},
                    },
                },
                "depends_on": ["train"],
                "condition": "${register_model} == true",
            },
        ],
    ),
    "system_health_check": WorkflowTemplate(
        name="system_health_check",
        description="Run system health check: monitor -> diagnose -> report",
        parameters={
            "parallel": False,
        },
        steps=[
            {
                "id": "monitor",
                "action": "execute_nature",
                "params": {"nature": "monitor", "parallel": False},
            },
            {
                "id": "diagnose",
                "action": "execute_nature",
                "params": {"nature": "diagnostic", "parallel": False},
                "depends_on": ["monitor"],
                "condition": "monitor.result.failure_count > 0",
            },
            {
                "id": "report",
                "action": "execute_worm",
                "params": {
                    "worm": "DashboardGen",
                    "method": "execute",
                },
                "depends_on": ["monitor", "diagnose"],
            },
        ],
    ),
    "security_audit": WorkflowTemplate(
        name="security_audit",
        description="Security audit: scan -> analyze -> report",
        steps=[
            {
                "id": "scan",
                "action": "execute_nature",
                "params": {"nature": "security", "parallel": True},
            },
            {
                "id": "analyze",
                "action": "execute_nature",
                "params": {"nature": "analysis", "parallel": False},
                "depends_on": ["scan"],
                "condition": "scan.result.success_count > 0",
            },
        ],
    ),
}


# =======================================================================
# CONDITIONAL ROUTER
# =======================================================================

class ConditionalRouter:
    """Evaluates conditions to determine if a step should execute.

    Supports simple expression syntax:
    - "step_id.success == true"
    - "step_id.result.value > 10"
    - "${param} == 'value'"
    - "engineer.success == true AND extract.result.count > 0"
    """

    @staticmethod
    def evaluate(condition: str, step_results: dict[str, Any],
                 params: dict[str, Any]) -> bool:
        """Evaluate a condition expression against step results and params.

        Args:
            condition: Condition expression string
            step_results: dict of {step_id: {success, result, ...}}
            params: Workflow parameter overrides

        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return True

        expr = condition.strip()

        # Replace ${param} references
        for key, val in params.items():
            placeholder = "${" + key + "}"
            if placeholder in expr:
                expr = expr.replace(placeholder, str(val).lower())

        # Handle AND/OR operators
        if " AND " in expr:
            parts = expr.split(" AND ")
            return all(ConditionalRouter._evaluate_simple(p.strip(), step_results) for p in parts)
        if " OR " in expr:
            parts = expr.split(" OR ")
            return any(ConditionalRouter._evaluate_simple(p.strip(), step_results) for p in parts)

        return ConditionalRouter._evaluate_simple(expr, step_results)

    @staticmethod
    def _evaluate_simple(expr: str, step_results: dict[str, Any]) -> bool:
        """Evaluate a simple condition like 'step_id.success == true' or 'false == true'."""
        # -- Determine comparison operator --
        op_str = None
        if " == " in expr:
            op_str = "=="
        elif " > " in expr:
            op_str = ">"
        elif " < " in expr:
            op_str = "<"
        else:
            return True

        left, right = expr.split(f" {op_str} ", 1)
        left = left.strip()
        right = right.strip().strip("'\"")

        # -- Literal comparison (no dot-path) — e.g. "false == true" --
        if "." not in left:
            left_lower = left.lower()
            right_lower = right.lower()
            if op_str == "==":
                if left_lower in ("true", "false"):
                    return (left_lower == "true") == (right_lower == "true")
                try:
                    return float(left) == float(right)
                except ValueError:
                    return left_lower == right_lower
            elif op_str == ">":
                try:
                    return float(left) > float(right)
                except ValueError:
                    return left_lower > right_lower
            elif op_str == "<":
                try:
                    return float(left) < float(right)
                except ValueError:
                    return left_lower < right_lower

        # -- Dot-path comparison — e.g. "step_id.field == value" --
        parts = left.split(".")
        if len(parts) < 2:
            return True

        step_id = parts[0]
        field_path = parts[1:]
        step = step_results.get(step_id, {})

        # Navigate the field path
        value = step
        for p in field_path:
            if isinstance(value, dict):
                value = value.get(p, None if op_str == "==" else 0)
            else:
                value = None if op_str == "==" else 0
                break

        if op_str == "==":
            if value is None:
                return right.lower() == "none"
            if isinstance(value, bool):
                return value == (right.lower() == "true")
            if isinstance(value, (int, float)):
                try:
                    return value == float(right)
                except ValueError:
                    return str(value) == right
            return str(value).lower() == right.lower()

        elif op_str == ">":
            try:
                return float(value) > float(right)
            except (ValueError, TypeError):
                return False

        elif op_str == "<":
            try:
                return float(value) < float(right)
            except (ValueError, TypeError):
                return False

        return True


# =======================================================================
# DEPENDENCY GRAPH
# =======================================================================

class DependencyGraph:
    """Resolves worm execution order from dependency declarations.

    Supports:
    - Parallel execution of independent steps
    - Sequential execution of dependent steps
    - Cycle detection
    - Topological sort
    """

    def __init__(self):
        self._graph: dict[str, list[str]] = {}  # {step_id: [depends_on_ids]}

    def build(self, steps: list[WorkflowStep]):
        """Build dependency graph from workflow steps."""
        self._graph = {}
        for step in steps:
            self._graph[step.id] = list(step.depends_on)

    def get_execution_order(self) -> list[list[str]]:
        """Get execution order as layers of parallel steps.

        Returns:
            list of layers, where each layer is a list of step IDs that can run in parallel.
        """
        # Compute in-degrees
        in_degree: dict[str, int] = {}
        for step_id, deps in self._graph.items():
            in_degree[step_id] = len(deps)
            for dep in deps:
                if dep not in in_degree:
                    in_degree[dep] = 0

        # Topological sort with layers
        layers = []
        remaining = set(self._graph.keys())
        unresolved = set()

        while remaining:
            # Find steps with no remaining dependencies
            ready = [
                sid for sid in remaining
                if in_degree.get(sid, 0) == 0
            ]
            if not ready:
                # Missing dependencies — check if deps exist in graph
                missing = set()
                for sid in remaining:
                    for dep in self._graph.get(sid, []):
                        if dep not in self._graph:
                            missing.add(dep)
                if missing:
                    # Dependencies that don't exist as steps — treat as blocked
                    unresolved.update(remaining)
                    break
                # Cycle detected
                raise RuntimeError(f"Cycle detected in dependency graph: {remaining}")

            layers.append(ready)
            for sid in ready:
                remaining.remove(sid)
                for step_id, deps in self._graph.items():
                    if sid in deps:
                        in_degree[step_id] -= 1

        return layers

    def detect_cycles(self) -> list[list[str]]:
        """Detect cycles in the dependency graph. Returns list of cycles found."""
        # Tarjan's algorithm for cycle detection
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self._graph.get(node, []):
                if dep not in visited:
                    dfs(dep, path)
                elif dep in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])

            path.pop()
            rec_stack.remove(node)

        for node in self._graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_dependents(self, step_id: str) -> list[str]:
        """Get all steps that depend on the given step."""
        return [sid for sid, deps in self._graph.items() if step_id in deps]

    def to_mermaid(self) -> str:
        """Generate Mermaid graph of dependencies."""
        lines = ["graph LR"]
        lines.append('    title["Workflow Dependency Graph"]')
        for step_id, deps in self._graph.items():
            for dep in deps:
                lines.append(f"    {dep}[{dep}] --> {step_id}[{step_id}]")
        return "\n".join(lines)


# =======================================================================
# WORKFLOW ENGINE
# =======================================================================

class WorkflowEngine:
    """Executes workflows with dependency resolution and conditional routing.

    Usage:
        engine = WorkflowEngine()

        # From template
        wf = engine.create_from_template("daily_training", {"n_episodes": 100})
        result = engine.execute(wf)

        # From DSL dict
        wf = engine.parse_dsl({
            "name": "custom_flow",
            "steps": [
                {"id": "step1", "action": "execute_worm",
                 "params": {"worm": "SystemZ"}},
            ],
        })
        result = engine.execute(wf)
    """

    def __init__(self):
        self._templates = dict(BUILTIN_TEMPLATES)
        self._history: list[WorkflowResult] = []
        self._lock = threading.Lock()

    # -- Template Management -----------------------------------------

    def register_template(self, template: WorkflowTemplate):
        """Register a custom workflow template."""
        self._templates[template.name] = template

    def list_templates(self) -> list[str]:
        """list all registered template names."""
        return list(self._templates.keys())

    def get_template(self, name: str) -> (WorkflowTemplate | None):
        """Get a template by name."""
        return self._templates.get(name)

    # -- DSL Parsing -------------------------------------------------

    def parse_dsl(self, dsl: dict) -> Workflow:
        """Parse a workflow DSL dict into a Workflow object.

        Expected format:
        {
            "name": "my_workflow",
            "description": "...",
            "params": {"key": "default"},
            "steps": [
                {"id": "s1", "action": "execute_worm",
                 "params": {"worm": "SystemZ"},
                 "depends_on": [],
                 "condition": "..."},
            ]
        }
        """
        wf_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time())}"
        steps_dict = dsl.get("steps", [])
        steps = []
        for s in steps_dict:
            steps.append(WorkflowStep(
                id=s["id"],
                action=s.get("action", "execute_worm"),
                params=s.get("params", {}),
                depends_on=s.get("depends_on", []),
                condition=s.get("condition"),
                timeout=s.get("timeout", 300),
            ))

        return Workflow(
            id=wf_id,
            name=dsl.get("name", "unnamed"),
            description=dsl.get("description", ""),
            steps=steps,
            params=dsl.get("params", {}),
            tags=dsl.get("tags", []),
        )

    # -- Template Instantiation --------------------------------------

    def create_from_template(self, template_name: str,
                             params: dict[str, Any] = None,
                             name_override: str = None) -> (Workflow | None):
        """Create a workflow from a named template with parameter overrides."""
        template = self._templates.get(template_name)
        if not template:
            return None

        wf_id = f"wf_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Merge params: defaults from template, overrides from caller
        merged_params = dict(template.parameters)
        if params:
            merged_params.update(params)

        # Build steps
        steps = []
        for s in template.steps:
            step_params = {}
            for k, v in s.get("params", {}).items():
                if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                    # Parameter reference
                    param_name = v[2:-1]
                    # Handle nested path like "step_id.result"
                    if "." in param_name:
                        step_params[k] = param_name  # Pass as template string
                    else:
                        step_params[k] = merged_params.get(param_name, v)
                else:
                    step_params[k] = v

            steps.append(WorkflowStep(
                id=s["id"],
                action=s.get("action", "execute_worm"),
                params=step_params,
                depends_on=s.get("depends_on", []),
                condition=s.get("condition"),
                timeout=s.get("timeout", 300),
            ))

        return Workflow(
            id=wf_id,
            name=name_override or template.name,
            description=template.description,
            steps=steps,
            params=merged_params,
            tags=list(template.tags),
        )

    # -- Step Execution ----------------------------------------------

    def _execute_step(self, step: WorkflowStep,
                      step_results: dict[str, Any],
                      params: dict[str, Any]) -> Any:
        """Execute a single workflow step."""
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()

        try:
            action = step.action
            action_params = step.params

            if action == "execute_worm":
                result = self._run_execute_worm(action_params)
            elif action == "execute_nature":
                result = self._run_execute_nature(action_params)
            elif action == "run_pipeline":
                result = self._run_pipeline(action_params, step_results)
            elif action == "condition":
                result = self._run_condition(action_params, step_results, params)
            elif action == "sleep":
                duration = float(action_params.get("seconds", 1))
                time.sleep(duration)
                result = {"slept": duration}
            elif action == "log":
                msg = action_params.get("message", "")
                print(f"[Workflow] {msg}", flush=True)
                result = {"logged": msg}
            else:
                raise ValueError(f"Unknown action: {action}")

            step.status = StepStatus.SUCCESS
            step.result = result
            return result

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            raise

        finally:
            step.duration_ms = (time.perf_counter() - start) * 1000
            step.completed_at = datetime.now(timezone.utc).isoformat()

    def _run_execute_worm(self, params: dict) -> Any:
        """Execute a worm by name and method."""
        worm_name = params.get("worm")
        method_name = params.get("method", "execute")
        args = params.get("args", {})

        try:
            # Resolve worm from registry
            from CORE.worm_registry import WORM_REGISTRY, discover_worms
            discover_worms()

            worm_info = WORM_REGISTRY.get(worm_name)
            if not worm_info:
                raise ValueError(f"Worm '{worm_name}' not found in registry")

            worm_class = worm_info.get("class")
            if not worm_class:
                raise ValueError(f"Worm '{worm_name}' has no class registered")

            instance = worm_class()
            method = getattr(instance, method_name, None)
            if not method:
                raise ValueError(f"Worm '{worm_name}' has no method '{method_name}'")

            return method(**args)

        except ImportError:
            raise ValueError("Worm registry not available")

    def _run_execute_nature(self, params: dict) -> Any:
        """Execute a Nature cluster."""
        nature = params.get("nature")
        parallel = params.get("parallel", False)

        try:
            from CORE.WORMS.METACLUSTER import MetaCluster
            mc = MetaCluster()
            mc.discover_all()
            result = mc.orchestrate_nature(nature, parallel=parallel)
            if result:
                return {
                    "success_count": result.total_worms_ok,
                    "failure_count": result.total_worms_fail,
                    "duration_ms": result.duration_ms,
                }
            return {"success_count": 0, "failure_count": 0}
        except Exception as e:
            raise ValueError(f"Failed to execute nature '{nature}': {e}")

    def _run_pipeline(self, params: dict, step_results: dict[str, Any]) -> Any:
        """Run a data pipeline step."""
        pipeline_name = params.get("pipeline")
        method_name = params.get("method", "execute")
        args = dict(params.get("args", {}))

        # Resolve template references in args
        for key, val in list(args.items()):
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                ref = val[2:-1]
                # Check if it references a previous step result
                parts = ref.split(".")
                if len(parts) >= 2 and parts[0] in step_results:
                    step_data = step_results[parts[0]]
                    field_path = parts[1:] if len(parts) > 1 else []
                    resolved = step_data
                    for p in field_path:
                        if isinstance(resolved, dict):
                            resolved = resolved.get(p, val)
                        else:
                            resolved = val
                            break
                    args[key] = resolved
                else:
                    args[key] = val

        if pipeline_name == "DataPipelineWorm":
            from CORE.WORMS.expansion.learning import DataPipelineWorm
            pipeline = DataPipelineWorm()
            method = getattr(pipeline, method_name)
            return method(**args)

        raise ValueError(f"Unknown pipeline: {pipeline_name}")

    def _run_condition(self, params: dict, step_results: dict[str, Any],
                       wf_params: dict) -> bool:
        """Evaluate a condition."""
        condition = params.get("condition", "")
        return ConditionalRouter.evaluate(condition, step_results, wf_params)

    # -- Workflow Execution ------------------------------------------

    def execute(self, workflow: Workflow) -> WorkflowResult:
        """Execute a workflow end-to-end with dependency resolution and conditional routing.

        Args:
            workflow: The workflow to execute

        Returns:
            WorkflowResult with step-by-step results
        """
        start = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()

        # Build dependency graph
        graph = DependencyGraph()
        graph.build(workflow.steps)
        step_map = {s.id: s for s in workflow.steps}

        # Check for cycles
        cycles = graph.detect_cycles()
        if cycles:
            return WorkflowResult(
                workflow_id=workflow.id,
                workflow_name=workflow.name,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=0,
                success=False,
                errors=[f"Cycle detected: {c}" for c in cycles],
            )

        # Resolve execution order
        try:
            layers = graph.get_execution_order()
        except RuntimeError as e:
            return WorkflowResult(
                workflow_id=workflow.id,
                workflow_name=workflow.name,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=0,
                success=False,
                errors=[str(e)],
            )

        step_results: dict[str, Any] = {}
        success_count = 0
        failure_count = 0
        skipped_count = 0
        errors: list[str] = []
        outputs: dict[str, Any] = {}

        for layer in layers:
            # Execute steps in this layer in parallel using ThreadPoolExecutor
            results_lock = threading.Lock()

            def _run_step(step_id: str):
                nonlocal success_count, failure_count, skipped_count
                step = step_map[step_id]

                # Check condition
                if step.condition:
                    should_run = ConditionalRouter.evaluate(
                        step.condition, step_results, workflow.params
                    )
                    if not should_run:
                        with results_lock:
                            step.status = StepStatus.SKIPPED
                            step.result = {"skipped": True, "reason": f"Condition not met: {step.condition}"}
                            step_results[step_id] = {"success": False, "skipped": True}
                            skipped_count += 1
                        return

                try:
                    result = self._execute_step(step, step_results, workflow.params)
                    with results_lock:
                        step_results[step_id] = {
                            "success": True,
                            "result": result,
                            "duration_ms": step.duration_ms,
                        }
                        success_count += 1
                        outputs[step_id] = result
                except Exception as e:
                    with results_lock:
                        step_results[step_id] = {
                            "success": False,
                            "error": str(e),
                            "duration_ms": step.duration_ms,
                        }
                        failure_count += 1
                        errors.append(f"Step '{step_id}' failed: {e}")

            with ThreadPoolExecutor(max_workers=min(len(layer), 8)) as executor:
                fut_map = {executor.submit(_run_step, sid): sid for sid in layer}
                try:
                    for fut in as_completed(fut_map, timeout=300):
                        # _run_step handles its own exceptions and updates shared state via lock
                        pass
                except TimeoutError:
                    for fut, sid in fut_map.items():
                        if not fut.done():
                            fut.cancel()
                            errors.append(f"Step '{sid}' timed out after 300s")

        duration_ms = (time.perf_counter() - start) * 1000

        result = WorkflowResult(
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=round(duration_ms, 2),
            step_results=step_results,
            success_count=success_count,
            failure_count=failure_count,
            skipped_count=skipped_count,
            errors=errors,
            outputs=outputs,
            success=failure_count == 0,
        )

        # Record to LocalMemoryStore
        try:
            from CORE.local_memory import get_memory_store
            store = get_memory_store()
            store.record_event(
                source="WorkflowEngine",
                event_type="workflow_completed",
                data={
                    "workflow_id": workflow.id,
                    "name": workflow.name,
                    "success": result.success,
                    "steps_ok": success_count,
                    "steps_fail": failure_count,
                    "steps_skipped": skipped_count,
                    "duration_ms": result.duration_ms,
                },
                severity="info" if result.success else "warning",
                tags=["workflow", workflow.name],
            )
        except Exception:
            pass

        with self._lock:
            self._history.append(result)
            if len(self._history) > 100:
                self._history = self._history[-50:]

        return result

    # -- Status ------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """Get workflow engine status."""
        with self._lock:
            return {
                "templates": len(self._templates),
                "templates_list": list(self._templates.keys()),
                "history_count": len(self._history),
                "last_execution": (
                    {
                        "id": self._history[-1].workflow_id,
                        "name": self._history[-1].workflow_name,
                        "success": self._history[-1].success,
                        "duration_ms": self._history[-1].duration_ms,
                    }
                    if self._history else None
                ),
            }

    def get_history(self, limit: int = 10) -> list[WorkflowResult]:
        """Get recent workflow execution history."""
        with self._lock:
            return self._history[-limit:]


# =======================================================================
# GLOBAL SINGLETON
# =======================================================================

_engine: (WorkflowEngine | None) = None
_engine_lock = threading.Lock()


def get_workflow_engine() -> WorkflowEngine:
    """Get or create the global WorkflowEngine singleton."""
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = WorkflowEngine()
    return _engine
