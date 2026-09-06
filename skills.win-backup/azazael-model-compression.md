---
name: azazael-model-compression
description: Model compression techniques — quantization (GPTQ, AWQ, GGUF), knowledge distillation, and pruning. Integration with ONNX pipeline, inference providers, and ml-platforms infrastructure.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Model Compression — Quantization, Distillation & Pruning

> **Relevance:** Deploying large models on constrained hardware (consumer GPU, edge)
> **Existing infra:** `azazael-ml-platforms` (ONNX pipeline), `azazael-inference-protocol` (provider failover)
> **External tools:** GPTQ, AWQ, GGUF, TensorRT

---

## Part 1: Quantization

### Overview
Quantization reduces model precision (e.g., FP16 → INT4) to shrink memory footprint and accelerate inference, with minimal accuracy loss.

### Modern Formats (2025-2026)

| Format | Bit Width | Best For | Hardware | Accuracy Retention |
|--------|:---------:|----------|----------|:------------------:|
| **GPTQ** | 2-8 bits | GPU inference (NVIDIA) | CUDA GPUs | 98-99% at 4-bit |
| **AWQ** | 4 bits | GPU inference (aware) | CUDA GPUs | 99%+ at 4-bit |
| **GGUF** | 2-8 bits | CPU + Apple Silicon | Universal | 97-99% at 4-bit |
| **Bitsandbytes** | 4-8 bits | Training + inference | CUDA GPUs | 99% at 8-bit |
| **NF4** (QLoRA) | 4 bits | Fine-tuning | CUDA GPUs | 99% at 4-bit |

### Format Selection Guide

| Scenario | Recommended Format |
|----------|:------------------:|
| NVIDIA GPU inference, throughput-critical | **GPTQ** (4-bit) |
| NVIDIA GPU inference, quality-critical | **AWQ** (4-bit) |
| CPU / Apple Silicon / cross-platform | **GGUF** (Q4_K_M) |
| Training + inference on same GPU | **Bitsandbytes** (8-bit) |
| Fine-tuning with quantization (QLoRA) | **NF4** |

### Integration with Existing ONNX Pipeline

```python
# Existing ml-platforms ONNX pipeline supports quantization-friendly export
# Note: quantize_onnx() is a proposed pattern — implement or use external tools
from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx

# Export → quantize (external) → deploy
onnx_model = export_to_onnx(pytorch_model, "model.onnx")
# Deploy via existing inference providers via azazael-inference-protocol
```

### Installation (External Tools)

```bash
# GPTQ
pip install auto-gptq

# AWQ
pip install autoawq

# GGUF (via llama.cpp)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Bitsandbytes (CUDA)
pip install bitsandbytes
```

---

## Part 2: Knowledge Distillation

### Overview
Train a smaller "student" model to mimic a larger "teacher" model, retaining most of the teacher's capability at a fraction of the compute cost.

### Distillation Types

| Type | Teacher | Student | Use Case |
|------|---------|---------|----------|
| **Response-based** | Output logits | Mimics final predictions | Classification, regression |
| **Feature-based** | Intermediate layers | Mimics hidden representations | Transfer learning |
| **Self-distillation** | Deeper layers of same model | Shallower layers | Single-model optimization |
| **Online distillation** | Peer models | Joint training | Multi-task, ensemble |

### Existing Codebase Integration

- **Teacher model source:** `CORE/WORMS/expansion/learning.py` (2,099L, 6 classes) — core RLTrainLoop and DataPipelineWorm serve as natural teacher models
- **Student evaluation:** `ml-platforms/harness.py` for student model testing
- **Deployment:** Via `azazael-inference-protocol` (provider failover) and `azazael-inference-providers`

```python
# Distillation output can be served via existing inference pipeline
# Use ml-platforms harness for student model evaluation
from ORCHESTRATION.ml_platforms.harness import Harness

harness = Harness()
# Train student (e.g., from learning.py teacher), evaluate via harness
```

---

## Part 3: Pruning

### Overview
Remove redundant weights or neurons from a trained model to reduce size with minimal accuracy degradation.

### Pruning Strategies

| Strategy | Granularity | Compression | Accuracy Impact |
|----------|:------------:|:-----------:|:----------------:|
| **Weight pruning** | Individual weights | 50-90% sparsity | Low (with retraining) |
| **Neuron pruning** | Entire neurons | 30-50% | Low |
| **Layer pruning** | Entire layers | 10-30% | Medium |
| **Structured pruning** | Channels/filters | 30-50% | Low |
| **Unstructured pruning** | Random weights | 50-80% | Low (with retraining) |

### Tools

| Tool | Approach | Integration |
|------|----------|-------------|
| **PyTorch pruning** (torch.nn.utils.prune) | Weight + structured | Direct Python |
| **TensorFlow Model Optimization** | Weight + structured | tf-models-official |
| **NNI pruning** | Automated pruning algorithms | `pip install nni` |
| **ONNX Runtime** | Graph optimization + pruning | Via existing ONNX pipeline |

---

## Part 4: Deployment Workflow

### From Training to Compressed Inference

```
Trained Model (FP16, ~7GB for 7B params)
        |
        v
    [Step 1: Quantize]
        |
        +-- GPTQ (GPU) → ~3.5GB at 4-bit
        +-- AWQ (GPU)  → ~3.5GB at 4-bit
        +-- GGUF (CPU) → ~4.1GB at Q4_K_M
        |
        v
    [Step 2: Distill (optional)]
        |
        +-- Teacher → Student (e.g., 7B → 1.5B)
        |
        v
    [Step 3: Prune (optional)]
        |
        +-- Remove 30% of neurons → ~1GB student
        |
        v
    [Step 4: Deploy via existing infrastructure]
        +-- azazael-inference-protocol (12-provider failover)
        +-- azazael-ml-platforms (ONNX pipeline, LM Studio serving)
        +-- azazael-inference-providers (provider registry)
```

---

## Part 5: Quality Evaluation

### Metrics to Track

| Metric | Tool | Target |
|--------|------|:------:|
| Perplexity (LLMs) | `lm-evaluation-harness` | Within 2% of baseline |
| Accuracy (classification) | Task-specific eval | Within 1% of baseline |
| Latency (ms/token) | `ml_platforms/run_qanalysis.py` | ≥2x improvement |
| Memory (GB) | System monitoring | ≥2x reduction |
| Model size (GB) | `du -sh` | ≥2x reduction |

## Related Skills

- `azazael-neural-architecture` — Parent neural architecture reference (MoE, SSM, NAS)
- `azazael-ml-platforms` — ONNX pipeline, LM Studio, Ray distributed compute (deployment targets)
- `azazael-inference-protocol` — 12-provider failover for compressed model serving
- `azazael-inference-providers` — Provider registry with model deployment slots
- `azazael-neural-pipeline` — End-to-end training orchestrator (input to compression)
