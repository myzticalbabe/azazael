# coding: utf-8
"""


__all__ = [
    "DedupAnalyzer",
    "DedupMatch",
    "DedupReport",
    "GovernanceReport",
    "LifecycleEntry",
    "LifecycleManager",
    "LifecycleReport",
    "LifecycleState",
    "NamingReport",
    "ValidationResult",
    "WormGovernanceReport",
    "WormGovernor",
    "WormNamingValidator",
    "print_governance_report",
    "run_governance_audit",
]

worm_governance — Worm Naming, Dedup, and Lifecycle Governance

Provides:
- WormNamingValidator: Validates worm class names against naming conventions
- DedupAnalyzer: Detects duplicate worm implementations via signature comparison
- LifecycleManager: Version-based lifecycle state tracking (DRAFT → ACTIVE → DEPRECATED → RETIRED)
- WormGovernor: Orchestrator that produces comprehensive governance reports

Usage:
    >>> from CORE.worm_governance import WormGovernor
    >>> governor = WormGovernor()
    >>> report = governor.govern()  # Full governance audit
    >>> print(report.naming_issues)  # Naming convention violations
    >>> print(report.dedup_issues)   # Potential duplicate worms
    >>> print(report.lifecycle_issues)  # Lifecycle concerns
"""

import re
import inspect
import logging
import threading
from datetime import datetime
from typing import Any, NamedTuple

_log = logging.getLogger("worm_governance")

# =====================================================================
# Data Types
# =====================================================================

class ValidationResult(NamedTuple):
    """Result of a single naming validation."""
    name: str
    valid: bool
    violations: list[str]
    suggestions: list[str]


class NamingReport(NamedTuple):
    """Full naming convention audit report."""
    total_worms: int
    valid_count: int
    violation_count: int
    violations: list[ValidationResult]
    legacy_exceptions: list[str]
    summary: str


class DedupMatch(NamedTuple):
    """A single dedup match between two worms."""
    worm_a: str
    worm_b: str
    match_type: str          # "exact_signature", "similar_structure", "cross_category"
    similarity: float        # 0.0 to 1.0
    shared_methods: list[str]
    recommendation: str


class DedupReport(NamedTuple):
    """Full dedup analysis report."""
    total_pairs_checked: int
    exact_matches: list[DedupMatch]
    near_matches: list[DedupMatch]
    cross_category_duplicates: list[DedupMatch]
    summary: str


