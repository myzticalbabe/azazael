# Architecture Decision Records

**Version:** 1.0.0  
**Date:** 2026-02-11

---

## ADR Index

| ID | Title | Status |
|----|-------|--------|
| ADR-001 | Tiered Architecture Design | ACCEPTED |
| ADR-002 | WORMZ Agent Design | ACCEPTED |
| ADR-003 | HYDRA Sequential Processing | ACCEPTED |
| ADR-004 | METAWORMS Composition | ACCEPTED |
| ADR-005 | HYDRAMETA Genetic Algorithm | ACCEPTED |
| ADR-006 | HORUS Animation System | ACCEPTED |
| ADR-007 | TERENCE Pattern Matching | ACCEPTED |
| ADR-008 | KLINK CLI Design | ACCEPTED |
| ADR-009 | Entry-point logging hygiene | ACCEPTED |

---

## ADR-001: Tiered Architecture Design

**Status:** ACCEPTED

### Context

The Azazael Ecosystem requires a structured approach to component organization that supports:
- Clear separation of concerns
- Scalable execution model
- Modular upgrades
- Cross-tier communication

### Decision

Implement a 7-tier hierarchical architecture:

| Tier | Name | Purpose |
|------|------|---------|
| 5 | DISTILLATION | Knowledge synthesis |
| 4 | HYDRAMETA | ML optimization |
| 3 | METAWORMS | Orchestration |
| 2 | CLUSTERWORMS | Coordinated execution |
| 1 | WORMS | Functional execution |
| 0 | CONCURRENCY | Parallel processing |
| -1 | OS_CONGRUENCY | OS integration |

### Consequences

**Positive:**
- Clear component boundaries
- Independent tier upgrades
- Focused testing strategies

**Negative:**
- Cross-tier dependencies require careful management
- Initial design complexity

---

## ADR-002: WORMZ Agent Design

**Status:** ACCEPTED

### Context

The system requires specialized functional agents for different system domains.

### Decision

Implement 6 functional worms:

| Worm | Domain | Responsibility |
|------|--------|----------------|
| WORMZ | Core | Discovery & crawling |
| SYSTEMZ | System | OS information |
| PROCESSZ | Processes | Process management |
| DISKZ | Storage | Disk analysis |
| CLOCKZ | Time | Synchronization |
| NETWORXZ | Network | Network analysis |

### Consequences

**Positive:**
- Focused responsibility per worm
- Easy to add new worms
- Clear testing boundaries

---

## ADR-003: HYDRA Sequential Processing

**Status:** ACCEPTED

### Context

ML pipeline requires structured, adaptive execution.

### Decision

Implement 6-stage sequential pipeline:

```
DISCOVER → ANALYZE → OPTIMIZE → VALIDATE → DEPLOY → FEEDBACK
```

Each stage:
- Receives input from previous stage
- Produces output for next stage
- Supports adaptive parameter tuning
- Can be executed independently

### Consequences

**Positive:**
- Clear data flow
- Stage-level error handling
- Parallel stage development

---

## ADR-004: METAWORMS Composition

**Status:** ACCEPTED

### Context

System requires higher-level static analysis and quality assurance.

### Decision

Implement 11 metaworms for Tier 3:

| Metaworm | Function |
|----------|----------|
| ERRORZ | Error pattern detection |
| TRIMZ | Content trimming |
| METAZ | Metadata extraction |
| DEPENDZ | Dependency mapping |
| VALIDZ | Syntax validation |
| DEADZ | Dead code detection |
| METRICZ | Code metrics |
| LOGZ | Log analysis |
| CHANGEZ | Change tracking |
| OPTIMIZ | Performance optimization |
| HEALTHZ | Health monitoring |

### Consequences

**Positive:**
- Comprehensive code analysis
- Modular improvement system

---

## ADR-005: HYDRAMETA Genetic Algorithm

**Status:** ACCEPTED

### Context

System requires adaptive optimization based on performance data.

### Decision

Implement genetic algorithm with:
- Population: 50-100 individuals
- Crossover rate: 0.8
- Mutation rate: 0.1 (Gaussian)
- Elitism: Top 10%
- Selection: Tournament method

