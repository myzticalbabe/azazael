# AZAZAEL PROJECT MAP — Complete Ecosystem Inventory

> *Last updated: June 2, 2026 — Full scan: Windows 11 Desktop + WSL2*
> *Next audit: Phase 23*

---

## 🔷 WINDOWS 11 DESKTOP PROJECTS (Discovered)

### Active / Maintained Projects

| # | Project | Path | Type | Status | Python Files | EXEs |
|---|---------|------|------|--------|-------------|------|
| 1 | **azazael** | `~/azazael/` | Core framework | ✅ Active | 305+ | - |
| 2 | **AZAZAEL_Standalone** | `~/Desktop/AZAZAEL_Standalone/` | Desktop EXEs | ✅ Active | 12+ build scripts | 51 EXEs |
| 3 | **AZAZAEL_Vault** | `~/Desktop/AZAZAEL_Vault/` | File system visualizer | ✅ Active | 2 (server+launcher) | 1 (Nuitka) |
| 4 | **EveUnleashed_Selector** | `~/Desktop/EveUnleashed_Selector/` | RANI-VL Framework | ✅ Active | 20+ | 1 (Eve) |

### Partially Operational

| # | Project | Path | Type | Status | Notes |
|---|---------|------|------|--------|-------|
| 5 | **PerformanceMonitor** | `~/Desktop/PerformanceMonitor/` | System monitoring | 🟡 Partial | Frontend + server, needs rebuild |
| 6 | **WSL_CrossExplorer** | `~/Desktop/WSL_CrossExplorer/` | WSL file transfer | 🟡 Partial | Frontend + Python server |
| 7 | **WSL Models** | `~/Desktop/WSL Models/` | Model management | 🟡 Partial | README only, scripts need audit |
| 8 | **Ultimate_Agent_Selector** | `~/Desktop/Ultimate_Agent_Selector/` | Agent launcher | 🟡 Partial | Includes RANI orchestrator |

### Deprecated / Stub

| # | Project | Path | Type | Status |
|---|---------|------|------|--------|
| 9 | **CODEX_Studio_Output** | `~/Desktop/CODEX_Studio_Output/` | Video output | 🔴 Deprecated |
| 10 | **agent_system** | `~/Desktop/agent_system/` | Agent scripts | 🔴 Stub |
| 11 | **SysTools_JSON_Converter** | `~/Desktop/SysTools_JSON_Converter/` | JSON tools | 🔴 Deprecated |
| 12 | **CODEX** | `~/Desktop/CODEX/` | Video generation | 🔴 Deprecated |

---

## 🔷 WSL2 PROJECTS (Discovered — Ubuntu 26.04, Kali Linux, Docker Desktop)

| # | Project | Path | Type | Notes |
|---|---------|------|------|-------|
| 1 | **azazael** | `~/azazael/` | Core framework | WSL2 copy |
| 2 | **llama.cpp** | `~/llama.cpp/` | LLM inference | C++ GGUF runner |
| 3 | **openmono.ai** | `~/openmono.ai/` | AI platform | OpenMono ecosystem |
| 4 | **open-interpreter** | `~/open-interpreter/` | AI coding agent | Python-based |
| 5 | **models** | `~/models/` | GGUF models | Llama models stored here |
| 6 | **workspace** | `~/workspace/` | Dev workspace | Scripts, orchestrators |
| 7 | **scripts** | `~/scripts/` | Automation | Shell/Python scripts |
| 8 | **go** | `~/go/` | Go workspace | Go projects |
| 9 | **intel** | `~/intel/` | Intel tooling | NPU/iGPU setup |

---

## 🔷 VL (Vision-Language) DATA & OBJECT TYPES

### RANI-VL Framework (`EveUnleashed_Selector/`)
The **RANI (Recursive Adversarial Native Intelligence) VL Framework** is a multi-modal vision-language agent system.

