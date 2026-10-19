# 🌐 MASTER ENVIRONMENT INVENTORY — Azazael Ecosystem

> **3.14t RETIRED 2026-10-19 — read this before quoting any number below.**
> This inventory is a **capture of 2026-09-20**, before Python 3.15 existed on
> this host. Production is now `C:\Azazael\.venvs\py315t` (3.15.0rc3,
> free-threaded); the GIL sidecar is `C:\Azazael\.venvs\py315`; the retired
> 3.14t venv `C:\Users\clint\venv-314t` is archived; the only sanctioned 3.14
> runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Every row below therefore
> describes an environment that no longer serves production, and a package count
> measured in a 3.14 venv is **not** evidence that the package imports on 3.15t.
> Re-run `scripts/build_runtime_baseline.py` for current numbers rather than
> reading these as capabilities.

**Generated:** 2026-09-20 (live probe, not derived from prose)
**Method:** direct interrogation of every reachable environment. Raw captures in
`azazael/reports/env_inventory/` (`*_raw.txt`, `*_pip.txt`, `*_apt.txt`,
`win_winget.txt`, `matrix.md`).
**Purpose:** a single authoritative list of *what is installed where*, to drive
hyper-optimization of the architecture toward self meta-evolution.

> Supersedes `CROSS_ENV_MANIFEST.md` (2026-07-02) and
> `ENVIRONMENT_AUDIT_2026-08-29.md`, both of which are now factually stale
> (see §7).

---

## 0. Executive summary — the one paragraph that matters

There are **eight** environments, **six** Python installations that matter, and
**1,448** distinct Python distributions across them — of which only **64** are
present everywhere. There is **no common runtime baseline**. Worse, and this is
the direct cause of "interoperability is not working to adapt": **the full
self-adaptation stack (gymnasium, stable-baselines3, peft, trl, transformers)
imports in exactly one interpreter on the whole estate — Windows
`Python314\python.exe`, which is the *GIL-enabled* build.** Every free-threaded
runtime (the architectural premise of the entire project) can import `torch` and
`numpy` and nothing else from that stack. The loop that is supposed to make the
architecture self-evolve therefore could not execute on the runtime the
architecture is built around.

> **Update 2026-09-20:** this was diagnosed and fixed during the same session.
> No package was wheel-blocked — the stack had simply never been installed into
the 3.14t venv, and `transformers` 5.17.0 omits two leaf dependencies. `venv-314t`
> now imports 12/12 stack modules with `gil_enabled=False` and runs `PPO.learn()`.
> See `reports/ADAPTATION_314T_WHEEL_AUDIT.md`. Ubuntu and Kali still differ.

---

## 1. Environment roster

| # | Environment | OS / kernel | `.py` in sync scope | Python | Packages | Status |
|---|---|---|---|---|---|---|
| 1 | **Windows 11 host** `C:\Users\clint\azazael` | Win 11 Home 10.0.26200 | **626** | 3.14.7 (**GIL on**), 3.14.7t, 3.13.13 | 637 (global) | ✅ Reference pillar |
| 2 | **WSL Ubuntu-26.04** `/root/azazael` | Ubuntu 26.04 LTS, 6.18.33.2 | 592 | 3.14.7 **free-threaded**, 3.14.4 GIL | 300 pip / 2,447 apt | ⚠️ OUT OF SYNC |
| 3 | **WSL Kali Linux** `/root/azazael` | Kali Rolling 2026.1 | 580 | 3.14.6 **free-threaded**, 3.13.12 GIL | 1,009 pip / 4,374 apt | ⚠️ OUT OF SYNC |
| 4 | **G: source-of-truth** `G:/source-of-truth/azazael` | 477 GB vol (82 % used) | 553 | n/a | — | ⚠️ Out of sync |
| 5 | **G: AZAZAEL_ROOT** `G:/AZAZAEL/AZAZAEL_ROOT` | same volume | **770** ← largest | n/a | — | ⚠️ Superset archive |
| 6 | **Desktop Standalone** `C:/Users/clint/Desktop/AZAZAEL_Standalone` | Nuitka 3.14t builds | 0 (release pillar) | frozen | **0 `.exe`** 🔴 | ⚠️ **Empty shell** |
| 7 | **Docker Desktop** | WSL2 backend | — | — | daemon **stopped** | ❌ Not running |
| 8 | **Ollama / LM Studio** | native + WSL | — | — | 8 models / 21+ GGUF | ✅ Running |

