# RENDER SERIES — HYPER-EDGE JAEGERMEISTER ZEITGEIST

**Plan date:** 2026-11-02 · **Renderer:** Blender 4.5.10 LTS, Cycles on ONEAPI
(`C:/Users/clint/blender/blender-4.5.10-windows-x64/blender.exe`) · **Shot 1 rendered.**

The subject is a **figure**, not a glyph (RULE 0Q): a huntsman-automaton that carries
the doctrine the canon states — it *hunts* defects, it stands on ground, it is posed
to do the work rather than labelled with it. The series is the figure moving through
the states the canon defines, one state per shot.

## Ladder, held honestly

| level | what it is | where this series sits |
|---|---|---|
| L1 | glyph | not used — a glyph is not a figure |
| L2 | flat vector figure | the existing wallboard / `capture_archetypes.js` (interim) |
| L3 | material + light | shots 1–3 (Blender, this series) |
| **L4** | photoreal | not claimed. Sampled image data (SSS, per-pixel texture, bokeh) is the requirement; shots 1–3 are procedural geometry with physically-based materials, which is L3 and says so |

## The series

| # | title | the state it carries | camera | light | status |
|---|---|---|---|---|---|
| 1 | **The Warden at the Threshold** | a default is on before anyone asks; the figure stands in the gate it guards | 3/4 low, 55 mm, f/2 | warm key left, cold rim behind the arch, emissive core | **rendered** |
| 2 | **Every Test, Every Time** | 499 files, one file per process; the huntsman walking a ranked row of identical lanterns, one extinguished | tracking dolly, 35 mm | practical lanterns only, figure half-lit | planned |
| 3 | **A Hung File Is Not a Pass** | the wedge: the figure stopped mid-stride, its seams gone dark, clock frozen above | locked-off, 85 mm | single hard side key, no fill | planned |
| 4 | **Blocked Is Not Empty** | the web leg: the huntsman at a sealed door, empty field behind it (0 results vs blocked) | wide, 24 mm | fog, cold | planned |
| 5 | **One Settings Surface** | the figure removing its own armour plates, each plate a named default | macro, 100 mm | soft top box | planned |
| 6 | **DEAD-SHOT** | the arrow: the figure drawing, the target already struck | profile, 135 mm | hard backlight, dust | planned |
| 7 | **The Zeitgeist** | all seven states at once: the figure standing among its own earlier poses, which are statues | crane-up, 40 mm | dawn, long shadows | planned |

## Rules that govern every shot

1. **Frame index from the argument, never from the clock** — a re-render is reproducible.
2. **One Chrome/one Blender profile per render**, absolute output paths, never edit a
   running script (playbook §4–6).
3. **Render, then read the PNG.** Three checks (file exists, hash differs from the last,
   decoded dimensions) plus a visual read; source review does not count as verification.
4. **A readout must not hide its number**: the render log prints samples, device and time.
5. Device is quoted with any time (**ONEAPI**, never "Blender took 34 s"). CPU fallback is
   a 13× swing and must be announced, not silently absorbed.

## Files

```
tools/render_jaeger_series.py     one script, --shot N, deterministic per shot
renders/jaeger/shot01_*.png       output (renders/ is gitignored; the script is tracked)
logs/jaeger_render.jsonl          one line per render: shot, device, samples, seconds, sha
```
