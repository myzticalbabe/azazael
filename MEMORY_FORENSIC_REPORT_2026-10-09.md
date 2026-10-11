# Memory Systems Forensic Report — 2026-10-09

Scope: every memory system in the stack that exposes tools and persists to disk —
DirectMemory (canonical session recording), PAMS (`persistent_ai_memory`, MCP),
PMB, Engram, and the `.audit/` dual-ledger partner.

Method: read-only census of every store on C: and G: (row counts per table, timestamp
ranges, marker scans), then a code read of the path-resolution chain. Nothing was
mutated before a backup existed.

---

## 1. Store verdicts

| System | Live store | Populated rows | Verdict |
|---|---|---|---|
| **DirectMemory** | `~/.azazael/memory_store.db` (368 MB) | 94,374 events / 2,811 sessions; `memories_fts` in sync | **WORKING — real.** Had 8 fake rows (now purged). |
| **DirectMemory telemetry** | `~/.azazael/telemetry_store.db` (300 MB) | 657,817 `otel_spans`, 3,881 queue | WORKING (oversized; retention target). |
| **DirectMemory history** | 4 files on G: (`AZAZAEL/azazael_data`, `memory_archive/…`) | 1,339,123 memories total | REAL, but orphaned from the live store. |
| **DirectMemory backups** | 3 files on C: | ~1.16M memories, **2.6 GB** | STALE — not pruned. |
| **PAMS** | 15 candidate locations | **0 curated memories everywhere** | **BROKEN — corpus lost.** |
| **PMB** | `~/.pmb/workspaces/04a151a73354/events.sqlite` (23.6 MB) | 1,158 events, 95,983 graph edges, 859 lessons | **WORKING — real.** |
| **Engram** | `engram.db` (2.9 MB) | 342 observations, 278 relations | **WORKING — real.** |

Live DirectMemory is healthy: `memories` = `memories_fts` = 94,374 (triggers intact),
0 empty sessions, real production event types (`clusterwormz_worm_executed`,
`memory_distilled`, `retools.check_*`) from real sources (`NatureCluster`, `Codebuff`,
`ReverseTools`, …), spanning 2026-07-06 → 2026-10-09.

## 2. Root causes

### 2.1 PAMS wrote to a directory that upgrades delete
`AIMemorySystem.__init__` **accepts `data_dir` and never reads it**. It derives every
path from `workspace_path = str(get_base_path())`, and
`ai_memory_core.get_base_path()` returns `Path(__file__).parent` — the **site-packages
install directory**. So all five databases land inside the package, where a
`pip install --force-reinstall` or a Python upgrade erases them. The launcher's own
docstring predicted exactly this loss.

### 2.2 The corpus was lost by that mechanism
The pre-3.14 archive `G:/python314-nonthreaded-archive/…` shows the last surviving
state: **87 curated memories** (2026-05-21 → 05-26) plus 1 conversation / 2 sessions
and 4 `ai_reflections`. The live stores show **0**. The documented "3639 memories in
site-packages" is not present in *any* of the 15 locations — no copy exists on C: or G:.

### 2.3 Fragmentation disguised it
PAMS had **15** candidate data directories (2 under site-packages, 10 on G:, plus the
archive). The launcher pinned `PAMS_ROOT` at `G:\source-of-truth\persistent-ai-memory`
— which held an **empty** store — so every PAMS tool answered "nothing" while the real
corpus had already been deleted from site-packages. The 10 `persistent-ai-memory-1…-9`
directories are all empty duplicates.

### 2.4 DirectMemory's `__main__` polluted production
The module's `if __name__ == "__main__"` block ran a self-test that **wrote fixture
events into the production store** on every bare invocation. Fixed previously (the
CLI now exists and `--self-test` is temp-DB-only); the **8** legacy rows it left in four
throwaway `codebuff_*` sessions were still resident until today.

## 3. Fixes applied — each verified

| # | Fix | Verification |
|---|---|---|
| 1 | **Canonical PAMS store moved to local disk** `~/.pams/memory_data` (launcher default is now `Path.home()/".pams"`, `PAMS_ROOT` still overrides). G: demoted to cold backup. | Imported the launcher: all 5 `AIMemorySystem` DBs and `workspace_path` resolve under `C:\Users\clint\.pams\memory_data`. |
| 2 | **Recovered the surviving corpus** (87 curated memories, 1 conversation + 2 sessions, 4 reflections) into that store. | Canonical store holds 94 populated rows; `create_memory → get_memories` round-trip returned the row; proof row then deleted (87 restored). |
| 3 | **Proved the write goes to the right place** | After the round-trip write: canonical `curated_memories=88 & roundtrip=1`; both site-packages decoys stayed at **0**. |
| 4 | **Purged the 8 self-test rows** via a new, re-runnable command `direct_memory.py --purge-test-fixtures` (dry-run by default, `--apply` to delete, exact fixture predicate). | Dry run listed exactly 8, exit 0, wrote nothing. `--apply`: `memories` 94,374 → **94,366**, `memories_fts` **94,366** (in sync), `sessions` unchanged (2,811), `/fake/` rows **0**, the four sessions kept their 2–5 real events. |
| 5 | **Cold backup on G:** mirrored to the single canonical destination. | SHA-256 of the local and G: copies match for all three populated DBs. |

## 4. Unrecoverable, and other known conditions

- **~3,552 curated PAMS memories are gone.** No copy exists on C: or G:. Only the 87
  archived rows survive. This is data loss, not a wiring bug, and it is not fixable.
- **The running pams server still holds pre-patch code.** The path fix takes effect when
  the client respawns the server; nothing verified here was observed through the live
  `pams__*` tool.
- **10 empty duplicate PAMS directories** (`G:/source-of-truth/persistent-ai-memory-1…-9`)
  remain; safe to delete, left in place deliberately (destructive).
- **~2.6 GB of stale DirectMemory backups** on C: (3 files) are unpruned.
- **657,817 `otel_spans`** in the telemetry store — retention, not corruption.
- **6 DirectMemory sessions remain open** (`ended_at IS NULL`); they are recent, not stale.
- The CHANGELOG's 8 "deep data" DirectMemory methods still do not exist anywhere.

## 5. Backups taken before mutation

`azazael/state/MEMORY_FORENSIC_BACKUP_20261009/`
- `directmemory_affected_sessions.json` — all 19 rows of the 4 affected sessions
- `pams_archive_ai_memories.db`, `pams_archive_conversations.db`,
  `pams_live_conversations.db`, `pams_archive_mcp_ai_reflections.db`
