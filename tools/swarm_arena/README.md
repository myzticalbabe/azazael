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
python make_cursors.py --uninstall # remove the scheme and its files
```

Sizes: the arrow carries 16, 32 and 48 px, each from the master that suits it
(the hand-tuned 16 px master at 16, the 32 px master at 32 and scaled at 48), so
the small rendition is not a squeezed copy of the large one. `Wait` and
`AppStarting` share an 8-frame `.ani` in which the salute waves with its
tip pinned.

**Slot coverage — 11 of the 15 scheme slots carry salute art.** Windows draws
four more whether or not a scheme supplies them (a crosshair has no pointer tip
to hang a hand on, and a pen cursor already *is* a hand), so those stay system
defaults and the scheme leaves their registry values empty.

| slot | artefact | built from | hotspot |
| --- | --- | --- | --- |
| Arrow | `vulcan-arrow.cur` | `pointer` master, 16/32/48 px | tip `8.5,2` |
| Hand | `vulcan-hand.cur` | `link` master, 16/32/48 px | tip `6,4` |
| AppStarting / Wait | `vulcan-busy.ani` | `pointer` master, 8 frames, ±6° wave | tip |
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

Two things this file had to get right, both measured rather than assumed:

- **`anih.iSteps` must equal `iFrames`.** The format lets 0 mean "same as
  `iFrames`", and Windows does not: with `steps=0` an otherwise correct file is
  refused by `LoadCursorFromFileW` with `GetLastError=87`
  (`ERROR_INVALID_PARAMETER`) and no other clue.
- **A rotating frame needs headroom inside its tile.** The glyph sits flush
  against the left edge of its viewBox, so a swing cut pixels off at the canvas
  edge during rasterisation — and no later pass can put them back. The wave tiles
  therefore render with an in-tile offset, and the hotspot moves with the glyph
  so the reported point stays on the fingertip.

`--install` refuses to copy anything unless every artefact comes back from
`LoadCursorFromFileW` as a real `HCURSOR`; `--apply` reads the live registry
values back after `SPI_SETCURSORS` and prints them. The hardware pointer is drawn
by the compositor and does not appear in a GDI screenshot, so `preview.png` —
the actual bytes, at 16/32/48 and all 8 frames — is the pixel evidence.
