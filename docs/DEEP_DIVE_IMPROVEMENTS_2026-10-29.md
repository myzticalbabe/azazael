# Deep-Dive Improvements (2026-10-29, second pass)

First pass (`SESSION_IMPROVEMENTS`) covered honesty, seams, process.
This pass audits failure modes, races, and architectural risks in the
new code. All findings measured against the tree at f3d38b20.

## D1. Store writes are not atomic (data-loss risk) — HIGH
`morphed_registry.json` and `sweep.json` are written by direct
`write_text`. A crash mid-write (power, kill, disk-full) leaves a
truncated JSON file; the next `_load_store` falls back to `{"generation":
0}` — silently resetting the generation counter and orphaning every
promoted trainer. Two writers (kilo + local) make partial writes likely,
not theoretical.
**Fix:** write-to-temp + `os.replace` (atomic on both NTFS and ext4).
Five lines per site. The evolution engine already uses fencing tokens
for exactly this class — reuse the pattern.

## D2. No locking on the morphed store (lost-update risk) — HIGH
`promote()` does read-modify-write with no lock. Two concurrent
promotions read generation N, both write N+1, one winner vanishes.
**Fix:** file lock (or reuse the evolution `fence_for` token) around
the read-increment-write. Single-host now, two-distros soon.

## D3. Proxy objectives are placeholders wearing production clothes — MEDIUM
`reward_proxy`/`cost_proxy` in `propose()` encode guesses (mid-range LR
good, edges bad) as if they were measurements. NSGA-II will faithfully
optimize the guess. The Pareto front is real math over fake fitness.
**Fix:** label them `heuristic_v0` in code + docs, and gate promotion
on a real training run (kilo's orders already say this — enforce it in
`promote()`: require a `trained_reward` field, refuse proxy-only entries).

## D4. md5-hashed temp files collide across languages — LOW but real
All five runners hash inline code to 12 hex chars under `build/<lang>/`.
Same code string in two languages maps to the same filename in different
dirs (fine), but 12 hex chars = 48 bits: at ~10k inline runs, birthday
probability of a same-language collision is ~1e-8 per pair — negligible
today, but the dirs are never cleaned. `build/` grows unboundedly.
**Fix:** `build/<lang>/` cleanup older than N days in `--sweep`, or TTL
on write. Cheap insurance.

## D5. Version recorded, never consumed — MEDIUM
Every runner records `self.version` at verify time; nothing reads it.
A node upgrade (v22→v24 type-stripping behavior change, pwsh 5→7 syntax
gaps) silently changes golden results while the sweep table claims
comparability.
**Fix:** include toolchain versions in `sweep.json`; `route_lang` warns
when current version differs from sweep-time version. Five lines.

## D6. Quoting asymmetry: pwsh inline args — LOW
`pwsh_runner._base(["-File", path] + args)` passes user args raw to the
script. PowerShell's `-File` argument passing has legacy quirks (quotes
stripped, `$` untouched — unlike `-Command`). Args containing quotes
will arrive differently than on bash/node.
**Fix:** document the contract (args are literal strings, no shell
evaluation) + add an args-with-spaces golden test per language.

## D7. `errors="replace"` hides the evidence it should keep — LOW
21 sites use `errors="replace"`. Correct for display, wrong for forensics:
a mojibake'd compiler error is unreproducible. The two TIKTOK/arena
commits tonight prove the pattern spreads.
**Fix:** keep `replace` for stdout display, but on failure also capture
`stderr_bytes` (raw) into the result dict. Display degrades, evidence
doesn't.

## D8. Sweep measures startup, not work — MEDIUM
Golden is a print statement. Ranked order (python 0.0 < bash 10.9 <
js 33 < rust 118 < go 145 < pwsh 228) mostly ranks *process spawn cost*,
not language throughput. Routing real work by these numbers misleads.
**Fix:** two-tier goldens — `instant` (current, for pipe health) and
`work` (1k-iteration loop, for routing). Sweep both; `route_lang`
spends the `work` table by default.

## D9. Doc-only shards are untestable by construction — LOW
`skills-core` etc. list `["doc"]` as a language; `run_shard("doc")`
returns unknown-language. The manifest claims coverage the harness
cannot verify.
**Fix:** doc-shard self-test = frontmatter validity + Related-Skills
link check (the check proposed in the review doc, never built). Make
it real: one function, runs in `--self-test`.

## D10. The review doc's Axis B is dead text — TRIVIAL
`MULTILINGUAL_SHARD_REVIEW` retains the struck-through locale section
with `~~` markers. Superseded text in a canonical record confuses the
next reader (is it scope or isn't it?).
**Fix:** delete the section, leave a one-line pointer to this decision
(owner: GO/RUST/PYTHON only, 2026-10-29). Records should show the scar,
not the wound.

## Priority
D1+D2 (atomicity + locking) first — data loss compounds. D3+D8 (honest
fitness, honest timing) second — both poison routing silently. Rest in
any order.
