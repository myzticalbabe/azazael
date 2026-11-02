# RENDERING SERIES PLAN: "The Headless Oxman & Lilith's Wraith"

## Series Overview
**Format:** Multi-episode photorealistic narrative renders (L4, ComfyUI/Blender)
**Style:** Dark fantasy / psychological horror / mythic realism
**Resolution:** 1024x1360 (portrait) denoised Cycles, 1024 spp
**Frame Rate:** 30 fps → interpolated to 60 via RIFE
**Output:** MP4 (H.265/HEVC CRF 22), PNG sequence archive

---

## CHARACTER SHEETS

### The Headless Oxman
**Archetype:** SENTINEL (planted, arms folded, immutable)
**Visual Identity:**
- No head — neck terminates in cauterized stump with faint glyph-carved bone
- Massive yoked shoulders (ox-hide pauldron fused to flesh)
- Hands: left holds severed horn (ritual), right grips chain disappearing into fog
- Torso: scar-map of every labor — furrowed like plowed earth
- Stance: feet planted, weight centered, gravity bends around him
- Palette: umber, ochre, rust, bone-white, cold iron grey
- Lighting: single overhead shaft (divine judgment), deep sub-surface scattering on skin

**Animation Keys:**
- Micro-breath: subtle rib expansion (3-frame cycle)
- Chain tension: periodic pull (12-frame cycle)
- Glyph pulse: faint amber glow at neck-stump (7-frame cycle)

### Lilith's Wraith
**Archetype:** ZEALOT (pitched forward, driving, hunting)
**Visual Identity:**
- Semi-corporeal: edges feather into particulate smoke
- Face: beautiful but wrong — eyes are voids with single-pixel highlights
- Hair: unbound, moves underwater-slow, strands detach → become moths
- Attire: tattered wedding shroud (silk → ash gradient), trailing 3m
- Hands: elongated fingers, nails blackened, clutching phylactery
- Aura: cold blue rim-light, volumetric fog follows motion
- Ground contact: none — hovers 2cm, dust swirls beneath

**Animation Keys:**
- Drift: perpetual forward lean (0.5°/frame)
- Moth release: every 15 frames a strand detaches
- Phylactery pulse: syncs with Oxman's glyph (inverse phase)
- Breath: visible frost plume (8-frame cycle)

---

## EPISODE ARC (6 Episodes × 90s)

| Ep | Title | Core Conflict | Visual Motif |
|---|---|---|---|
| 1 | "The Yoke Remembers" | Oxman's origin — the beheading that made him eternal | Horn → chain transformation |
| 2 | "She Who Waits in Wire" | Lilith's binding — the ritual that severed her | Shroud threads → circuit traces |
| 3 | "Crossroads of Bone" | First meeting — neither can kill the other | Glyph ↔ Phylactery resonance |
| 4 | "The Harvest of Silence" | They hunt the thing that cursed them both | Fog reveals memory-echoes |
| 5 | "Unmaking the Knot" | Climax — chain wraps phylactery, both unravel | Light eats shadow, shadow eats light |
| 6 | "Neither Head Nor Name" | Aftermath — two hollows where legends stood | Empty yoke, floating veil, silence |

---

## TECHNICAL PIPELINE

### Stage 1: Asset Generation (ComfyUI)
```yaml
Models:
  - FLUX.1-dev (primary) — 1024x1360, 28 steps, CFG 3.5
  - SDXL-refiner (detail pass) — 0.3 denoise
  - ControlNet: depth (Oxman), openpose (Wraith), canny (environment)
  
Prompts (per episode, 6 camera angles each):
  - Character close-up (portrait)
  - Environmental wide (establishing)
  - Action moment (dynamic)
  - Memory echo (ethereal overlay)
  - Glyph/phylactery detail (macro)
  - Transition frame (morph target)
```

### Stage 2: 3D Reconstruction (Blender)
```python
# Photogrammetry from ComfyUI multi-angle outputs
# → Meshroom / RealityCapture → clean topology in Blender
# Rig: MetaHuman-compatible skeleton + custom glyph/chain rig
# Materials: Principled BSDF + custom OSL for glyph glow, Wraith dissipation
# Hair: Geometry Nodes (Wraith) / Particle System (Oxman chain)
```