### VL Data Types
| Type | Description | Example |
|------|-------------|---------|
| `GGUF` | Quantized model format | `qwen3-vl-8b-q4_k_m.gguf` |
| `VL_IMAGE` | Image input for vision models | JPEG, PNG, WebP |
| `VL_TEXT` | Text input/output | String, tokens |
| `VL_DOCUMENT` | Document input (PDF, DOCs) | Extract text via vision |
| `VL_EMBEDDING` | Vector embeddings | 4096-dim vectors |
| `VL_CONFIG` | Model configuration | Context size, temp, top_k |
| `VL_SESSION` | Inference session state | Messages, history |
| `VL_RESULT` | Inference output | Generated text + metadata |

### Object Types
| Object | Fields | Description |
|--------|--------|-------------|
| `ModelConfig` | `name, path, port, ctx_size, temperature` | LLM model configuration |
| `InferenceResult` | `text, tokens_per_sec, model, timestamp` | Single inference output |
| `BackendState` | `type, available, model_loaded` | Backend status (Ollama/llama.cpp/Transformers) |
| `BenchmarkResult` | `prompt, response_time, tps, model` | Performance benchmark |
| `MemoryEvent` | `source, event_type, data, timestamp` | PAMS/LocalMemory event |
| `GGUFModel` | `path, size, quantization, context` | Local GGUF model file |

### Backend Types
| Backend | Protocol | Use Case | Status |
|---------|----------|----------|--------|
| Ollama | HTTP REST | Fast inference, model management | ✅ Active |
| llama.cpp | Subprocess/HTTP | Local GGUF models | ✅ Active |
| HuggingFace Transformers | Python API | Python-native inference | ✅ Active |
| llama-server | HTTP Server | Dedicated model server | ✅ Active |

### Model Registry (Known Models)
| Model | Size | Type | Quantization | Location |
|-------|------|------|-------------|----------|
| Qwen3-VL 8B | 4.8 GB | Vision-Language | Q4_K_M | ~/.lmstudio/models/ |
| Qwen3-VL abliterated v2.0 | 4.5 GB | Vision-Language | Q4_K_S | ~/.lmstudio/models/ |
| Gemma 4 E4B | ~3 GB | Text | Q4_K_M | models/ |
| Eve-V2-Unleashed | ~5 GB | Text | Q4_K_M | eve_rebuild_test/ |

---

## 🔷 MISSING PROJECTS — Now Tracked

| Project | Previously Missing | Now Added | Source |
|---------|-------------------|-----------|--------|
| AZAZAEL_Vault | ✅ Was unknown | ✅ In PROJECT_MAP | Desktop scan |
| WSL2: workspace | ✅ Was unknown | ✅ In PROJECT_MAP | WSL2 scan |
| WSL2: open-interpreter | ✅ Was unknown | ✅ In PROJECT_MAP | WSL2 scan |
| WSL2: intel | ✅ Was unknown | ✅ In PROJECT_MAP | WSL2 scan |
| WSL2: go | ✅ Was unknown | ✅ In PROJECT_MAP | WSL2 scan |
| RANI-VL Framework | ✅ Not catalogued | ✅ VL data types documented | EveUnleashed scan |
| Qwen3-VL models | ✅ Not catalogued | ✅ In model registry | Model scan |

---

## 🔷 NEXT STEPS — Pure Python & Desktop Standalone Apps

### Pure Python (azazael core)
1. **Test Suite Expansion** — Add unit tests for all 76 worms
2. **Error Recovery** — Circuit breaker, retry, dead letter queue
3. **Config System** — Centralized YAML/TOML config
4. **Performance** — ThreadPoolExecutor, lazy loading, caching
5. **Documentation** — API reference, architecture diagrams, usage examples

### Desktop Standalone Apps
1. **Vault Enhancements** — Visual diff, keyboard shortcuts, settings panel
2. **Nuitka 3.14t** — Verify Nuitka compatibility with 3.14 free-threading
3. **Cross-Platform** — Linux/macOS builds for core EXEs
4. **Unified Launcher** — Single entry point for all Desktop apps
5. **Auto-Updater** — Built-in update mechanism for standalone EXEs

### Integration
1. **WSL Bridge** — Seamless file transfer between Windows/WSL2
2. **Memory Sync** — Cross-project memory store synchronization
3. **VL Pipeline** — Unified vision-language inference across all apps