Installed WSL distros (`wsl -l -v`): `Ubuntu-26.04` (default, stopped),
`docker-desktop` (stopped), `kali-linux` (stopped).

### 1.1 Live sync status — ``sync_all.py --status`` (2026-09-20T16:01:47)

```
[OK] Windows 11 (primary dev)   .py 626   docs 48
[OK] WSL2 Ubuntu-26.04 (wsl)    .py 592   docs 48
[OK] Desktop AZAZAEL_Standalone docs 48
[OK] G: source-of-truth         .py 553   docs 48
[OK] G: AZAZAEL_ROOT (archive)  .py 770   docs 48
[OK] Kali Linux (WSL2)          .py 580   docs 48

Integrity: OUT OF SYNC
  expansion: FAIL
  tests:     FAIL
  scripts:   FAIL
```

Every pillar reports `[OK]` for *reachability*, and the run then declares
**OUT OF SYNC** — the tool's own per-pillar check is weaker than its aggregate
check. Note also **Desktop Standalone is the pillar that is supposed to ship the
release, and it contains 0 executables** while G: holds 52.

---

## 2. Per-environment detail

### 2.1 Windows 11 host

**System:** 15,741 MB RAM · Win 11 Home build 26200 · drives:

| Drive | Size | Used | Free | Use% |
|---|---:|---:|---:|---:|
| C: | 756 G | 743 G | **13 G** | **99 %** 🔴 |
| D: | 115 G | 46 G | 70 G | 40 % |
| E: | 97 G | 68 G | 29 G | 71 % |
| G: | 477 G | 387 G | 90 G | 82 % |

**Python interpreters (`py -0p`)**

| Interpreter | Version | GIL | Site-packages |
|---|---|---:|---|
| `Python314\python3.14t.exe` | 3.14.7 | **off** | (free-threaded tree) |
| `Python314\python.exe` | 3.14.7 | **on** | **637 dists** |
| `Python313\python.exe` | 3.13.13 | on | 35 dists |
| uv `cpython-3.14.3+freethreaded` | 3.14.3 | off | — |
| uv `cpython-3.12.12` | 3.12.12 | on | — |
| uv `cpython-3.11.15` | 3.11.15 | on | — |

**Project virtualenvs**

| Venv | Python | GIL | Packages | Adaptation stack importable? |
|---|---|---:|---:|---|
| `venv-314t` | 3.14.7 | **off** | 161 | ❌ torch, numpy only |
| `venv-interpreter` | 3.14.7 | on | 149 | ❌ numpy only |
| `venv-313-tools` | 3.13.13 | on | 127 | ❌ |
| `azazael/.venv-3.14t` | 3.14.7 | **off** | **11** | ❌ (effectively empty) |
| `aider-venv` | — | — | 8 | ❌ |
| `python` (global) | 3.14.7 | **on** | **637** | ✅ **the only one** |

**Global toolchain**

| Tool | Version | Path |
|---|---|---|
| node / npm | v24.14.0 / 11.9.0 | `C:\Program Files\nodejs` |
| bun | 1.3.14 | `~/.bun/bin` |
| go | 1.26.3 windows/amd64 | `C:\Program Files\Go` |
| rustc / cargo | 1.95.0 | `~/.cargo/bin` |
| ffmpeg | 8.1.1 full_build (gyan.dev) | WinGet Links |
| git | 2.53.0.windows.1 | `/mingw64/bin` |
| ollama | 0.32.15 | `AppData\Local\Programs\Ollama` |
| docker | Desktop (daemon down) | `AppData\Local\Programs\DockerDesktop` |
| VS Code | installed | `Program Files\Microsoft VS Code` |

**npm globals (6):** `@kilocode/cli@7.5.13`, `@zilliz/memsearch-opencode@0.3.0`,
`freebuff@0.0.110`, `node-gyp@12.3.0`, `opencode-ai@1.18.31`, `pnpm@10.30.3`

**winget:** 188 packages (`reports/env_inventory/win_winget.txt`)

**Model stores on C::** `.ollama` = **35 G**, `.lmstudio` = **56 G** → **91 G** of
the 743 G used on a volume with 13 G free. This is a hard architectural ceiling.

