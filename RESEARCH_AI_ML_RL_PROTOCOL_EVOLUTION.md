# AI/ML/RL Protocol Evolution for Agent Self-Improvement

**Date:** 2026-06-03
**Scope:** Gap analysis + actionable protocol design for evolving Azazael agents
**Status:** Research complete — implementation roadmap below

---

## Executive Summary

Azazael has a solid ML foundation (Q-learning, IsolationForest, SchemaAwareFeatureExtractor, temporal CV, SpawnDiversityEngine) but lacks **6 critical capabilities** for true agent evolution:

1. **Preference-based learning** (RLHF/DPO/GRPO) — agents can't learn "better vs worse"
2. **Cross-agent knowledge transfer** — each worm learns in isolation
3. **Experience replay with intrinsic motivation** — no curiosity-driven exploration
4. **Genetic/evolutionary optimization** — worm configs are static
5. **Curriculum learning** — no progressive difficulty scaling
6. **Self-modifying code generation** — MORPHING_WORM creates stubs, doesn't learn

---

## 1. Current State: What Exists

### 1.1 RL/ML Infrastructure (well-built)

| Component | Location | Capability |
|-----------|----------|------------|
| `RLTrainLoop` | `expansion/learning.py` | Q-learning, epsilon-greedy, hyperparameter tuning, temporal CV |
| `DataPipelineWorm` | `expansion/learning.py` | ETL from LocalMemoryStore, train/val/test split, schema discovery |
| `SchemaAwareFeatureExtractor` | `expansion/learning.py` | Typed feature vectors from data blobs, one-hot encoding |
| `FeatureEngineer` | `expansion/learning.py` | Normalization, imputation, worm feature extraction |
| `ModelVersioner` | `expansion/learning.py` | Version tracking, rollback, history |
| `ABTestRunner` | `expansion/learning.py` | Split-test framework |
| `SYSTEMZ_ML` | `SYSTEMZ_ML.py` | IsolationForest anomaly detection |
| `WORMZ_ML` | `WORMZ_ML.py` | TF-IDF + RandomForest classification |
| `ScheduledTrainingWorm` | `expansion/scheduling.py` | Automated ML pipeline on schedule |
| `SpawnDiversityEngine` | `worm_registry.py` | Category rotation, staleness, weighted selection |
| `MorphingWorm` | `MORPHING_WORM.py` | Self-modifying error detection genomes |

### 1.2 Agent Infrastructure

| Component | Location | Capability |
|-----------|----------|------------|
| `FreeThreadedAgent` | `Agent.py` | Base class, stats, sub-agents, PAMS recording |
| `AgentPool` | `AgentPool.py` | Pool management |
| `WORM_REGISTRY` | `worm_registry.py` | 74 registered worms, category/priority/cooldown |
| `LocalMemoryStore` | `local_memory.py` | 1,122 entries, 409 sessions, FTS5 search |
| `PAMS` | `PAMS/` | 133 memories, 51 insights, cross-references |

### 1.3 Key Gaps Identified

| Gap | Impact | Effort |
|-----|--------|--------|
| No preference learning (DPO/GRPO) | Agents can't learn relative quality | Medium |
| No cross-agent knowledge transfer | Each worm learns in isolation | Low |
| No experience replay | Training data is ephemeral | Low |
| No genetic optimization | Worm configs are static | Medium |
| No curriculum learning | No progressive difficulty | Medium |
| No intrinsic motivation | No curiosity-driven exploration | High |
| Q-table won't scale | Feature space too large for tabular RL | Medium |
| No human-in-the-loop | No active learning from feedback | Low |

---

## 2. Priority 1: Preference-Based Learning (DPO/GRPO)

### 2.1 Problem

The current `_compute_reward()` in `RLTrainLoop` is binary:
```python
reward = 1.0 if success else -1.0
if duration:
    reward -= duration / 10000.0
```

This doesn't capture **relative quality** — two successful worm runs may differ significantly in effectiveness, but both get reward ≈ 1.0.

### 2.2 Solution: DPO for Worm Selection

**Direct Preference Optimization (DPO)** learns from pairwise comparisons without explicit reward models.

**Protocol:**
```python
class WormPreferenceLearner:
    """Learns worm preferences from execution pairs.
    
    When two worms complete similar tasks, record which performed better.
    Uses DPO-style loss to update a preference model.
    """
    
    def record_preference(self, 
                          task_context: Dict,
                          chosen_worm: str,    # better performer
                          rejected_worm: str,  # worse performer
                          metrics: Dict):
        """Record a preference pair from execution results."""
        pass
    
    def compute_dpo_loss(self, 
                         chosen_rewards: List[float],
                         rejected_rewards: List[float],
                         beta: float = 0.1) -> float:
        """DPO loss: -log(sigmoid(beta * (r_chosen - r_rejected)))"""
        pass
    
    def get_preferred_worm(self, task_context: Dict) -> str:
        """Given a task context, return the preferred worm."""
        pass
```

