# swarm-arena — blind pairwise judging, 3-language shards + Elo

Arena-style judging for pair corpora (default: `pairs_for_judgment.txt`).
Three independent judge shards vote blind per pair; majority wins; Elo board.

## Shards (deliberately disjoint signals — independent voters, not echoes)

| shard | language | signal |
|---|---|---|
| `judge_rs` | Rust, stdlib only | evidence refs: Root cause/Fix/Evidence, task refs, PMB ids, dates, hashes |
| `judge_go` | Go, stdlib only | investigative structure: What/Why/Where/Learned, NPI/EIN, dollars, detail |
| `judge_py.py` | Python, stdlib only | cross-reference density: RULE cites, obs ids, file paths, measured-claims |

## Build

```bash
cd judge_rs && cargo build --release
cd ../judge_go && go mod init judgo 2>/dev/null; go build -o judge_go.exe .
```

(`target/` and `*.exe` are git-ignored build artifacts; rebuild after pull.)

## Run

```bash
python arena.py [pairs_file] [out_dir]
# default pairs: ~/.pams/logs/pairs_for_judgment.txt, default out: ./out
```

Outputs `out/arena_results.json` (per-pair votes, winner, Elo delta) and
`out/elo_board.json` (rating per observation id, K=16, init 1500).
Posts an `ARENA-SHARD-JUDGE` wave row to the LaneMessageBoard for the swarm.

## Blinding

The orchestrator randomizes X/Y per pair (seed 20261029); shards never see
candidate ids — position bias is structurally impossible. 3 voters ⇒
majority always exists; `unanimous: false` rows are the interesting ones
(12/41 on the first corpus) and mark genuine judgment calls.

## Cursor view — the Vulcan salute as the pointer

```bash
python swarm_view.py [--top 12] [--field 960x420]
# reads out/arena_results.json + out/elo_board.json
# writes out/swarm_view.html + out/swarm_view_frames.jsonl   (both git-ignored)
```

One salute glyph per candidate, placed so its **index fingertip** — not its
corner — lands on the node it scored. The hotspot is read from each SVG's own
`data-hotspot` and cross-checked against `cursors/registry.json`; a disagreement
exits 2 rather than drawing a cursor whose tip is not where it says.

States: `ok` won every pair unanimously, `warn` won with dissent, `error` lost
all, `unknown` no pair, plus `absent` (the plan asked for more cursors than the
run produced) and `blind` (a shard cast zero votes). Colour comes from
`monitor_theme.SEMANTIC`; an import failure exits 2 instead of inventing a
palette.

Each run appends a hash-chained ledger row per cursor
(`sha256` over `frame, cursor_id, tree, node, verdict, claim, prev_hash`,
`GENESIS` first). Rows that do not recompute are **quarantined and never drawn
on the field** — the builder recomputes every row before writing and exits 2 if
any fails. Adjacent cursors alternate vertical bands so labels cannot share a
height, and the emitted schedule is proven inside the 900 ms budget
(`stagger = min(35, (900-300)//(n-1))`).

The page prints its own denominator (`X of Y candidates drawn`) and a self-test
line — `hotspot_misaligned` is the count of cursors whose tip drifted more than
0.01 px from the node it claims, and `CHAIN` is `MISMATCH` when that count is
non-zero or the slowest cursor exceeds the budget.

### Scope and rollback proof (audit I1, I5)

```bash
python swarm_view.py                                  # scope defaults to tools/swarm_arena
python swarm_view.py --scope tools/swarm_arena --prove # strict: exit 2 unless clean
```

`read_scope` enumerates **`git ls-files`**, not the worktree, so the denominator
counts what the commit will contain. The worktree count is printed beside it
(`4 modules in the index (4 on disk)`) so the two are never mistaken for each
other. A scope with no index entry is refused with the remedy named and exit 2:
`` `git add <path>` `` when the path exists untracked, "name a tracked path that
exists" when it does not.

