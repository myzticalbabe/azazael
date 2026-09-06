---
name: azazael-neural-integration
description: Cross-system integration architecture — data flow, training-to-deployment pipeline, and coupling points between ml-platforms, neural-architecture, training-pipeline, and inference-protocol with model-compression as bridge.
metadata:
  category: system
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Neural Integration — Cross-System Architecture

> **Purpose:** Document how 4 core neural systems connect — the data flows, coupling points, deployment paths, and error boundaries between them.
> **Skills covered:** `ml-platforms`, `neural-architecture`, `training-pipeline`, `inference-protocol`, `model-compression`, `inference-providers`

---

## Part 1: System Boundaries & Responsibilities

| System | Skill | Role | Key Files |
|--------|:-----:|------|-----------|
| **Training Pipeline** | `training-pipeline` | ETL → Feature Extraction → Training → Model Versioning | `learning.py` (2,099L), `sb3_agent.py` (831L), `NeuralPipeline.py` (748L) |
| **Neural Architecture** | `neural-architecture` | Architecture patterns (MoE, SSM, NAS), trainer selection guidance | Reference patterns, `verify_moe.py` |
| **ML Platforms** | `ml-platforms` | ONNX export, Ray distributed, LM Studio serving, metrics tracking | 44 files across ORCHESTRATION + HYDRA |
| **Inference Protocol** | `inference-protocol` | 12-provider failover, auto-fallback, provider registry | `providers.py`, `api_client.py`, `secrets_manager.py` |
| **Model Compression** | `model-compression` | Quantization, distillation, pruning (bridge between training & inference) | External tools (GPTQ, AWQ, GGUF) |

---

## Part 2: Complete Data Flow

### End-to-End Pipeline

```
+------------------------------------------------------------------+
|                     AZAZAEL NEURAL ECOSYSTEM                       |
+------------------------------------------------------------------+

= DATA INGESTION                        = TRAINING
+--------------------------------+      +--------------------------------+
| LocalMemoryStore               |      |  +--------------------------+   |
| (11,633+ memories)             |      |  | RLTrainLoop              |   |
|         |                      |      |  | (Q-Learning)             |   |
|         v                      |      |  +----------+---------------+   |
| DataPipelineWorm               |      |  +--------------------------+   |
| (ETL: extract,                 |------+->| SB3Agent                 |   |
|  transform,load,split,CV)      |   Temp | (PPO/DQN/A2C)            |   
|         |                      |   split+----------+---------------+   |
|         v                      |   +CV  +--------------------------+   |
| SchemaAwareFeatureExtractor    |      |  | GRPOTrainer              |   |
| (typed via DATA_SHAPES)        |      |  | (Group Relative)         |   |
+--------------------------------+      |  +----------+---------------+   |
                                         |             v                  |
       <-------- REWARD SHAPING -------- | NeuralPipeline                |
                                         | (orchestrates all 3           |
                                         |  via WorkStealingPool)        |
                                         |             |                  |
                                         |             v                  |
                                         | ModelVersioner                 |
                                         | (version + rollback)          |
                                         +--------------------------------+
                                                  |
                                                  v
= EXPORT (ml-platforms)                = COMPRESSION (model-compression)
+--------------------------------+     +----------------------------------+
| ONNX export                    |---->| GPTQ (GPU, 4-bit, 98-99%)        |
| (onnx_integration.py)          |     | AWQ (GPU, 4-bit, 99%+)            |
|                                |     | GGUF (CPU, Q4_K_M, 97-99%)       |
| Ray hyperparameter tune        |     | Distillation (optional)          |
| (ray_integration.py)           |     | Pruning (optional)               |
|                                |     +----------------------------------+
| Metrics tracking               |                    |
| (metrics_tracker.py)           |                    v
+--------------------------------+     = DEPLOYMENT (inference-protocol)
                                        +--------------------------------+
                                        | LM Studio (local LLM)          |
                                        |         |                      |
                                        |         v                      |
                                        | 12-Provider Failover Chain:    |
                                        | Groq -> OpenRouter -> NIM ->   |
                                        | Mistral -> GitHub -> HF -> ... |
                                        |                                |
                                        | Auto-fallback (thinker-gpt)    |
                                        +--------------------------------+
```

### Flow Summary

| Step | System | Action | Key Artifact |
|:----:|--------|--------|:------------:|
| 1 | `training-pipeline` | Extract memories from LocalMemoryStore | Raw event data |
| 2 | `training-pipeline` | Featurize via SchemaAwareFeatureExtractor | Feature matrix |
| 3 | `training-pipeline` | Train via RLTrainLoop / SB3Agent / GRPOTrainer | Trained policy |
| 4 | `training-pipeline` | Version via ModelVersioner | Versioned model |
| 5 | `ml-platforms` | Export to ONNX | `model.onnx` |
| 6 | _optional_ | `model-compression` | Quantize/distill/prune | Compressed model |
| 7 | `ml-platforms` / `inference-protocol` | Deploy via LM Studio / provider failover | Running inference |

---

## Part 3: Integration Points (Coupling Map)

