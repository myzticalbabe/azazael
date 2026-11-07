# Hyper-Edge Quant Doctrine — 2026-11-06

Forensic basis: two web legs (GGUF quant quality; EXO/decentralized-edge
adaptation) plus our own live proof (Qwen3-4b Q4_K_S sidecar serving fine
on one box via LM Studio :1234). Doctrine: **F32 is the archive format,
not the serving format. Emit spec-exact simple quants; delegate K-quants
upstream; never hand-roll what llama.cpp already encodes canonically.**

## The ladder (community-measured, our sidecar confirms the shape)

| tier | size vs F32 | perplexity cost | Eve foundry status |
| --- | --- | --- | --- |
| F32 | 1x | 0 (reference) | archival opt-in (`--dtype F32`) |
| Q8_0 | ~4x smaller | +0.03% (near-lossless) | **default** (`gguf:Q8_0`) |
| Q4_0 | ~7x smaller | ~+2% | aggressive tier (`--dtype Q4_0`) |
| Q4_K_M | ~7-8x smaller | +1.7% (sweet spot) | delegated to llama.cpp encoder (not hand-rolled) |
| Q6_K | ~5x smaller | best quality/size | same delegation path |

Measured in-tree (toy 8x8+8 scale, exact): F32 288B tensor data,
Q8_0 102B (3.76x), Q4_0 54B (5.33x; alignment absorbs more at scale).
`max_recon_error` recorded per build: Q8_0 < 0.05, Q4_0 < 0.12 asserted.

## Native rules

1. **Quant-first foundry.** Every `eve foundry` build defaults to Q8_0.
   F32 requires asking for it. Serving F32 by accident is the old reality.
2. **Per-layer precision where it matters.** `--hi-prec foundry.bias`
   keeps small anchor tensors at F32 (`gguf:mixed`); attention-mass
   tensors would take the same path at real scale.
3. **Imatrix hook, honest proxy.** Manifest records `static_importance`
   (normalized |w|) per tensor today; the same hook consumes
   activation-based imatrices from a calibration corpus through a real
   runner when available. Static numbers, not narrative.
4. **K-quants are upstream's job.** Q4_K_M/Q6_K super-block packing lives
   in llama.cpp's canonical encoder. A drifted clone is worse than none.
5. **Parse-back or it didn't happen.** Every build re-reads its own bytes
   (magic, version, arch, per-tensor dtype + data_bytes). Runner-loadable
   weights for a named arch need that arch's real tensors — queued.

## Hyper-edge adaptations ( queued paths, named owners)

- **EXO-style pipeline-parallel sharding** across consumer devices
  (community: 2.2x on 3 phones) — Eve swarm already pools explicitly;
  shard placement is the next slice, not this one.
- **NPU/OpenVINO targets** for Intel AI PC fleets — foundry emits the
  quant; the NPU backend binding is queued behind a real device.
- **evML/TEE attestation** for trust without a datacenter — queued
  behind the same device reality.
- **Local-first serving** is already live: therapy prefers the :1234
  sidecar, cloud is fallback. That ordering IS the hyper-edge posture.

## Acceptance (re-run, don't quote)

```
pytest tests/test_eve_foundry.py -q            # 5 passed
eve foundry --out /tmp/q --name q --dtype Q4_0 # gguf:Q4_0 ok
eve foundry --out /tmp/m --name m --dtype Q4_0 --hi-prec foundry.bias  # gguf:mixed
```
