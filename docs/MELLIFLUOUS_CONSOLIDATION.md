# MELLIFLUOUS consolidation — one native tool (measured 2026-11-12)

## Why one tool

16 scripts / ~6,850 lines across `tools/` all serve one system: the native
memory + MCP stack behind MellifluousML (PAMS embed on :8080, pmb daemon on
:8765, floor-proxy on :8766, supervisor verdicts, session gates). They grew
one per need, each with its own argv dialect and no shared envelope. The
consolidation is interface-first: one entry point, one help surface, one
timing/JSON envelope — then leaf-by-leaf inlining, daemons last.

## Vendor baseline (this turn, measured)

llama-server/models is exactly the A-I-O set: gemma-4-E2B (chat, 2.8GB,
active in use_model.dat), mxbai-embed-large-v1 (embed, 206MB, PAMS :8080
answers with its path), Eve-V2-Unleashed (evolution subject, 4.1GB).
Ollama holds only qwen3-embedding:0.6b (639MB). HF hub holds the 5 organs
(1.6GB). C: is 87.6GB free — the brick already landed (a prior session
cleared ~80GB). Removed this turn: nomic-embed-text-v1.5 (81MB,
superseded, zero references) + empty bartowski residue.

## Migration map (phase → scripts)

Phase 1 — DISPATCH (this turn, `tools/mellifluous.py`): every live script
is a subcommand that lazily imports its module and calls its entry in
process. No logic moves; the map below is code, not prose.

| subcommand | module | entry | phase |
|---|---|---|---|
| memory backup | memory_backup | main(argv) | 2 (inline first: cleanest, brick-proven) |
| pmb capture/pickup/observe/session | pmb_capture, pmb_outbox_pickup, pmb_observe_transcript, pmb_session_observe | main(argv) | 2 (leaves, argv-native) |
| pams capture | pams_capture | main(argv) | 2 |
| pmb e2e/client | pmb_e2e_check, pmb_client | main() bare | 3 (needs argv-shim wrapper) |
| prune | prune_memory_debt | main() bare | 3 |
| gate / verify-engram / eight-verify | mcp_startup_gate, verify_engram_mcp, mcp_eight_verify | mixed | 3 (gates: wrap, never weaken) |
| proxy / supervisor | pmb_floor_proxy, supervisor_mcp | main() bare / main(argv) | 4 LAST (live daemons; inline only with a parallel-run proof) |
| pmb token | pmb_token | top-level, no main | 3 (needs entry-point rewrite first) |

Excluded: `memory_profile.py` (68 lines, imports dead modules from
`~/Desktop/azazael-project-e`, top-level code, zero callers) — recommend
deletion, not migration. Pollution in, pollution out otherwise.

## Phase rules

1. Daemons (proxy, supervisor) are NEVER inlined without a parallel-run
   proof: old + new side by side, same verdicts, then cut over.
2. Gate semantics are frozen: a migration that changes an exit code or a
   finding class is a new gate, not a move — it re-proves from scratch.
3. Every phase lands as ≤8 files with its own proof bar (dispatch parity:
   `mellifluous <cmd>` output identical to the direct call).
4. `tools/<name>.py` originals stay as shims until their phase inlines
   them; no caller breaks mid-migration.

## Proof bars

- Phase 1: `mellifluous --help` lists all subcommands; `mellifluous memory
  backup --dry-run` output identical to the direct call; compile clean.
- Phase 2+: per-script parity diff + the script's own control test green.
- Phase 4: proxy + supervisor parallel-run, verdicts identical, then cut.