The rollback proof (the C2 replacement for hashing the whole worktree) is
`git ls-tree -r HEAD` object ids plus an empty `git status --porcelain` over the
same scope — exact, cheap, and unable to race a concurrent writer. It prints
`PROVEN (clean worktree)` or `NOT PROVEN` with every dirty path named, and
`--prove` refuses to render in the latter state. `scope hash` is a sha256 over
`path object-id` pairs, i.e. **committed content only** — the same value the
design's `scope_hash_before` / `scope_hash_after` needs, without a worktree read.

## Compiling the salute into a Windows pointer

`make_cursors.py` turns the same SVG masters into a real cursor scheme, with no
new dependency: Chrome rasterises the glyph (PIL and cairosvg are both absent
from the 3.16t venv), and `struct`+`zlib` build the PNG decode and the
`.cur` / `.ani` containers.

```bash
python make_cursors.py --build     # -> out/cursors/*.cur, *.ani, preview.png
python make_cursors.py --install   # copy to %LOCALAPPDATA%\...\Cursors\vulcan-swarm,
                                   # register scheme "Vulcan Swarm" (HKCU)
python make_cursors.py --apply     # back up the live scheme, install, go live
python make_cursors.py --restore   # put the backed-up scheme back
python make_cursors.py --defaults  # write Windows Aero back, backup or not
python make_cursors.py --check     # read back what is built and installed
python make_cursors.py --uninstall # remove the scheme and its files
```

Three of those verbs exist because of one ordering fact each. `--apply` writes
`cursors_backup.json` **only when the live pointers are not already this
scheme**, so a second `--apply` cannot replace the genuine pre-install reading
with the scheme itself — the overwrite that loses a user's arrows happens on the
second run, not the first. `--defaults` is the undo that needs no backup: it
reads the `Windows Aero` string out of `HKLM` ...\Control Panel\Cursors\Schemes
and writes those 15 paths into the live slots. `--uninstall` clears the live
values and calls `SPI_SETCURSORS` **before** it deletes a file, because the other
order leaves Windows holding pointers into files that are gone.

Sizes: the arrow carries 16, 32 and 48 px, each from the master that suits it
(the hand-tuned 16 px master at 16, the 32 px master at 32 and scaled at 48), so
the small rendition is not a squeezed copy of the large one. `Wait` and
`AppStarting` share an 8-frame `.ani` in which the salute swings ±24° with its
tip pinned — the palm travels 9.71 px at 32 px, 51% of the glyph's own ink
height, which took a six-times-larger raster canvas to draw (see the three notes
at the end of this file).

**Slot coverage — 11 of the 15 scheme slots carry salute art.** Windows draws
four more whether or not a scheme supplies them (a crosshair has no pointer tip
to hang a hand on, and a pen cursor already *is* a hand), so those stay system
defaults and the scheme leaves their registry values empty.

| slot | artefact | built from | hotspot |
| --- | --- | --- | --- |
| Arrow | `vulcan-arrow.cur` | `pointer` master, 16/32/48 px | tip `8.5,2` |
| Hand | `vulcan-hand.cur` | `link` master, 16/32/48 px | tip `6,4` |
| AppStarting / Wait | `vulcan-busy.ani` | `pointer` master, 8 frames, ±24° swing, 192 px raster → 32 px | tip |
| IBeam | `vulcan-text.cur` | `pointer`, rotated 180° | fingertip (now pointing down) |
| SizeAll | `vulcan-move.cur` | `pointer` ×4 at 0/90/180/270°, s 0.42, off ±7.0 | centre |
| SizeNS | `vulcan-ns.cur` | `pointer` ×2 at 0°/180°, s 0.48, dy ±7.5 | centre |
| SizeWE | `vulcan-we.cur` | `pointer` ×2 at 90°/270°, s 0.48, dx ±7.5 | centre |
| SizeNWSE | `vulcan-nwse.cur` | `pointer` ×1 at 315°, s 0.66 | centre |
| SizeNESW | `vulcan-nesw.cur` | `pointer` ×1 at 45°, s 0.66 | centre |
| No | `vulcan-no.cur` | `pointer` + corner-to-corner bar | tip `8.5,2` |
| Help, Crosshair, NWPen, UpArrow | *(unset)* | Windows default | — |

