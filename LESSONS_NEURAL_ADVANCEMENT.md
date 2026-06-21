# LESSONS — Neural Advancement Realignment (June 4, 2026)

## Lesson 1: MetaCognitionWorm — Always Observe Before Adapting

**Issue:** The ecosystem had no self-reflection mechanism. Errors repeated without learning.

**Lesson Learned:**
- **OBSERVE → ANALYZE → ADAPT → VALIDATE** must be the standard loop for all decisions
- MetaCognitionWorm records every execution observation (success/error/timeout)
- Error patterns are clustered and scored for recurrence
- Strategy adaptation requires at least 15% confidence improvement before switching
- Validation confirms whether adaptations actually improved performance

**Implementation:** `src/CORE/WORMS/expansion/meta_cognition.py`
- `MetaCognitionWorm` (priority=7, cooldown=90s)
- `MetaCognitionAgent` (priority=9, registered in agent_registry)

**Key Rules:**
1. Never adapt strategy without analyzing historical error patterns first
2. Confidence models must be updated after every observation
3. Adaptations must be validated before being committed permanently
4. Strategy scores decay over time to allow re-exploration

---

## Lesson 2: EvolutionEngine — Tournament Selection Beats Random Search

**Issue:** HYDRAMETA genetic algorithms existed but weren't practical for per-worm parameter optimization.

**Lesson Learned:**
- Tournament selection (pick N random, return fittest) provides better diversity than rank-based selection
- Elitism (keep best N genomes unchanged) prevents fitness regression
- Adaptive crossover/mutation rates improve convergence speed
- CurativePool governance must gate every evolution phase (evaluate, crossover, mutate)
- Population size of 50 with 5 elites works well for most parameter spaces

**Implementation:** `src/CORE/WORMS/expansion/evolution.py`
- `EvolutionEngine` (priority=6, cooldown=120s)
- `GeneticOptimizer` (priority=5, cooldown=180s)

**Key Rules:**
1. Always initialize population within gene bounds
2. Crossover rate should start at 0.7 and adapt based on population diversity
3. Mutation rate should start at 0.1 and decrease as fitness plateaus
4. Never replace the entire population — preserve elites

---

## Lesson 3: DreamingModule — Offline Simulation Prevents Live Catastrophes

**Issue:** Policy improvements were tested live, risking ecosystem stability.

**Lesson Learned:**
- RECALL → SIMULATE → EVALUATE → INTEGRATE pipeline prevents live risk
- Dreams must be scored on quality (state coverage), creativity (novelty), and coherence (consistency)
- Only integrate dreams with composite score above threshold
- HypnagogicSynthesizer blends cross-domain patterns for creative solutions
- Dream creativity_factor of 0.3 balances exploration vs. exploitation

**Implementation:** `src/CORE/WORMS/expansion/dreaming.py`
- `DreamingModule` (priority=5, cooldown=180s)
- `HypnagogicSynthesizer` (priority=4, cooldown=300s)

**Key Rules:**
1. Never apply policy changes without dreaming first
2. Score dreams on quality (40%), creativity (30%), coherence (30%)
3. Hypnagogic blends require at least 2 domains
4. Auto-integrate only the best dream per cycle

---

## Lesson 4: CurativePool Governance — Gate Every ML Decision

**Issue:** ML pipelines ran unchecked without scope validation, necessity judgment, or emotional attunement.

**Lesson Learned:**
- Every HYDRA pipeline stage must pass through CurativePool.evaluate_action()
- ScopeValidator checks if the action fits within ecosystem boundaries
- NecessityJudge determines if the action is actually needed
- EmotionDetector ensures actions are emotionally attuned
- Blocked stages should report block_reasons clearly

**Implementation:** Wired into `src/ORCHESTRATION/hydra_bridge.py`
- HydraBridge v2.0.0 with CurativePool governance
- Neural advancement status reported in get_status()

**Key Rules:**
1. Never execute a pipeline stage without CurativePool governance
2. Blocked stages must be logged and reported
3. Evolution gates must pass CurativePool before crossover/mutation
4. Dreaming cycles must pass CurativePool before integration

---

## Lesson 5: G: Drive CI — Always Verify Mount Before Operations

**Issue:** G: drive CI operations failed silently when the drive wasn't mounted.

**Lesson Learned:**
- Always check G: drive mount status before CI operations
- Write test before trusting drive availability
- Daily health checks via scheduled CI workflow
- GOSP project requires its own CI workflow for Python 3.14t compatibility

**Implementation:** `/g/source-of-truth/GOSP/.github/workflows/`
- `gosp-ci.yml` — GOSP Python 3.14t CI pipeline
- `ci-status.yml` — Daily G: drive accessibility check

**Key Rules:**
1. Always `mkdir -p` before writing to subdirectories
2. Verify write test before any CI operation
3. G: drive has 477G total / 364G available — sufficient for CI

---

## Session Actions Recorded (June 4, 2026)

1. **Created** MetaCognitionWorm + MetaCognitionAgent (493 lines)
2. **Created** EvolutionEngine + GeneticOptimizer (412 lines)
3. **Created** DreamingModule + HypnagogicSynthesizer (511 lines)
4. **Wired** all 5 worms into `expansion/__init__.py` and WORM_REGISTRY
5. **Wired** MetaCognitionAgent into AGENT_REGISTRY (priority=9)
6. **Wired** CurativePool governance into HydraBridge v2.0.0
7. **Wired** MetaCognition + Evolution + Dreaming into HYDRA pipeline
8. **Converted** G:/source-of-truth/GOSP/ to Python 3.14t project
9. **Created** GOSP CI workflow + G: drive status check
10. **Created** LESSONS_NEURAL_ADVANCEMENT.md
11. **Verified** all 5 worms + 1 agent registered (83 total worms, 5 new)

**Worm Registry Status:** 83 → 88 worms (5 new neural advancement worms)