**Ollama models (8):** `MichelRosselli/bonsai-27b:Q1_0`, `ornith-9b`,
`qwythos-9b`, `qwopus-9b`, `qwythos-9b-lenient`, `eve-v2u`, `qwen3-embedding:0.6b`,
`nomic-embed-text`

**LM Studio (21 GGUF):** gemma-4-E2B/E4B, Qwen3.5-4B/9B, Qwen2.5-Coder-7B,
Qwen3.5-9B-Claude-4.6-HERETIC, Llama3.3-8B-Heretic, UI-TARS-1.5-7B,
Qwen3-VL-8B-abliterated, nomic-embed-text-v1.5

**Skills:** `C:\Users\clint\.agents\skills` → **1,228 `SKILL.md`** files
(1,459 files total under `.agents`). Mirrored at `azazael/.agents` (1,226) and
`azazael/skills` (1,227).

**Source:** `azazael/src` = **626 `.py`**; whole tree = **7,230 `.py`**.

### 2.2 WSL Ubuntu-26.04

- **OS:** Ubuntu 26.04 LTS · 4 cores · 3,916 MB RAM · root disk `/dev/sdd` **175 G used / 1,007 G**
- **Python:** `/usr/bin/python3` → 3.14.7 **free-threaded** · `/usr/bin/python3.14` → 3.14.4 GIL · pip 26.2.1 from **`/usr/local/python314t`** (a *third* 3.14 tree)
- **Venvs found:** `/root/azazael/.nox/{quick-314t,lint,quick-314}`, `/root/venv-interpreter`, `/root/venv-314`, `/root/azazael-dev/.venv`, `/root/open-interpreter/venv`
- **apt:** 2,447 installed / **157 explicit**
- **pip:** 300
- **Toolchain:** gcc 15.2.0, clang, cmake, go 1.26.0, node v22.22.1/npm 9.2.0, docker, ffmpeg 8.0.1, bazel 7.7.0, Intel oneAPI (dpcpp + MKL), CUDA toolkit 13.0.2
- **Adaptation stack:** `transformers, numpy, networkx, llama_cpp` ✅ — **`torch, gymnasium, SB3, peft, trl, datasets, sentence_transformers, igraph, kuzu, chromadb, onnxruntime` all MISSING**
- **Project copy:** `/root/azazael` = 854 M
- **Mounts:** `/mnt/c` ✅, `/mnt/e` ✅, **`/mnt/g` present but NOT mounted** 🔴

### 2.3 WSL Kali Linux

- **OS:** Kali Rolling 2026.1 · 4 cores · 3,916 MB RAM · root disk `/dev/sde` **85 G used / 1,007 G**
- **Python:** `/usr/bin/python3` → 3.14.6 **free-threaded** (`/usr/local/lib/python3.14t`) · `/usr/bin/python3.13` → 3.13.12 GIL · `/usr/local/bin/python3.14` → 3.14.6 free-threaded
- **apt:** 4,374 installed / **867 explicit** — the full Kali tool meta-packages (`kali-linux-core`, `kali-tools-*` ×12)
- **pip:** **1,009** (the largest single Python surface; drives the 968 `azazael-pkg-*` skills)
- **Venvs:** `/root/osint-tools/.venv`, `/root/osint-tools/blackbird/.venv`, `/root/openwebui-venv`, `/root/azazael/.nox/*`, `/root/osint_venv`, `/opt/osint-venv`, `/opt/security-tools`
- **Toolchain:** gcc 15.2.0, cargo/rustc 1.95.0, go 1.26.4, node v24.15.0/npm 11.16.0, ffmpeg 8.1.1, terraform, helm, java, sqlite3, psql, redis-cli, nginx, chromium, firefox
- **Services running:** `docker.service` ✅ (containerd up, listening 127.0.0.1:36031), cron, dbus, rsyslog, polkit
- **Adaptation stack:** `numpy, networkx` only — **13 of 15 probed modules missing**
- **Project copies:** `/root/azazael` = 497 M · `/root/vermillion_lightfury` = 5.5 M
- **Mounts:** `/mnt/c` ✅, `/mnt/e` ✅, **`/mnt/g` present but NOT mounted** 🔴

### 2.4 G: archive (Windows-visible only)

