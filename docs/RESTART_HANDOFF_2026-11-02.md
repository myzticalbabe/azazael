# Restart handoff — 2026-11-02

Written for the next session. **HEAD at handoff is the commit containing this file; its parent is
`7a6a2da3`.** Five commits landed today, in order:

| commit | what it did |
| --- | --- |
| `a876c781` | pick-driven live mutation (`touch` op, `picked.json`, `PICK-UNPROVENANCED`), the bible dossier quoting the 1987 TNG guide, the DJT prose audit, the subagent-guard audit |
| `0dbd384` | the AI→SI decree inside the bible, with the cost-benefit, harm assessment and 10-measure pathway |
| `ed96f5fe` | improvement pass: pick coverage hole closed, unreadable-record refusals, prose negative control, instrument band disclosed |
| `7a6a2da3` | checks-and-balances gap analysis + state policy comparison |
| *(this)* | `.gitignore` for the scratch dirs, this handoff |

## State that can be trusted

- `Project_SHARDEX/tests/test_mesh_live.py` — **14 pass**; `tests/test_prose_forensics.py` — **6 pass**.
- `python Project_SHARDEX/meshscene.py --verify .live_pick` → **VERIFIED**, chain
  `69da083da4268ec8`, final mesh `110df7ea0bb30364` (`.live_pick` is gitignored but present locally).
- `tools/preflight_all.py` → **24 of 25 PASS**; the one FAIL is `transcript-ap5`, which reports two
  historical "Want me to…" lines in another session's stored transcript. Not introduced by this
  work and not blocking — leave it visible rather than suppress it.
- Board: row **47187** (`industry_standards_analysis`) is deliberately **pending** — it must run
  *after* startup so it measures the post-session tree. Row 47189/47190 are announcements.

## Open items, in the order I would take them

1. **IMP-2 — `--verify` still trusts its inputs.** `mesh.json`, `field.json` and
   `applied_ops.jsonl` could be edited consistently and verify would pass. Fix: have the page report
   the **base** digest and the field sha256 into `browser_probe.json`, and require both to match.
   This is the same defect class as the pick hole, one level up.
2. **G1/G2** — the claim trailer (`Task: Board-<n>`) and the receipt (`command`, `exit_code`,
   `stdout_sha256`). `docs/SUBAGENT_GUARDS_2026-11-02.md` §4 specifies both; G2 is ~40 lines and is
   the cheapest real gain in the tree.
3. **Board 47187** — industry-standards analysis against a captured baseline (NIST AI RMF/SSDF,
   ISO 42001/25010, SLSA+SBOM+Scorecard, OWASP ASVS, WCAG 2.2, DORA). Every cell carries a receipt;
   unmeasured cells report UNRUN.
4. **IEA figures** — §7 of the DJT audit carries 415 TWh (2024) / 945 TWh (2030) as tier **C/P**;
   the report body was never fetched. Re-derive from the PDF before any official use.
5. **Prose instrument** — guarded sentence splitter (abbreviations + lowercase rejoin) and a
   `--compare` that prints all twelve metrics it computes instead of five.
6. **Corpus arm 2** — the 2015 announcement. Time returns **406**; `presidency.ucsb.edu` served the
   campaign release fine, so use the APP spoken-address archive.

## SHARDEX capability reasoning — recorded 2026-11-02 (late), for the restart

Not features. Each row is a **reasoning question with a falsifying test**, because every capability
in SHARDEX today is verified by two implementations written by the same author, and a shared
misreading passes both. Measured state these rows assume: L0-L4 built; `meshscene` 576 neurons /
1,201 synapses, 5 pure ops, per-op digests replayed after the page applies them; `transubstantiate`
489 segments / 822 leaves, browser MATCH; `launch.py --bracket` ranks each entry's **golden hash**
(`run_round` computes hashes) -- so two shards' arenas have never shared a space.

| id | question | falsifying test | evidence command | blocked by |
| --- | --- | --- | --- | --- |
| `shx-r1` | Is any golden hash reproducible from the **artifact alone**? | An implementation that never reads `shardex.py` or the page JS reproduces `1c045e596f950543` for `highend_duel` | `pytest Project_SHARDEX/tests -q -k third_impl` | nothing -- do this first; it redefines "verified" for every row below |
| `shx-r2` | Is an extracted rule the rule that made the source move? | Perturb each of the 5 extracted constants, **predict** the observable change, then measure it in the original animation; score < 3/5 is REFUSED | `transubstantiate.py --predict .transub/rules.json` | `shx-r1` |
| `shx-r3` | Where does the pipeline actually break on a real tree? | Second `--shatter` run must produce byte-identical shard ids; every refusal named with its byte count | `shardex.py --mirror <tree>` + `--shatter` twice, diff the ids | nothing -- measurement, runs alongside |
| `shx-r4` | What is the law when two arenas share a space? | A round whose hash depends on **both** golden hashes, replayed from the input log alone | `launch.py --bracket <a> <b> --compose` | `shx-r1`, `shx-r3` (needs ≥2 real shards) |
| `shx-r5` | Is the op log an addressable program? | `shardscript.json` replays every digest for a third party; a hand-edited op is REFUSED | `meshscene.py --verify-program shardscript.json` | `shx-r2` |

