---
name: azazael-neural-pipeline
description: NeuralPipeline v1.0.0 — unified end-to-end ML orchestrator. 6-step lifecycle (Extract → Featurize → Train → LLM-Augment → Register → Persist), DeadLetterQueue error recovery, WorkStealingPool parallel execution, 6-API reward shaping.
metadata:
  category: codex
  project: azazael
  priority: high
  auto_load: true
---

# Azazael NeuralPipeline — Unified End-to-End ML Orchestrator

> **Implementation:** `CORE/NeuralPipeline.py` (748L)
> **Orchestrates:** RLTrainLoop (Q-learning), SB3Agent (PPO/DQN/A2C), GRPOTrainer (GRPO)
> **Related skills:** `azazael-neural-architecture`, `azazael-training-pipeline`, `azazael-ml-platforms`, `azazael-inference-protocol`

---

## Part 1: Architecture Overview

`NeuralPipeline` (v1.0.0) orchestrates the complete neural training lifecycle as a unified pipeline, managing data extraction, feature engineering, model training (3 agent types), inference-powered reward shaping, model versioning, and error recovery.

### 6-Step Lifecycle

```text
                          NeuralPipeline v1.0.0
                           (748L orchestrator)
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+------------------+   +------------------+   +------------------+
| Step 1: EXTRACT  |-->| Step 2:          |-->| Step 3: TRAIN    |
| (DataPipeline-   |   | FEATURIZE        |   | (RLTrainLoop     |
|  Worm)           |   | (SchemaAware     |   |  SB3/GRPO)       |
|                  |   |  FeatureExt)     |   |                  |
+------------------+   +------------------+   +--------+---------+
                                                        |
                                                        v
+------------------+   +------------------+   +------------------+
| Step 6: PERSIST  |<--| Step 5: REGISTER  |<--| Step 4: LLM-     |
| (LocalMemory-    |   | (ModelVersioner)  |   | AUGMENT          |
|  Store)          |   |                  |   | (6 Inference     |
|                  |   |                  |   |  APIs)           |
+------------------+   +------------------+   +------------------+
                                                        |
                                                        v
                                               +------------------+
                                               | DeadLetterQueue  |
                                               | (error recovery) |
                                               +------------------+
```

### Architecture Diagram

```text
LocalMemoryStore (11,633+ memories)
        |
        v
DataPipelineWorm (ETL: extract, split, temporal CV)
        |
        v
SchemaAwareFeatureExtractor (typed features from DATA_SHAPES)
        |
        +--> RLTrainLoop (Q-learning) ------------+
        +--> SB3Agent (PPO/DQN/A2C) -------------+--> WorkStealingPool (parallel)
        +--> GRPOTrainer (GRPO) -----------------+
                     |
                     v
        6 Inference APIs (reward shaping)
        Groq | OpenRouter | NIM | Mistral | GitHub | HuggingFace
                     |
                     v
              ModelVersioner (register + version)
                     |
                     v
              DeadLetterQueue (error recovery)
```

---

## Part 2: Key Features & Patterns

### Parallel Execution via WorkStealingPool

The pipeline can execute all 3 agent types in parallel using `WorkStealingPool` from `CORE/freethreading.py`:

| Feature | Description |
|---------|-------------|
| **WorkStealingPool** | Task-stealing thread pool for Python 3.14t free-threading |
| **agent_type="ALL"** | Spawns RLTrainLoop + SB3Agent + GRPOTrainer concurrently |
| **max_workers** | Configurable parallelism (default 4) |
| **Thread safety** | Double-checked locking for lazy provider initialization |

```python
# All 3 agents train simultaneously, results merged after completion
result = pipeline.run_end_to_end(source="SystemZ", agent_type="ALL")
```

### Inference-Powered Reward Shaping

During training, NeuralPipeline queries 6 inference APIs for real-time reward shaping — the same providers used by `azazael-inference-protocol` for serving:

| Provider | Model | Use Case |
|----------|-------|----------|
| **Groq** | llama-3.3-70b | Primary reward shaping |
| **OpenRouter** | llama-3.3-70b | Fallback reward shaping |
| **NVIDIA NIM** | llama-3.3-70b | High-throughput batch |
| **Mistral** | mistral-large | Diversity reward |
| **GitHub** | gpt-4o-mini | Quick validation |
| **HuggingFace** | varies | Specialized reward models |

If inference fails during training, the pipeline captures the failure in DeadLetterQueue for replay.

### Cross-API Convergence Analysis

```python
# Analyzes convergence across all 6 inference providers
convergence = pipeline.run_cross_api_analysis(source="SystemZ")
# Returns: {provider_name: {episode_rewards, convergence_rate, ...}}
```

### Session Persistence

- Policies auto-saved to LocalMemoryStore after each training run
- ModelVersioner tracks version history and enables rollback
- Session-to-session policy continuity via auto-save/load

---

## Part 3: Error Recovery — DeadLetterQueue

Failed pipeline runs are captured and replayable:

