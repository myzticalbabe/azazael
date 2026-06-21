# coding: utf-8
"""
CROSS_NATURE_ROUTER — Cross-Nature Routing Engine

Routes data between Natures based on NATURE_DEFINITIONS feeds_into chains.
Handles automatic data flow, topological sort, and path discovery.

Extracted from METACLUSTER.py to reduce import chain and enable independent testing.

Architecture:
    CrossNatureRoutingEngine
    +-- Routes built from NATURE_DEFINITIONS feeds_into chains
    +-- route_nature_output(from_nature, results, meta_state) -> int
    +-- compute_routing_order(start_natures) -> [natures in execution order]
    +-- get_all_paths() -> [[chains of natures]]

Usage:
    >>> from CORE.WORMS.CROSS_NATURE_ROUTER import CrossNatureRoutingEngine
    >>> from CORE.WORMS.NATURE_CLUSTERS import NATURE_DEFINITIONS
    >>> router = CrossNatureRoutingEngine()
    >>> order = router.compute_routing_order(["security"])
"""
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Any
from collections import defaultdict, deque

# -- Import Dependencies -------------------------------------------
try:
    from CORE.WORMS.NATURE_CLUSTERS import (
        CrossNatureRoute, NATURE_DEFINITIONS,
    )
    _NATURE_OK = True
except ImportError:
    _NATURE_OK = False
    NATURE_DEFINITIONS = {}
    @dataclass  # Module-level import (3.14t safe)
    class _CrossNatureRoute:
        from_nature: str = ""
        to_nature: str = ""
        data_mapping: dict = None
        description: str = ""
        def __post_init__(self):
            if self.data_mapping is None:
                self.data_mapping = {}
    CrossNatureRoute = _CrossNatureRoute

# -- MemoryBus (lazy, double-checked locking for 3.14t) --------------
_BUS_OK = False
_mem_bus = None
_mem_bus_lock = threading.Lock()
def _get_mem_bus():
    global _BUS_OK, _mem_bus
    if _mem_bus is None and not _BUS_OK:
        with _mem_bus_lock:
            if _mem_bus is None and not _BUS_OK:
                try:
                    from CORE.MemoryBus import MemoryBus
                    _mem_bus = MemoryBus()
                    _BUS_OK = True
                except ImportError:
                    _BUS_OK = False
    return _mem_bus if _BUS_OK else None

# -- PAMS Memory Recording (lazy, double-checked locking for 3.14t) --
_PAMS_OK = False
_pams = None
_pams_lock = threading.Lock()
def _get_pams():
    global _PAMS_OK, _pams
    if _pams is None and not _PAMS_OK:
        with _pams_lock:
            if _pams is None and not _PAMS_OK:
                try:
                    from CORE.PamsRecorder import PamsRecorder
                    _pams = PamsRecorder()
                    _PAMS_OK = True
                except ImportError:
                    _PAMS_OK = False
    return _pams if _PAMS_OK else None


def _record_event(event_type: str, data: dict[str, Any]):
    """Record event to PAMS memory."""
    pams = _get_pams()
    if pams:
        try:
            pams.record_event(
                event_type, data,
                source="CrossNatureRoutingEngine",
                severity="info",
            )
        except Exception:
            pass


# -- InferenceWorm (lazy, double-checked locking for 3.14t) --------
_INFERENCE_OK = False
_inference_worm = None
_inference_lock = threading.Lock()
def _get_inference():
    global _INFERENCE_OK, _inference_worm
    if _inference_worm is None and not _INFERENCE_OK:
        with _inference_lock:
            if _inference_worm is None and not _INFERENCE_OK:
                try:
                    from CORE.WORMS.INFERENCE_WORM import InferenceWorm
                    _inference_worm = InferenceWorm()
                    _INFERENCE_OK = True
                except ImportError:
                    _INFERENCE_OK = False
    return _inference_worm if _INFERENCE_OK else None


# =======================================================================
# CROSS-NATURE ROUTING ENGINE
# =======================================================================

# Note: MetaClusterState is received as a parameter to route_nature_output().
# The routing engine does not import it directly to avoid circular dependencies.

