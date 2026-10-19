---
name: azazael-314t-optimum
description: Optimum free-threaded agent configuration for Python 3.14t — inference backends, model selection, import status, troubleshooting
metadata:
  category: environment
  project: azazael
---
# AZAZAEL 3.14t Optimum Free-Threaded Agent Configuration
> **Memory File** — /skill azazael-314t-optimum
> **Generated:** 2026-05-28 | **Python:** 3.14.5 free-threading | **CPU:** Intel 16-core
## EXECUTIVE SUMMARY
After comprehensive testing of all available backends on Python 3.14.5 free-threading (GIL disabled, CPU-only):
| Component | Selection | Why |
|-----------|-----------|-----|
| Inference Backend | **Ollama** (subprocess) | Only working LLM backend |
| Python ML | NumPy 2.4.6 + PyTorch 2.12.0 CPU | Both import with PYTHON_GIL=0 |
| Fastest Model | llama3.2:1b (1.3GB) | Minimal resource usage |
| Best Vision | moondream:latest (1.7GB) | Vision-capable |
| Best Quality | eve-unleashed:latest (3.4GB) | 8B params, uncensored |
| Embeddings | nomic-embed-text:latest (274MB) | Fast, lightweight |
| GUI | tkinter | Only available GUI on 3.14t |
## HARDWARE
- CPU: Intel 16-core (AMD64), no GPU
- RAM: ~32GB estimated
- Python 3.14.5 free-threading (GIL disabled)
## AVAILABLE MODELS
### Ollama (6 models, ~17GB total)
- llama3.2:1b (1.3GB) — fastest
- nomic-embed-text:latest (274MB) — embeddings
- moondream:latest (1.7GB) — vision
- eve-unleashed:latest (3.4GB) — large, uncensored
- llava:7b (4.7GB) — multimodal
- minicpm-v:latest (5.5GB) — multimodal
### LM Studio GGUF (local files, ~20GB)
- gemma-4-E4B-it-IQ4_XS.gguf — User's requested Gemma model
- gemma-4-E4B-it-heretic-Q4_K_M.gguf — Alternative Gemma quant
- DeepSeek-R1-Distill-Qwen-7B.gguf
- Llama3.3-8B-Instruct-Thinking-Heretic.gguf
- Eve-V2-Unleashed-Qwen3.5-8B variants
## PYTHON 3.14t IMPORT STATUS
- numpy 2.4.6: OK (30.8ms 500x500 matmul)
- PIL 12.2.0: OK
- torch 2.12.0+cpu: OK (with PYTHON_GIL=0)
- scipy: BROKEN
- transformers: FAILS (regex conflict)
- onnxruntime: NOT INSTALLED
## INFERENCE STRATEGY
### Primary: Ollama subprocess
```python
import subprocess
result = subprocess.run(['ollama', 'run', 'llama3.2:1b', prompt],
capture_output=True, text=True, timeout=60)
```
### Secondary: Torch for tensor ops only
import os; os.environ['PYTHON_GIL'] = '0'
import torch; import numpy as np
### Future: llama-cpp-python
Not yet working on 3.14t. Use Ollama as bridge to GGUF models in LM Studio.
## TROUBLESHOOTING
1. ML packages crash: Set PYTHON_GIL=0 before import
2. Unicode crash on Windows CLI: Use ASCII chars only (no emoji)
3. Ollama timeout: Ensure ollama serve is running
4. PyInstaller fail: Exclude psutil, torch, zmq, matplotlib, bcrypt, win32com, pandas
## INFERENCE STUDIO v5.0.1
- Path: AZAZAEL_Standalone/AZAZAEL_Inference_Studio_314t.exe (11.2 MB)
- 7 tabs: Inference, Artifacts, Wiring, Lang/Compile, Animation
- CLI: --detect --frameworks --models --scan --json
- Thread-safe (root.after), os.walk scanner, 10-state emotion engine
## TODO (55 PRODUCTION items remaining)
Priority: Circuit breaker wiring, centralized YAML config, integration tests
> RETIRED 2026-10-19 — a backend survey measured on 3.14.5 free-threading, an interpreter this project no longer
> runs. Kept as provenance, not callable. Current stack: `C:/Azazael/.venvs/py315t`.
