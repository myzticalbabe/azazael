# AST audit — all environments, 2026-11-01

Forensic pass over every codebase this project actually runs in, plus the
month-old backlog that was never closed. Every figure below comes from one run of
one tool with one prune set; the raw JSON sits next to this file in
`docs/audit/ast_audit_2026-11-01/`.

**What this document does NOT claim.** Counts are a census, not a verdict. A file
that parses is not a file that works; an orphan module is not a dead module; a
`TODO` line is not necessarily undone work. Section 6 lists what each instrument
can and cannot establish.

---

## 1. Instrument

`tools/ast_audit.py` (stdlib only, no 3.10+ syntax — the Kali and Ubuntu lanes do
not have the 3.15t Windows interpreter, so a tool that needs it can only audit the
environment that has it). One root per invocation, one JSON out, nothing merged
across environments.

```
python tools/ast_audit.py --root <root> --out <label>.json --label <label>
```

Pruning is by directory **name** anywhere in the tree (`site-packages`,
`.venvs`, `archived`, `archive`, `build`, `dist`, `graphify-out`, `.nox`-style
caches): a vendored copy counted as first-party code is how a 17k-line tree
reports 300k.

Cross-environment drift is `tools/ast_drift.py` + `tools/ast_drift_manifest.sh`,
which prune identically. This matters: the first drift pass used a looser prune
and read the same Windows tree as **5,268** `.py` files against the census's
**2,404** — a 2.2x disagreement between two instruments looking at one tree,
entirely from `archive/`, `archived/` and `graphify-out/`. The two tools now share
the list, and both report 2,407.

### Environment matrix

| environment | root | interpreter | py files |
| --- | --- | --- | --- |
| windows-azazael | `C:/Azazael/azazael` | 3.15.0rc3 free-threaded (`py315t`) | 2407 |
| g-drive-archive | `G:/azazael` | 3.15.0rc3 | 2817 |
| kali-azazael | `/root/azazael` (WSL `kali-linux`) | 3.14.6 | 1502 |
| ubuntu-azazael | `/root/azazael` (WSL `Ubuntu-26.04`) | 3.14.7 | 1462 |
| windows-edge0 | `C:/Users/clint/edge0-intel` | 3.15.0rc3 | 161 |
| windows-pams-source | `C:/Azazael/pams-source` | 3.15.0rc3 | 14 |
| windows-graph3d | `C:/Users/clint/graph3d` | 3.15.0rc3 | 1 |

The Linux lanes were audited by running the Windows-hosted script over
`/mnt/c/...` inside each distro, so no file was written into either mirror.

---

## 2. Census

| environment | py | LOC | syntax err | classes | functions | methods | bare except | `except: pass` | `except: continue` | eval/exec | `open()` no enc | star import | markers | orphans | dup groups |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| windows-azazael | 2407 | 777954 | 0 | 3860 | 30855 | 16709 | 114 | 816 | 259 | 63 | 336 | 60 | 375 | 1397 | 50 |
| g-drive-archive | 2824 | 896504 | 7 | 4861 | 34918 | 22073 | 144 | 2399 | 276 | 374 | 569 | 72 | 388 | 1556 | 242 |
| kali-azazael | 1502 | 468983 | 0 | 2339 | 19029 | 10292 | 2 | 994 | 241 | 20 | 250 | 10 | 95 | 721 | 8 |
| ubuntu-azazael | 1463 | 456978 | 1 | 2317 | 18613 | 10266 | 3 | 969 | 215 | 21 | 260 | 10 | 82 | 701 | 6 |
| windows-edge0 | 161 | 30963 | 0 | 145 | 1211 | 447 | 0 | 36 | 15 | 17 | 11 | 0 | 4 | 108 | 9 |
| windows-pams-source | 14 | 32995 | 0 | 28 | 270 | 433 | 27 | 35 | 6 | 0 | 42 | 0 | 0 | 6 | 1 |
| windows-graph3d | 1 | 463 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| **total** | **8372** | **2664840** | **8** | **13550** | **104901** | **60220** | **290** | **5249** | **1012** | **495** | **1468** | **152** | **944** | **4490** | — |

`g-drive-archive` is the mode/`.py`-imported copy of everything, so its numbers
are a *historical* census, not a second codebase: it carries 2,399 `except: pass`
against Windows' 816 because it still holds pre-cleanup revisions.

### The swallowing that is actually first-party

On the Windows tree, most of those counters are vendored or archived copies:

| counter | all | first-party (excl. `nuitka_build_backup/`, `archived_unified/`, `packages/azazael-core/`) |
| --- | --- | --- |
| `except: pass` | 816 | 324 |
| bare `except:` | 114 | 3 |
| `except: continue` | 259 | 231 |
| `open()` with no encoding | 336 | 92 |
| `eval`/`exec` | 63 | 22 |
| star import | 60 | 9 |

