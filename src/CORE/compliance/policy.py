"""
RULE 0X-1 + 0X-2: Policy-as-Code Gate + Runtime Broker Interception

PolicyEngine provides RBAC/ABAC-style policy evaluation without Casbin.
BrokerInterceptor provides @enforce_gate decorators using wrapt.

Usage:
    engine = PolicyEngine()
    engine.add_rule(PolicyRule("allow", "code_edit", role="developer"))
    assert engine.evaluate("code_edit", role="developer")

    @enforce_gate("code_edit", role="developer")
    def my_func():
        pass
"""

import functools
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

# Optional wrapt import for robust decorators
try:
    import wrapt
    HAS_WRAPT = True
except ImportError:
    note_failure("policy:L27", None)
    HAS_WRAPT = False


# ---------------------------------------------------------------------------
# Policy Rule
# ---------------------------------------------------------------------------

class PolicyEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class PolicyRule:
    """A single policy rule with subject, action, and conditions.

    Rules are evaluated in priority order. First matching rule wins.
    If no rule matches, the default is DENY.

    Attributes:
        effect: ALLOW or DENY
        action: The action being requested (e.g., "str_replace", "write_file")
        role: Required role (subject attribute)
        conditions: Additional key=value conditions for fine-grained ABAC
        priority: Higher priority rules evaluated first (default 0)
    """

    def __init__(
        self,
        effect: str,
        action: str,
        role: str = "",
        conditions: (dict[str, Any] | None) = None,
        priority: int = 0,
    ):
        self.effect = PolicyEffect(effect.lower())
        self.action = action
        self.role = role
        self.conditions = conditions or {}
        self.priority = priority

    def matches(self, action: str, role: str = "", attributes: (dict[str, Any] | None) = None) -> bool:
        """Check if this rule matches the given action + subject + context."""
        attributes = attributes or {}

        # Action must match (exact or wildcard)
        if self.action != "*" and self.action != action:
            return False

        # Role must match if specified
        if self.role and self.role != role:
            return False

        # All conditions must match
        for key, value in self.conditions.items():
            actual = attributes.get(key)
            if actual != value:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "effect": self.effect.value,
            "action": self.action,
            "role": self.role,
            "conditions": self.conditions,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PolicyRule":
        return cls(
            effect=data["effect"],
            action=data["action"],
            role=data.get("role", ""),
            conditions=data.get("conditions", {}),
            priority=data.get("priority", 0),
        )

    def __repr__(self) -> str:
        return f"PolicyRule({self.effect.value}, action={self.action}, role={self.role})"


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------

class PolicyEngine:
    """Policy evaluation engine — replaces Casbin for Azazael compliance gates.

    Evaluates rules in priority order. First matching rule wins.
    Default is DENY (fail-closed). Thread-safe for concurrent evaluation.
    """

    def __init__(self):
        self._rules: list[PolicyRule] = []
        self._lock = threading.Lock()
        self._audit_log: list[dict[str, Any]] = []
        self._audit_lock = threading.Lock()

    def add_rule(self, rule: PolicyRule):
        """Add a policy rule. Re-sorts by priority after adding."""
        with self._lock:
            self._rules.append(rule)
            self._rules.sort(key=lambda r: r.priority, reverse=True)

    def add_rules(self, rules: list[PolicyRule]):
        """Add multiple policy rules at once."""
        with self._lock:
            self._rules.extend(rules)
            self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, action: str, role: str = "") -> int:
        """Remove all rules matching action + role. Returns count removed."""
        with self._lock:
            before = len(self._rules)
            self._rules = [r for r in self._rules if not (r.action == action and r.role == role)]
            return before - len(self._rules)

    def evaluate(self, action: str, role: str = "", attributes: (dict[str, Any] | None) = None) -> tuple[bool, str]:
        """Evaluate an action against all rules.

        Args:
            action: The action being requested (e.g., "str_replace", "write_file")
            role: The subject's role
            attributes: Additional context attributes for ABAC conditions

        Returns:
            (allowed: bool, reason: str)
        """
        attributes = attributes or {}

        with self._lock:
            for rule in self._rules:
                if rule.matches(action, role, attributes):
                    allowed = rule.effect == PolicyEffect.ALLOW
                    reason = (
                        f"Rule {rule.effect.value}: {rule}"
                        if allowed
                        else f"DENIED by rule: {rule}"
                    )
                    self._log_evaluation(action, role, attributes, allowed, reason)
                    return allowed, reason

        # Default: DENY (fail-closed)
        reason = f"DENIED (default): no matching rule for action={action}, role={role}"
        self._log_evaluation(action, role, attributes, False, reason)
        return False, reason

    def evaluate_all(self, action: str, role: str = "", attributes: (dict[str, Any] | None) = None) -> dict[str, Any]:
        """Full evaluation result with all metadata. Used by ComplianceOrchestrator."""
        allowed, reason = self.evaluate(action, role, attributes)
        return {
            "allowed": allowed,
            "reason": reason,
            "action": action,
            "role": role,
            "policy_version": "1.0.0",
        }

    def _log_evaluation(self, action: str, role: str, attributes: dict, allowed: bool, reason: str):
        """Record evaluation to internal audit log."""
        with self._audit_lock:
            self._audit_log.append({
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "action": action,
                "role": role,
                "attributes": attributes,
                "allowed": allowed,
                "reason": reason,
            })

    def get_audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._audit_lock:
            return list(self._audit_log[-limit:])

    def clear_rules(self):
        with self._lock:
            self._rules.clear()

    def rule_count(self) -> int:
        with self._lock:
            return len(self._rules)

    def __repr__(self) -> str:
        return f"PolicyEngine({self.rule_count()} rules)"


