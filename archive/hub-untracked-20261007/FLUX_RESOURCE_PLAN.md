# FLUX RESOURCE PLAN — 2026-09-30

The machine has **7.80 GiB of usable VRAM** and **15.37 GiB of RAM**. FLUX.1 is a
12B model. At fp8 the UNet is 11.08 GiB, so **it does not fit** — and that single
fact generates every problem below.

## The core finding

**The streaming is not inherent to FLUX. It is a consequence of choosing an fp8
UNet that does not fit.** Per-step PCIe traffic for one 1024×1360 image:

| configuration | passes/step | traffic/image | note |
|---|---|---|---|
| schnell fp8 (local) | 4 × 1 | **13.6 GB** | CFG is distilled in — one forward pass |
| dev fp8 (local) | 28 × 2 | **190 GB** | real CFG doubles the passes |
| **dev Q4_K_S** | 28 × 2 | **0 GB** | 6.34 GiB UNet, fully resident |

dev fp8 is the worst of both worlds: 190 GB of traffic for the sole privilege of
not downloading a 6.34 GiB file.

## Why Q4_K_S and not Q5

| variant | GiB | spare at 7.80 | verdict |
|---|---|---|---|
| **Q4_K_S** | **6.34** | **1.46** | chosen — room for activations |
| Q4_1 | 7.01 | 0.79 | viable, weaker K-quant |
| Q5_0 / Q5_K_S | 7.70 / 7.72 | **0.10** | **rejected** — activations exceed it |
| Q5_1 / Q6_K / Q8_0 | 8.39 / 9.18 / 11.83 | negative | exceeds VRAM |

The gap between Q4_K_S and Q5 is only 1.4 GiB, and that 1.4 GiB is exactly the
activation budget. Q5 does not fit at 1024×1360.

## The plan

### Phase 0 — reclaim, before the restart
1. **Dedup the 7 duplicate model sets: 16.62 GB.** Four are C:-only and need no
   judgement. Two span C: and G: (Eve-V2-Unleashed, nomic-embed). Keep the copy
   each tool actually reads — `llama-server\models` for the router,
   `.lmstudio` for LM Studio — and drop app-bundle and quarantine copies.
2. **WSL compaction: ~44 GB, deletes nothing.** `C:\wsl\Ubuntu-26.04\ext4.vhdx`
   is 186.59 GB on disk, 142 GB used inside. Requires `wsl --shutdown`, which
   stops two running distros. **User's call — do not run unasked.**
3. Disk is currently 51.80 GB free. Phase 0 takes it to ~70 GB. Neither phase
   depends on this, but both are easier after.

### Phase 1 — after restart, before rendering
The restart exists for **RAM**, not VRAM. Establish the budget first:
1. Close LM Studio, Edge, Chrome, and the AI Playground UI. Each holds model
   memory; with a 6.34 GiB UNet plus a 4.80 GiB text encoder, every idle
   gigabyte counts.
2. Confirm: ~12–13 GiB RAM free, ~7.5 GiB VRAM free.

### Phase 2 — get the model that fits
Download `city96/FLUX.1-dev-gguf` → `flux1-dev-Q4_K_S.gguf` (6.34 GiB,
1454 likes / 205k downloads, the standard repo). ComfyUI loads it via the
`UnetLoaderGGUF` node; GGUF is the format ComfyUI has first-class support for,
not a workaround.

**Do not delete the fp8 files yet.** They cost 22 GB and are the fallback if
Q4 turns out worse than expected — quality at 4-bit on a 12B model is a real
trade, and having both lets that be a measurement rather than a guess.

### Phase 3 — render order, cheapest first
| # | model | steps | cost | purpose |
|---|---|---|---|---|
| 1 | **schnell fp8** | 4, cfg 1.0 | 13.6 GB traffic | validate the whole pipeline end-to-end |
| 2 | **dev Q4_K_S** | 20–28, cfg 2.5 | 0 GB | first real quality read, at 896×1152 |
| 3 | dev Q4_K_S | 28–50, cfg 2.5 | 0 GB | finals at 1024×1360 |

Schnell first is deliberate: it exercises ComfyUI startup, model discovery, the
workflow JSON, the T5 encoder, the sampler and the output path, at 1/14th the
transfer cost. If something is misconfigured, find it on the cheap run.

### Phase 4 — measure, then decide
Record for one image: wall clock, peak RAM, peak VRAM, whether any offload
occurred. Then:
- **If a Q4 image lands under ~10 min** — go straight to finals, and delete the
  22 GB of fp8 weights.
- **If it lands over ~25 min** — the bottleneck is XPU compute on integrated
  graphics, not memory, and no amount of quantisation will fix that. Drop to
  schnell, or reduce steps.

## What will NOT work, so it is not attempted
- **Resolution increases.** 1024×1360 is already at the activation ceiling for a
  6.34 GiB UNet. 1536×2048 will OOM regardless of model.
- **Running both models at once.** They share the text encoder but each wants the
  whole VRAM.
- **Letting dev fp8 stream.** 190 GB of PCIe traffic is slower than the download
  that would replace it.

## The honest unknown
**Nothing here is measured yet.** Every number above is arithmetic from component
sizes, not from a render. The first image on each model is the measurement, and
the plan is structured so the cheap one comes first.