---
name: azazael-gil-sidecar
description: Azazael free-threaded vs GIL Python environment — why CPython 3.14t rejects cp314 wheels, how the same-version GIL sidecar is laid out, which packages need it, and how to resolve the right interpreter (CORE/python_env.py, python3.14-gil).
metadata:
  category: environment
  project: azazael
---
# Azazael GIL Sidecar — Two Interpreters, One Version
## The rule in one line
A **free-threaded** CPython build (`cpython-314t`) accepts **only `cp314t` wheels**.
Any package with no `cp314t` wheel must run on a **GIL-enabled interpreter of the
same version** (`cpython-314`) — the *sidecar*.
## Why `-X gil=1` does not fix it
The extension suffix `.cpython-314t-x86_64-linux-gnu.so` is **compiled into** the
free-threaded build. A GIL-built `.so` (`.cpython-314-…`) can never be loaded into
it, whatever `PYTHON_GIL`/`-X gil` says. Resolution happens at the **process**
level: pick the interpreter, then spawn it. `PYTHON_GIL=1` only re-enables the GIL
*inside* a free-threaded build; it does not change which wheels are loadable.
## Layout (Ubuntu pillar, verified 2026-09-30)
| Role | Path | ABI |
|---|---|---|
| Primary (free-threaded) | `/usr/local/python314t/bin/python3.14t` | `cpython-314t` |
| Sidecar (GIL) | `/usr/local/python3147-gil/bin/python3.14` | `cpython-314` |
| Sidecar venv | `/root/venv-314-gil` | — |
| Entry point | `/usr/local/bin/python3.14-gil` | — |
| Prebuilt GIL ML stack | `/usr/local/lib/python3.14/site-packages` (11 GB, **tensorflow 2.22.0-dev**) | `cpython-314` |
The sidecar reuses the prebuilt stack via one `.pth`:
`/root/venv-314-gil/lib/python3.14/site-packages/zzz_prebuilt_gil.pth`.
## The trap: `PYTHON_GIL=0`
`/root/.bashrc` exports `PYTHON_GIL=0`. A GIL build treats that as **fatal**
(`Fatal Python error: config_read_gil: Disabling the GIL is not supported by this
build`). Every GIL invocation must clear it — the `python3.14-gil` wrapper does,
`CORE/python_env.py`'s `probe()` does, and `scripts/rebuild_gil_sidecar.sh` does.
## Resolving an interpreter from code
```python
import sys; sys.path.insert(0, "src")
from CORE import python_env
python_env.interpreter_for("tensorflow")   # -> /root/venv-314-gil/bin/python
python_env.interpreter_for("torch")        # -> the running free-threaded primary
python_env.probe("import tensorflow as tf; print(tf.__version__)", module="tensorflow")
python_env.describe()                      # table of both interpreters
```
CLI: `python3 -m CORE.python_env --probe`
`probe()` also sets `KERAS_BACKEND` (torch on the primary, tensorflow on the
sidecar) and strips the inherited `PYTHON_GIL`.
## Packages that need the sidecar
`tensorflow`, `tf2onnx`, `orjson` (*the keystone* — it gates `langchain` and
`chromadb`), `polars`, `ray`, `spacy`.
Packages that are fine on the primary: `torch`, `keras`, `numpy`, `scipy`,
`pandas`, `sklearn`, `jax`, `transformers`, `onnxruntime`, `xgboost`, `lightgbm`,
`faiss`, `gymnasium`.
## TensorFlow specifically
There is **no `tensorflow` wheel on PyPI for Python 3.14 on any ABI** — verified
for `tensorflow`, `tensorflow-cpu` and `tf-nightly`. The pillar's TF is a local
`2.22.0-dev` build inside the prebuilt site-packages tree; the container takes
vendored wheels (`docker/Dockerfile.ubuntu`, `ARG TENSORFLOW_WHEELS`).
## Rebuild
```bash
bash scripts/rebuild_gil_sidecar.sh          # idempotent
GIL_VERSION=3.14.8 bash scripts/rebuild_gil_sidecar.sh
The interpreter comes prebuilt from `astral-sh/python-build-standalone`
(`…-install_only.tar.gz`, no `freethreaded` marker = the GIL build), so nothing is
compiled.
## Anti-patterns
* Installing a GIL-only package into the primary and expecting it to import — it
will fail with `ModuleNotFoundError` or an ABI error.
* Building a *second* free-threaded interpreter to fix this — wrong axis.
* Removing `/usr/bin/python3.14` (3.14.4) to "clean up": `apt` depends on
`python3.14-minimal` / `python3` / `python3-minimal`.
# Azazael GIL Sidecar — Two Interpreters: 3.15t Primary, 3.14-GIL Fallback
A **free-threaded** CPython build (`cpython-315t`) accepts **only `cp315t` wheels**.
Any package with no `cp315t` wheel must run on the **sanctioned 3.14 GIL fallback**
(`cpython-314`) — the *sidecar*. There is no GIL 3.15 on this pillar, so the
sidecar is deliberately cross-version. Rule: 314m (mainline-GIL 3.14) is the
ONLY 3.14 on any pillar — verified live 2026-10-21 (torch 2.16.0 CPU imports
on 3.15t free-threaded AND on the 3.14m sidecar). If 3.15t cannot serve a
workload (no cp315t wheel; e.g. SB3 training, which segfaults free-threaded),
run it on the 3.14m sidecar — never on a 3.14t build.
The extension suffix `.cpython-315t-x86_64-linux-gnu.so` is **compiled into** the
## Layout (Ubuntu pillar, verified 2026-10-21)
| Primary (free-threaded) | `/opt/python315t/bin/python3.15` (alias `/usr/local/bin/python3.15t`) | `cpython-315t` |
| Primary venv | `/root/py315t` | `cpython-315t` |
| Sidecar base (GIL) | `/usr/local/python3147-gil` | `cpython-314` |
| Entry point | `/usr/local/bin/python3.14-gil` (scrubs `PYTHON_GIL`) | — |
> Retired 2026-10-19: the 3.14t primary prefix (`/usr/local/python314t`) is
> archived. The 3.14 GIL sidecar stays: it is the ONLY sanctioned GIL runtime.