**Data Sources:**
- `NatureCluster` execution: when multiple worms run, compare their `duration_ms`, `success`, and downstream error rates
- `CLUSTERWORMS` parallel execution: natural A/B tests
- `MetaCluster` orchestration: compare Nature-level performance

**Integration Point:** Add to `expansion/learning.py` as a new worm or extend `ABTestRunner`.

### 2.3 Solution: GRPO for Policy Optimization

**Group Relative Policy Optimization (GRPO)** is better for multi-worm scenarios where you have groups of outputs.

**Protocol:**
```python
class GRPOTrainer:
    """Group Relative Policy Optimization for worm selection.
    
    For each task, generates a group of candidate worms,
    scores them relative to each other, and updates the policy.
    """
    
    def generate_group(self, task_context: Dict, group_size: int = 8) -> List[str]:
        """Generate a group of candidate worms for a task."""
        pass
    
    def compute_group_rewards(self, group: List[str], task: Dict) -> List[float]:
        """Run each worm and compute rewards."""
        pass
    
    def compute_grpo_loss(self, rewards: List[float], beta: float = 0.04) -> float:
        """GRPO loss: normalize rewards within group, then policy gradient."""
        mean_r = sum(rewards) / len(rewards)
        std_r = (sum((r - mean_r)**2 for r in rewards) / len(rewards)) ** 0.5
        advantages = [(r - mean_r) / max(std_r, 1e-8) for r in rewards]
        return advantages
```

**Why GRPO over PPO:**
- No separate critic model needed (simpler)
- Works well with relative comparisons (perfect for worm selection)
- Lower variance than vanilla policy gradient
- Already proven in DeepSeek-R1

---

## 3. Priority 2: Cross-Agent Knowledge Transfer

### 3.1 Problem

Each worm learns independently. When `SYSTEMZ_ML` discovers that CPU spikes correlate with errors, that knowledge stays in `SYSTEMZ_ML`. When `VulnScanner` learns that certain file patterns are high-risk, that knowledge stays there.

### 3.2 Solution: Shared Embedding Space

**Protocol:**
```python
class AgentKnowledgeGraph:
    """Shared knowledge graph across all agents.
    
    Stores learned patterns as typed embeddings that can be
    queried by any agent. Enables transfer learning.
    """
    
    def register_pattern(self, 
                         source_agent: str,
                         pattern_type: str,  # "anomaly", "preference", "correlation"
                         embedding: List[float],
                         metadata: Dict):
        """Agent publishes a learned pattern."""
        pass
    
    def query_similar(self, 
                      query_embedding: List[float],
                      pattern_type: str = None,
                      top_k: int = 5) -> List[Dict]:
        """Any agent can query for similar patterns."""
        pass
    
    def transfer_to(self, target_agent: str, pattern_type: str) -> List[Dict]:
        """Get patterns relevant to a target agent."""
        pass
```

**Integration Point:** Add to `LocalMemoryStore` as a new table `agent_patterns` with vector similarity (or cosine similarity for now).

**Data Flow:**
```
SYSTEMZ_ML detects CPU anomaly pattern
  → AgentKnowledgeGraph.register_pattern("SYSTEMZ_ML", "anomaly", embedding, {...})
  → CLUSTERWORMS queries: query_similar(my_context_embedding, "anomaly")
  → Gets: "When CPU > 80%, reduce parallel worm count"
```

---

## 4. Priority 3: Experience Replay for Continuous Learning

### 4.1 Problem

Training data in `LocalMemoryStore` grows continuously (1,122 entries) but the `RLTrainLoop` trains from scratch each time. There's no prioritized replay of important experiences.

### 4.2 Solution: Prioritized Experience Replay

**Protocol:**
```python
class PrioritizedReplayBuffer:
    """Prioritized experience replay for RL training.
    
    Stores (state, action, reward, next_state) tuples with priorities
    based on TD-error. High-error experiences are replayed more often.
    """
    
    def __init__(self, capacity: int = 10000, alpha: float = 0.6):
        self.capacity = capacity
        self.alpha = alpha  # prioritization exponent
        self.buffer = []
        self.priorities = []
    
    def add(self, state, action, reward, next_state, done):
        """Add experience with max priority (will be sampled soon)."""
        max_priority = max(self.priorities) if self.priorities else 1.0
        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(max_priority)
    
    def sample(self, batch_size: int, beta: float = 0.4) -> Tuple:
        """Sample batch with priority-weighted probability."""
        # P(i) = p_i^alpha / sum(p_k^alpha)
        # IS weights: (1/N * 1/P(i))^beta
        pass
    
    def update_priorities(self, indices: List[int], td_errors: List[float]):
        """Update priorities based on new TD-errors."""
        for idx, td_error in zip(indices, td_errors):
            self.priorities[idx] = abs(td_error) + 1e-6
```