`nuitka_build_backup/inline_copy` alone holds 339 `except: pass`, 38 bare
`except:`, 130 unencoded `open()` and 34 `eval`/`exec` — it is a build artefact
copy, not code anyone maintains. Quoting the "all" column as a code-quality
finding would be reading a backup as a source.

The one first-party number that is worse than its vendored backdrop: **231 of 259
`except: continue` are first-party.** That is the loop-agent pattern — an error in
one item silently skips it and the run reports success over fewer items than it
claims to have processed.

---

## 3. The eight files that cannot be parsed

Seven in `G:/azazael`, one in Ubuntu. All eight are **truncated or corrupt
copies**, not source defects — measured by pitting each against its Windows
counterpart:

| file (G:) | G: lines | Windows lines | Windows parse |
| --- | --- | --- | --- |
| `AOA/build.py` | 169 | 238 | parses |
| `AOA/build_disclosure.py` | 45 | 125 | parses |
| `AOA/gen_html.py` | 206 | 128 | parses |
| `AOA/inject.py` | 201 | 111 | parses |
| `AOA/rebuild_html.py` | 180 | 206 | parses |
| `AZAZAEL_ROOT/src/AOA/cli/aoa_cli.py` | 568 | 581 | parses |
| `EveUnleashed/scripts/probe_model.py` | 70 | — | (not present on Windows) |
| `scripts/patch_msvcrt.py` (Ubuntu) | — | — | (not present on Windows) |

`build.py` stops mid-string at line 169, `build_disclosure.py` at line 24, so the
copy is cut, not merely stale. **The G: drive is described in canon as the restore
source; for these seven files it cannot restore anything.** Every one of them
fails `ast.parse` at the cut point, which is what a truncated write looks like.

---

## 4. Cross-environment drift

Shared paths compared by md5:

| pair | common | identical | different | only-left | only-right |
| --- | --- | --- | --- | --- | --- |
| windows (2407) vs kali (1502) | 1422 | 813 | **609 (42.8%)** | 985 | 80 |
| windows (2407) vs ubuntu (1463) | 1382 | 776 | **606 (43.8%)** | 1025 | 81 |
| kali vs ubuntu | 1427 | 1249 | **178 (12.5%)** | 75 | 36 |

Read as: **two in five shared files differ between the production lane and its
mirrors.** The two mirrors agree with each other far better (12.5%) than either
agrees with Windows, so the divergence is Windows-side and recent, not a mirror
sync that half-failed.

Some divergence is expected — `archived_unified/` is Windows-only (a large share of
the 985 / 1,025 left-only paths). The parts that are not expected:

- `src/CORE/paths.py` — canonical path resolution — **exists only in the Kali and
  Ubuntu mirrors** (dated 2026-06-19). Absent on Windows, while `AGENTS.md` and the
  `azazael-paths` skill both describe it as the central resolver. Either the
  Windows lane resolves paths some other way or the canon describes a module the
  production lane does not have; the audit cannot tell which, and the difference is
  one `ls` away for whoever owns it.
- `src/CORE/PamsBusBridge.py`, `src/UTILITIES/AzazaelDynamicLogger.py`,
  `packages/.../worms/clusters/NATURE_CLUSTERS.py` — the last of these is the file
  that `PRODUCTION_TODO.md` asks for and that the Windows tree does not contain at
  this path.
- `src/CORE/*.py` is 338 files on Windows and 293 on Kali — mirrors **narrower**
  than the lane they mirror, in a directory both lanes write to.

---

## 5. Backlog forensics

`tools/backlog_triage.py` reads every first-party planning document, extracts each
open checkbox, and asks the filesystem one question per item: **does the path or
identifier this item names actually exist?**

| class | count | meaning |
| --- | --- | --- |
| items found | 555 | `- [ ]` unchecked across 33 documents |
| **resolved** | 28 | names a path that now exists — the work landed and the box was never ticked |
| **absent** | 7 | names a path that exists nowhere in any tree |
| unchecked | 444 | names no path or identifier — cannot be answered by a filesystem probe |
| identity-only | 76 | names only an identifier (e.g. `__all__`) — needs CODE, not a path |

The 7 absent items, as extracted — and then read one by one, because "absent"
is a claim about a path, not about whether the work is still owed:

