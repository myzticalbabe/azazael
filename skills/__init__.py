"""AZAZAEL Skills — Optimum configurations, benchmarks, and agent memory."""

OPTIMUM_CONFIG = {
    "timestamp": "2026-05-28",
    "python": "3.14.5", "free_threading": True, "gil_disabled": True,
    "cpu": "Intel 16-core", "gpu": "None",
    "primary_backend": "ollama_subprocess",
    "best_models": {
        "fast": "llama3.2:1b", "quality": "eve-unleashed:latest",
        "vision": "moondream:latest", "embedding": "nomic-embed-text:latest",
    },
    "ml_status": {
        "numpy": "2.4.6 OK", "torch": "2.12.0+cpu OK (GIL=0)",
        "PIL": "12.2.0 OK", "scipy": "BROKEN", "transformers": "FAILS",
    },
    "benchmarks": {"numpy_500x500_matmul_ms": 30.8},
    "available_ollama": [
        "llama3.2:1b", "moondream:latest", "nomic-embed-text:latest",
        "eve-unleashed:latest", "llava:7b", "minicpm-v:latest",
    ],
    "local_gguf": [
        "gemma-4-E4B-it-IQ4_XS.gguf", "gemma-4-E4B-it-heretic-Q4_K_M.gguf",
    ],
    "recommendations": [
        "Use ollama subprocess for LLM inference",
        "Set PYTHON_GIL=0 for torch/numpy imports",
        "Avoid Unicode emoji in Windows CLI",
        "Use circuit_breaker.py for production resilience",
    ],
}

def recommend(task="inference"):
    m = {"inference":"llama3.2:1b","vision":"moondream:latest",
         "embedding":"nomic-embed-text:latest","tensor":"torch_cpu"}
    return {"backend":"ollama","model":m.get(task,"llama3.2:1b")}
