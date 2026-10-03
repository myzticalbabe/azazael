---
name: azazael-system-wiring
description: System-level neural wiring map — how LocalMemoryStore, DataPipelineWorm, DirectMemory and neural subsystems connect.
metadata:
  category: architecture
  project: azazael
  priority: high
  auto_load: false
---

# Azazael System-Level Neural Wiring

## Complete Neural Subsystem Map
```
                    LocalMemoryStore (11,633+ memories)
                            |
            +---------------+---------------+
            |                               |
      DataPipelineWorm                DirectMemory
      (ETL: extract,                  (session audit)
       transform, load)
            |
            +-----> SchemaAwareFeatureExtractor
            |         (typed features from DATA_SHAPES)
            |
            +-----> FeatureEngineer
            |         (normalization, encoding, imputation)
            |
            +-----> RLTrainLoop
            |         (Q-learning, epsilon-greedy)
            |           |
            |           +-> PrioritizedReplayBuffer (TD-error priority)
            |           +-> ModelVersioner (version tracking)
            |           +-> Hyperparameter tuning (CV folds)
            |
            +-----> SB3Agent
            |         (PPO/DQN/A2C via gymnasium)
            |           |
            |           +-> SB3AgentPool (parallel training)
            |           +-> ModelVersioner (auto-register)
            |
            +-----> GRPOTrainer
                      (Group Relative Policy Optimization)
                        |
                        +-> ABTestRunner (DPO preferences)
                        +-> Policy persistence

Inference Providers (14 APIs)
    |
    providers.py (OpenAIProvider, 14 providers)
        |
        +-> nim_client.py (NimClient extends OpenAIProvider)
        +-> api_client.py (ThreadSafeCall, retry, masking)
        +-> INFERENCE_WORM.py (worm-based dispatch)
        +-> NIM_INFERENCE.py (NVIDIA-specific worm)

Evolutionary Optimization
    |
    EvolutionEngine (NSGA-II, Pareto front)
        |
        +-> GeneticOptimizer (per-worm param optimization)
        +-> CurativePool (governance gates)

Cross-Cutting
    |
    freethreading.py (FreeThreadPool, WorkStealingPool)
    dead_letter_queue.py (failed operation persistence + retry)
    secrets_manager.py (API key rotation + audit)
```

## Integration Gaps
1. **No unified NeuralPipeline** — each trainer independently calls DataPipelineWorm
2. **RLTrainLoop and SB3Agent don't share** — separate Q-tables and policies
3. **GRPOTrainer doesn't feed into SB3Agent** — worm selection vs parameter optimization
4. **EvolutionEngine doesn't use inference providers** — standalone optimization

## Key Files by Layer
| Layer | Files |
|-------|-------|
| Data | learning.py (DataPipelineWorm, SchemaAwareFeatureExtractor) |
| Training | learning.py (RLTrainLoop), sb3_agent.py (SB3Agent), learning_grpo.py (GRPOTrainer) |
| Inference | providers.py, nim_client.py, api_client.py |
| Evolution | evolution.py (EvolutionEngine, GeneticOptimizer) |
| Infrastructure | freethreading.py, dead_letter_queue.py, secrets_manager.py |
