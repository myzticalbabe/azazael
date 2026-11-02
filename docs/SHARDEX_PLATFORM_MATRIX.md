# GAMING PLATFORM MATRIX — the work surface for SHARDEX forging

**What this is.** A matrix of hardware classes, from 1972 to 2026, so a shard can be
forged *for a target* instead of for whatever the machine happens to be. Companion:
`docs/shardex_platforms.json` (the same rows, machine-readable, each carrying the URL it
came from).

**What this is not.** It is not a complete hardware database, and **no row in this file is
quoted without a source**. Where a figure was not verified in this pass it is *absent* and
the platform is listed under **Gaps** below — an invented MHz number would be exactly the
defect this estate keeps paying for, in a document that would then be cited for years.

Read on 2026-11-02. Two sources carried almost everything:

- **[W]** Wikipedia, *History of video game consoles* — the generation-level specification
  table (CPU / GPU / memory / media / common features / time period).
  <https://en.wikipedia.org/wiki/History_of_video_game_consoles>
- **[S]** system16.com and Sega Retro hardware pages, for arcade boards.
  <https://www.system16.com/hardware.php?id=720> · <https://segaretro.org/Sega_Model_3>

---

## 1. Home console generations — the spine [W]

| gen | period | primary consoles | CPU | GPU | RAM | media | what it means for a forge |
|---|---|---|---|---|---|---|---|
| 1 | 1972–1983 | Odyssey, Home Pong, Telstar, Color TV-Game | discrete diode–transistor logic | none | none | custom PCBs | no shard: there is no code to mirror |
| 2 | 1976–1992 | Channel F, Atari 2600, Odyssey², Intellivision, ColecoVision | 8-bit, 1–2 MHz | none | **64 B – 1 KB** | cartridges | a shard is a *ruleset*, not an asset bundle |
| 3 | 1983–2003 | NES, Master System, Atari 7800 | 8-bit, 2–4 MHz | none | **2–8 KB** | cartridges | 24-file ceiling is generous here; payload is irrelevant |
| 4 | 1987–2004 | TurboGrafx-16, Genesis, Neo Geo, SNES | 8/16-bit, 4–8 MHz | none | **8–128 KB** | cartridges, CD add-ons | first tier where sprite sheets dominate payload |
| 5 | 1993–2006 | 3DO, Jaguar, Saturn, PlayStation, N64 | 32/64-bit, 12–94 MHz | 26–63 MHz | **2–4 MB** | cartridges, optical | the first console class where a 2 MiB shard is *tight* |
| 6 | 1998–2013 | Dreamcast, PS2, GameCube, Xbox | 32/64-bit, 200–733 MHz | 100–233 MHz | **16–64 MB** | optical | texturing and audio outgrow the low-end payload cap |
| 7 | 2005–2017 | Xbox 360, PS3, Wii | 32/64-bit, 729 MHz–3.2 GHz | 243–500 MHz | **88–512 MB** | optical + digital | first generation that needs `tier: highend` for a whole game |
| 8 | 2012–present | Wii U, PS4, Xbox One, Switch | 32/64-bit, 1.0–2.3 GHz | 384–1172 MHz | **2–12 GB** | cart + optical + digital | shard budgeting must be per-slice, not per-game |
| 9 | 2020–present | Xbox Series X/S, PS5 | 64-bit, 3.5–3.9 GHz | 1565–2350 MHz | **10–16 GB** | digital, SSD streaming | the golden run must be *state*, never a frame |

The one number that changes SHARDEX's design is the memory column: a gen-3 shard and a
gen-9 shard differ by **six orders of magnitude of RAM**, while the METTHEW low-end cap is
2 MiB. That is not a bug in the cap — it is why `tier` exists, and why a forged arena
declares which class it is for.

## 2. Arcade boards — where the "hyper-edge" idea actually comes from [S]

