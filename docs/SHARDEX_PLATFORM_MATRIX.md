# GAMING PLATFORM MATRIX — the work surface for SHARDEX forging

**What this is.** A matrix of hardware classes, from 1972 to 2026, so a shard can be
forged *for a target* instead of for whatever the machine happens to be. Companion:
`docs/shardex_platforms.json` (the same rows, machine-readable, each carrying the URL it
came from).

**What this is not.** It is not a complete hardware database, and **no row in this file is
quoted without a source**. Where a figure was not verified it is *absent* and the platform
is listed under **Gaps** below — an invented MHz number would be exactly the defect this
estate keeps paying for, in a document that would then be cited for years.

Read on 2026-11-02. Sources, by tag:

- **[W]** Wikipedia, *History of video game consoles* — the generation-level specification
  table. <https://en.wikipedia.org/wiki/History_of_video_game_consoles>
- **[WS]** Wikipedia, *List of Sega arcade system boards* — the Model 2 prose (GE Aerospace
  co-development, i960 CPU, 300,000 textured polygons/s at 60 fps, texture filtering and
  anti-aliasing, 130,000 boards sold by 1996).
  <https://en.wikipedia.org/wiki/List_of_Sega_arcade_system_boards>
- **[M]** **MAME driver source** — the arcade numbers below are the emulator's own clock and
  address-map declarations, i.e. what is asserted in a driver that has to boot the board:
  `model2.cpp`, `cps1.cpp`, `cps2.cpp`, `neogeo.cpp`, `neogeo.h`.
  <https://github.com/mamedev/mame/blob/master/src/mame/sega/model2.cpp> ·
  <https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps1.cpp> ·
  <https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp> ·
  <https://github.com/mamedev/mame/blob/master/src/mame/snk/neogeo.cpp>
- **[P]** Per-platform vendor/technical pages for the handhelds: Wikipedia console articles
  (Game Boy, Game Boy Color, Game Boy Advance, Nintendo DS, Nintendo 3DS, PlayStation
  Portable, PlayStation Vita), switchbrew.org for Switch board components, and Valve's own
  spec sheet for the Steam Deck. Each row in §3 names its own.

`[M]` is a stronger claim than a wiki for *clocks* (a driver that is 2× wrong does not run a
game at the right speed) and a weaker one for *marketing* (no driver declares a polygon
rate). So clocks are `[M]`, polygon rates and collaboration history are `[WS]`, and the two
are never blended into one number.

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

## 2. Arcade boards — where the "hyper-edge" idea actually comes from [WS][M]

Clocks in this table are the **emulator's declarations** `[M]`; the prose around them is
`[WS]`. "Work RAM" and "video RAM" are address-map ranges from the same driver, recorded as
*what the machine decodes*, not as a marketing total.

| board | era | CPU | coprocessor / video | memory (decoded) | note |
|---|---|---|---|---|---|
| Sega Model 2 | 1993 | **Intel i960KB @ 25 MHz** (`50 MHz XTAL / 2`) | **Fujitsu MB86234 "TGP" @ 50 MHz** (2A-CRX/2B); 2C variants: **MB86235 @ 20 MHz + ADSP-21062 @ 32 MHz**. Geometry from GE Aerospace/Lockheed Martin; texture filtering and anti-aliasing `[WS]` | **1 MiB work RAM** (0x0050_0000–0x005F_FFFF), **128 KiB buffer RAM**, **4 MiB texture RAM** (2 banks × 2 MiB), 16 KiB backup SRAM; sound: **68000 @ 11.2896 MHz + SCSP @ 22.5792 MHz** | **300,000 textured polygons/s at 60 fps**; 130,000 boards sold by 1996 `[WS]` — the board that made texture-mapped 3D an arcade standard |
| Capcom CPS-1 | 1988 | **Motorola 68000 @ 10 MHz** (`XTAL 10 MHz`, "verified on pcb"); later revisions **12 MHz** | CPS-A/B graphics processors; sound: **Z80 @ 3.579545 MHz**, **YM2151 @ 3.579545 MHz**, **OKI6295 @ 1 MHz** (16 MHz ÷ 4 ÷ 4) | **64 KiB main RAM** (0xFF_0000–0xFF_FFFF), **192 KiB graphics RAM** (0x90_0000–0x92_FFFF), 2 KiB sound RAM | the sprite-scaling workhorse: 384×224 from a 16 MHz pixel clock, no polygons at all |
| Capcom CPS-2 | 1993 | **Motorola 68000 @ 16 MHz** | CPS-A/B graphics processors; **QSound** (DL-1425) with **Z80/Kabuki @ 8 MHz** (encrypted Z80, ~250 Hz IRQ) | **64 KiB main RAM**, **192 KiB graphics RAM**, 16 KiB optional high-score RAM | same video silicon as CPS-1 at a higher clock plus QSound: the cheapest way to buy a *louder* arcade feel |
| SNK Neo Geo MVS | 1990 | **68000 @ 12 MHz** (`24 MHz master ÷ 2`) | LSPC-A0/A2; sound: **Z80 @ 4 MHz** (`÷6`), **YM2610 @ 8 MHz** (`÷3`), pixel clock 6 MHz (`÷4`) | **64 KiB work RAM** (0x10_0000–0x10_FFFF), **2 KiB Z80 RAM**, **64 KiB battery-backed save RAM** | one cartridge, two markets: AES at home and MVS in the cabinet, identical silicon |
| Sega Model 3 | 1996 | PowerPC 603ev **@ 166 MHz** (498 MIPS, 332 MFLOPS) | **2×** Lockheed Martin Real3D/PRO-1000 | **8 MB** work RAM | the "champion cabinet" class: what a 2026 tournament config should feel like |
| Sega NAOMI | 1998 | Hitachi SH-4 **64-bit RISC @ 200 MHz** (360 MIPS / 1.4 GFLOPS) | PowerVR (PVR2DC) | **32 MB** main RAM, up to **168 MB** solid-state ROM | the arcade twin of the Dreamcast: same silicon, different contract |

