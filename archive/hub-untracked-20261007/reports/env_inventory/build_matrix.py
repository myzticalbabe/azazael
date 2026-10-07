#!/usr/bin/env python3
"""Cross-environment package matrix for Azazael.

Reads pip freeze files written by the env inventory probes and reports:
  - per-environment package counts
  - packages shared by all environments
  - packages unique to a single environment
  - a matrix for a curated set of runtime-critical packages

Stdlib only; prints markdown to stdout.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

SOURCES = {
    "win-main": "win_main_py.txt",
    "win-314t": "win_venv-314t.txt",
    "win-313tools": "win_venv-313-tools.txt",
    "win-interp": "win_venv-interpreter.txt",
    "ubuntu": "ubuntu_pip.txt",
    "kali": "kali_pip.txt",
}

PKG_RE = re.compile(r"^([A-Za-z0-9_.+-]+)==")


def load(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = PKG_RE.match(line.strip())
        if m:
            out[normalize(m.group(1))] = line.strip().split("==", 1)[1]
    return out


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


envs = {name: load(HERE / fn) for name, fn in SOURCES.items()}

print("# Cross-Environment Python Package Matrix\n")
print("| Environment | Packages |")
print("|---|---:|")
for name, pkgs in envs.items():
    print(f"| {name} | {len(pkgs)} |")

all_names = set().union(*(set(p) for p in envs.values()))
shared = {n for n in all_names if all(n in p for p in envs.values())}
print(f"\n- Union of distinct distributions: **{len(all_names)}**")
print(f"- Present in *every* environment: **{len(shared)}**")

print("\n## Packages unique to one environment (top 40 each)\n")
for name, pkgs in envs.items():
    others = set().union(*(set(p) for k, p in envs.items() if k != name))
    uniq = sorted(set(pkgs) - others)
    print(f"\n### {name} — {len(uniq)} unique")
    for n in uniq[:40]:
        print(f"- {n}=={pkgs[n]}")
    if len(uniq) > 40:
        print(f"- …and {len(uniq) - 40} more")

CRITICAL = [
    "numpy", "scipy", "torch", "torchvision", "transformers", "tokenizers",
    "safetensors", "accelerate", "peft", "trl", "datasets", "sentence-transformers",
    "onnxruntime", "onnx", "openvino", "llama-cpp-python", "llama-cpp-python-cuda",
    "gymnasium", "stable-baselines3", "sb3-contrib", "scikit-learn", "pandas",
    "matplotlib", "networkx", "igraph", "python-louvain", "community",
    "fastapi", "uvicorn", "flask", "aiohttp", "httpx", "openai", "anthropic",
    "litellm", "google-generativeai", "pydantic", "rich", "psutil", "pillow",
    "nuitka", "pytest", "mypy", "ruff", "hypothesis", "soundfile", "librosa",
    "chromadb", "faiss-cpu", "sentencepiece", "tiktoken", "pyarrow", "polars",
    "ray", "dask", "sqlalchemy", "alembic", "redis", "kuzu", "graphiti-core",
    "neo4j", "rustworkx", "pyvis", "plotly", "dash", "streamlit", "gradio",
]

print("\n\n## Runtime-critical package matrix\n")
header = "| package | " + " | ".join(envs) + " |"
print(header)
print("|" + "---|" * (len(envs) + 1))
for pkg in CRITICAL:
    key = normalize(pkg)
    row = [pkg] + [envs[e].get(key, "—") for e in envs]
    if any(v != "—" for v in row[1:]):
        print("| " + " | ".join(row) + " |")

missing_everywhere = [p for p in CRITICAL if normalize(p) not in all_names]
print(f"\n**Absent from every Python environment:** {', '.join(missing_everywhere) or 'none'}")