### 3A: Training Pipeline ↔ Inference Protocol (Reward Shaping)

The training pipeline uses inference APIs **during training** for real-time reward shaping. This is the most tightly coupled integration between the systems.

```python
# NeuralPipeline.py — orchestrates both systems
from CORE.NeuralPipeline import NeuralPipeline
from CORE.inference.providers import get_provider

pipeline = NeuralPipeline(max_workers=4, llm_augmentation=True)

# During training, NeuralPipeline calls 6 inference APIs for reward shaping:
# Groq, OpenRouter, NIM, Mistral, GitHub, HuggingFace
# These are the SAME providers used by the inference protocol for serving
result = pipeline.run_end_to_end(
    source="SystemZ", agent_type="ALL",
)
```

**Training-time subset (6 providers):** Groq, OpenRouter, NIM, Mistral, GitHub, HuggingFace — sourced from `CORE/inference/providers.py`. These are a subset of the full 12-provider failover chain used at serving time. If inference fails during training, DeadLetterQueue captures the run for replay.

**Full serving chain (12 providers):** Groq → OpenRouter → NVIDIA NIM → Mistral → GitHub → HuggingFace → Cloudflare → SiliconFlow → Zhipu AI → Cohere + additional endpoints (RULE 0D).

**Coupling: HIGH** — Training depends on inference provider availability.

**Key Interface:**
```python
# Training → Inference (reward shaping)
# Uses 6-provider subset: Groq, OpenRouter, NIM, Mistral, GitHub, HuggingFace
reward = infer_reward(state, action)

# Inference → Training (model deployment)
# After training, policy is exported and served via full 12-provider chain
```

### 3B: Training Pipeline ↔ ml-platforms (Export & Tuning)

```python
# Training → Export (via ONNX)
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx

policy = sb3_agent.get_policy()
onnx_model = export_to_onnx(policy, "sb3_policy.onnx")
# Now deployable via inference providers or LM Studio

# Training → Hyperparameter Tuning (via Ray)
from ORCHESTRATION.ml_platforms.ray_integration import tune_hyperparameters

best_params = tune_hyperparameters(
    trainer_class=SB3Agent,
    param_space={"learning_rate": (1e-5, 1e-3), "gamma": (0.9, 0.99)},
    metrics_tracker=metrics_tracker,
)
```

**Coupling: MODERATE** — Export is a one-way operation. Tuning is loosely coupled via Ray's distributed backend.

### 3C: ml-platforms ↔ Inference Protocol (Serving)

```python
# LM Studio serves as local inference endpoint
from ORCHESTRATION.ml_platforms.lm_studio_server import start_lm_studio
from CORE.inference.providers import get_provider

# Option 1: Local via LM Studio
port = start_lm_studio()
# Model served at localhost:{port}

# Option 2: Remote via provider failover
provider = get_provider("groq")  # Falls through chain on failure
response = provider.chat("prompt")
```

**Coupling: LOW** — Both serve as independent deployment targets. The inference protocol's failover chain can include local LM Studio instances.

### 3D: Model Compression ↔ All Systems

Compression sits between training and inference, bridging all systems:

```python
# Training → Compression
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx

# Export from training pipeline
onnx_model = export_to_onnx(trained_policy, "model.onnx")

# Compress (using external tools, proposed pattern)
# GPTQ, AWQ, or GGUF quantization applied here

# Compression → Inference
from CORE.inference.providers import get_provider
# Compressed model served via inference protocol
```

**Coupling: MODERATE** — Compression is an optional bridge step. The ONNX export is the shared interface.

### 3E: Neural Architecture → Training Pipeline (Guidance)

Architecture patterns guide which trainer to use:

| Architecture Pattern | Recommended Trainer | Rationale |
|---------------------|:------------------:|-----------|
| **Dense RL** (standard) | RLTrainLoop (Q-learning) | Epsilon-greedy exploration, simple state-action spaces |
| **Policy Gradient** (continuous) | SB3Agent (PPO) | Stable-baselines3 implements PPO, DQN, A2C |
| **Preference-based** (human feedback) | GRPOTrainer (GRPO + DPO) | ABTestRunner for pairwise preference learning |
| **MoE** (large scale) | SB3Agent + Ray Tune | MoE benefits from distributed hyperparameter search |
| **Compressed** (edge deploy) | Any trainer + model-compression | Train dense, then quantize/distill/prune |

**Coupling: LOOSE** — Architecture patterns inform choices but don't create runtime dependencies.

---

## Part 4: Deployment Scenarios

### Scenario A: Full Pipeline (Training → Deployment)

```
DataPipelineWorm → FeatureEngineer → GRPOTrainer → ModelVersioner
                                                           │
                                                           v
                                              ONNX export (ml-platforms)
                                                           │
                                                           v
                                              LM Studio / Provider Failover
```

**Use case:** End-to-end training with GRPO, then deploy via ONNX to inference providers.

### Scenario B: Compressed Pipeline (Training → Quantize → Deploy)

```
SB3Agent → ONNX → GPTQ Quantize → GGUF → CPU/Edge Deployment
```