| Failure Type | Recovery | File |
|:------------:|----------|:----:|
| Inference API timeout | Auto-retry with backoff → DeadLetterQueue | `NeuralPipeline.py` |
| Training divergence | Capture checkpoint → DeadLetterQueue for replay | `dead_letter_queue.py` |
| Data pipeline failure | HALT pipeline → store failed config in DLQ | `DataPipelineWorm` |
| Model export failure | Rollback to last version via ModelVersioner | `ModelVersioner` |

```python
# After a failed run, replay from DeadLetterQueue
pipeline.replay_failed()  # Re-runs all failed pipelines with same config
```

---

## Part 4: Supported Agent Types

| Type | Trainer | Algorithm | Description |
|:----:|---------|:---------:|-------------|
| **SB3** | SB3Agent | PPO / DQN / A2C | Stable-baselines3 integration with gym environment |
| **GRPO** | GRPOTrainer | Group Relative Policy Optimization | Group-based advantage estimation + DPO preference learning |
| **QLEARN** | RLTrainLoop | Q-learning (epsilon-greedy) | PrioritizedReplayBuffer + TD-error priority sampling |
| **ALL** | All three | Parallel | Concurrent execution via WorkStealingPool |

### When to Use Each Agent

| Scenario | Recommended Agent | Rationale |
|----------|:-----------------:|-----------|
| Simple state-action spaces | RLTrainLoop (QLEARN) | Epsilon-greedy, lightweight |
| Continuous action spaces | SB3Agent (PPO) | Stable-baselines3, well-tested |
| Human preference learning | GRPOTrainer (GRPO) | ABTestRunner for DPO |
| Maximum throughput | ALL | Parallel training via WorkStealingPool |
| Benchmarking | ALL | Cross-agent convergence comparison |

---

## Part 5: Key Files

| File | Lines | Key Classes | Role |
|------|:-----:|-------------|------|
| `CORE/NeuralPipeline.py` | 748 | NeuralPipeline | Main orchestrator — 6-step lifecycle |
| `CORE/WORMS/expansion/learning.py` | 2,099 | RLTrainLoop, DataPipelineWorm, SchemaAwareFeatureExtractor, ModelVersioner | Core training + data pipeline |
| `CORE/sb3_agent.py` | 831 | SB3Agent, SB3AgentPool | Stable-Baselines3 integration |
| `CORE/WORMS/expansion/learning_grpo.py` | 615 | GRPOTrainer, ABTestRunner | Group Relative Policy Optimization |
| `CORE/inference/providers.py` | — | 14+ provider registry | Inference API providers for reward shaping |
| `CORE/WORMS/dead_letter_queue.py` | 89 | DeadLetterQueue | Failed run recovery |
| `CORE/freethreading.py` | — | WorkStealingPool, FreeThreadPool | Parallel execution engine |

---

## Part 6: Integration with Other Systems

| System | Skill | Integration Point |
|--------|:-----:|-------------------|
| **Training Pipeline** | `training-pipeline` | NeuralPipeline orchestrates RLTrainLoop, SB3Agent, GRPOTrainer from the training pipeline |
| **Neural Architecture** | `neural-architecture` | Architecture patterns (MoE, SSM, NAS) inform which agent type to use |
| **ML Platforms** | `ml-platforms` | ONNX export, Ray tuning, LM Studio serving post-training |
| **Inference Protocol** | `inference-protocol` | 6 inference APIs used for reward shaping during training |
| **Model Compression** | `model-compression` | Post-training quantization, distillation, pruning |
| **Neural Integration** | `neural-integration` | Cross-system architecture connecting all neural subsystems |

---

## Part 7: Usage Patterns

### Basic Single Agent Run

```python
from CORE.NeuralPipeline import NeuralPipeline

pipeline = NeuralPipeline(max_workers=4, llm_augmentation=True)

result = pipeline.run_end_to_end(
    source="SystemZ",
    event_type="monitor",
    agent_type="SB3",
    total_timesteps=5000,
)
```

### Parallel Multi-Agent Run

```python
result = pipeline.run_end_to_end(
    source="SystemZ",
    agent_type="ALL",  # Parallel via WorkStealingPool
)
```

### Convergence Analysis

```python
convergence = pipeline.run_cross_api_analysis(source="SystemZ")
```

### Error Recovery

```python
pipeline.replay_failed()  # Replay all DeadLetterQueue entries
```

## Related Skills

- `azazael-neural-architecture` — RL architecture reference (MoE, SSM, NAS patterns)
- `azazael-training-pipeline` — Training data pipeline (ETL, feature extraction)
- `azazael-ml-platforms` — ML platform infrastructure (ONNX, Ray, LM Studio)
- `azazael-inference-protocol` — 12-provider failover for inference serving
- `azazael-model-compression` — Post-training quantization, distillation, pruning
- `azazael-neural-integration` — Cross-system architecture connecting all neural subsystems
- `azazael-parallel` — WorkStealingPool, FreeThreadPool parallel execution