class CrossNatureRoutingEngine:
    """
    Routes data between Natures based on NATURE_DEFINITIONS feeds_into chains.
    
    Handles automatic data flow:
        security -> defense -> repair -> orchestration
        profiling -> optimization -> monitor -> defense
        telemetry -> visualization -> orchestration
    
    Also publishes routed data to MemoryBus for inter-agent communication.
    """
    
    def __init__(self):
        self.routes: list[CrossNatureRoute] = self._build_routes()
        self.routing_history: list[dict] = []
        self._lock = threading.Lock()
    
    def _build_routes(self) -> list[CrossNatureRoute]:
        """Build all cross-Nature routes from definitions."""
        routes = []
        for nature, definition in NATURE_DEFINITIONS.items():
            for target in definition.get("feeds_into", []):
                routes.append(CrossNatureRoute(
                    from_nature=nature,
                    to_nature=target,
                    description=f"Auto-route: {nature} -> {target}",
                ))
        return routes
    
    def get_routes_from(self, nature: str) -> list[CrossNatureRoute]:
        """Get all routes originating from a Nature."""
        return [r for r in self.routes if r.from_nature == nature]
    
    def get_routes_to(self, nature: str) -> list[CrossNatureRoute]:
        """Get all routes targeting a Nature."""
        return [r for r in self.routes if r.to_nature == nature]
    
    def route_nature_output(self, from_nature: str, results: dict[str, Any],
                            meta_state) -> int:
        """
        Route one Nature's output to its downstream Natures.
        Returns number of routes activated.
        
        Args:
            from_nature: The Nature that just executed
            results: The Nature's execution results
            meta_state: A MetaClusterState-like object with .lock, .routed_messages, .events
        """
        routes = self.get_routes_from(from_nature)
        if not routes:
            return 0
        
        count = 0
        for route in routes:
            routing_data = {
                "from_nature": from_nature,
                "to_nature": route.to_nature,
                "data": results,
                "route_description": route.description,
                "timestamp": datetime.now().isoformat(),
            }
            
            with self._lock:
                self.routing_history.append(routing_data)
            
            with meta_state.lock:
                meta_state.routed_messages.append(routing_data)
                meta_state.events.append({
                    "type": "cross_nature_route",
                    "from": from_nature,
                    "to": route.to_nature,
                    "timestamp": datetime.now().isoformat(),
                })
            
            # Publish to MemoryBus
            mem_bus = _get_mem_bus()
            if mem_bus:
                try:
                    mem_bus.publish(
                        f"nature.route.{from_nature}.{route.to_nature}",
                        routing_data,
                        source="CrossNatureRoutingEngine",
                    )
                except Exception:
                    pass
            
            # Record to PAMS
            _record_event("cross_nature_route", {
                "from": from_nature, "to": route.to_nature,
                "data_keys": list(results.keys())[:10],
            })
            
            count += 1
        
        return count
    
    def compute_routing_order(self, start_natures: list[str]) -> list[str]:
        """
        Compute optimal Nature execution order using topological sort
        of the routing graph, starting from specified Natures.
        
        Includes cycle detection -- circular dependencies are broken
        at the lowest-priority edge in each cycle.
        """
        # Build dependency graph
        dependencies: dict[str, set[str]] = defaultdict(set)
        for route in self.routes:
            dependencies[route.to_nature].add(route.from_nature)

        # Detect and break cycles
        cycles = self.detect_cycles()
        for cycle in cycles:
            if len(cycle) >= 3:
                # Break the first edge in the cycle: remove cycle[0] from dependencies[cycle[1]]
                # In the route graph, cycle[0] -> cycle[1] is an edge forming the cycle.
                # In dependencies, downstream[cycle[1]] depends on upstream[cycle[0]].
                if cycle[0] in dependencies.get(cycle[1], set()):
                    dependencies[cycle[1]].discard(cycle[0])

        visited: set[str] = set()
        visiting: set[str] = set()
        order: list[str] = []

        def visit(nature: str):
            if nature in visited or nature in visiting:
                return
            visiting.add(nature)
            for upstream in sorted(dependencies.get(nature, set())):
                visit(upstream)
            visiting.discard(nature)
            visited.add(nature)
            if nature not in order:
                order.append(nature)
        
        for start in start_natures:
            visit(start)
        
        for nature in sorted(NATURE_DEFINITIONS.keys()):
            if nature not in order:
                order.append(nature)
        
        return order

    def detect_cycles(self) -> list[list[str]]:
        """
        Detect circular dependencies in the routing graph.
        Uses DFS with 3-color marking (0=unvisited, 1=visiting, 2=done).
        Returns list of cycles as Nature name lists.
        """
        adj: dict[str, list[str]] = defaultdict(list)
        for route in self.routes:
            adj[route.from_nature].append(route.to_nature)

        color: dict[str, int] = {}
        parent: dict[str, (str | None)] = {}
        cycles: list[list[str]] = []

        for n in sorted(set(list(adj.keys()) + list(NATURE_DEFINITIONS.keys()))):
            color[n] = 0
            parent[n] = None

        def dfs(u: str):
            color[u] = 1
            for v in adj.get(u, []):
                if v not in color:
                    color[v] = 0
                if color[v] == 0:
                    parent[v] = u
                    dfs(v)
                elif color[v] == 1:
                    cycle = [v]
                    cur = u
                    while cur is not None and cur != v:
                        cycle.append(cur)
                        cur = parent.get(cur)
                    cycle.append(v)
                    cycle.reverse()
                    ck = tuple(sorted(cycle))
                    if not any(tuple(sorted(c)) == ck for c in cycles):
                        cycles.append(cycle)
            color[u] = 2

        for n in sorted(color.keys()):
            if color[n] == 0:
                dfs(n)

        return cycles

    def shortest_path(self, from_nature: str, to_nature: str) -> (list[str] | None):
        """Find the shortest path between two Natures using BFS."""
        if from_nature == to_nature:
            return [from_nature]

        adj: dict[str, list[str]] = defaultdict(list)
        for route in self.routes:
            adj[route.from_nature].append(route.to_nature)

        queue = deque([[from_nature]])
        visited = {from_nature}

        while queue:
            path = queue.popleft()
            current = path[-1]
            for neighbor in adj.get(current, []):
                if neighbor == to_nature:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return None

    def optimize_pipeline(self, start_nature: str,
                          target_outcomes: (list[str] | None) = None) -> list[str]:
        """Optimize pipeline from start Nature using shortest paths."""
        if not target_outcomes:
            return self.compute_routing_order([start_nature])

        all_natures: set[str] = set()
        for target in target_outcomes:
            path = self.shortest_path(start_nature, target)
            if path:
                all_natures.update(path)

        if not all_natures:
            return self.compute_routing_order([start_nature])

        return self.compute_routing_order(list(all_natures))
    
    def analyze_routing(self, execution_results: dict[str, Any],
                        available_natures: list[str]) -> dict[str, Any]:
        """Use LLM to analyze results and suggest optimal next Natures.

        Replaces static feeds_into chains with adaptive LLM-powered routing.
        Falls back to existing static routes if inference is unavailable.

        Args:
            execution_results: dict of {nature_name: {success_count, failure_count, ...}}
            available_natures: list of Nature names available for next execution

        Returns:
            dict with 'suggested_next' (list), 'routing_insight' (str), 'confidence' (str)
        """
        # Default: use static routes
        suggested = []
        for nature in execution_results:
            routes = self.get_routes_from(nature)
            for route in routes:
                if route.to_nature in available_natures:
                    suggested.append(route.to_nature)

        # Try LLM-powered routing
        try:
            worm = _get_inference()
            if not worm:
                raise ImportError("InferenceWorm unavailable")

            summary = []
            for nature, result in sorted(execution_results.items()):
                ok = result.get("success_count", 0)
                fail = result.get("failure_count", 0)
                dur = result.get("duration_ms", 0)
                summary.append(f"{nature}: {ok}OK/{fail}FAIL ({dur:.0f}ms)")

            prompt = (
                "Azazael Nature execution results:\n"
                + "\n".join(f"  {s}" for s in summary) + "\n"
                f"Available next Natures: {', '.join(sorted(available_natures))}\n\n"
                f"Based on results, which Natures should run next? "
                f"Respond: NEXT: nature1, nature2 | REASON: <one sentence>"
            )

            result = worm.execute(
                prompt=prompt,
                system_prompt=(
                    "You optimize execution routing for an AI ecosystem. "
                    "Recommend next Natures to run based on execution results. "
                    "Prioritize Natures that address failures or build on successes."
                ),
                max_tokens=100,
            )
            if result.get("success") and result.get("content"):
                content = result["content"]
                llm_suggested = []
                reason = ""
                for line in content.split("\n"):
                    line = line.strip()
                    if line.upper().startswith("NEXT:"):
                        parts = line.split(":", 1)[-1].strip()
                        llm_suggested = [n.strip() for n in parts.split(",") if n.strip() in available_natures]
                    elif line.upper().startswith("REASON:"):
                        reason = line.split(":", 1)[-1].strip()
                if llm_suggested:
                    return {
                        "suggested_next": llm_suggested,
                        "routing_insight": reason,
                        "confidence": "medium",
                        "provider": result.get("provider", "unknown"),
                    }
        except Exception:
            pass

        return {
            "suggested_next": list(dict.fromkeys(suggested)),
            "routing_insight": "Static routing (LLM unavailable)",
            "confidence": "low",
        }

    def get_all_paths(self) -> list[list[str]]:
        """
        Find all complete routing paths through the Nature graph.
        Returns list of paths like [security, defense, repair, orchestration].
        """
        paths = []
        
        # Find root Natures (those that nothing feeds into)
        all_from = {r.from_nature for r in self.routes}
        all_to = {r.to_nature for r in self.routes}
        roots = all_from - all_to
        
        # Also include Natures with no upstream
        for nature in NATURE_DEFINITIONS:
            if nature not in all_to:
                roots.add(nature)
        
        def dfs(current: str, visited: set[str], path: list[str]):
            path = path + [current]
            visited = visited | {current}
            
            next_natures = {r.to_nature for r in self.routes if r.from_nature == current}
            next_natures -= visited
            
            if not next_natures:
                paths.append(path)
            else:
                for nxt in sorted(next_natures):
                    dfs(nxt, visited, path)
        
        for root in sorted(roots):
            dfs(root, set(), [])
        
        return paths