**Integration:** Extend `DataPipelineWorm` to maintain a replay buffer alongside the raw memory store. The `RLTrainLoop` samples from the buffer instead of iterating sequentially.

**Key Insight:** Error experiences (worm failures, slow operations) should have higher priority — they're more informative than routine successes.

---

## 5. Priority 4: Genetic/Evolutionary Worm Optimization

### 5.1 Problem

Worm configurations (priority, cooldown, detection thresholds) are hardcoded in `@register_worm` decorators. `MorphingWorm` can modify detection code but doesn't optimize parameters.

### 5.2 Solution: Evolutionary Strategy for Worm Configs

**Protocol:**
```python
class WormEvolutionEngine:
    """Evolutionary optimization for worm configurations.
    
    Treats each worm's configurable parameters as a genome.
    Uses CMA-ES or simple genetic algorithm to evolve better configs.
    """
    
    PARAM_RANGES = {
        "priority": (1, 10),
        "cooldown_seconds": (5, 300),
        "detection_threshold": (0.1, 0.9),
        "max_parallel": (1, 16),
        "timeout_seconds": (10, 120),
    }
    
    def create_genome(self, worm_name: str) -> Dict[str, float]:
        """Create a random genome for a worm."""
        pass
    
    def mutate(self, genome: Dict[str, float], mutation_rate: float = 0.1) -> Dict[str, float]:
        """Mutate genome parameters."""
        pass
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict[str, float]:
        """Uniform crossover between two genomes."""
        pass
    
    def evaluate_fitness(self, worm_name: str, genome: Dict) -> float:
        """Evaluate fitness: success_rate * (1 / avg_duration) * diversity_bonus."""
        pass
    
    def evolve_population(self, 
                          worm_name: str,
                          population_size: int = 20,
                          generations: int = 10) -> Dict[str, float]:
        """Run evolutionary optimization."""
        pass
```

**Fitness Function:**
```python
def evaluate_fitness(genome, execution_history):
    success_rate = count(successes) / count(total)
    avg_reward = mean(rewards)
    diversity_score = SpawnDiversityEngine.staleness_bonus(worm_name)
    error_recovery = count(recovered_errors) / count(errors)
    
    return (
        success_rate * 0.3 +
        avg_reward * 0.3 +
        diversity_score * 0.2 +
        error_recovery * 0.2
    )
```

**Integration:** Add to `SpawnDiversityEngine` — after N executions, evolve the top-performing worms' configs.

---

## 6. Priority 5: Curriculum Learning for Agents

### 6.1 Problem

All worms run at the same complexity level. There's no mechanism to start simple and increase difficulty as agents improve.

### 6.2 Solution: Adaptive Curriculum

**Protocol:**
```python
class AgentCurriculum:
    """Adaptive curriculum for progressive agent training.
    
    Tracks agent performance and adjusts task difficulty accordingly.
    """
    
    DIFFICULTY_LEVELS = {
        1: {"max_files": 10, "timeout": 30, "complexity": "simple"},
        2: {"max_files": 50, "timeout": 60, "complexity": "moderate"},
        3: {"max_files": 200, "timeout": 120, "complexity": "complex"},
        4: {"max_files": 1000, "timeout": 300, "complexity": "adversarial"},
    }
    
    def get_difficulty(self, worm_name: str) -> int:
        """Get current difficulty level based on recent performance."""
        pass
    
    def update(self, worm_name: str, success: bool, reward: float):
        """Update difficulty based on performance.
        
        If success_rate > 0.8 over last 20 episodes → increase difficulty
        If success_rate < 0.4 over last 20 episodes → decrease difficulty
        """
        pass
    
    def get_task_params(self, worm_name: str) -> Dict:
        """Get task parameters for current difficulty level."""
        pass
```

**Integration:** Add to `ScheduledTrainingWorm` — the curriculum adjusts `n_episodes`, `max_steps`, and data complexity based on training progress.

---

## 7. Priority 6: Intrinsic Motivation / Curiosity

### 7.1 Problem

The epsilon-greedy exploration in `RLTrainLoop` is random. There's no mechanism for agents to seek out novel or surprising experiences.

### 7.2 Solution: RND (Random Network Distillation) Curiosity

**Protocol:**
```python
class CuriosityModule:
    """Random Network Distillation for curiosity-driven exploration.
    
    Uses prediction error as intrinsic reward — states that are
    surprising (high prediction error) get bonus reward.
    """
    
    def __init__(self, state_dim: int = 64):
        # Target network (fixed random)
        self.target_net = self._create_target_net(state_dim)
        # Predictor network (learned)
        self.predictor_net = self._create_predictor_net(state_dim)
    
    def compute_curiosity_reward(self, state: List[float]) -> float:
        """Compute intrinsic reward based on prediction error.
        
        High error = novel state = high curiosity reward.
        """
        target = self.target_net(state)
        predicted = self.predictor_net(state)
        error = sum((t - p)**2 for t, p in zip(target, predicted))
        return error
    
    def update_predictor(self, state: List[float]):
        """Train predictor to reduce error on seen states."""
        pass
```