### Consequences

**Positive:**
- Global optimization
- Automatic parameter tuning

**Negative:**
- Computational overhead
- Requires historical data

---

## ADR-006: HORUS Animation System

**Status:** ACCEPTED

### Context

Visual feedback requires engaging, informative animations.

### Decision

Implement 24 animation protocols:

| Category | Animations |
|----------|------------|
| Text | Glitch, Typewriter, Marquee |
| Glow | Neon Pulse, Shimmer |
| Motion | Slide, Bounce, Shake, Zoom |
| Background | Particles, Matrix Rain, Hex Grid |

### Consequences

**Positive:**
- Rich visual feedback
- Configurable effects

---

## ADR-007: TERENCE Pattern Matching

**Status:** ACCEPTED

### Context

Code quality requires automated pattern detection and fixing.

### Decision

Implement 26 fix patterns across categories:

| Category | Count | Examples |
|----------|-------|----------|
| Syntax | 6 | bare except, missing docstrings |
| Style | 8 | print statements, tab indentation |
| Security | 4 | hardcoded secrets |
| Performance | 8 | inefficient string concat |

### Consequences

**Positive:**
- Automated code improvement
- Consistent style enforcement

---

## ADR-008: KLINK CLI Design

**Status:** ACCEPTED

### Context

System requires unified command-line access.

### Decision

Implement hierarchical command structure:

```
klink <component> <action> [options]
```

Commands:
- `status` - Show ecosystem status
- `worms` - Run WORMZ
- `hydra` - Run HYDRA
- `metaworms` - Run METAWORMS
- `terence` - Run error resolution
- `horus` - Launch output formatter
- `all` - Full ecosystem run

### Consequences

**Positive:**
- Consistent interface
- Easy to extend

---

---

## ADR-009: Entry-point Logging Hygiene

**Status:** ACCEPTED  
**Date:** 2026-09-21

### Context

Entry points that import the worm registry used to quiet its one-INFO-per-worm
import chatter with `logging.disable(logging.CRITICAL)`. That switch is
process-wide: it silences WARNING and ERROR too. On 2026-09-21 the
proprioception gate refused to write for ~30 hours and emitted a WARNING from
inside exactly such a process, so the refusal read as success and nothing was
red. A sweep found ten entry points carrying the same blanket switch.

### Decision

1. **No entry point may call `logging.disable(...)`.** Silence noisy loggers by
   NAME instead, via `CORE.log_hygiene.quiet_noisy_loggers()`, which sets the
   known-chatty loggers (currently `worm_registry`) to WARNING and leaves
   WARNING+ live for the rest of the process.
2. **The canonical helper lives in `src/CORE/log_hygiene.py`** and imports only
   stdlib `logging`, so it is safe to import before the rest of CORE. Entry
   points reach it via the standard src path:

   ```python
   sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
   from CORE.log_hygiene import quiet_noisy_loggers
   quiet_noisy_loggers()
   ```

3. **No hardcoded user paths for the src root.** Entry points resolve src/
   from their own location (above) rather than `C:/Users/<user>/...`, so the
   same file works from Windows and from WSL (`/mnt/c/...`).
4. **A refusal must be visible.** A script that drives
   `SpineCycleWorm.run_cycle(apply=True)` must read `rep.get("skipped")` and
   report it; a refusal is not a success and must not print a success-shaped
   line.

### Enforcement

- `tests/test_logging_hygiene_sweep.py` fails on any AST-level `logging.disable`
  in `scripts/` or `src/`, and confines module-scope `logging.basicConfig` in
  `src/` to a documented allowlist.
- `tests/test_entry_point_smoke.py` runpy-executes every entry point and asserts
  logging is left on and `worm_registry` is quieted by name.
- `tests/test_spine_caller_refusals.py` fails if a gate caller omits the
  `skipped` check.

### Consequences

**Positive:** operator warnings survive in every scheduled process; a stalled
loop cannot read as green; the noisy-logger list has one home.

**Negative:** the known-noisy logger list must be maintained when a new chatter
appears (one edit, in one file).

---

*Generated: 2026-02-11*
