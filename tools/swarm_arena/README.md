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