| Path | Size | Content |
|---|---:|---|
| `G:/AZAZAEL` | **52 G** | wheels, CODEX videos, AZAZAEL_ROOT |
| `G:/AZAZAEL_SOURCE_OF_TRUTH` | **56 G** | core docs, configs, function catalogs |
| `G:/AZAZAEL_Standalone` | 2.9 G | **52 `.exe`** + bats + HTML |
| `G:/AZAZAEL_UBUNTU` | 207 M | drivers, python-wheels |
| `G:/source-of-truth/azazael` | 553 `.py` | **what `sync_all.py` actually targets** |
| `G:/AZAZAEL/AZAZAEL_ROOT` | 770 `.py` | full project archive (superset) |
| `G:/AZAZAEL_BOOT` | **absent** | listed in older manifests; no longer present |
| `G:/kali_recovery.vhdx` | 67 G | crashed Kali recovery disk |
| `G:/WORKING.HTML.AZAZAEL`, `Archive`, `Desktop_Archive`, … | remainder | historical |

### 2.5 Desktop Standalone (`G:/AZAZAEL_Standalone`)

**52 `.exe` on G:** — but the *Desktop* copy (`C:/Users/clint/Desktop/AZAZAEL_Standalone`),
which is the path `sync_all.py` declares as the `desktop` / `exe_only` pillar, is
**1.3 M with 0 `.exe`** — an empty shell. The sync tool therefore reports the
release pillar `[OK]` while checking a directory that ships nothing.
Names present include `AZAZAEL_CLI_314t`, `CLUSTERWORMS_314t`, `METACLUSTER_314t`,
`NATURE_Clusters_314t`, `HYDRA_314t`, `AZAZAEL_Inference_Studio_314t`,
`Environment_Manager_314t`, `Eve_Unleashed_314t`, `CODEX_Studio_314t`, … plus
several near-duplicate pairs (`Changelog_Generator_314t` **and** `Changelog_Gen_314t`,
`Matrix_Animation_314t` **and** `Matrix_Video_314t`, `Compress_Video_314t` **and**
`Create_Video_314t`, 4× `POPUP_*`).

### 2.6 Docker

- **Docker Desktop** on Windows: installed, daemon **not running** (npipe absent)
- **Kali WSL:** `docker.service` **running**, containerd on `127.0.0.1:36031`
- `azazael/docker-compose.yml` + `Dockerfile` + `docker/` exist in-repo
- Net: container capability exists but is **asymmetric and unverified** — no running containers observed on either side

---

## 3. Cross-environment package matrix

Full matrix: `reports/env_inventory/matrix.md`. Headline numbers:

| Environment | Packages |
|---|---:|
| win-main (GIL **on**) | 637 |
| win-314t (free-threaded) | 161 |
| win-313tools | 127 |
| win-interpreter | 149 |
| ubuntu | 300 |
| kali | **1,009** |

- **Union of distinct distributions: 1,448**
- **Present in *every* environment: 64** ← the entire shared baseline is 4.4 % of the estate

### 3.1 The adaptation stack — where it can actually run

| Module | win-main (GIL **on**) | win-314t (**3.14t**) | ubuntu (**3.14t**) | kali (**3.14t**) |
|---|:--:|:--:|:--:|:--:|
| `torch` | ✅ | ✅ | ❌ | ❌ |
| `transformers` | ✅ | ❌ | ✅ | ❌ |
| `gymnasium` | ✅ | ❌ | ❌ | ❌ |
| `stable_baselines3` | ✅ | ❌ | ❌ | ❌ |
| `peft` | ✅ | ❌ | ❌ | ❌ |
| `trl` | ✅ | ❌ | ❌ | ❌ |
| `datasets` | ✅ | ❌ | ❌ | ❌ |
| `sentence_transformers` | ✅ | ❌ | ❌ | ❌ |
| `igraph` | ❌ | ❌ | ❌ | ❌ |
| `kuzu` | ❌ | ❌ | ❌ | ❌ |
| `chromadb` | ✅ | ❌ | ❌ | ❌ |
| `onnxruntime` | ✅ | ❌ | ❌ | ❌ |

**Every free-threaded interpreter on the estate can run 0–4 of these 15 modules.
The single interpreter that runs the full stack is not free-threaded.**

### 3.2 Version skew on load-bearing libraries