| board | era | CPU | GPU / video | memory | note |
|---|---|---|---|---|---|
| Sega Model 2 | 1993 | (not verified here) | (not verified here) | up to ~62 MB across main/video/audio/other per secondhand sources | the board that made texture-mapped 3D an arcade standard |
| Sega Model 3 | 1996 | PowerPC 603ev **@ 166 MHz** (498 MIPS, 332 MFLOPS) | **2×** Lockheed Martin Real3D/PRO-1000 | **8 MB** work RAM | the "champion cabinet" class: what a 2026 tournament config should feel like |
| Sega NAOMI | 1998 | Hitachi SH-4 **64-bit RISC @ 200 MHz** (360 MIPS / 1.4 GFLOPS) | PowerVR (PVR2DC) | **32 MB** main RAM, up to **168 MB** solid-state ROM | the arcade twin of the Dreamcast: same silicon, different contract |

Model 3's date and clocks are the useful anchor: **166 MHz and 8 MB produced the arcade
look that tournaments still imitate**, which is why a forged arena can be "hyper-edge" at
`sim_hz: 60` with three orbs and a 12-metre floor. The look was never the polygon count.

## 3. Handhelds — mostly a gap, and that is stated rather than filled

| class | what is known here | what is NOT verified here |
|---|---|---|
| Game Boy / GBA | exist, and are the low-end floor for control latency | CPU clocks, RAM, panel resolution |
| DS / 3DS | dual-screen class; 3DS adds stereoscopic output | clocks, RAM, per-screen resolution |
| PSP / Vita | the 2005–2012 Sony handheld line | clocks, RAM, GPU |
| Switch / Switch 2 | hybrid class; docked vs handheld changes the thermal budget, not the rules | CPU/GPU clocks per mode |
| Steam Deck / ROG Ally class | x86 handheld PC; runs an existing build unchanged | TDP envelope per performance profile |

Handheld rows are deliberately empty of numbers. Filling them from memory would produce a
matrix that *looks* complete and is wrong in exactly the column a shard budget depends on.

## 4. What the matrix decides for SHARDEX (ENGINEERING DECISION — not hardware fact)

These are *our* thresholds, derived from the table above. They are choices, and they are
listed as choices so a reader can argue with them:

| shard class | target hardware | payload | `orbs` | `sim_hz` | tick budget |
|---|---|---|---|---|---|
| `lowend` | gen 3–5 console, or a phone | ≤ 2 MiB, ≤ 24 files (the METTHEW gate) | 3–5 | 30 | p99 < 33.3 ms |
| `midend` | gen 6–7 console, arcade Model 3 | ≤ 8 MiB | 6–8 | 60 | p99 < 16.7 ms |
| `highend` | gen 8–9, PC, Steam Deck class | declared, schema allows up to 8 GiB | 9–12 | 120 | p99 < 8.33 ms |

The rule that does not move: **the golden hash covers simulation state at `sim_hz` and
nothing else.** Resolution, upscaling, frame generation and lighting are presentation, and
a hash taken with them in the pipeline is a hash of the painter.

## 5. Gaps, named so they can be closed

Each of these needs its own source before a number appears in the table:

1. Model 2's CPU and video chips (the memory total arrived secondhand — it is marked as
   such, not promoted to a fact).
2. CPS-1 / CPS-2 / Neo Geo MVS clocks and RAM.
3. Handheld rows above.
4. Lifetime unit sales per platform — needed for "which games were actually on the market",
   which this pass did not attempt at all.
5. A per-platform *game* inventory (what shipped, what genre, what ruleset) — the matrix
   above is hardware only. The games column is the next document, and SHX-7's intake is
   where real game files enter the pipeline.

## 6. How to use it

```bash
python Project_SHARDEX/shardex.py --mirror <game> --out .shardex
python Project_SHARDEX/shardex.py --shatter --mirror-file .shardex/mirror.json --out .shardex
python Project_SHARDEX/shardex.py --forge .shardex/shards/<name> --out flame \
    --tune sim_hz=120 --tune orbs=9 --tune arena=16      # the highend column
python Project_SHARDEX/shardex.py --verify flame
```

Tune to a row, then publish the golden hash from that row. A bracket that does not name
its row and its hash is a bracket of opinions.