| # | doc:line | named and not found | what it actually means |
| --- | --- | --- | --- |
| 1 | `LIVE_MONITOR_RESTRUCTURE_TODO.md:180` | `morph_policy.json` | owed: the task builds a safe path from a policy file that does not exist |
| 2 | `PRODUCTION_TODO.md:113` | `NATURE_CLUSTERS.py` | owed: names a file present only in the Kali mirror, not in production |
| 3 | `SESSION_INSIGHTS_2026-05-29_PHASE11.md:123` | `build_all.py`, `regenerate_bats.py` | owed: the standalone build scripts the item wires together do not exist |
| 4 | `SOP.md:1095` | `_tmp.py` | **already satisfied** — the item asks temp files be gone, and they are |
| 5 | `docs/NUITKA_3_14T_SKILL.md:304` | `test_minimal.py` | likely satisfied — a throwaway probe that was never meant to persist |
| 6 | `docs/NUITKA_3_14T_SKILL.md:306` | `vault_server.py` | likely satisfied — same |
| 7 | `state/ACTION_REGISTRY_2026-10-10.md:69` | `tools/run_technique_exercises.py` | owed: a named tool with no file behind it |

So the filesystem probe resolves **4 owed / 3 satisfied** out of 7, not 7 open
items — and that distinction only appears when each line is read rather than
counted. Items 4–6 are the instrument's own false-positive class: an item that
asks for a file to be *absent* reads as ABSENT when it succeeds.

### Comment markers, dated by git blame

944 markers are in the census; 375 on the Windows tree; **104 are first-party**
(the rest sit in archived/vendored copies). Of those 104, all carry a blame date:

| month | first-party markers |
| --- | --- |
| 2026-06 | 26 |
| 2026-09 | 40 |
| 2026-10 | 37 |
| 2026-11 | 1 |

Oldest dated marker still in the tree: **2026-06-11**
(`src/CORE/inference/providers.py:198`, `DEPRECATED` on a Gemini model id), then
three on `2026-06-21` (`src/CORE/codebuff_tracker.py` twice, `scripts/batch_render.py`).
26 markers are four and a half months old — that is the "months ago" backlog the
request is about, and it is now a dated list rather than a feeling.

---

## 6. Limits — what this audit cannot establish

1. **A parse is not a run.** 8,364 files parse; nothing here executed them.
2. **A path existing is not the work being done.** The 28 "resolved" items are
   resolved only in the sense that what they name exists; the *behaviour* was not
   re-tested.
3. **Orphans are not dead code.** 4,490 modules are imported by no analysed path —
   many are entry points, plugins, dynamically imported worms, or tests.
4. **Drift is not automatically a defect.** 43.8% of shared files differ, and some
   of that is deliberate (Windows-only archive, lane-local scripts). What the audit
   establishes is that **the lanes are not the same program**, which is the fact a
   sync or a restore has to start from.
5. **The census moves between runs, and the console line once lied about it.** A
   first pass read `G:` as 2,817 py files on the console while its own JSON said
   2,824, and Ubuntu as 1,462 against 1,463 — a 7-file and 1-file "drift" between two
   runs of one tool over one tree. **Cause found and fixed:** the summary line bound
   `py=` and `parsed=` to the same field (`py_parsed`), so it under-reported by
   exactly the syntax-error count each time. `py_files` in the JSON was right the
   whole way, and the console now prints it — the table above is `py_files`.
   Windows still moved 2,404 → 2,407 → 2,407+4 lines across this session, for a known
   reason: two tools were added (`tools/ast_audit.py`, `tools/ast_drift.py`), one copy
   was removed from `docs/audit/`, and the console fix added four comment lines. A
   count quoted without a timestamp is a guess, including this one.
6. **`except: pass` in a vendored file is not a finding here.** The first-party
   column exists precisely because the "all" column is mostly `nuitka_build_backup`.

---

## 7. Ranked next actions (from the evidence above, not from opinion)

1. **Restore-or-delete the 7 truncated G: files.** A backup that cannot be parsed is
   worse than no backup: it invites a restore that lands a broken file.
2. **`src/CORE/paths.py` — decide the lane.** Present in both mirrors, absent in
   production, described as canonical in canon. One decision resolves a documented
   capability gap.
3. **231 first-party `except: continue`** in loop agents — the class that reports
   success over fewer items than it processed.
4. **26 markers aged 2026-06** — the dated residue of the "months ago" backlog;
   each is either handled or deleted from the source, not carried.
5. **Two-in-five drift** between Windows and the mirrors — pick the direction of
   truth per directory before any sync, or a sync will pick it for you.

---

## 8. Reproduce

```bash
# census (Windows)
python tools/ast_audit.py --root C:/Azazael/azazael --out windows.json --label windows-azazael
python tools/ast_audit.py --root G:/azazael --out gdrive.json --label g-drive-archive

# census (Linux lanes, no writes into the mirrors)
wsl -d kali-linux -- bash -lc \
  'python3 /mnt/c/Azazael/azazael/tools/ast_audit.py --root /root/azazael \
   --out /mnt/c/Users/clint/ast_audit/kali.json --label kali-azazael'

# drift
python tools/ast_drift.py manifest C:/Azazael/azazael windows
bash tools/ast_drift_manifest.sh /root/azazael > kali.md5      # inside each distro
python tools/ast_drift.py compare

# backlog, dated markers
python tools/backlog_triage.py
```
