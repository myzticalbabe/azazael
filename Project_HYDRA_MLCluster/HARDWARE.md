# Hardware Requirements — Project HYDRA MLCluster

## Reference platform (the machine the work was done on)

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 285H (16 cores, 22 threads) |
| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |
| **RAM** | 32 GB LPDDR5x-8533 (dual channel) |
| **OS** | Windows 11 Pro 24H2 (build 26100) |
| **Python** | 3.14.7 (free-threaded) / 3.15.0rc3 (free-threaded) |

This table describes where the code was written. It is **not** a validated
configuration, and nothing in this tree was benchmarked for this document.

## What this component needs

| Component | Requirement | Source |
|---|---|---|
| Python | 3.10+ | `tools/HYDRA/*.py` |
| ML runtimes | TensorFlow and others, discovered at run time | `tools/HYDRA/find_python_with_tensorflow.bat` |
| GPU | optional; the cluster is meant to span heterogeneous compute | README |
| Disk | must hold datasets named by `datasets.json` | `tools/HYDRA/datasets.json` |

## What was validated

`tools/HYDRA/10min_test_results.json` is a stored run result, but this document did
not read it to extract a figure, and the run it came from is not described in the
tree with enough detail to repeat it. Treat the stored result as evidence that a run
happened, not as a benchmark.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