class LifecycleState:
    """Lifecycle states for a worm."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class LifecycleEntry(NamedTuple):
    """Lifecycle status for a single worm."""
    name: str
    state: str
    version: str
    priority: int
    spawn_count: int
    hours_since_last_spawn: (float | None)
    vitality_score: float
    deprecation_reason: (str | None)
    concerns: list[str]
    recommendation: str


class LifecycleReport(NamedTuple):
    """Full lifecycle audit report."""
    total_worms: int
    draft_count: int
    active_count: int
    deprecated_count: int
    retired_count: int
    stale_count: int
    entries: list[LifecycleEntry]
    summary: str


class GovernanceReport(NamedTuple):
    """Comprehensive worm governance report."""
    timestamp: str
    naming_report: NamingReport
    dedup_report: DedupReport
    lifecycle_report: LifecycleReport
    convergence_issues: list[str]
    category_health: dict[str, dict[str, Any]]
    overall_grade: str  # A, B, C, D, F


class WormGovernanceReport(NamedTuple):
    """Governance report for a single worm."""
    name: str
    naming: ValidationResult
    lifecycle: LifecycleEntry
    category: str
    source_file: str
    governance_score: float

# =====================================================================
# Naming Conventions
# =====================================================================

class WormNamingValidator:
    """
    Validates worm class names against established naming conventions.

    Rules:
    1. PascalCase (first letter uppercase, no underscores)
    2. Descriptive name (no generic names like "MyWorm", "Worm1")
    3. No version suffixes in class name (use VERSION attribute)
    4. No ALL_CAPS naming (legacy Z-suffix worms are grandfathered)
    5. Category-appropriate name (name should hint at purpose)

    Legacy exceptions: ALL_CAPS names from early codebase are grandfathered
    but flagged for eventual migration.
    """

    # -- PascalCase pattern --
    PASCALCASE_RE = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    # -- Forbidden generic names --
    FORBIDDEN_NAMES: set[str] = {
        "Worm", "MyWorm", "NewWorm", "TestWorm", "Worm1", "Worm2",
        "TempWorm", "BaseWorm", "SampleWorm", "ExampleWorm",
    }

    # -- Forbidden patterns in names --
    FORBIDDEN_PATTERNS: list[re.Pattern] = [
        re.compile(r'V\d+$', re.IGNORECASE),          # Trailing version: MyWormV2
        re.compile(r'_\d+$'),                          # Trailing underscore+number: MyWorm_2
    ]

    # -- Legacy ALL_CAPS exceptions (grandfathered but flagged) --
    LEGACY_ALL_CAPS: set[str] = {
        "SYSTEMZ", "WORMZ", "NETWORXZ", "PROCESSZ",
        "CLOCKZ", "DISKZ", "SMARTDISK", "METAZ",
        "ERRORZ", "HEALTHZ", "METRICZ", "TELEMETRYZ",
        "DEPENDZ",
    }

    # -- Legacy version-suffix exceptions --
    LEGACY_VERSION_SUFFIX: set[str] = {
        "MorphingWormV2",
        "OMNIV2",
    }

    # -- Category naming guidance --
    CATEGORY_PREFIX_HINTS: dict[str, str] = {
        "monitor": "Name should suggest observation or measurement (e.g., SystemZ, ProcessMonitor)",
        "security": "Name should suggest protection or auditing (e.g., VulnScanner, PortAuditor)",
        "diagnostic": "Name should suggest inspection or detection (e.g., NetworkDiag, ErrorScanner)",
        "analysis": "Name should suggest examination or reverse-engineering (e.g., BinaryAnalysis)",
        "orchestration": "Name should suggest coordination or management (e.g., MetaCluster, WormFleet)",
        "utility": "Name should suggest a tool or service (e.g., MemoryBus, PamsRecorder)",
        "backup": "Name should suggest persistence or recovery (e.g., StateSnapshotter, ColdArchivist)",
        "learning": "Name should suggest training or experimentation (e.g., RLTrainLoop, ABTestRunner)",
        "visualization": "Name should suggest rendering or presentation (e.g., DashboardGen, GraphRenderer)",
        "communication": "Name should suggest messaging or transport (e.g., MessageBroker, IPCBridge)",
        "container": "Name should suggest orchestration or management (e.g., ContainerOrch, ImageAuditor)",
        "config": "Name should suggest validation or management (e.g., ConfigLinter, SecretRotator)",
        "migration": "Name should suggest transformation or upgrade (e.g., CodeMigrator, SchemaVersioner)",
        "profiling": "Name should suggest measurement or analysis (e.g., CodeProfiler, GILContentionProbe)",
        "telemetry": "Name should suggest event or metric handling (e.g., SpanTracer, EventRouter)",
        "sync": "Name should suggest time or state coordination (e.g., CLOCKZ)",
        "ml": "Name should suggest model or learning (e.g., WORMZ_ML, SYSTEMZ_ML)",
    }

    def validate_name(self, name: str, category: str = "") -> ValidationResult:
        """
        Validate a worm class name against naming conventions.

        Args:
            name: The class name to validate
            category: Optional category for category-specific guidance

        Returns:
            ValidationResult with violations and suggestions
        """
        violations: list[str] = []
        suggestions: list[str] = []

        # -- Check forbidden names --
        if name in self.FORBIDDEN_NAMES:
            violations.append(f"Generic name '{name}' — use a descriptive name")

        # -- Check PascalCase --
        if name in self.LEGACY_ALL_CAPS:
            violations.append(
                f"ALL_CAPS name '{name}' violates PascalCase convention. "
                f"Consider renaming to PascalCase (e.g., '{self._to_pascalcase(name)}')"
            )

        if name in self.LEGACY_VERSION_SUFFIX:
            violations.append(
                f"Version suffix in name '{name}'. "
                f"Use VERSION attribute instead of embedding version in class name."
            )

        if name not in self.LEGACY_ALL_CAPS and name not in self.LEGACY_VERSION_SUFFIX:
            if not self.PASCALCASE_RE.match(name):
                violations.append(
                    f"Name '{name}' is not PascalCase. "
                    f"PascalCase names start with uppercase and contain no underscores."
                )

            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern.search(name):
                    violations.append(
                        f"Name '{name}' contains forbidden pattern '{pattern.pattern}'. "
                        f"Use version attribute instead."
                    )
                    break

        # -- Category guidance --
        if category:
            hint = self.CATEGORY_PREFIX_HINTS.get(category)
            if hint:
                suggestions.append(f"[{category}] {hint}")

        # -- Suggest rename for violations --
        if violations:
            suggested = self.suggest_rename(name)
            if suggested and suggested != name:
                suggestions.append(f"Suggested rename: '{suggested}'")

        return ValidationResult(
            name=name,
            valid=len(violations) == 0,
            violations=violations,
            suggestions=suggestions,
        )

    def validate_registry(self, registry: dict[str, dict]) -> NamingReport:
        """
        Validate all worms in the registry against naming conventions.

        Args:
            registry: WORM_REGISTRY dict

        Returns:
            NamingReport with all validation results
        """
        violations: list[ValidationResult] = []
        legacy: list[str] = []
        valid_count = 0

        for name, info in registry.items():
            category = info.get("category", "")
            result = self.validate_name(name, category)
            if not result.valid:
                violations.append(result)
                if name in self.LEGACY_ALL_CAPS or name in self.LEGACY_VERSION_SUFFIX:
                    legacy.append(name)
            else:
                valid_count += 1

        total = len(registry)
        summary = (
            f"{valid_count}/{total} worm names comply with PascalCase convention. "
            f"{len(violations)} violations found "
            f"({len(legacy)} grandfathered legacy exceptions)."
        )

        return NamingReport(
            total_worms=total,
            valid_count=valid_count,
            violation_count=len(violations),
            violations=violations,
            legacy_exceptions=legacy,
            summary=summary,
        )

    def suggest_rename(self, name: str) -> str:
        """Suggest a PascalCase rename for a non-compliant name."""
        if name in self.LEGACY_ALL_CAPS:
            return self._to_pascalcase(name) + "Worm"
        if name in self.LEGACY_VERSION_SUFFIX:
            base = re.sub(r'V\d+$', '', name, flags=re.IGNORECASE)
            return base
        return name

    @staticmethod
    def _to_pascalcase(name: str) -> str:
        """Convert an ALL_CAPS or snake_case name to PascalCase."""
        # Remove trailing Z
        clean = name.rstrip('Z')
        # Split on underscore and capitalize each part
        parts = clean.split('_')
        result = ''.join(p.capitalize() for p in parts if p)
        return result or name


# =====================================================================
# Dedup Analysis
# =====================================================================

class DedupAnalyzer:
    """
    Detects duplicate worm implementations.

    Uses three strategies:
    1. Exact signature match: Same method names and parameter signatures
    2. Similar structure: Overlapping method sets with similar names
    3. Cross-category duplication: Worms in different categories with same structure

    Does NOT use MD5 file hashing (too noisy for this codebase).

    Thread-safety: This class is stateless and safe for concurrent use.
    """

    # -- Minimum similarity threshold for flagging --
    NEAR_MATCH_THRESHOLD = 0.7

    # -- Methods to compare (the "public API" of a worm) --
    SIGNIFICANT_METHODS = frozenset({
        "execute", "run", "scan", "check", "analyze", "audit", "collect",
        "probe", "profile", "inspect", "monitor", "report", "validate",
        "detect", "measure", "track", "fix", "heal", "test", "verify",
        "publish", "subscribe", "deliver", "negotiate", "orchestrate",
        "get_summary", "get_status", "summarize",
    })

    def __init__(self):
        # Cache: class id -> {method_name: [param_names]}
        self._sig_cache: dict[int, dict[str, list[str]]] = {}

    def _get_method_signatures(self, cls: type) -> dict[str, list[str]]:
        """
        Extract method signatures from a class, with caching.

        Results are cached by class id to avoid O(n^2) inspect calls
        when comparing all worm pairs.

        Returns dict of {method_name: [param_names]}
        Only includes significant methods defined on the class itself (not inherited).
        """
        cls_id = id(cls)
        if cls_id in self._sig_cache:
            return self._sig_cache[cls_id]

        signatures: dict[str, list[str]] = {}
        for name in dir(cls):
            if name.startswith("_"):
                continue
            if name not in self.SIGNIFICANT_METHODS:
                continue

            method = getattr(cls, name, None)
            if not callable(method):
                continue

            try:
                sig = inspect.signature(method)
                params = [p.name for p in sig.parameters.values()
                          if p.name != "self" and p.name != "cls"]
                signatures[name] = params
            except (ValueError, TypeError):
                pass

        self._sig_cache[cls_id] = signatures
        return signatures

    def _jaccard_similarity(self, set_a: set[str], set_b: set[str]) -> float:
        """Jaccard similarity between two sets (intersection / union)."""
        if not set_a and not set_b:
            return 0.0
        union = set_a | set_b
        if not union:
            return 0.0
        return len(set_a & set_b) / len(union)

    def compare_worms(self, name_a: str, info_a: dict,
                      name_b: str, info_b: dict) -> (DedupMatch | None):
        """
        Compare two worms for potential duplication.

        Returns DedupMatch if similarity exceeds threshold, None otherwise.
        """
        cls_a = info_a.get("class")
        cls_b = info_b.get("class")

        if not cls_a or not cls_b:
            return None

        sigs_a = self._get_method_signatures(cls_a)
        sigs_b = self._get_method_signatures(cls_b)

        if not sigs_a and not sigs_b:
            return None

        methods_a = set(sigs_a.keys())
        methods_b = set(sigs_b.keys())

        similarity = self._jaccard_similarity(methods_a, methods_b)

        if similarity < self.NEAR_MATCH_THRESHOLD:
            return None

        shared_methods = sorted(methods_a & methods_b)

        cat_a = info_a.get("category", "")
        cat_b = info_b.get("category", "")
        same_category = cat_a == cat_b

        if similarity >= 1.0:
            match_type = "exact_signature"
            recommendation = (
                f"'{name_a}' and '{name_b}' have identical method signatures. "
                f"Consider consolidating into one worm with category aliases."
            )
        elif same_category:
            match_type = "similar_structure"
            recommendation = (
                f"'{name_a}' and '{name_b}' share {len(shared_methods)}/"
                f"{len(methods_a | methods_b)} methods ({similarity:.0%} similarity). "
                f"Review for overlap — they may be doing the same work."
            )
        else:
            match_type = "cross_category"
            recommendation = (
                f"'{name_a}' [{cat_a}] and '{name_b}' [{cat_b}] share "
                f"{len(shared_methods)} methods ({similarity:.0%} similarity). "
                f"Cross-category duplication detected — consider moving shared logic "
                f"to a utility worm."
            )

        return DedupMatch(
            worm_a=name_a,
            worm_b=name_b,
            match_type=match_type,
            similarity=round(similarity, 2),
            shared_methods=shared_methods,
            recommendation=recommendation,
        )

    def analyze_registry(self, registry: dict[str, dict]) -> DedupReport:
        """
        Analyze the entire registry for duplicate worms.

        Caches method signatures per class to avoid O(n^2) inspect overhead.

        Args:
            registry: WORM_REGISTRY dict

        Returns:
            DedupReport with all matches
        """
        names = list(registry.keys())
        exact_matches: list[DedupMatch] = []
        near_matches: list[DedupMatch] = []
        cross_cat: list[DedupMatch] = []
        total_pairs = 0

        # Pre-compute signatures once per class
        for info in registry.values():
            cls = info.get("class")
            if cls:
                self._get_method_signatures(cls)

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                total_pairs += 1
                match = self.compare_worms(
                    names[i], registry[names[i]],
                    names[j], registry[names[j]],
                )
                if match is None:
                    continue

                if match.match_type == "exact_signature":
                    exact_matches.append(match)
                elif match.match_type == "cross_category":
                    cross_cat.append(match)
                else:
                    near_matches.append(match)

        summary = (
            f"Checked {total_pairs} worm pairs: "
            f"{len(exact_matches)} exact signature matches, "
            f"{len(near_matches)} near matches, "
            f"{len(cross_cat)} cross-category duplicates."
        )

        return DedupReport(
            total_pairs_checked=total_pairs,
            exact_matches=exact_matches,
            near_matches=near_matches,
            cross_category_duplicates=cross_cat,
            summary=summary,
        )


# =====================================================================
# Lifecycle Management
# =====================================================================

class LifecycleManager:
    """
    Manages worm lifecycle state and provides vitality scoring.

    Lifecycle states (derived from version):
        - DRAFT: version == "0.0.0" (pre-release, experimental)
        - ACTIVE: version >= "1.0.0" (stable, ready for production)
        - DEPRECATED: lifecycle_state in registry is "deprecated"
        - RETIRED: lifecycle_state in registry is "retired"

    Vitality scoring (0.0 - 10.0):
        - Version maturity: 0.0 for v0.0.0, 2.5 for v0.x, 5.0 for v1.x, 7.5 for v2.x+
        - Priority contribution: priority / 10 * 3.0 (max 3.0)
        - Spawn activity: spawn_count > 0 gets 2.0, else 0.0
        - Total: version_score + priority_score + spawn_score (max 10.0)
    """

    # -- How long without spawning before a worm is "stale" (hours) --
    STALE_HOURS = 72.0

    # -- Minimum spawns to be considered "active" --
    MIN_ACTIVE_SPAWNS = 1

    def get_state(self, name: str, info: dict) -> str:
        """Determine lifecycle state from registry entry."""
        # Check explicit lifecycle state first
        explicit_state = info.get("lifecycle_state")
        if explicit_state in (LifecycleState.DEPRECATED, LifecycleState.RETIRED):
            return explicit_state

        # Derive from version
        version = info.get("version", "0.0.0")
        if version == "0.0.0":
            return LifecycleState.DRAFT

        return LifecycleState.ACTIVE

    def get_vitality_score(self, name: str, info: dict) -> float:
        """
        Compute vitality score for a worm (0.0 - 10.0).

        Factors:
        - Version maturity: 0-5 points
        - Priority: 0-3 points (priority/10 * 3)
        - Spawn activity: 0-2 points (has been spawned at least once)
        """
        version = info.get("version", "0.0.0")
        priority = info.get("priority", 5)
        spawn_count = info.get("spawn_count", 0)

        # Version maturity score
        if version == "0.0.0":
            version_score = 0.0
        elif version.startswith("0."):
            version_score = 2.5
        elif version.startswith("1."):
            version_score = 5.0
        elif version.startswith("2."):
            version_score = 7.5
        else:
            version_score = 5.0

        # Priority contribution (max 3.0)
        priority_score = (priority / 10.0) * 3.0

        # Spawn activity (max 2.0)
        spawn_score = 2.0 if spawn_count >= self.MIN_ACTIVE_SPAWNS else 0.0

        return min(10.0, version_score + priority_score + spawn_score)

    def get_stale_worms(self, registry: dict[str, dict]) -> list[str]:
        """
        Get worms that haven't been spawned recently.

        A worm is stale if it has never been spawned, or if it was last
        spawned more than STALE_HOURS ago.
        """
        now = datetime.now()
        stale: list[str] = []

        for name, info in registry.items():
            spawn_count = info.get("spawn_count", 0)
            last_spawned = info.get("last_spawned")

            if spawn_count == 0:
                stale.append(name)
                continue

            if last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned)
                    hours_since = (now - last_time).total_seconds() / 3600
                    if hours_since > self.STALE_HOURS:
                        stale.append(name)
                except (ValueError, TypeError):
                    stale.append(name)

        return stale

    def analyze_registry(self, registry: dict[str, dict]) -> LifecycleReport:
        """
        Analyze lifecycle state of all worms in registry.

        Args:
            registry: WORM_REGISTRY dict

        Returns:
            LifecycleReport with per-worm entries and summary
        """
        now = datetime.now()
        entries: list[LifecycleEntry] = []
        state_counts: dict[str, int] = {s: 0 for s in [
            LifecycleState.DRAFT, LifecycleState.ACTIVE,
            LifecycleState.DEPRECATED, LifecycleState.RETIRED,
        ]}

        for name, info in registry.items():
            state = self.get_state(name, info)
            state_counts[state] = state_counts.get(state, 0) + 1

            spawn_count = info.get("spawn_count", 0)
            last_spawned = info.get("last_spawned")
            hours_since: (float | None) = None
            if last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned)
                    hours_since = (now - last_time).total_seconds() / 3600
                except (ValueError, TypeError):
                    pass

            vitality = self.get_vitality_score(name, info)
            deprecation_reason = info.get("deprecation_reason")

            concerns: list[str] = []
            if state == LifecycleState.DRAFT:
                concerns.append("Pre-release (v0.0.0) — not ready for production")
            if spawn_count == 0:
                concerns.append("Never spawned — no production usage")
            if vitality < 3.0:
                concerns.append("Low vitality score — consider deprecation")
            if deprecation_reason:
                concerns.append(f"Deprecated: {deprecation_reason}")

            recommendation = self._recommend_action(name, state, vitality, spawn_count)

            entries.append(LifecycleEntry(
                name=name,
                state=state,
                version=info.get("version", "0.0.0"),
                priority=info.get("priority", 5),
                spawn_count=spawn_count,
                hours_since_last_spawn=round(hours_since, 1) if hours_since else None,
                vitality_score=round(vitality, 1),
                deprecation_reason=deprecation_reason,
                concerns=concerns,
                recommendation=recommendation,
            ))

        stale = self.get_stale_worms(registry)

        summary = (
            f"{len(registry)} worms: "
            f"{state_counts.get(LifecycleState.ACTIVE, 0)} active, "
            f"{state_counts.get(LifecycleState.DRAFT, 0)} draft, "
            f"{state_counts.get(LifecycleState.DEPRECATED, 0)} deprecated, "
            f"{state_counts.get(LifecycleState.RETIRED, 0)} retired. "
            f"{len(stale)} stale (never spawned or >{self.STALE_HOURS}h since last spawn)."
        )

        return LifecycleReport(
            total_worms=len(registry),
            draft_count=state_counts.get(LifecycleState.DRAFT, 0),
            active_count=state_counts.get(LifecycleState.ACTIVE, 0),
            deprecated_count=state_counts.get(LifecycleState.DEPRECATED, 0),
            retired_count=state_counts.get(LifecycleState.RETIRED, 0),
            stale_count=len(stale),
            entries=sorted(entries, key=lambda e: e.vitality_score),
            summary=summary,
        )

    @staticmethod
    def deprecate(name: str, registry: dict[str, dict],
                  reason: str = "No longer needed") -> bool:
        """Mark a worm as deprecated in the registry."""
        if name not in registry:
            return False
        registry[name]["lifecycle_state"] = LifecycleState.DEPRECATED
        registry[name]["deprecation_reason"] = reason
        registry[name]["lifecycle_changed_at"] = datetime.now().isoformat()
        _log.info("Deprecated worm '%s': %s", name, reason)
        return True

    @staticmethod
    def retire(name: str, registry: dict[str, dict]) -> bool:
        """Mark a worm as retired (removed from active registry)."""
        if name not in registry:
            return False
        registry[name]["lifecycle_state"] = LifecycleState.RETIRED
        registry[name]["lifecycle_changed_at"] = datetime.now().isoformat()
        _log.info("Retired worm '%s'", name)
        return True

    @staticmethod
    def _recommend_action(name: str, state: str, vitality: float,
                          spawn_count: int) -> str:
        """Generate a lifecycle recommendation."""
        if state == LifecycleState.RETIRED:
            return "Remove from registry"
        if state == LifecycleState.DEPRECATED:
            return "Schedule removal or re-evaluate"
        if state == LifecycleState.DRAFT:
            if spawn_count == 0:
                return "Test and promote to v1.0.0, or retire if experimental"
            return "Promote to v1.0.0 when stable"
        # ACTIVE
        if vitality < 5.0:
            return "Improve vitality (increase priority, spawn more, bump version)"
        if spawn_count == 0:
            return "Ready for production — schedule first spawn"
        return "Healthy — no action needed"


# =====================================================================
# Governance Orchestrator
# =====================================================================

class WormGovernor:
    """
    Governance orchestrator combining naming, dedup, and lifecycle analysis.

    Provides a single entry point for comprehensive governance reports.
    """

    # -- Convergence analysis findings (from 8-provider audit) --
    CONVERGENCE_FINDINGS = [
        "Nuitka onefile mode breaks discover_worms() — worm registry fails in compiled EXEs",
        "Global WORM_REGISTRY dict is shared mutable state — thread safety relies on RLock",
        "Zero spawns across all worm types — SpawnDiversityEngine configured but unused",
        "4 worms at v0.0.0 (pre-release) — DiagnosticWorm, FastErrorScanner, OSCongruency, WormFleet",
        "No dedup detection process — potential for duplicate worm implementations",
        "No lifecycle management — no deprecation or retirement process",
        "48/77 worms originate from single ECOSYSTEM_EXPANSION.py file",
        "All 77 worms imported at startup — lazy-loading not implemented",
    ]

    def __init__(self):
        self.naming_validator = WormNamingValidator()
        self.dedup_analyzer = DedupAnalyzer()
        self.lifecycle_manager = LifecycleManager()
        self._lock = threading.Lock()

    def govern(self, registry: dict[str, dict]) -> GovernanceReport:
        """
        Run a full governance audit on the worm registry.

        Takes a snapshot of the registry under lock to ensure
        consistent reads during analysis.

        Args:
            registry: WORM_REGISTRY dict

        Returns:
            GovernanceReport with naming, dedup, lifecycle, and convergence analysis
        """
        # Snapshot under lock to prevent dict-mutation during iteration
        with self._lock:
            snapshot = dict(registry)

        naming = self.naming_validator.validate_registry(snapshot)
        dedup = self.dedup_analyzer.analyze_registry(snapshot)
        lifecycle = self.lifecycle_manager.analyze_registry(snapshot)
        category_health = self._compute_category_health(snapshot)

        # Overall grade: weighted average of sub-scores
        naming_grade = naming.valid_count / max(naming.total_worms, 1)
        dedup_grade = 1.0 - (len(dedup.exact_matches) + len(dedup.near_matches)) / max(len(registry), 1) * 2
        dedup_grade = max(0.0, dedup_grade)
        lifecycle_grade = lifecycle.active_count / max(lifecycle.total_worms, 1)

        overall = naming_grade * 0.4 + dedup_grade * 0.3 + lifecycle_grade * 0.3
        grade = self._score_to_grade(overall)

        # Flag convergence issues relevant to current state
        convergence_issues = self._assess_convergence_issues(registry)

        return GovernanceReport(
            timestamp=datetime.now().isoformat(),
            naming_report=naming,
            dedup_report=dedup,
            lifecycle_report=lifecycle,
            convergence_issues=convergence_issues,
            category_health=category_health,
            overall_grade=grade,
        )

    def govern_worm(self, name: str, info: dict) -> (WormGovernanceReport | None):
        """
        Run governance analysis on a single worm.

        Args:
            name: Worm class name
            info: Registry entry dict

        Returns:
            WormGovernanceReport or None if worm not in registry
        """
        if not info:
            return None

        naming = self.naming_validator.validate_name(
            name, info.get("category", "")
        )
        lifecycle = LifecycleEntry(
            name=name,
            state=self.lifecycle_manager.get_state(name, info),
            version=info.get("version", "0.0.0"),
            priority=info.get("priority", 5),
            spawn_count=info.get("spawn_count", 0),
            hours_since_last_spawn=None,  # Not needed per-worm
            vitality_score=round(self.lifecycle_manager.get_vitality_score(name, info), 1),
            deprecation_reason=info.get("deprecation_reason"),
            concerns=[],
            recommendation="",
        )

        # Compute single-worm governance score
        naming_score = 1.0 if naming.valid else 0.0
        vitality = lifecycle.vitality_score / 10.0
        governance_score = round((naming_score * 0.3 + vitality * 0.7) * 10.0, 1)

        return WormGovernanceReport(
            name=name,
            naming=naming,
            lifecycle=lifecycle,
            category=info.get("category", "utility"),
            source_file=info.get("source_file", ""),
            governance_score=governance_score,
        )

    def get_category_health(self, registry: dict[str, dict],
                            category: str) -> dict[str, Any]:
        """Get health metrics for a specific category."""
        worms = {
            n: i for n, i in registry.items()
            if i.get("category") == category
        }
        if not worms:
            return {"category": category, "count": 0, "health": 0.0}

        vitality_scores = [
            self.lifecycle_manager.get_vitality_score(n, i)
            for n, i in worms.items()
        ]
        naming_valid = sum(
            1 for n in worms
            if self.naming_validator.validate_name(n).valid
        )
        avg_vitality = sum(vitality_scores) / len(vitality_scores)
        naming_ratio = naming_valid / len(worms)

        health = round((avg_vitality / 10.0) * 0.5 + naming_ratio * 0.5, 2)

        return {
            "category": category,
            "count": len(worms),
            "avg_vitality": round(avg_vitality, 1),
            "naming_compliance": f"{naming_valid}/{len(worms)}",
            "draft_count": sum(
                1 for n, i in worms.items()
                if self.lifecycle_manager.get_state(n, i) == LifecycleState.DRAFT
            ),
            "health": health,
        }

    def _compute_category_health(self, registry: dict[str, dict]) -> dict[str, dict[str, Any]]:
        """Compute health metrics for all categories."""
        categories = set(
            i.get("category", "utility") for i in registry.values()
        )
        return {
            cat: self.get_category_health(registry, cat)
            for cat in sorted(categories)
        }

    def _assess_convergence_issues(self, registry: dict[str, dict]) -> list[str]:
        """Assess which convergence analysis findings still apply."""
        issues = list(self.CONVERGENCE_FINDINGS)  # Copy all findings

        # Some findings may have been partially addressed
        # Check if any worms have been spawned
        total_spawns = sum(i.get("spawn_count", 0) for i in registry.values())
        if total_spawns > 0:
            issues = [i for i in issues if "Zero spawns" not in i]

        # Check draft worm count
        draft_count = sum(
            1 for i in registry.values()
            if i.get("version", "0.0.0") == "0.0.0"
        )
        if draft_count == 0:
            issues = [i for i in issues if "v0.0.0" not in i]

        # Check ECOSYSTEM_EXPANSION.py deprecation
        expansion_count = sum(
            1 for i in registry.values()
            if "ECOSYSTEM_EXPANSION" in i.get("source_file", "")
        )
        if expansion_count == 0:
            issues = [i for i in issues if "ECOSYSTEM_EXPANSION" not in i]

        return issues

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert a 0.0-1.0 score to a letter grade."""
        if score >= 0.9:
            return "A"
        if score >= 0.8:
            return "B"
        if score >= 0.6:
            return "C"
        if score >= 0.4:
            return "D"
        return "F"