| Package | win-main | win-314t | ubuntu | kali | Skew |
|---|---|---|---|---|---|
| numpy | 2.5.3 | 2.4.6 | 2.4.6 | 2.5.3 | 3 minors |
| torch | 2.14.0+cpu | 2.14.0 | 2.12.0 | — | 2 minors + cpu tag |
| transformers | 5.17.0 | — | 5.9.0 | — | 8 minors |
| networkx | 3.6.1 | — | **2.8.8** | **2.8.8** | **major (2→3)** |
| pandas | 3.0.5 | 3.0.3 | 2.3.3 | 2.3.3 | **major (2→3)** |
| openai | 3.16.2 | 3.16.0 | 2.41.1 | 2.21.0 | **major (2→3)** |
| anthropic | 0.37.1 | 1.6.0 | 1.0.0 | — | 3 incompatible lines |
| rich | 15.0.0 | 15.0.0 | 15.0.0 | 13.9.4 | 2 majors |
| scikit-learn | 1.9.1 | 1.9.0 | 1.8.0 | 1.8.0 | 2 minors |
| tiktoken | 0.7.0 | 0.14.0 | 0.14.0 | — | **2× major** |
| pytest | 9.0.3 | 9.1.1 | 9.0.3 | 9.1.0 | minor |

Two `networkx` majors and two `pandas` majors in the same codebase mean graph
code and dataframe code **cannot be assumed portable across environments**.

### 3.3 Distribution-unique packages (structural fragmentation)

| Environment | Unique packages | Examples that lock it in |
|---|---:|---|
| win-main | 276 | `accelerate`, `peft`, `trl`, `datasets`, `stable_baselines3`, `gymnasium`, `ray`, `faiss-cpu`, `streamlit`, `alembic` |
| kali | 561 apt / ~800 pip | the whole offensive-security surface |
| ubuntu | ~200 | Intel oneAPI/OpenVINO/CUDA stack, bazel |
| win-313tools | — | `kuzu`, `igraph`, `rustworkx` (graph stack) |
| win-314t | — | `graphiti-core` (temporal graph) |

---

## 4. Interop faults — ranked

| # | Fault | Evidence | Impact |
|---|---|---|---|
| ~~I1~~ | ~~The adaptation stack runs only on a GIL-enabled interpreter~~ **→ CLOSED 2026-09-20** | §3.1 | Was *the* reason it "is not working to adapt". **Root cause was not wheels** — nothing is wheel-blocked. The stack was simply never installed into the 3.14t venv, and `transformers` 5.17.0 omits two leaf deps (`narwhals`, `threadpoolctl`) from its metadata. `venv-314t` now runs 12/12 modules **free-threaded** with SB3 training and peft config construction verified live. See `reports/ADAPTATION_314T_WHEEL_AUDIT.md`. **Remaining:** Ubuntu (resolves, not installed), Kali (resolver backtracks to `transformers 2.3.0`). |
| **I2** | **No common runtime baseline** | 64 / 1,448 shared | Any cross-env code path is untestable by construction. |
| **I3** | **G: is invisible from both Linux environments** | `/mnt/g` present, not mounted, both distros | The archive/source-of-truth pillar is unreachable from Linux; the documented `rsync → /mnt/g/azazael_shared/` sync path **cannot work**. |
| **I4** | **Major-version skew on graph + dataframe + LLM-SDK libs** | §3.2 | `networkx` 2 vs 3 and `pandas` 2 vs 3 break silently, not loudly. |
| **I5** | **Skills exist in 3+ divergent mirrors** | 1,228 / 1,226 / 1,227 `SKILL.md` | No single authority; drift is unmeasurable. |
| **I6** | **Kali has forked into its own codebase** | 497 M vs 854 M vs 13 G; 1,009 pip | Three "mirrors" of one project with three different contents. |
| **I7** | **`azazael/.venv-3.14t` is an 11-package stub** | §2.1 | Any script resolving to the project venv gets an unusable interpreter. |
| **I8** | **Standalone distribution is duplicated + mis-pointed** | 52 exe on G:, **0** at the path `sync_all.py` treats as the release pillar, near-duplicate pairs | The release pillar validates an empty directory; unclear which binary is canonical. |
| **I9** | **Docker capability is asymmetric** | §2.6 | Containers run on Kali, not Windows, not Ubuntu; compose file targets neither. |
| **I10** | **C: is near-full — ACCEPTED BY DECISION 2026-09-20** | §2.1 | 78 GB of model weights (`.ollama/models` 25 G + `.lmstudio/models` 53 G) sit on the system volume; C: free fluctuates 25–36 GB. A relocation (Ollama → D: 70 G free, LM Studio → G: 90 G free) was **planned and declined** — C: stays near-full deliberately, so this is a *standing condition*, not drift. Procedure is staged in `scripts/relocate_model_stores.sh --plan`. Accepted in the drift alarm; it still prints, it just no longer counts as drift. **Review when C: free drops below 10 GB.** |
| **I11** | **Documentation contradicts measurement** | §7 | Planning is being done against fictional numbers. |