**Use case:** Train with SB3, compress via quantization, deploy on resource-constrained hardware.

### Scenario C: Distillation Pipeline (Large → Small)

```
RLTrainLoop (Teacher, ~2B) → Distillation → SB3Agent (Student, ~350M) → LM Studio
```

**Use case:** Train a large teacher model, distill into a smaller student for local deployment.

### Scenario D: NAS Pipeline (Search → Train → Deploy)

```
Evolutionary NAS (evolution.py) → Best Architecture → GRPOTrainer → ONNX → Inference
```

**Use case:** Search for optimal architecture, train the best candidate, deploy.

---

## Part 5: Error Boundaries & Recovery

| Failure Point | System Boundary | Recovery | Responsible |
|:-------------:|:---------------:|----------|:-----------:|
| Inference API down during training | training-pipeline ↔ inference-protocol | DeadLetterQueue (`CORE/WORMS/dead_letter_queue.py`) captures failed run → replay later | NeuralPipeline |
| ONNX export failure | training-pipeline ↔ ml-platforms | ModelVersioner rollback to previous version | ModelVersioner |
| Provider all fail during serving | inference-protocol | Report raw errors — do NOT substitute own analysis | RULE 0D |
| Quantization produces degraded model | model-compression ↔ inference-protocol | Fall back to uncompressed model, report PPL delta | Deployment script |
| Data pipeline failure (ETL) | training-pipeline internal | DeadLetterQueue replay | DataPipelineWorm |

### Critical Rules

| Rule | Mandate | System |
|:----:|---------|:------:|
| RULE 0D | Auto-failover on inference failure — never block | inference-protocol |
| RULE 0Z-A | Auto-fallback when thinker-gpt unavailable | inference-protocol |
| RULE 0H | Anti-pattern detection on all code changes | All systems |
| RULE 0S | Pre-action gate before any code modification | All systems |

---

## Part 6: Quick Reference — Cross-System APIs

### Calling INTO Training Pipeline

```python
# From any system: trigger training via NeuralPipeline
from CORE.NeuralPipeline import NeuralPipeline

pipeline = NeuralPipeline()
result = pipeline.run_end_to_end(source="SystemZ", agent_type="SB3")
```

### Calling INTO Inference Protocol

```python
# From any system: query inference providers
from CORE.inference.providers import get_provider, get_best_provider

# Get specific provider
groq = get_provider("groq")
response = groq.chat("prompt", max_tokens=500)

# Get best available (respects failover)
best = get_best_provider()
response = best.chat("prompt")
```

### Calling INTO ml-platforms

```python
# From any system: export or analyze
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx
from ORCHESTRATION.ml_platforms.harness import Harness

# Export trained model
export_to_onnx(model, "export.onnx")

# Evaluate student model
Harness().evaluate(student_model, test_data)
```

### Calling INTO Model Compression

```python
# Step 1: ONNX export is code-based via ml-platforms
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx
onnx_model = export_to_onnx(trained_policy, "model.onnx")

# Step 2: Quantization step uses external CLI tools
#   GPTQ (GPU): auto-gptq CLI or Python API
#   AWQ (GPU):  autoawq CLI or Python API
#   GGUF (CPU): llama.cpp convert script
# azazael-model-compression provides format selection guidance:
#   GPTQ -> GPU inference, 4-bit, 98-99% retention
#   AWQ  -> GPU inference, 4-bit, 99%+ retention
#   GGUF -> CPU/Apple Silicon, Q4_K_M, 97-99% retention
```

---

## Part 7: Architecture Decisions & Trade-offs

| Decision | Current State | Alternative | Rationale |
|----------|:-------------:|-------------|-----------|
| **Training orchestration** | Monolithic NeuralPipeline class (748L) | Microservice architecture | Simpler for single-host; refactor if multi-node needed |
| **Inference failover** | Client-side provider chain | Service mesh / sidecar | Direct provider control; no infrastructure dependency |
| **Model export format** | ONNX | TorchScript, TF SavedModel | Cross-platform, mature tooling, hardware-accelerated |
| **Compression integration** | External tools only | Native integration | Avoid bloat; external tools evolve faster |
| **Data pipeline** | SQLite + LocalMemoryStore | Postgres / Redis | Single-user; adequate for current scale |

---

## Related Skills

- `azazael-ml-platforms` — ML platform infrastructure (ONNX, Ray, LM Studio, diagnostics)
- `azazael-neural-architecture` — Neural architecture reference (MoE, SSM, NAS, RL patterns)
- `azazael-training-pipeline` — Training data pipeline (ETL, feature extraction, 3 trainers)
- `azazael-inference-protocol` — 12-provider failover, auto-fallback, RULE 0D/0Z-A
- `azazael-inference-providers` — Provider registry (16 providers, OpenAI-compatible API)
- `azazael-model-compression` — Quantization, distillation, pruning (bridge system)
- `azazael-neural-pipeline` — NeuralPipeline orchestrator (6-step lifecycle)
- `azazael-orchestration` — High-level ORCHESTRATION + HYDRA overview
