# Hardware Requirements — Project WASM Compiler

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
| Rust | edition 2024; `wasm32-unknown-unknown` target | `tools/RUST_WASM/Cargo.toml` |
| wasm target | `target-feature=+simd128` via `.cargo/config.toml` | `tools/RUST_WASM/.cargo/config.toml` |
| Node | any version that runs ES modules | `tools/RUST_WASM/bench.mjs` |
| GPU | none | the workload is a 1536-dimension `Float32Array` dot product |

## What was measured, and on what

`tools/RUST_WASM/MEASURED_2026-11-01.md` records Node 24.14.0, wasm-pack 0.15.1
and rustc 1.95.0. Those are the only version claims this tree makes, and they come
from the record rather than from this document.

The record does **not** name the CPU or the memory, so it is not a citation for
the development-machine table below — it is a citation for the toolchain only.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