---

## 5. What this means for hyper-optimization / self meta-evolution

### 5.1 The blockers, in dependency order

1. **Get the adaptation stack onto a free-threaded interpreter** (fixes I1).
   Today the evolution loop is either GIL-bound or absent. Until `gymnasium` +
   `stable_baselines3` import on `python3.14t`, "3.14t free-threaded
   self-evolution" is a description of an intention, not a running system.
2. **Establish one pinned baseline** (fixes I2, I4). A single
   `requirements-3.14t.lock` resolved identically on all six interpretations,
   with a CI job that fails on drift.
3. **Re-mount or re-locate the archive** (fixes I3, I10). G: is not automounted
   in WSL and C: is at 99 %. Move `.ollama` + `.lmstudio` (91 G) off C: onto G:
   (90 G free) or D: (70 G free), then add G: to `automount` in `/etc/wsl.conf`.
4. **Collapse the mirrors** (fixes I5, I6). One canonical tree, hard-linked
   mirrors, and a checksum manifest — not three copies that drift silently.
5. **Make the standalone pass reproducible** (fixes I8). One naming authority,
   no `*_314t` / `*_314t` pairs.

### 5.2 Budget reality check (from `ADAPTATION_BUDGET_AUDIT_2026-09-18.md`)

Even with I1 fixed, the loop is measurably too coarse to adapt:

| Layer | Budget | Required | Ratio |
|---|---|---|---|
| Measurement | fitness noise 1.47 | effect 0.75 (`PROMOTE_MARGIN`) | **2.0× too coarse** (fixed at 320 episodes → 0.478 noise) |
| Model | 8,192-token context | ~33,610 tokens mandatory reading | **4.1× too small** |
| Data | 200 records extracted | ~244,000 rows / 880 MB | **1,220× short** |

The two free fixes (paired estimator, `80 → 320` episodes) are the highest-value
changes available and neither requires a new package.

### 5.3 What "hyper-optimize to self meta-evolve" should target first

| Lever | Current | Target | Cost |
|---|---|---|---|
| Free-threaded adaptation runtime | ✅ **done 2026-09-20** (12/12 modules, `PPO.learn()` verified) | — | — |
| Baseline lock | none | 1 lockfile, 6 envs | writing |
| Fitness budget | 80 episodes, min-of-salts | 320 episodes, paired deltas | **free** |
| Operator context | 8,192 | ≥ 34,000 | server config |
| `max_nudges` | 0 | > 0 | config |
| `data_limit` | 200 | paginated past 500 | code |
| C: headroom | 25–36 G | *declined* | relocation staged but **not** executed — see §5.4 |
| Environment drift alarm | none | scheduled `benchmark_evolution.py` + integrity check | wiring |

`benchmark_evolution.py` check [7] sat **red for three days** while the loop was a
no-op — nothing was wired to run it. An inventory that is not re-run on a
schedule will be stale again within a week; the drift alarm matters more than the
inventory itself.

### 5.4 Accepted conditions (decisions, not drift)

The drift alarm treats deliberately-chosen conditions as **accepted**: still
printed on every run, no longer counted as drift. This is the mechanism that
keeps the alarm readable — an alarm that fires forever on a known decision is an
alarm nobody reads.

| Condition | Decision | Rationale | Review trigger |
|---|---|---|---|
| `disk-headroom` (C: near-full) | **Accepted 2026-09-20** | Model-store relocation (Ollama 25 G → D:, LM Studio 53 G → G:) planned, then declined. Nothing was moved; `settings.json` and `OLLAMA_MODELS` unchanged. | C: free < 10 GB, or a build needs the space |

