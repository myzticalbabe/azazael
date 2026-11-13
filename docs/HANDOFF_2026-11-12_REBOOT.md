# HANDOFF 2026-11-12 — REBOOT PRE-FLIGHT + HOUSEKEEPING

Written 2026-11-13T02:15Z (2026-11-12 21:15 local) from live measurements only.
Every claim below carries the command that produced it. Numbers are trusted for
the session that measured them and not one minute longer.

## 1. HEAD

- branch `azazael-intel-ultra-9-evo`, HEAD `22b88341` ("BM production partition
  sizing from live estates") — `git rev-parse --short HEAD` in `C:/Azazael/azazael`.
- `git rev-list --left-right --count HEAD...@{u}` -> `23  0`: 23 local commits are
  ahead of the upstream and 0 behind. They exist on disk, so the reboot cannot
  lose them; they are simply unpublished.
- `git status --porcelain | wc -l` -> 1693 (other lanes' pre-existing dirt; not
  this session's work). `git stash list | wc -l` -> 2.
- `python azazael/tools/head_state.py --write` -> `head 22b88341, 7507 tests,
  204 skills`, written `2026-11-13T02:15:59+00:00` to `azazael/state/head.json`.

## 2. Trusted state (claim -> command -> result)

| claim | command | result |
| --- | --- | --- |
| stack gate clean | `python azazael/tools/mcp_startup_gate.py --fix` | `gate: PASS=9 WARN=1 in 14.4s`, exit 0 |
| memory both stores loaded | `python azazael/tools/session_start.py "pre-flight + housekeeping for reboot"` | `delivered PMB=2076ch (ok) engram=9453ch (ok) mcp_guard=exit=0`, exit 0 |
| supervisor verdict | `python azazael/tools/supervisor_mcp.py --verdict` | `VERDICT: CLARIFY - advisory items outstanding (exit 0)`; 5 unjudged conflict pairs, doctor ok |
| memory backed up | `python azazael/tools/memory_backup.py` | `snapshot: C:\Azazael\backups\memory\20261112T212257`, `stores ok: 3/3; failures: 0` |
| board store is the shared one | `python _board.py store` | `C:\Users\clint\.azazael\telemetry_store.db`, `rows: 47077` |
| lane instructions in sync | `python tools/agent_orders_sync.py --check --wsl` | `69 target(s) in sync, 0 problem(s), 0 written (incl. 18 WSL block(s))` |
| durable proxy survived to logon | gate `floor-origin` | `started by the logon Startup item (pid 19264, 2026-11-11T17:28:01-05:00)` |
| WSL estates clean for reboot | `wsl.exe --list --running` after `--terminate` | `There are no running distributions.` |
| no staged OS update | registry probes (RebootRequired, CBS, PendingFileRename) | `no pending reboot flags`; uptime 1.2 d, last boot 2026-11-11 17:27 |
| durable starters present | `ls Startup/` | `pmb-floor-proxy.vbs` (origin=logon), `semantic_index.vbs`; `AzazaelParallaxValidator.bat.disabled` |
| scheduled tasks armed | `Get-ScheduledTask` filtered | 8 `Ready`: EvolutionTailgate, TechniqueHeartbeat, NightlyConverge, Watchdog5min, WSL2_Cleanup, Ex Machina Health, PAMS-Reflect-5min, WormExecutionMatrix |

### What dies at reboot, and why that is correct

`pams`, `codegraph_mcp`, `barta_scrape_mcp` and the pmb daemon (port 8765, pid
14564, started 20:15) are all client stdio children — `pams_server_launcher.py`
owns the daemon via `_keep_pmb_warm()` and respawns it after a restart. Only the
floor proxy (:8766) is meant to predate the client, and it does, from the logon
VBS. The proxy waits `PMB_UPSTREAM_WAIT` (default 30 s) for a daemon that is still
loading its embedding model, so a cold start is a wait, not a 502.

## 3. Attempted and failed

- **Two sizing attempts produced a false zero.** `robocopy /l /s /bytes` piped
  through `Select-String '^\s*Bytes'` and split on whitespace returned `0 bytes`
  for seventeen directories that are not empty. Re-measured with
  `Get-ChildItem -Recurse -Force -File | Measure-Object Length -Sum`, which
  printed file counts as well as sizes. **A reading that hides its count is a
  defect** (HED-3); any future dust census must print `files=` beside `MB=`.
- **`du -sh` on `C:/Users/clint/AppData/Local/Temp` timed out at 120 s and again
  at 180 s.** No Temp figure is quoted in this document for that reason.
- **`df -h /` inside `wsl -e` failed** (`df: 'C:/Program Files/Git/': No such
  file or directory`) because the Git-for-Windows `df` won the PATH race. The
  working form is `wsl -d <distro> -e bash -lc "df -h /"`.
- **`bcdedit /enum firmware` printed nothing** — it needs elevation. Boot-entry
  state is therefore UNVERIFIED here, not verified-clean.
- **`_board.py` in this tree has no `release` verb** (`claim|done|block|stats|
  tasks|announce|max|store`). A surplus claim cannot be returned; it expires on
  the 30-minute lease. This session claimed 10 freebuff rows (48985-48994) for
  `claim`, found them to be unrelated queued product work, and left them to
  expire rather than retire work it did not do. Recorded, not worked around.

## 4. The queue

Board (`python _board.py stats`): freebuff `available 100 / claimed 10 / done 109
/ blocked 21 / archived 322`; kilo `available 0 / done 247 / blocked 1`; opencode
`available 47 / done 95 / blocked 3`.

Open items this session did **not** touch, in blocking order:

1. **Lane-instruction defect (recorded, not fixed).** The `RESTART QUEUE` section
   reaches agents in 2 of 7 lane files (`C:/Users/clint/AGENTS.md`: 9 AO blocks,
   `C:/Azazael/AGENTS.md`: 8) and in no other. It exists in no
   `docs/agent_orders/` source (`grep -rln "RESTART QUEUE" docs/agent_orders/`
   returns nothing), so `agent_orders_sync --check` cannot see it. Its content is
   dated 2026-11-07 and says `freebuff 0 open; kilo 6; opencode 11` where the
   live board reads `100 / 0 / 47`, and it says "3.15t interpreter only" while
   the `session-order` block **in the same file** names 3.16t as production and
   3.15t as the GIL sidecar. Remedy, if the principal wants it: promote a
   numberless restart block to `docs/agent_orders/09_restart_queue.md`, register
   it in `tools/agent_orders_sync.py:TARGETS` for all seven files, insert the
   markers, `--apply`, then re-run `--check --wsl`. Deliberately not done
   unprompted: it edits seven generated lane files and the sync tool.
2. **13.7 GB of build debris on C:,** listed with sizes in section 5. Deletion
   waits for an explicit GO.
3. **~180 GiB of stale VHDX blocks** across the two WSL estates, same gate.

## 5. Housekeeping, measured and prepared (nothing deleted)

Free space (`df -h`): C: 83 G of 756 G (90% used), D: 105 G of 115 G, E: 47 G of
97 G, G: 40 G of 477 G (92% used). Recycle bin 0.0 GB, `azazael/logs` 16 MB.

Build/temp debris under `C:/Users/clint`, `files`/`MB` from
`Get-ChildItem -Recurse -Force -File | Measure-Object Length -Sum`:

| path | files | size |
| --- | --- | --- |
| `azazael.archived-20261021` | 66 007 | 10 502.4 MB |
| `temp_llama_cpp_build` | 4 629 | 950.1 MB |
| `temp_build` | 452 | 660.4 MB |
| `build` | 602 | 621.0 MB |
| `tf-build` | 36 350 | 519.8 MB |
| `nuitka_aoa` / `aoa2` / `aoa3` | 113 / 115 / 129 | 115.3 / 117.0 / 124.5 MB |
| `nuitka_test` / `nuitka_test2` | 58 / 77 | 72.0 / 97.3 MB |
| `npExtractDir` | 11 | 22.4 MB |
| `verify.build` | 26 | 18.8 MB |
| `build_test` | 21 | 14.4 MB |
| `verify.dist`, `blobs`, `checkpoints` | 0 | 0 MB |

Total 13.7 GB. The archive directory is the only one that is not obviously
rebuildable and must be inspected before any deletion.

WSL estates (booted, measured, terminated in this session):

| estate | vhdx on disk | used inside | stale blocks |
| --- | --- | --- | --- |
| Ubuntu-26.04 (`C:/wsl/Ubuntu-26.04/ext4.vhdx`) | 193.5 GiB | 77 G (`df -h /`) | ~116 GiB |
| kali-linux (`E:/Kali/ext4.vhdx`) | 104.6 GiB | 40 G (`df -h /`) | ~64 GiB |

`Optimize-VHD` is **not** available (Hyper-V module absent); WSL is 2.7.14.0, so
the reclaim path is `fstrim` inside the distro, then
`wsl --manage <distro> --set-sparse true` with every distro shut down. That is a
size-changing operation on a live image and is not run here.

## 6. First commands for the next session

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix   # expect PASS=9 WARN=1 or better
python C:/Azazael/azazael/tools/session_start.py "<task>"    # PMB + Engram + verdict
python C:/Users/clint/_board.py stats                        # quote live, never this file
```

After the reboot the only state that must be re-created rather than resumed is
the client's stdio children (pams, codegraph, barta, pmb daemon). Nothing on this
host requires manual intervention to boot.

## 7. Expiry

The numbers in this document are valid for **2026-11-13 only**. Board counts move
hourly, disk figures move with every build, and the 23-commit lead over upstream
changes the moment anything is pushed. Re-measure before quoting.
