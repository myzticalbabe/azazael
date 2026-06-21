---
name: azazael-neural-architecture
description: Neural architecture reference — RL pipelines (RLTrainLoop, SB3Agent, GRPOTrainer), Mixture of Experts patterns, State Space Models, and modern Neural Architecture Search approaches.
metadata:
  category: codex
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Neural Architecture — RL + MoE + SSM + NAS

> **Covers:** Existing RL/SB3/GRPO wiring, modern architecture patterns (MoE, SSM), NAS approaches
> **Related skills:** `azazael-neural-pipeline` (end-to-end orchestrator), `azazael-ml-platforms` (infra)

---

## Part 1: Existing Implementation — RL Training Loop

### Architecture Diagram
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

### Key Files

| File | Purpose | Lines |
|------|---------|:-----:|
| `CORE/WORMS/expansion/learning.py` | RLTrainLoop, ModelVersioner, DataPipelineWorm | ~2,100 |
| `CORE/WORMS/expansion/learning_grpo.py` | GRPOTrainer, ABTestRunner (DPO) | ~615 |
| `CORE/WORMS/expansion/learning_replay.py` | PrioritizedReplayBuffer | ~250 |
| `CORE/WORMS/expansion/learning_features.py` | FeatureEngineer (fast-loading) | ~125 |
| `CORE/sb3_agent.py` | SB3Agent, SB3AgentPool | ~830 |

### Patterns
- Double-checked locking for lazy initialization
- ThreadSafeDict for shared caches under 3.14t
- Q-table persistence via LocalMemoryStore + ModelVersioner
- Auto-save/load for session-to-session policy continuity
- Temporal cross-validation for hyperparameter tuning

---

## Part 2: Mixture of Experts (MoE) Pattern

### Concept
MoE activates only a subset of "expert" neurons per input token, allowing massive parameter counts while keeping inference costs manageable.

### Existing Codebase Support
| File | Status |
|------|:------:|
| `ml_platforms/verify_moe.py` | ✅ MoE verification tool |
| `ml_platforms/improvements/` | Q-learning pipeline (complementary) |

### Recommended Implementation Pattern
```python
# Sparse MoE routing — activate top-k experts per token
class SparseMoELayer:
    def __init__(self, num_experts=8, top_k=2):
        self.experts = [Expert() for _ in range(num_experts)]
        self.router = Router()  # Learned gating function
        self.top_k = top_k

    def forward(self, x):
        weights = self.router(x)                    # [batch, num_experts]
        top_k_weights, top_k_indices = weights.topk(self.top_k)
        # Route input only to top-k experts
        outputs = [self.experts[i](x) for i in top_k_indices]
        return sum(w * o for w, o in zip(top_k_weights, outputs))
```

### When to Use
| Scenario | Recommendation |
|----------|---------------|
| Large model (>1B params), moderate throughput | ✅ MoE with 8-64 experts, top_k=2 |
| Latency-critical inference | ❌ Prefer dense model or distilled variant |
| Multi-task learning | ✅ MoE with task-specific expert routing |

---

## Part 3: State Space Models (SSM / Mamba)

### Concept
SSMs offer **linear scaling** in memory and compute with respect to sequence length (vs. Transformer's O(n²) attention). Mamba is the leading open-source SSM variant.

### Key Characteristics
| Property | SSM/Mamba | Transformer |
|----------|:---------:|:-----------:|
| Sequence scaling | **O(n)** linear | O(n²) quadratic |
| Long context (100K+ tokens) | ✅ Efficient | ❌ Prohibitive memory |
| Parallel training | ✅ | ✅ |
| Text generation quality | ✅ Competitive | ✅ SOTA |

### Integration Points
```python
# SSM layers can replace or augment Transformer attention blocks
# Existing ONNX pipeline supports SSM export
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx
```

### Provider Compatibility (Existing Inference)
| Provider | SSM Support | Notes |
|----------|:-----------:|-------|
| **Groq** | ✅ Optimized | LPU architecture excels at SSM inference (Mamba) |
| **HuggingFace** | ✅ Supported | Hosts Mamba, Mamba-2, and hybrid SSM variants |
| **NVIDIA NIM** | ✅ Supported | TensorRT-LLM supports SSM optimization |
| **OpenRouter** | ⚠️ Model-dependent | Routes to providers that may support SSM |

Leverage existing `azazael-inference-protocol` (12-provider failover) and `azazael-inference-providers` (provider registry) for SSM model serving.

---

## Part 4: Neural Architecture Search (NAS)

### Modern NAS Approaches (2025-2026)

| Approach | Method | Compute Cost | Suitability |
|----------|--------|:------------:|-------------|
| **Modular Search** | Search for building blocks, not full topologies | Low | Good for domain-specific tasks |
| **Zero-Shot NAS** | Performance proxies without full training | **Very low** | Rapid architecture prototyping |
| **Weight-Sharing** | One-shot supernet with weight sharing | Medium | Large-scale architecture search |
| **Hardware-Aware NAS** | Co-design architecture + device constraints | High | Production deployment |
| **Evolutionary NAS** | Genetic algorithms over architecture space | Medium | Exploration-focused |

### Existing Codebase Support
| File | Capability |
|------|------------|
| `CORE/WORMS/expansion/evolution.py` | Evolutionary algorithms (can be adapted for NAS) |
| `ml_platforms/improvements/ray_integration.py` | Ray distributed compute (NAS backend) |
| `ml_platforms/improvements/metrics_tracker.py` | Performance metrics for evaluation |

### Recommended Tools (External)
| Tool | Best For | Integration |
|------|----------|-------------|
| **Optuna** | Define-by-run search spaces | Python API |
| **Ray Tune** | Distributed hyperparameter/NAS | Ray cluster |
| **NNI** | Evolutionary + RL-based NAS | pip install nni |

---

## Part 5: Anti-Patterns

- **RLTrainLoop** is tightly coupled to DataPipelineWorm and ModelVersioner
- **FeatureEngineer**'s `features`/`labels` lists are not thread-safe
- **learning.py** is a large monolith (~2,100 lines) — prefer fast-loading sub-modules
- **MoE without load balancing** leads to expert collapse (router always picks same expert)
- **NAS without hardware constraints** produces architectures that don't fit on target devices

## Related Skills

- `azazael-neural-pipeline` — End-to-end orchestrator (6-step pipeline with DeadLetterQueue)
- `azazael-ml-platforms` — ML platform infrastructure (LM Studio, ONNX, Ray, diagnostics)
- `azazael-training-pipeline` — Training split strategies and cross-validation
- `azazael-inference-protocol` — 12-provider failover for inference
- `azazael-evolutionary-optimization` — EvolutionEngine, GeneticOptimizer (NAS-adjacent)