Revisit with `python scripts/env_drift_alarm.py --list-accepted`, or reverse with
`--unaccept disk-headroom`. The staged procedure is
`bash scripts/relocate_model_stores.sh --plan` (read-only; `--execute` is a
separate, explicit step).

---

## 6. Reproduce this inventory

```bash
cd azazael/reports/env_inventory

# Windows
python build_matrix.py > matrix.md
  # feeds: win_main_py.txt, win_venv-314t.txt, win_venv-313-tools.txt,
  #        win_venv-interpreter.txt, ubuntu_pip.txt, kali_pip.txt

# Linux sides (base64 avoids multi-layer quoting corruption)
B64=$(base64 -w0 probe_linux.sh);  wsl.exe -d Ubuntu-26.04 -- bash -c "echo $B64 | base64 -d | bash"
B64=$(base64 -w0 probe_linux.sh);  wsl.exe -d kali-linux   -- bash -c "echo $B64 | base64 -d | bash"
B64=$(base64 -w0 probe_pyver.sh);  wsl.exe -d <distro>     -- bash -c "echo $B64 | base64 -d | bash"
B64=$(base64 -w0 probe_adapt.sh);  wsl.exe -d <distro>     -- bash -c "echo $B64 | base64 -d | bash"
```

> Note: piping a loop body directly through `wsl.exe ... bash -lc '<script>'`
> **silently corrupted the loop variable** in this session (every iteration
> emitted an empty name). The base64-pipe form above is the reliable pattern —
> worth codifying as the standard remote-probe idiom.

---

## 7. Corrections to prior documents

| Prior claim | Source | Measured 2026-09-20 |
|---|---|---|
| "WSL Ubuntu: **No native project files**" | `CROSS_ENV_MANIFEST.md` | `/root/azazael` = 854 M, `/root/vermillion_lightfury` = 6.2 M |
| "Kali: No native project files" | `CROSS_ENV_MANIFEST.md` | `/root/azazael` = 497 M, `/root/vermillion_lightfury` = 5.5 M |
| "G: drive … 477 G, 99 % used" | `ENVIRONMENT_AUDIT_2026-08-29.md` | **82 % used, 90 G free** |
| "C: 96 % (722/756 G)" | same | **99 % (743/756 G, 13 G free)** |
| "G:/AZAZAEL … 16 GB" | `CROSS_ENV_MANIFEST.md` | **52 G** |
| "G:/AZAZAEL_SOURCE_OF_TRUTH … 8.9 MB" | same | **56 G** |
| "Azazael … 5,277 files" | same | 7,230 `.py` alone |
| "39 `.exe`" | `azazael-standalone` skill | **52 `.exe` on G:; 0 on the Desktop pillar** |
| "Desktop Standalone = release output" | `sync-patterns` skill | The tracked path `C:/Users/clint/Desktop/AZAZAEL_Standalone` holds **0 `.exe`**; the 52 binaries live at `G:/AZAZAEL_Standalone` |
| "WSL2 Ubuntu… 319 `.py`" / "Kali…" | `azazael-sync-patterns` | Ubuntu **592**, Kali **580**, G: source **553**, G: ROOT **770**, Windows **626** |
| "`sync_all.py` missing on every pillar" (earlier draft of this file) | — | **Retracted.** `azazael/scripts/sync_all.py` (753 lines) exists and runs; see §1.1. The earlier `glob`/search miss was a tooling artefact, not an absent file |
| "No venv in this tree has `peft`/`trl`/`transformers`; 3.14t has no wheels for them" | `PRIORITIES_2026-09-18.md` | **False for the Windows global env** — `peft 0.19.1`, `trl 1.4.0`, `transformers 5.17.0` are installed and importable (on the GIL build) |
| "Canonical source: Kali `/root/azazael/`" | `SYNC.md` | Contradicts `CROSS_ENV_MANIFEST.md` ("Windows is source of truth") — **the project has two contradictory canonicality claims** |
| "1,259 skills" / "1,224 skills" | `SKILLS_CATALOG.md` | **1,228 `SKILL.md`** on disk |

---

*Raw evidence: `azazael/reports/env_inventory/`. Regenerate before trusting any
number in this file — see §5.3, the drift alarm is the point.*