### Stage 3: Animation & Lighting (Blender Cycles)
```python
Render Settings:
  - Engine: Cycles (ONEAPI on Arc 140T)
  - Samples: 1024 (denoised: OIDN)
  - Resolution: 1024x1360 (portrait)
  - Color: Filmic Log, sRGB output
  - Frames: 2700 per episode (90s × 30fps)
  
Lighting Rig:
  - Key: Sun (Oxman) / Area cold (Wraith)
  - Fill: HDRI (environment-specific)
  - Rim: Volumetric scatter (fog interaction)
  - Practical: Glyph emission / Phylactery pulse
```

### Stage 4: Compositing & Interpolation
```bash
# RIFE 4.25 (2x interpolation) → 60fps
# DaVinci Resolve: color grade (LUT: Kodak 2383 + custom curve)
# Audio: Spatial mix (Oxman low freq rumble / Wraith high freq whisper)
# Export: HEVC CRF 22, 10-bit, HDR10 metadata
```

---

## PRODUCTION SCHEDULE

| Week | Deliverable | Tool |
|---|---|---|
| 1 | Character concept sheets (6 views each) | ComfyUI + Photoshop |
| 1-2 | Environment concepts (6 locations) | ComfyUI |
| 2-3 | 3D base meshes + rigs | Blender + Meshroom |
| 3-4 | Animation blocking (all 6 eps) | Blender |
| 4-5 | Lighting + render (16,200 frames total) | Blender Cycles (ONEAPI) |
| 5 | RIFE interpolation + comp | RIFE + Resolve |
| 5-6 | Audio design + final export | Reaper + Resolve |

**Estimated Render Time:** 16,200 frames × 34s/frame = **153 hours** (6.4 days continuous on Arc 140T)
**Parallelization:** 3 GPU instances (2 ep each) → **~2.1 days**

---

## QUALITY GATES

| Gate | Criteria | Tool |
|---|---|---|
| **Asset** | 3 distinct perceptual hashes per frame (pHash, dHash, aHash) | ImageMagick |
| **Animation** | Temporal consistency: SSIM > 0.98 frame-to-frame | Custom Python |
| **Render** | No fireflies (max pixel < 1.0 after tonemap), no NaN pixels | Custom Python |
| **Compression** | VMAF > 95 vs source PNG | FFmpeg + VMAF |
| **Sync** | Audio-video drift < 5ms over 90s | FFprobe |

---

## MEMORY INTEGRATION

**PMB Chains:** `oxman_episodes`, `lilith_wraith_episodes`, `render_queue`
**Engram Observations:** Each render session → `mem_save` with frame hashes, timings, anomalies
**Board Tasks:** `lane.kilo.tasks` → one per episode render batch

---

## FALLBACK PLAN

If Arc 140T Cycles proves unstable:
1. **CPU fallback:** Blender Cycles CPU (13× slower → 20 days) — unacceptable
2. **Cloud burst:** Runpod A6000 (48GB) — $0.76/hr → ~$116 for full render
3. **Hybrid:** Keyframes local, in-betweens cloud — $40 estimate

---

## LANDING CHECKLIST

- [ ] Character sheets approved (Oxman + Wraith)
- [ ] Episode 1 ComfyUI batch complete (36 images)
- [ ] Blender photogrammetry test passes (mesh < 50k tris/char)
- [ ] Cycles ONEAPI render test: 1 frame < 40s
- [ ] RIFE interpolation verified on 10-frame test clip
- [ ] PMB chains created, board tasks posted
- [ ] Runbook documented for cloud burst failover

---

**Next Action:** Generate Episode 1 character concepts in ComfyUI (prompt engineering session).
**Owner:** kilo lane (rendering)
**Dependencies:** ComfyUI FLUX.1-dev loaded, ControlNet models cached, Blender 4.5.10 + ONEAPI verified.