**Traps, named so they are not re-derived.** Rendering polish, more arena knobs and more operators
are all linear -- none raises a ceiling, and each needs a second port. The golden hash proves
self-consistency, never fidelity: FLAME's own text says the original rules are not extracted, and
`transubstantiate` records the *line* that proves a rule, which is evidence of presence, not of
causation. And the 24-file / 2 MiB low-end ceiling is the contract the validator enforces -- moving
it to make a tree fit turns a measurement into a preference.

## The queue, with ids (posted 2026-11-02, all `pending`)

`python C:/Users/clint/_board.py claim freebuff 10` hands these out oldest-first; retire each with
`done <id> "<command + result>"`. Row 47187 predates this list.

| board | task_id | action | one line |
| --- | --- | --- | --- |
| 47192 | `jaeger-000` | decide | what Project Jaeger *is* before any code — tracer of this tree vs an OTLP client |
| 47193 | `jaeger-001` | scaffold | `Project_JAEGER/` to `Project_CRADLE`'s shape |
| 47194 | `jaeger-002` | aoa-arm | `BaseArm` + `@register_arm` + **`_ARM_MODULES`** entry, with the negative control |
| 47195 | `jaeger-003` | export | the transport AOA does not have; the trace-correlation field `DelegationSpec` lacks |
| 47196 | `imp2-verify-inputs` | harden | `--verify` must check the base digest and field sha, not trust its inputs |
| 47197 | `g1-claim-trailer` | build | a claim carries `Task: Board-<n>` or is refused |
| 47198 | `g2-receipt` | build | a completion carries `command / exit_code / stdout_sha256` or is refused |
| 47199 | `djt-iea-rederive` | verify | the 415/945 TWh figures were never fetched from the report body |
| 47200 | `prose-splitter` | improve | guarded splitter; `--compare` shows all twelve metrics, not five |
| 47201 | `corpus-2015-arm` | build | 2015 arm via the APP archive (`time.com` → 406) |
| 47409 | `shardex-r1` | prove | third implementation reproduces a golden hash from the artifact alone |
| 47411 | `shardex-r2` | falsify | perturb-and-predict scorer over the 5 extracted rules |
| 47413 | `shardex-r3` | measure | real-tree intake: shard ids byte-identical on a second run |
| 47415 | `shardex-r4` | design | the interaction law between two arenas, hashed and replayable |
| 47417 | `shardex-r5` | reframe | the op log as an addressable program (`shardscript.json`) |
| 47419 | `promptcheck-blind-fresh-host` | decide | `state/head.json` is gitignored, so a fresh host reaches the prompt gate BLIND (exit 2) |
| 47421 | `handoff-expiry-and-failures` | add | this file lacks an expiry line and an *attempted and failed* section, which block 0.5 requires |
| 47423 | `unified-cli-exemption` | resolve | `tools/unified_cli.py:68` carries a standing failure-evidence exemption; implement the bound or date the exemption |

Blocking order is real: `jaeger-001..003` sit behind `jaeger-000`, and `jaeger-003` should not start
before `g2-receipt`, because an exporter with no receipt discipline produces spans nobody can audit.

## First commands at startup (canon order — do not skip)

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix
python C:/Azazael/azazael/tools/session_start.py "<the task>"
# then supervisor__verdict through the MCP tool
python C:/Users/clint/_board.py claim freebuff 10     # the queue is the work queue
```

## Scratch directories, now ignored

`/.live/`, `/.live_pick/`, `/.prose/`, `/.transub/`, `/.tmp_mirror/` are in `.gitignore` as of this
commit. `.live_pick/` is **94 MB** and holds `frames/` (120 PNGs) plus `mesh_pick.mp4`; the frames
are regenerable from the committed source, and the *evidence* is `applied_ops.jsonl` +
`picked.json` + `mesh.json` + the digests quoted in commit `a876c781`, not the video. If disk
pressure matters (this box runs near 98%), `rm -rf .live_pick/frames .live/frames` is safe and
reversible by re-running capture — **but re-run `--forge` first**, because the page in those
directories was generated before the `touch` operator existed.

## One caution for the next session

The worktree carries ~200 pre-existing modifications from other lanes (workflows, baseline JSONs,
platform docs). **Do not `git add -A`.** Stage by path, and if a commit needs a bulk override,
declare `ALLOW_BULK_COMMIT=1` in the message as the two commits today did.
