# Azazael Neural Architecture — RL + SB3 + GRPO Wiring

## Overview
Azazael's neural learning subsystem spans three complementary approaches:
- **RLTrainLoop** — Q-learning with epsilon-greedy exploration from LocalMemoryStore
- **SB3Agent** — PPO/DQN/A2C via stable-baselines3 wrapping gym environments
- **GRPOTrainer** — Group Relative Policy Optimization for worm selection

## Architecture Diagram
```
LocalMemoryStore (11,633+ memories)
        |
        v
DataPipelineWorm (ETL: extract, transform, load)
        |
        +--> SchemaAwareFeatureExtractor (typed features from DATA_SHAPES)
        |         |
        |         v
        |    RLTrainLoop (Q-learning, epsilon-greedy)
        |         |
        |         +--> PrioritizedReplayBuffer (TD-error priority sampling)
        |         +--> ModelVersioner (version tracking + rollback)
        |
        +--> SB3Agent (PPO/DQN/A2C via gym environment)
                  |
                  +--> SB3AgentPool (parallel multi-agent training)
                  +--> ModelVersioner (auto-register after training)

GRPOTrainer (Group Relative Policy Optimization)
        |
        +--> Policy persistence via LocalMemoryStore
        +--> ABTestRunner (DPO preference learning)
```

## Key Files
| File | Purpose | Lines |
|------|---------|-------|
| `CORE/WORMS/expansion/learning.py` | RLTrainLoop, ModelVersioner, DataPipelineWorm, SchemaAwareFeatureExtractor | ~3,000 |
| `CORE/WORMS/expansion/learning_grpo.py` | GRPOTrainer, ABTestRunner (DPO) | ~600 |
| `CORE/WORMS/expansion/learning_replay.py` | PrioritizedReplayBuffer | ~250 |
| `CORE/WORMS/expansion/learning_features.py` | FeatureEngineer (fast-loading) | ~180 |
| `CORE/sb3_agent.py` | SB3Agent, SB3AgentPool | ~600 |

## Patterns
- All trainers use **double-checked locking** for lazy initialization
- **ThreadSafeDict** for shared caches under 3.14t
- **Q-table persistence** via LocalMemoryStore + ModelVersioner
- **Auto-save/load** for session-to-session policy continuity
- **Hyperparameter tuning** via temporal cross-validation folds

## Anti-Patterns to Avoid
- RLTrainLoop is tightly coupled to DataPipelineWorm and ModelVersioner
- FeatureEngineer's `features`/`labels` lists are not thread-safe
- learning.py is a large monolith (~3K lines) — prefer fast-loading sub-modules
