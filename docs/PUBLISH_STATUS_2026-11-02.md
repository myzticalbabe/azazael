# PUBLISH STATUS — 2026-11-02, freebuff lane took over the opencode push

**Subject:** the five publishable `Project_*` repos, staged and verified as standalone
git repositories under `C:/Azazael/publish`.
**Verdict:** five repos staged, self-verifying from a fresh `git clone`, and **one
step from published**. That step is `gh auth login`, which is interactive and
therefore owner-only. Nothing was pushed today, by decision.

---

## 1. What actually happened to opencode — it did not crash

Measured, not inferred:

| Evidence | Reading |
|---|---|
| `tasklist \| grep opencode` | `opencode.exe` pid 19632, 296 MB — **still running** |
| `~/.local/share/opencode/log/opencode.log:186626` | `12:02:45.948Z level=ERROR "Failed to drain Session" cause=AI.Error.QuotaExceeded: Free usage limit reached ... subscribe to OpenCode Go` |
| same log, `grep -c QuotaExceeded` | **24** occurrences, back to 2026-10-19 |
| `~/.config/opencode/opencode.json:3` | `"model": "opencode/muse-spark-1.3-contributor-free"` |

The process is alive and serving; the **session drain** fails on the free-tier
quota for the configured model. A dead client and a quota-refused client look
identical from the TUI, which is why this was reported as "OPENCODE DIED".

Also visible in the same log and **not** the cause, but worth fixing separately:
`level=WARN ... Invalid MCP stdio message from pams: Unexpected identifier "INFO"`
— the pams stdio server writes `INFO` log lines to **stdout**, which is the MCP
protocol channel. Any lane that spawns pams gets corrupt frames; the tools that
did answer still answered, so this is noise today and a fragile transport tomorrow.

The local fallbacks configured in `opencode.json` (`spark` :8087, `ollama` :11434,
`local-xml` :11435) were all **down** (`curl /v1/models` → `000` on every port), so
"just switch model" was not available without starting a runtime first.

## 2. What the take-over is

The push cannot happen, so the take-over is everything **up to** it:

| Tool | Purpose |
|---|---|
| `tools/stage_publish_repos.py` | snapshot each `Project_*` into its own single-commit repo on `main`; `--check` audits the set |
| `tools/publish_repos.py` | create + push all five once `gh` is authenticated; **dry run is the default**, `--execute` required, `--public`/`--private` mandatory |

The reason the monorepo is not the publish unit: `docs/PUBLISH_READINESS_2026-11-02.md`
B1 — two blobs in its history exceed GitHub's 100 MB hard per-file limit
(`archived/2026-05-31/onnxruntime.tar.gz` 272.339 MB,
`archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz` 228.847 MB, 501.186 MB
of a 954.92 MiB pack), and `origin` is the local path `C:\Users\clint\azazael`.
Staging fresh histories **contains no vendored tarball by construction** — no
`filter-repo`, no monorepo SHA changes, no 501 MB upload.

## 3. Staged set (measured 2026-11-02)

| repo | HEAD | tracked | size |
|---|---|---|---|
| `flaming-sword` | `18eeb3e70c58` | 21 files | 1 MB |
| `nurse-ratchet` | `fbb264747f03` | 55 files | 2 MB |
| `shardex` | `a4d89b612b83` | 14 files | 1 MB |
| `cradle` | `631afb52c1cb` | 8 files | 1 MB |
| `flame-engine` | `d903c78666ea` | 7 files | 1 MB |

`python tools/stage_publish_repos.py --check` → **PUBLISHABLE** (each: branch
`main`, exactly 1 commit, clean tree, required files present, nothing over the
file limit).

## 4. Verification — from a fresh clone, not from the staging directory

Each repo was `git clone`d to `C:/Azazael/.tmp_pubcheck`, installed with
`pip install --no-deps .`, and its own suite run:

| repo | result |
|---|---|
| flaming-sword | **109 passed** |
| nurse-ratchet | **169 passed** |
| shardex | **34 passed, 1 skipped** |
| cradle | **4 passed, 8 skipped** (skips are the `N/A — not installed` sibling checks by design) |
| flame-engine | **no tests** — pytest exit 5, expected: the project ships none |

**316 passing tests**, matching the numbers in `docs/FULL_REVIEW_2026-11-02.md`,
now proven against the artifact that would actually be pushed rather than against
a directory copy.

## 5. Three defects found during the take-over, and fixed

1. **`nurse_ratchet/tools/publicize.py` failed in exactly the layout publishing creates.**
   It read the manifest and demanded every `../src/...` source exist; in a
   standalone repo those sources are the monorepo's and are not shipped, so CI's
   first step exited **1** while printing `public tree: OK`. Fixed as a **third
   state**: source missing **and** target present = already materialised (exit 0);
   source missing **and** target missing = still a refusal. Verified after fix:
   `PUBLICIZE RC=0`, `already materialised: 27 entries`, `public tree: OK`,
   169 tests still pass.
2. **Restaging failed with `WinError 5` on `git`'s read-only objects.** `shutil.rmtree`
   stops at the first read-only file; `force_rmtree` clears the bit and retries.
   Verified: `--only nurse-ratchet --force` now succeeds.
3. **The publish precondition check crashed instead of refusing.** `gh` is installed at
   `C:/Azazael/tools_bin/bin/gh.exe` but not on `PATH`, and an unguarded
   `subprocess.run` raised `FileNotFoundError` through the refusal path. `run()`
   now returns rc 127. Verified all three paths: no visibility flag → `REFUSED`;
   no `gh` → clean preflight failure; `gh` present but logged out →
   `You are not logged into any GitHub hosts`.

A fourth thing that looked like a defect and is not: running `publicize.py` in a
clone leaves 27 files "modified", but `git diff --stat` is **empty** — this machine
has `core.autocrlf=true` and the tool writes LF. No content drift; a Linux runner
sees a clean tree. Recorded so it is not diagnosed as drift twice.

## 6. The one remaining gate

```
gh auth login --hostname github.com --git-protocol https --web
python tools/publish_repos.py --public --execute      # or --private
```

Until that login happens `--execute` refuses before any network call. The login is
interactive, which is why opencode being unavailable did not stop this work but
does stop the push.

## 7. Risks carried into the push, stated rather than smoothed

- **`flame-engine` ships no tests.** 7 files, installs and imports, nothing asserts
  it works. Publishing it as-is invites the question "proven by what?". Either
  publish it last, publish it private, or leave it out (`--skip flame-engine`).
- **`nurse_ratchet/psyche/` is committed here although `.gitignore` calls it generated.**
  That is deliberate for the standalone layout — the generator's sources are not in
  this repo — but it means the committed copy is the source of truth until someone
  rebuilds from the monorepo. `publicize.py --check` passes against it.
- **`Project_ELIZA` is excluded.** It does not build (`package directory 'eliza' does
  not exist`, 9 test errors) and its metadata still describes the therapeutic stack
  while its NOTICE says forensic.
- **The monorepo itself remains unpushable** for the reasons in
  `PUBLISH_READINESS_2026-11-02.md`. This take-over publishes the five projects, not
  the monorepo.
