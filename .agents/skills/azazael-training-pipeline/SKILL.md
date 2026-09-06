---
name: azazael-training-pipeline
description: Training data pipeline — ETL (DataPipelineWorm), feature extraction (SchemaAwareFeatureExtractor), RL training (RLTrainLoop, SB3Agent, GRPOTrainer), model versioning, and ml-platforms integration.
metadata:
  category: codex
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Training Pipeline — ETL to Model Training

> **Covers:** Data pipeline, feature extraction, 3 trainers (Q-learning, SB3, GRPO), model versioning
> **Key files:** `learning.py` (2,099L), `learning_grpo.py` (615L), `sb3_agent.py` (831L), `NeuralPipeline.py` (748L)

---

## Part 1: ETL Pipeline

### Overview
```
Extract (DataPipelineWorm) -> Transform (FeatureEngineer/SchemaAware) -> Load (ModelVersioner)
                                                                              |
                                                                              v
                                                                     Train (RLTrainLoop/SB3Agent/GRPO)
```

### DataPipelineWorm (v2.0.0)
| Stage | Function | Details |
|-------|----------|---------|
| **Extract** | FTS5 full-text search | source/event_type/severity filters, temporal queries |
| **Transform** | Chain of callables | field extraction, severity filtering, flattening, dedup |
| **Load** | JSON + LocalMemoryStore | file output, memory record, batch processing |
| **Split** | Temporal session-based | prevents data leakage (same session never spans splits) |
| **CV** | Temporal cross-validation | expanding window + gap_days, default 5 folds |

### SchemaAwareFeatureExtractor (v1.0.0)
- Uses **DATA_SHAPES** (static) and **DYNAMIC_SHAPES** (auto-discovered) registries
- Categorical fields → one-hot with learned vocabularies
- Numeric fields → direct float extraction
- Falls back to generic extraction for unknown event types
- `fit()` builds category vocabs, `extract()` returns 2D feature matrix
- **DATA_SHAPES** covers 10 event types: cluster_created, execution_started/completed, cross_nature_route, metacluster_orchestrated/discovery, model_registered, nature_cluster_executed/discovery, training_complete

### Split Strategies
| Strategy | Method | Use Case |
|----------|--------|----------|
| **by_session=True** | Splits by session_id (temporal) | Prevents data leakage |
| **by_session=False** | Random record-level shuffle | Non-temporal datasets |

---

## Part 2: Trainers

### RLTrainLoop (Q-Learning) — learning.py (2,099L)
- Houses **4 core classes**: RLTrainLoop, ModelVersioner, DataPipelineWorm, SchemaAwareFeatureExtractor (monolith concern — see anti-patterns below)
- Epsilon-greedy exploration from LocalMemoryStore
- PrioritizedReplayBuffer (TD-error priority sampling)
- ModelVersioner (version tracking + rollback, auto-register after training)
- 6 inference API integration for reward shaping

> **Note:** `learning.py` is the single largest pipeline file (2,099L, 6 classes). Its monolithic nature is a known anti-pattern — refactoring into separate modules is recommended for maintainability.

### SB3Agent (PPO/DQN/A2C) — sb3_agent.py
- Wraps stable-baselines3 algorithms
- SB3AgentPool for parallel multi-agent training
- Auto-register with ModelVersioner after training
- Gym environment from extracted features

### GRPOTrainer (Group Relative Policy Optimization) — learning_grpo.py
```
GRPOTrainer
   |
   +--> Group-based advantage estimation
   +--> Policy persistence via LocalMemoryStore
   +--> ABTestRunner (DPO preference learning)
   +--> Cross-API convergence analysis
```

**GRPO Key Features:**
| Feature | Description |
|---------|-------------|
| Group advantages | Normalize rewards within groups to reduce variance |
| KL penalty | Prevent policy divergence from reference model |
| DPO integration | ABTestRunner for pairwise preference learning |
| Memory persistence | Policy save/load via LocalMemoryStore |

### Unified Orchestration — NeuralPipeline (748L)
```python
from CORE.NeuralPipeline import NeuralPipeline

pipeline = NeuralPipeline(max_workers=4, llm_augmentation=True)

# Single agent type
result = pipeline.run_end_to_end(
    source="SystemZ", event_type="monitor",
    agent_type="SB3", total_timesteps=5000,
)

# All 3 agents in parallel via WorkStealingPool
result = pipeline.run_end_to_end(
    source="SystemZ", agent_type="ALL",
)

# Cross-API convergence analysis
convergence = pipeline.run_cross_api_analysis(source="SystemZ")
```

---

## Part 3: ml-platforms Integration

### Deployment Path
```
Trained Policy/Model (RLTrainLoop/SB3Agent/GRPO)
        |
        v
[Export via ONNX]  ← ml_platforms/onnx_integration.py
[Optimize via Ray] ← ml_platforms/improvements/ray_integration.py
[Serve via LM Studio] ← ml_platforms/lm_studio_*.py
        |
        v
[Inference via azazael-inference-protocol (12-provider failover)]
```

### Integration Points

| ml-platforms Component | Training Integration |
|------------------------|----------------------|
| **ONNX pipeline** | Export trained policies for cross-platform deployment |
| **Ray distributed** | Hyperparameter tuning via `ray_integration.py` |
| **LM Studio** | Serve trained models as local LLM endpoints |
| **Metrics tracker** | Log training metrics via `metrics_tracker.py` |
| **Q-analysis** | Evaluate trained policies via `run_qanalysis.py` |
| **Model compression** | Post-training quantization via `azazael-model-compression` |

### Error Recovery — DeadLetterQueue
Failed pipeline runs are stored and replayable:
```python
# Replay from DeadLetterQueue
pipeline.replay_failed()
```

---

## Part 4: Key Files Reference

| File | Lines | Key Classes | Role |
|------|:-----:|-------------|------|
| `CORE/WORMS/expansion/learning.py` | 2,099 | RLTrainLoop, ModelVersioner, DataPipelineWorm, SchemaAwareFeatureExtractor | Core training + data pipeline |
| `CORE/WORMS/expansion/learning_grpo.py` | 615 | GRPOTrainer, ABTestRunner | Group Relative Policy Optimization |
| `CORE/WORMS/expansion/learning_replay.py` | 247 | PrioritizedReplayBuffer | Experience replay with TD-error priority |
| `CORE/WORMS/expansion/learning_features.py` | 124 | FeatureEngineer | Fast-loading feature extraction |
| `CORE/sb3_agent.py` | 831 | SB3Agent, SB3AgentPool | Stable-Baselines3 integration |
| `CORE/NeuralPipeline.py` | 748 | NeuralPipeline | Unified end-to-end orchestrator |
| `CORE/WORMS/dead_letter_queue.py` | 89 | DeadLetterQueue | Failed run recovery |

## Related Skills

- `azazael-neural-architecture` — RL architecture reference (MoE, SSM, NAS patterns)
- `azazael-neural-pipeline` — NeuralPipeline orchestrator (6-step lifecycle)
- `azazael-ml-platforms` — ML platform infrastructure (ONNX, Ray, LM Studio)
- `azazael-model-compression` — Post-training quantization, distillation, pruning
- `azazael-inference-protocol` — 12-provider failover for deployed models
- `azazael-evolutionary-optimization` — EvolutionEngine for architecture search