Model 3's date and clocks are the useful anchor: **166 MHz and 8 MB produced the arcade
look that tournaments still imitate**, which is why a forged arena can be "hyper-edge" at
`sim_hz: 60` with three orbs and a 12-metre floor. The look was never the polygon count.

**Where this table used to lie, and now does not.** Model 2's memory was previously quoted
as "~62 MB across main/video/audio/other, secondhand". That figure is **withdrawn from the
table**: the driver decodes 1 MiB work + 4 MiB texture + 128 KiB buffer RAM, and a 62 MB
"total" counts ROM boards and unpopulated address space as if it were RAM. The withdrawn
number stays in `shardex_platforms.json` under `withdrawn` so the next reader can see it was
not silently edited away.

## 3. Handhelds — filled, per row, with its own source

Every row below names the page it came from. Where a page does not state a number, the cell
says **not stated** rather than borrowing a figure from a neighbouring model. `[P]` tags
from §0 apply.

| platform | year | CPU + clock | RAM / VRAM | panel | source | forge reading |
|---|---|---|---|---|---|---|
| Game Boy | 1989 | Sharp SM83 **@ 4.194304 MHz** (stated 4.2) | **8 KB RAM + 8 KB VRAM** | 160 × 144, 4-shade STN | [GB](https://en.wikipedia.org/wiki/Game_Boy) | `lowend` floor: a 24-file shard is already 1000× the 1989 budget |
| Game Boy Color | 1998 | Sharp SM83 **@ 4.194 / 8.388 MHz** (double-speed mode) | **32 KB RAM + 16 KB VRAM** | 160 × 144, 56 colours on screen | [GBC](https://en.wikipedia.org/wiki/Game_Boy_Color) | `lowend`: double-speed mode is the first hint that *clock* is a per-mode property |
| Game Boy Advance | 2001 | **ARM7TDMI @ 16.78 MHz** (+ SM83 @ 4.19/8.38 MHz for GB games) | **288 KB RAM + 98 KB VRAM** | 240 × 160 | [GBA](https://en.wikipedia.org/wiki/Game_Boy_Advance) | `lowend`, at the top of it: 288 KB is where a sprite sheet stops being free |
| Nintendo DS | 2004 | **ARM946E-S @ 67 MHz + ARM7TDMI @ 33 MHz** | **4 MB RAM** | 2 × 256 × 192, lower is a touchscreen | [DS](https://en.wikipedia.org/wiki/Nintendo_DS) | `lowend`→`midend` boundary: two screens are two draw passes |
| PlayStation Portable | 2004 | **MIPS32 R4000-based @ 222–333 MHz** | **32 MB RAM (64 MB on 2000/3000/Go/E1000) + 2 MB VRAM** | 480 × 272, 4.3″ | [PSP](https://en.wikipedia.org/wiki/PlayStation_Portable) | `midend`: 272 lines is the first handheld row that wants `sim_hz: 60` |
| Nintendo 3DS | 2011 | **2× ARM11 MPCore @ 268 MHz** + ARM9; GPU **DMP PICA200 @ 268 MHz** | **128 MB FCRAM + 6 MB VRAM** | upper 800 × 240 (400 × 240 per eye, autostereoscopic), lower 320 × 240 | [3DS](https://en.wikipedia.org/wiki/Nintendo_3DS) | `midend`: stereoscopy doubles the render, not the ruleset |
| PlayStation Vita | 2011 | **Quad-core ARM Cortex-A9** (clock not stated in the cited page); GPU **PowerVR SGX543MP4+** | **512 MB RAM + 128 MB VRAM** | 960 × 544, 5″ | [Vita](https://en.wikipedia.org/wiki/PlayStation_Vita) | `midend`: Nintendo-DS-era clocks with 4× the DS memory |
| Nintendo Switch | 2017 | **4× ARM Cortex-A57 @ 1.02 GHz** (one core reserved for the OS; up to **1.785 GHz** in some loading screens after the April 2019 firmware). GPU: **768 MHz docked**, **307.2 / 384 / 460 MHz handheld** | **4 GB LPDDR4** @ **1600 MHz docked / 1331.2 MHz undocked** | 720p handheld; up to 1080p docked | [SW](https://en.wikipedia.org/wiki/Nintendo_Switch) · board parts: [switchbrew](https://switchbrew.org/wiki/Hardware) | `highend` in docked mode, `midend` handheld — **the same console is two rows**, which is why `sim_hz` is a shard field and not a platform field |
| Steam Deck (OLED) | 2022 | **Zen 2 4c/8t @ 2.4–3.5 GHz**; GPU **8 RDNA 2 CUs @ 1.6 GHz**; **APU power 4–15 W** | **16 GB LPDDR5**, 6400 MT/s, quad 32-bit channels | 1280 × 800, 7.4″ HDR OLED, up to 90 Hz | [SD](https://www.steamdeck.com/en/tech) (Valve's own spec sheet) | `highend`: the only row where the thermal envelope, not the RAM, is the binding constraint |

Two conclusions the numbers force, and they are engineering consequences rather than
hardware facts:

1. **A handheld is not one performance class, it is two.** Switch proves it on one die
   (768 MHz docked vs 307.2–460 MHz handheld), Deck proves it with a 4–15 W envelope. A
   shard that declares `sim_hz` but not the *mode* it was tuned in cannot be replayed.
2. **The RAM range across this table is 8 KB → 16 GB (2×10⁶).** The `lowend` cap of 2 MiB is
   the *upper* end of a 2004 DS, not a low-end device — which is exactly why the METTHEW
   gate is generous for gen 3–5 and tight only above the PSP.

## 4. What the matrix decides for SHARDEX (ENGINEERING DECISION — not hardware fact)

These are *our* thresholds, derived from the table above. They are choices, and they are
listed as choices so a reader can argue with them:

| shard class | target hardware | payload | `orbs` | `sim_hz` | tick budget |
|---|---|---|---|---|---|
| `lowend` | gen 3–5 console, Game Boy→GBA, or a phone | ≤ 2 MiB, ≤ 24 files (the METTHEW gate) | 3–5 | 30 | p99 < 33.3 ms |
| `midend` | gen 6–7 console, DS/3DS/Vita, arcade Model 3 | ≤ 8 MiB | 6–8 | 60 | p99 < 16.7 ms |
| `highend` | gen 8–9, PC, Switch docked, Steam Deck | declared, schema allows up to 8 GiB | 9–12 | 120 | p99 < 8.33 ms |

The rule that does not move: **the golden hash covers simulation state at `sim_hz` and
nothing else.** Resolution, upscaling, frame generation and lighting are presentation, and
a hash taken with them in the pipeline is a hash of the painter.

## 5. Gaps, named so they can be closed

Closed in this pass (2026-11-02): Model 2's CPU and video (§2); CPS-1/CPS-2/Neo Geo MVS
clocks and RAM (§2); the handheld rows, Switch's per-mode clocks and the Deck's power
envelope (§3).

Still open, each needing its own source before a number appears:

1. **Lifetime unit sales per platform** — needed for "which games were actually on the
   market". Not attempted: none of the pages read here was read *for* sales, and a figure
   lifted incidentally from an infobox is not a figure this file may quote.
2. **A per-platform *game* inventory** (what shipped, what genre, what ruleset) — the matrix
   above is hardware only. That is the next document, and SHX-7's intake is where real game
   files enter the pipeline.
3. **Residual, discovered while closing the above** — stated rather than papered over:
   - **PlayStation Vita CPU clock**: the cited page names the core, not the clock.
   - **New Nintendo 3DS** clock (the 2014 revision raises the ARM11 above 268 MHz): not
     verified here, so the 3DS row carries the original model's clock only.
   - **Nintendo Switch 2 (2025)**: no specification column at all — nothing read here states
     clocks, memory or display, and the gap is left empty rather than extrapolated from
     Switch.
   - **Model 2 total memory**: the previously quoted "~62 MB" is withdrawn (§2); what is
     recorded is what the driver decodes.

## 6. How to use it

```bash
python Project_SHARDEX/shardex.py --mirror <game> --out .shardex
python Project_SHARDEX/shardex.py --shatter --mirror-file .shardex/mirror.json --out .shardex
python Project_SHARDEX/shardex.py --forge .shardex/shards/<name> --out flame \
    --tune sim_hz=120 --tune orbs=9 --tune arena=16      # the highend column
python Project_SHARDEX/shardex.py --verify flame
```

Tune to a row, then publish the golden hash from that row. A bracket that does not name
its row, its mode and its hash is a bracket of opinions.