**Why RND over count-based:**
- Works in continuous state spaces (our feature vectors)
- No need to discretize or hash states
- Naturally decreases as states become familiar
- Simple to implement (two small networks)

**Integration:** Add intrinsic reward to `RLTrainLoop._compute_reward()`:
```python
extrinsic = 1.0 if success else -1.0
intrinsic = curiosity_module.compute_curiosity_reward(state_features)
reward = extrinsic + 0.1 * intrinsic  # scale curiosity
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (1-2 days)
- [ ] **Experience Replay Buffer** — Extend `DataPipelineWorm` with `PrioritizedReplayBuffer`
- [ ] **Cross-Agent Knowledge Graph** — Add `agent_patterns` table to LocalMemoryStore
- [ ] **DPO Preference Collection** — Add preference recording to `ABTestRunner`

### Phase 2: Learning (2-3 days)
- [ ] **GRPO Trainer** — New class in `expansion/learning.py` for group-relative optimization
- [ ] **Curiosity Module** — RND-based intrinsic motivation in `RLTrainLoop`
- [ ] **Curriculum Manager** — Adaptive difficulty in `ScheduledTrainingWorm`

### Phase 3: Evolution (3-5 days)
- [ ] **Worm Evolution Engine** — Genetic algorithm for worm config optimization
- [ ] **MorphingWorm v2** — Learn from evolved genomes, not just error patterns
- [ ] **Meta-Learning** — Agents that learn how to learn (MAML-style)

### Phase 4: Integration (2-3 days)
- [ ] **Unified Training Pipeline** — Wire all components into `ScheduledTrainingWorm`
- [ ] **Dashboard Integration** — Visualize evolution progress in `dashboard.py`
- [ ] **PAMS Insights** — Auto-generate insights from training runs

---

## 9. Libraries to Consider

| Library | Purpose | Relevance |
|---------|---------|-----------|
| `torch` / `pytorch` | Neural networks for RND, DPO | Medium (already have numpy) |
| `stable-baselines3` | PPO/A2C/SAC implementations | Low (tabular RL sufficient right now) |
| `deap` | Genetic algorithms | High (for WormEvolutionEngine) |
| `optuna` | Hyperparameter optimization | Medium (replaces grid search in `hyperparameter_tune`) |
| `sentence-transformers` | Embedding generation for knowledge graph | Medium |
| `faiss` | Vector similarity search | Low (cosine similarity sufficient for now) |

**Recommendation:** Start with pure Python + numpy (no new deps). Add `deap` for genetic algorithms only when Phase 3 begins.

---

## 10. Anti-Patterns to Avoid

1. **Don't add PyTorch/TensorFlow for tabular RL** — Q-learning with 74 worms and ~1000 states is perfectly fine with dicts
2. **Don't train on production data without validation** — Always use temporal CV splits
3. **Don't let agents self-modify without guardrails** — `MorphingWorm` should validate generated code before deploying
4. **Don't optimize for reward alone** — Include diversity, fairness, and exploration metrics
5. **Don't ignore the 3 slow tests** — Cluster/nature/metacluster tests need fixing before ML training can be automated

---

## 11. Connection to Existing TODO Items

| TODO Item | ML/RL Enhancement |
|-----------|-------------------|
| PAMS insights #13 (scheduled training) | Add curriculum + replay buffer |
| PAMS insights #14 (A/B testing) | Extend to GRPO group evaluation |
| Anti-pattern #19 (off-by-one paths) | Curiosity module would detect novel path patterns |
| Registry cache (1038x) | Enables fast worm lookup for GRPO candidate generation |
| t-strings (structured logging) | Essential for training data quality |

---

## 12. Summary: What to Build First

**Immediate wins (no new deps, 1-2 days):**
1. `PrioritizedReplayBuffer` in `DataPipelineWorm` — 50 lines
2. Preference recording in `ABTestRunner` — 30 lines
3. Cross-agent pattern table in LocalMemoryStore — 40 lines + SQL migration

**High-impact (new deps, 3-5 days):**
4. `GRPOTrainer` — 100 lines, pure Python
5. `WormEvolutionEngine` with `deap` — 200 lines
6. `CuriosityModule` with numpy — 80 lines

**Long-term (significant effort, 1-2 weeks):**
7. Full curriculum system
8. Meta-learning (MAML)
9. Self-modifying code with validation

---

*This document is a living artifact. Update as implementations land.*