The derived slots are **composed at build time** from the 32 px pointer master
inside one 32-unit viewBox (`translate(16+dx,16+dy) scale(s) rotate(a)
translate(-12.5,-15)`), never authored as separate SVGs: one glyph, ten cursors,
so a change to the salute reaches every slot on the next `--build`. Rotations turn
the hand about its own ink centre `(12.5,15)` and the composition re-centres it in
the box, because the glyph is 26×29 and flush left — without that step every
rotated copy clips.

Two of those compositions were decided by rendering, not by taste:

- **The diagonals use one hand, not two.** At scale 0.40 the two-copy NW-SE pair
  merged into a single smear at 32 px, and every larger scale that kept the two
  notches apart pushed ink out of the tile. One hand at 0.66 reads as a single
  diagonal limb with a clear notch, which is what a resize diagonal needs to be
  legible at 16 px.
- **`No` is a filled hand with a bar through it, not an outlined one.** An
  outline-plus-halo was rendered at four stroke widths; at 16 px every one
  dissolved into a crossed-out box with no hand silhouette left. Filled ink
  survives, so the negation is carried by a `M 5 29 L 27 3` bar (dark 5.4 under
  white 2.6) laid over an intact salute.

`PROGRAMS` is the single slot→container table that both `--install` and
`--apply` read, so what gets registered and what gets switched on live cannot
drift apart.

**Two roles, two sets of pixels.** `cursors/registry.json` marks every master
with a `role`: `pointer` is the upright salute, `link` is a salute leaned 30° so
the pairs reach up-left and the palm trails bottom-right, which is what tells a
clickable link apart from the arrow at a glance. Both roles are authored as their
own masters with their own hotspots (arrow `8.5,2` / `4.25,1`, link `6,4` /
`3,2`) — the lean and a deliberately deeper V and longer thumb lobe are drawn
into the geometry rather than rotated in at build time. Until this existed,
`make_cursors.py` reproduced the arrow's DIBs verbatim for the hand, so the two
`.cur` files were byte-identical; `do_build()` now refuses to build when the
registry holds no `link` master, so that silent reuse cannot come back.

Three things this file had to get right, all measured rather than assumed:

- **`anih.iSteps` must equal `iFrames`.** The format lets 0 mean "same as
  `iFrames`", and Windows does not: with `steps=0` an otherwise correct file is
  refused by `LoadCursorFromFileW` with `GetLastError=87`
  (`ERROR_INVALID_PARAMETER`) and no other clue.
- **A wide swing does not fit its tile, and a bigger canvas does not fix a
  ratio.** The glyph hangs about 27 units below a pivot two units under its top,
  so at ±24° the union of the eight rotated ink boxes is 46.5 × 40.7 units
  against a 32-unit tile: no placement fits it, and the in-tile offset that
  served ±6° stopped being enough. The busy frames are now rasterised at 192 px
  with the glyph scaled to fit its own arc plus a 1 px margin (`wave_layout`),
  every frame is refused if its outer ring carries ink (`assert_unclipped` — a
  cut frame cannot be repaired later), and the canvas is box-filtered 6:1 back
  to 32 px. Scaling the canvas up alone would change nothing: canvas and art
  grow together, so the fit is a ratio and the glyph has to be drawn smaller.
- **The wave had to be wide enough to read as motion, and the arc is the only
  lever that pays.** Measured from the built frames: ±6° moved the palm
  3.05 px, 10.2% of the glyph's own ink height — a tremble. ±24° moves it
  9.71 px, 51.1% of a 19 px ink height, and the same 9.71 px separates the two
  extreme frames, which is the metric `--check` reports against `MOTION_FLOOR`.
  A vertical bob was tried first and measured worse, because a bob has to be
  added to the layout margin: at 6 canvas px it bought 8.32 px of travel and
  cost the salute 6 px of height (a 20 px glyph), so the bob was removed and
  the arc widened instead — 9.71 px of travel on a 19 px glyph is the better
  trade. The price is a glyph 7 px shorter than the static arrow's 26 × 29.

`--install` refuses to copy anything unless every artefact comes back from
`LoadCursorFromFileW` as a real `HCURSOR`; `--apply` reads the live registry
values back after `SPI_SETCURSORS` and prints them. `--check` re-derives both
claims from disk on demand: it parses every `.cur` index and `.ani` fram list,
compares each installed copy against `out/`, measures the palm's spread from the
shipped frames, and fails on a hotspot outside its image, an `anih` that
disagrees with the fram list, a spread under `MOTION_FLOOR`, or a live value
aimed at a file that is not there.

