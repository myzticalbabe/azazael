# HANDOFF 2026-11-17 — Kali toolset measured into openSUSE, native lane built, four renders verified

**Expiry: 2026-11-19.** Every number below was measured on 2026-11-17. Re-measure
before quoting; board counts, free space and dirty counts move while lanes work.

This is the **Kali-consolidation / render** lane's handoff. The Sarah-vocabulary
lane wrote its own `docs/HANDOFF_2026-11-17.md` earlier the same day; the two are
separate workstreams and neither supersedes the other.

## 1. HEAD

`git log --oneline -1` at write time: **`2136ac50`** *"state(toolset): record the
openSUSE install result - 471 of 473 landed, 2 named gaps"*. The commit that
writes this note is the next one; read it live rather than trusting a SHA pinned
here (a note that pins the SHA of the commit that writes it goes stale on landing).

The two commits this lane added:

- `f6ca4311` — "state(toolset): measure the Kali package closure against openSUSE
  instead of recalling it" — 3 files, 1707 insertions.
- `2136ac50` — "state(toolset): record the openSUSE install result - 471 of 473
  landed, 2 named gaps" — 2 files, 43 insertions, 1 deletion.

The install reading in `2136ac50`'s subject ("471 of 473 landed, 2 named gaps") is
the **zypper pass only**. Both gaps were closed afterwards, outside zypper, and the
corrected reading is in §2 and in the artifact's `gap_closure` block — do not read
that commit subject as the current state.

`git status --porcelain | wc -l` → **44**. That dirt is other lanes' in-flight
work; this lane staged by explicit path only and left all of it untouched.

## 2. Trusted state — each claim with the command that produced it

| claim | command | output line |
|---|---|---|
| The Kali toolset closure is measured, not recalled | `py316t -c "import json; d=json.load(open('state/kali_toolset_inventory_2026-11-17.json')); print(d['kali'])"` | 15 metapackages, 2115 closure packages, 1636 installed, 479 in closure not installed |
| openSUSE's own name universe | same artifact, `d['opensuse']` | 6 enabled repos, **54,503** unique names, source `repodata primary.xml(.gz\|.zst)` |
| Overlap between the two | same artifact, `d['match']` | 522 same-name RPM (24.68% of closure), 1593 without; of installed 473 same-name / 1163 not (28.91%) |
| The install result | same artifact, `d['opensuse_install']` | `requested=473 present_after_install=471 present_now=473 missing=[] total_rpms_after=1840` — 471 is the zypper pass; +2 closed outside it |
| `sslsplit` is installed and runs | `wsl -d openSUSE-Tumbleweed -u root -- /usr/local/sbin/sslsplit -h` | usage text printed; binary 249,456 bytes, links `libssl.so.3`; built from source, `MAKE_RC=0` |
| `wfuzz` is installed and fuzzes | `bash /mnt/c/Azazael/tmp_wfuzz_smoke.sh` against a local `http.server` | `WFUZZ_RC=0`, `Total requests: 2`, found `known` (301) and `absent` (404), target log records both GETs |
| The native build lane holds | `python tools/native_tools.py --doctor` then `--build-all` | `8 of 8 recipes ready`; `all 8 ok`; 9 binaries present (mdk4 in `/usr/local/sbin`, rest `/usr/local/bin`) |
| The bake lane merged with zero drops | `py316t tools/merge_bake_lane.py --lane state/bake_harvest_freebuff_2026-11-17.jsonl --apply` | `BASE=11273 ACCEPTED=40 MERGED=11313 DROPPED=0 SUPERSEDED=0` |
| The harvest lane holds 40 rows | `wc -l state/bake_harvest_freebuff_2026-11-17.jsonl` | `40` (gitignored via `.gitignore:263`) |
| Four renders exist and are well-formed | `ffprobe -show_entries format=duration -show_entries stream=codec_type,codec_name,width,height,r_frame_rate` over each file | every file `h264 1920x1080 30/1` + `aac`, `duration=298.133008` |
| The render payload is on disk | `ls -la C:/Users/clint/Desktop/SCREENSAVER_AUDIO_REACTIVE_WAYS/` | 988,562,161 + 1,041,174,766 + 1,136,260,559 + 2,266,235,920 bytes (5.1 G total) |
| Kali insurance is readable | `ls -la /g/KALI_PAYLOAD.tar /g/kali_recovery_2026-11-12.tar` | 2,791,219,200 and 40,180,070,400 bytes |
| The board has nothing for this lane | `py316t C:/Users/clint/_board.py stats freebuff` | `available 0`, `open 0`, `retired 961` |
| Free space, as of now | `df -h /c /g` | C: 12 G of 756 G (99%); G: 30 G of 477 G (94%) |
| WSL distros | `wsl.exe -l -v` | `openSUSE-Tumbleweed` Stopped (default), `Ubuntu-26.04` Stopped, `kali-linux` Running |

### 2a. The four renders — what each argument changes

Source of truth for all four is one `feat.json` (8944 frames @ 30 fps, 298.13 s).
Full table with per-file sha256 prefixes, laplacian detail and blue-share at a loud
and a quiet timestamp: `C:/Users/clint/Desktop/SCREENSAVER_AUDIO_REACTIVE_WAYS/MANIFEST.md`.

| file | oct | crf | preset | bytes |
|---|---|---|---|---|
| `1_oct3_smooth_crf20.mp4` | 3 | 20 | medium | 988,562,161 |
| `2_oct5_reference_crf20.mp4` | 5 | 20 | medium | 1,041,174,766 |
| `3_oct6_maxdetail_crf20.mp4` | 6 | 20 | medium | 1,136,260,559 |
| `4_oct5_master_crf16_slow.mp4` | 5 | 16 | slow | 2,266,235,920 |

