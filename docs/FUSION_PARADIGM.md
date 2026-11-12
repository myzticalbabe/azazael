# Fusion paradigm: fixed Kali partition -> expanding hybrid (measured 2026-11-12)

## Forensic baseline (every number measured this session)

- Disk 0: C: 810GB NTFS (67.6GB free, 91% full), E: 104GB NTFS fixed
  partition (23.4GB free) holding ONLY `E:\Kali\ext4.vhdx` (104.6GB logical),
  plus unknown partitions 100GB + 5.5GB (likely BM Ubuntu, hands off).
- Kali fs-used 93GB: `/root/azazael-dev` 38GB worktree, `/tmp` 9.3GB,
  `/root/.cache` 5.3GB. Ubuntu fs-used 156GB (VHD 193.6GB on C:):
  `/mnt/g_local_stash` 67GB archives INSIDE the VHD, `/opt/intel` 11GB,
  `/tmp` 4.9GB, `/opt/python315t` 5.7GB.
- G: archive drive 511GB has 10GB free: relocation target is FULL.
- Both VHDX are ALREADY dynamically expanding (sparse). "Fixed" is the E:
  PARTITION walling off 104GB, not the VHD format.
- Neither distro has 3.16t (Kali: 3.14t; Ubuntu: 3.14t/3.15t). Windows prod
  is 3.16t. Fusion runtime = build 3.16t in both distros (staged, long).
- C: fits Kali only after ~95GB freed (Kali needs ~93GB, C: has 67.6GB).

## Options

A. DISSOLVE E: (recommended, staged, confirmation-gated). Slim estates
   (67GB stash dedupe + 38GB stale worktree triage + 25GB tmp/cache/intel),
   compact both VHDXs, move Kali VHDX to C:, delete E:, extend C: +104GB.
   End state: one expanding pool, no fixed wall. Needs 3 staged
   confirmations (slim list, move, partition delete/extend).
B. COMPACT IN PLACE (no partition change). fstrim + Optimize-VHD Full on
   both VHDXs after slimming. Keeps E: wall; buys E: headroom only.
C. INVERT (rejected). Ubuntu VHD 193GB cannot fit E: 104GB. Dead on numbers.
D. INTEROP FUSION (independent of storage, do now). 316t-everywhere +
   `wsl.exe` dispatch + `\\wsl$` mounts; Windows shrinks by uninstalling
   Windows-side dupes absorbed by WSL (catalogued, user confirms each).
E. BM partitions (noted, untouched). 100GB+5.5GB unknown: likely BM Ubuntu.
   No action without BM-lane evidence.

## Decision

D now (tooling in this commit) + A staged (runbook below, gates on user).
B is A's pre-step (compaction runs either way). C rejected. E deferred.

## Staged migration (each step needs one explicit user GO)

1. GO-SLIM: delete-after-verify list (stash dupes vs G:, worktree status,
   intel/tmp/cache). Frees ~100GB+ across both VHDs.
2. GO-COMPACT: `wsl --shutdown`, `Optimize-VHD -Mode Full` both VHDXs,
   re-measure. Expect Kali ~80GB, Ubuntu ~90GB file sizes.
3. GO-MOVE: `wsl --export kali-linux`, `--import` to C:, boot-verify,
   re-point lane config, THEN delete E: VHDX.
4. GO-MERGE: delete E: partition, extend C:. Point of no return.
5. GO-316T: build 3.16t free-threaded in both distros, pin lanes, re-smoke.

## Windows-shrink catalog (winget-measured 2026-11-12, uninstall = user confirms each)

- 3x system Pythons (3.13 MSIX, 3.14.5, 3.14.7) + 3.15.0rc3: superseded by
  .venvs 3.16t prod. Remove after lane pins verified on 3.16t only.
- Node.js 24 LTS (26 available): keep iff Gamora/opencode hooks need it;
  else WSL node absorbs.
- Docker Desktop (Stopped): dead weight unless a lane needs it; WSL-native
  docker absorbs.
- Kali Linux Store stub (OffSec 2026.2.0.0): distro actually runs from
  E:\Kali (custom import). Stub uninstall only AFTER E: migration lands.
- 17 winget rows match python|node|docker|git|ssh|vim surface: full dedupe
  list is a queued lane task, not this commit.

## 316t rollout notes

- Build from source per distro (no 316t wheels stage yet); expect 30+ min
  each on free-threaded flags. Do NOT start unprompted: it wedges the
  box and blocks the lanes. Schedule with a GO like the storage steps.
- Until then: Windows 3.16t = prod, Ubuntu 3.15t = sidecar, Kali 3.14t =
  recon only. Current pins stand.