## SOULFORGE — the same swarm as one Windows binary

`soulforge.py` is the front end; `build_soulforge.py` compiles it with Nuitka
(MSVC 14.5, the same 3.16t interpreter as everything else here):

```bash
python build_soulforge.py   # -> dist/SOULFORGE.exe, then runs it --status
dist/SOULFORGE.exe          # status, then the menu (double-clickable)
dist/SOULFORGE.exe --apply  # build from its own masters, install, go live
dist/SOULFORGE.exe --check  # read it all back; exit 1 names each defect
dist/SOULFORGE.exe --selftest # build, install, check, uninstall on a throwaway key
```

The binary carries the SVG masters as data (`--include-data-dir=cursors=cursors`)
and no third-party library at all. Onefile unpacks to a temp directory that is
deleted on exit, and that directory is the only handle on the masters —
`sys.executable` points at the same temp path, and Nuitka sets `__compiled__`
rather than `sys.frozen`. So `make_cursors` reads masters beside the module and
writes artefacts to `%LOCALAPPDATA%\SOULFORGE\out\cursors`, which outlives the
process; `SOULFORGE_OUT` overrides that. Run from the repo, both paths are what
they always were.

### `--selftest` — proving the binary without moving the user's pointer

The four verbs change the desktop, so testing them by hand means testing them on
the person using it. `--selftest` runs each as a child of itself with
`SOULFORGE_CURSOR_KEY`, `SOULFORGE_SCHEME_DIR` and `SOULFORGE_OUT` pointed at
`HKCU\Software\SOULFORGE\selftest-<pid>` and a temp folder, snapshots the live
`Cursors` key before and after, and fails if any value moved. Negative control:
patching the second read so it differs prints `DEFECT the live Cursors key
changed: Arrow` and exits 1. `reload_pointers()` prints `skip SPI_SETCURSORS
under a throwaway key` rather than repainting the live scheme, and `--apply`
creates the throwaway key instead of refusing a missing one.

The part a source run cannot reveal is re-running itself: a onefile build leaves
`sys.executable` inside its extraction folder at a path that never exists
(`...\onefile_21916_...\python.exe`, `FileNotFoundError WinError 2`, measured
2026-11-14), so the identical code passed `python soulforge.py --selftest` and
failed as an exe — which is the reason the verb exists. `self_command()` takes
the real program from `SOULFORGE_SELF`, then the bootstrap parent's image
(`NUITKA_ONEFILE_PARENT` plus `QueryFullProcessImageNameW`), then `argv[0]`, then
`sys.executable`, and prints `DEFECT no runnable self` when none is a file
rather than reporting a pass it did not have.

Measured here on 2026-11-14: `dist\SOULFORGE.exe --selftest` printed `selftest
self ...\dist\SOULFORGE.exe`, its `--check` child printed `motion AppStarting 8
frame(s), 32 px, palm 9.71 px = 51.1% of 19 px ink` and `clean 0 defect(s)`, and
the verb ended `selftest PASS ... live key untouched (20 value(s))`, exit 0.

The exe itself. Measured the same day, `dist/SOULFORGE.exe` is 8 263 168 B; `--apply`
built 10 artefacts from the packed masters, installed 10 files, wrote 11 live
values and ended `scheme      Vulcan Swarm` at exit 0; `--check` printed
`10 read back, 10 installed copy(ies), 11 live value(s)` and `clean 0 defect(s)`.
That check is not vacuous inside the binary either: XOR-ing one byte of the built
`vulcan-no.cur` (md5 `5328883c…` → `c09cde29…`) made the exe print
`DEFECT installed … differs from …` and exit 1. The first attempt at that control
wrote `0xff` over a byte that was already `0xff` and read clean — an unchanged
fixture proves nothing, which is why the hash is printed before and after now. The hardware pointer is drawn
by the compositor and does not appear in a GDI screenshot, so `preview.png` —
the actual bytes, at 16/32/48 and all 8 frames — is the pixel evidence.