- **oct** is the shader's real input `uOct` and changes the picture: laplacian
  3.898 → 4.768 → 5.619 across oct 3/5/6.
- **crf/preset** change fidelity, not composition: master vs reference differs on
  0.02% of pixels while carrying 2.08× the bytes.
- **Sound reactivity is evidenced per variant**: at t=74.53 s (rms 0.527) all four
  read ~77.5% blue-dominant; at t=173.90 s (rms 0.113) all four fall to ~20% and
  the frame turns warm. No variant is a re-encode of a static clip.
- Recommended delivery master: `4_oct5_master_crf16_slow.mp4`.

## 3. Attempted and failed — read before repeating any of it

- **The destructive half of the consolidation was not performed.** `wsl --unregister
  Ubuntu-26.04` would destroy **747 modified / 162 untracked** files in
  `/root/azazael` (1.8 M untracked) plus a 209 M `/root/BCC-REINVESTIGATION` copy,
  and it frees 102 GB of a disk at 12 G free. That is a decision for the user, not
  a lane default; it is unblocked only by an explicit GO.
- **G: cannot take a 27 G `/root` tar as-is.** 30 G free of 477 G. Either compress
  first and verify it fits, or the unregister waits.
- **`sslsplit` has no *installable* Tumbleweed RPM** — **closed 2026-11-17**, keep
  the route: `nothing provides 'libcrypto.so.1.1()(64bit)'`, and
  `zypper search --provides --match-exact` finds no provider anywhere. Fixed by
  building from source against OpenSSL 3 with one compat macro for the removed
  `ERR_GET_FUNC`; `/usr/local/sbin/sslsplit` exists (249,456 bytes) and `-h` prints
  usage. Do not re-chase the RPM: it is `0.5.5-2.63` in the `security` repo and
  cannot install on OpenSSL 3.
- **`wfuzz` cannot run on 3.16t unpatched** — **closed 2026-11-17**, and the chain
  is four deep: PyPI 2.4.5 imports `collections.MutableMapping` (removed in 3.10)
  and pins `pycurl<=7.43`; pip >= 24.1 also rejects 3.1.0's metadata; `pkg_resources`
  is gone from setuptools 84.2.1; `imp` was removed in 3.12 and `cgi` in 3.13. Fixed
  with the hand-unpacked pure-Python 3.1.0 wheel, an `imp` -> `importlib.util`
  patch, `legacy-cgi`, and `setuptools<81` (80.10.2). The broken 2.4.5 stub is
  **preserved** at `/usr/local/bin/wfuzz-2.4.5.stub`, not deleted.
- **`ffprobe --count_frames` over four 8944-frame files timed out at 180 s.** The
  frame counts in `MANIFEST.md` come from the render run's own probe; the
  container-level probe (`format=duration` + stream shape) is the cheap re-check
  and it agrees on all four.
- **WSL boundary traps, each of which cost a cycle**: `nohup … &` inside
  `wsl … bash -lc` dies with the session (run long work host-side); MSYS rewrites
  `/usr/local/bin` → `C:/Program Files/Git/usr/local/bin` (use
  `MSYS_NO_PATHCONV=1`); shell variables, pipes and `%{NAME}` format strings get
  re-parsed through `wsl.exe` (put logic in a script file on `/mnt/c`); a `\n`
  inside `--qf` collapsed 1840 names to one line (`total_rpms=1`).
- **Windows text-mode writes produce CRLF.** zypper read `libhandy-1-0\r` and
  answered "not found in package names" for all 473 until lists were written in
  binary mode and passed through `tr -d '\r'`.
- **Tumbleweed metadata is `primary.xml.zst`** and `zstd` was missing; installed via
  `zypper -n in -y zstd`. A killed zypper also leaves a stale `/var/run/zypp.pid`
  that must be cleared.

## 4. Queue — claim it, do not remember it

```bash
py316t C:/Users/clint/_board.py claim freebuff 10
```

| item | state |
|---|---|
| freebuff board | `available 0`, `open 0` — `claim` printed `NO OPEN TASKS` |
| unregister `Ubuntu-26.04` | **blocked on user GO** (destructive; see §3) |
| `sslsplit`, `wfuzz` | **closed 2026-11-17** — both installed and smoke-run; evidence in §2 and in the artifact's `gap_closure` block |
| 1593 closure packages with no same-name RPM | not attempted; many are Kali-only or renamed, and the native lane covered the ones that mattered |
| graphify labels | stale after rebuilds — LLM work behind `tools/graphify_label_safe.py --probe-only`, deliberately not run |

## 5. First commands for the next session

```bash
py316t C:/Azazael/azazael/tools/mcp_startup_gate.py --fix     # exit 0, every line [PASS]
# then the MCP tool supervisor__verdict                        # expect GO
py316t C:/Users/clint/_board.py stats freebuff                 # quote this, never §4
df -h /c /g                                                    # free space moves
```

If `supervisor__verdict` is unavailable, print `VERDICT UNAVAILABLE: <error>` as
the first line and do memory work only.

## 6. Expiry

**2026-11-19.** After that date re-measure every count in §2 — free space, board
counts, dirty count, RPM totals — before quoting it. §2a is a property of files on
disk and stays true while their sizes and durations match; §3 is structural until
the named packages or the WSL image change.