# =====================================================================
# Convenience Functions
# =====================================================================

def run_governance_audit() -> GovernanceReport:
    """
    Run a full governance audit on the current WORM_REGISTRY.

    Convenience function that discovers worms, then runs the full
    governance pipeline.

    Returns:
        GovernanceReport with all findings
    """
    from CORE.worm_registry import discover_worms, WORM_REGISTRY
    discover_worms()
    governor = WormGovernor()
    return governor.govern(WORM_REGISTRY)


def print_governance_report(report: GovernanceReport) -> None:
    """Print a human-readable governance report to stdout."""
    print("=" * 60)
    print(f"WORM GOVERNANCE REPORT — {report.timestamp[:19]}")
    print("=" * 60)
    print(f"Overall Grade: {report.overall_grade}")
    print()

    # Naming
    n = report.naming_report
    print(f"[Naming] {n.summary}")
    for v in n.violations:
        print(f"  ! {v.name}: {'; '.join(v.violations)}")
        for s in v.suggestions:
            print(f"    -> {s}")

    print()

    # Dedup
    d = report.dedup_report
    print(f"[Dedup] {d.summary}")
    for m in d.exact_matches + d.near_matches + d.cross_category_duplicates:
        print(f"  * {m.worm_a} <-> {m.worm_b} ({m.match_type}, {m.similarity:.0%})")
        print(f"    {m.recommendation}")

    print()

    # Lifecycle
    lc = report.lifecycle_report
    print(f"[Lifecycle] {lc.summary}")
    print(f"  Bottom {min(5, len(lc.entries))} (lowest vitality):")
    for e in lc.entries[:5]:
        print(f"  {e.state:10s} v{e.version:5s} p={e.priority} vitality={e.vitality_score:.1f}  {e.name}")
        for c in e.concerns[:2]:
            print(f"    ! {c}")
    print(f"  Top {min(3, len(lc.entries))} (highest vitality):")
    for e in lc.entries[-3:]:
        print(f"  {e.state:10s} v{e.version:5s} p={e.priority} vitality={e.vitality_score:.1f}  {e.name}")

    print()

    # Convergence
    print(f"[Convergence] {len(report.convergence_issues)} outstanding issues:")
    for issue in report.convergence_issues:
        print(f"  * {issue}")

    print()

    # Category health
    print("[Category Health]")
    for cat, health in sorted(report.category_health.items()):
        bar = "=" * int(health["health"] * 10)
        print(f"  {cat:20s} {health['count']:2d} worms |{'':1s}{bar:<10s}| health={health['health']:.2f}")

    print("=" * 60)
