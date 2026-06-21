# Azazael NeuralPipeline — Unified End-to-End ML Orchestrator

## Overview
`NeuralPipeline` (v1.0.0) orchestrates the complete neural training lifecycle:
```
Extract -> Featurize -> Train -> LLM-Augment -> Register -> Persist
```

## Architecture
```
LocalMemoryStore (11,633+ memories)
        |
        v
DataPipelineWorm (ETL: extract, split, temporal CV)
        |
        v
SchemaAwareFeatureExtractor (typed features from DATA_SHAPES)
        |
        +--> RLTrainLoop (Q-learning) ---+
        +--> SB3Agent (PPO/DQN/A2C) ----+--> WorkStealingPool (parallel)
        +--> GRPOTrainer (GRPO) ---------+
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

## Key Features
- **6-step pipeline** with automatic error recovery via DeadLetterQueue
- **WorkStealingPool** for parallel training (agent_type="ALL")
- **6 inference API integration** for real-time reward shaping
- **Cross-API convergence analysis** (`run_cross_api_analysis`)
- **Session persistence** via LocalMemoryStore
- **API reliability scoring** with dynamic fallback

## Usage
```python
from CORE.NeuralPipeline import NeuralPipeline

pipeline = NeuralPipeline(max_workers=4, llm_augmentation=True)

# Single run
result = pipeline.run_end_to_end(
    source="SystemZ", event_type="monitor",
    agent_type="SB3", total_timesteps=5000,
)

# All 3 agents in parallel
result = pipeline.run_end_to_end(
    source="SystemZ", agent_type="ALL",
)

# Cross-API convergence analysis
convergence = pipeline.run_cross_api_analysis(source="SystemZ")

# Replay failed runs
pipeline.replay_failed()
```

## Supported Agent Types
| Type | Trainer | Description |
|------|---------|-------------|
| SB3 | SB3Agent | PPO/DQN/A2C via stable-baselines3 |
| GRPO | GRPOTrainer | Group Relative Policy Optimization |
| QLEARN | RLTrainLoop | Q-learning with epsilon-greedy |
| ALL | All three | Parallel execution via WorkStealingPool |

## Key Files
- `CORE/NeuralPipeline.py` — Main orchestrator class
- `CORE/WORMS/expansion/learning.py` — RLTrainLoop, DataPipelineWorm, SchemaAwareFeatureExtractor
- `CORE/sb3_agent.py` — SB3Agent, SB3AgentPool
- `CORE/WORMS/expansion/learning_grpo.py` — GRPOTrainer
- `CORE/inference/providers.py` — 14 inference API providers
- `CORE/WORMS/dead_letter_queue.py` — Failed run recovery
- `CORE/freethreading.py` — WorkStealingPool, FreeThreadPool