# ---------------------------------------------------------------------------
# Default Policy Rules (Azazael-specific)
# ---------------------------------------------------------------------------

def default_policy_rules() -> list[PolicyRule]:
    """Create the default Azazael compliance policy rules.

    These implement the PRE-ACTION GATE (RULE 0J) as programmatic policy:
    - DEVELOPER role: full access to all code actions
    - REVIEWER role: can read and review, but not edit
    - AUDITOR role: read-only access
    - GUEST role: no access
    """
    return [
        # DEVELOPER — full access
        PolicyRule("allow", "*", role="developer", priority=100),
        # REVIEWER — read + review, no edit
        PolicyRule("allow", "read_files", role="reviewer", priority=90),
        PolicyRule("allow", "spawn_agents", role="reviewer", priority=90),
        PolicyRule("deny", "str_replace", role="reviewer", priority=90),
        PolicyRule("deny", "write_file", role="reviewer", priority=90),
        # AUDITOR — read only
        PolicyRule("allow", "read_files", role="auditor", priority=80),
        PolicyRule("deny", "*", role="auditor", priority=80),
        # GUEST — no access
        PolicyRule("deny", "*", role="guest", priority=70),
        # Default deny for all other subjects
        PolicyRule("deny", "*", priority=0),
    ]


# ---------------------------------------------------------------------------
# @enforce_gate decorator (RULE 0X-2: Runtime Broker Interception)
# ---------------------------------------------------------------------------

def enforce_gate(action: str = "", role: str = "developer", **conditions):
    """Decorator that enforces policy gate before function execution.

    Uses wrapt for robust signature-preserving decoration. Falls back to
    functools.wraps if wrapt is not available.

    Args:
        action: The policy action name (defaults to function name)
        role: Required role for execution
        **conditions: Additional ABAC conditions passed to PolicyEngine

    Usage:
        @enforce_gate("str_replace", role="developer")
        def str_replace_func(filepath, new_content):
            pass

        @enforce_gate()  # Uses function name as action
        def write_file(filepath):
            pass

    Raises:
        PermissionError: If the gate evaluation returns DENY
    """
    def decorator(wrapped=None, wrapper=None, instance=None):
        # Determine the action name
        nonlocal action
        actual_action = action or getattr(wrapped, "__name__", "unknown")

        def gate_wrapper(func, *args, **kwargs):
            # Build attributes from the function arguments
            attributes = dict(conditions)

            # Evaluate policy
            engine = _get_global_engine()
            allowed, reason = engine.evaluate(actual_action, role=role, attributes=attributes)

            if not allowed:
                raise PermissionError(
                    f"[COMPLIANCE GATE] Action '{actual_action}' DENIED for role '{role}': {reason}"
                )

            return func(*args, **kwargs)

        if HAS_WRAPT and isinstance(wrapped, wrapt.ObjectProxy):
            # wrapt-based decoration (signature-preserving)
            @wrapt.decorator
            def wrapper_func(wrapped, instance, args, kwargs):
                return gate_wrapper(wrapped, *args, **kwargs)
            return wrapper_func(wrapped)
        elif wrapped is not None:
            # Direct function decoration
            @functools.wraps(wrapped)
            def wrapper_func(*args, **kwargs):
                return gate_wrapper(wrapped, *args, **kwargs)
            return wrapper_func
        else:
            # Called with arguments (e.g., @enforce_gate("action"))
            return decorator

    return decorator


# ---------------------------------------------------------------------------
# Broker Interceptor
# ---------------------------------------------------------------------------

class BrokerInterceptor:
    """Runtime broker that intercepts tool calls and enforces policy gates.

    Acts as middleware between the agent and the actual tool execution.
    Compatible with wrapt for transparent function wrapping.

    Usage:
        interceptor = BrokerInterceptor()
        interceptor.intercept("str_replace", actual_function)
        # Now all calls to str_replace go through policy evaluation first
    """

    def __init__(self, engine: (PolicyEngine | None) = None):
        self._engine = engine or _get_global_engine()
        self._intercepted: dict[str, Callable] = {}

    def intercept(self, action: str, func: Callable, role: str = "developer") -> Callable:
        """Wrap a function with policy enforcement.

        Args:
            action: The action name for policy evaluation
            func: The function to wrap
            role: Required role

        Returns:
            The wrapped function
        """
        actual_action = action

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            allowed, reason = self._engine.evaluate(actual_action, role=role)
            if not allowed:
                raise PermissionError(f"[BROKER] Action '{actual_action}' DENIED: {reason}")
            return func(*args, **kwargs)

        self._intercepted[action] = wrapped
        return wrapped

    def get_intercepted(self, action: str) -> (Callable | None):
        return self._intercepted.get(action)

    def release(self, action: str):
        self._intercepted.pop(action, None)


# ---------------------------------------------------------------------------
# Global engine singleton
# ---------------------------------------------------------------------------

_global_engine: (PolicyEngine | None) = None
_global_lock = threading.Lock()


def _get_global_engine() -> PolicyEngine:
    """Get or create the global policy engine singleton with default rules."""
    global _global_engine
    if _global_engine is None:
        with _global_lock:
            if _global_engine is None:
                _global_engine = PolicyEngine()
                _global_engine.add_rules(default_policy_rules())
    return _global_engine


def reset_global_engine():
    """Reset the global policy engine (for testing)."""
    global _global_engine
    with _global_lock:
        _global_engine = None
