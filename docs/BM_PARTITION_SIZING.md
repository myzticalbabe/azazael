# BM production partition sizing (measured 2026-11-12)

## Disk 0 (1TB NVMe, GPT, zero unallocated)

| Part | Size | Free | Contents |
|---|---|---|---|
| P3 C: | 755GB NTFS | 87.6GB | Windows, models 7.2GB, repos, VHDX hosts |
| P7 E: | 97GB NTFS | 49.4GB | Kali ext4.vhdx (~47GB physical, 1TB sparse), grub tools |
| P8 | 100.8GB Unknown | ? | BM native Linux (fixed partition; interior unmeasured from here) |
| P9 | 5.5GB Unknown | ? | almost certainly BM swap |
| misc | ~3GB | — | EFI/system/recovery ×4 |

G: is a 512GB USB stick at 10GB free — not a migration target.

## Estate sizes (live `du`, ext4 used)

WSL Kali 41G: /usr 29G (tool packages — the supersede estate), /root
6.1G (go 1.4, osint-tools 1.0, azazael mirror 0.5, venvs, BCC 0.4),
/var 4.8G (lib 2.7, log 1.2 prunable, cache 0.9), /opt 0.8G.

WSL Ubuntu ~71G: /usr 28G, /root 27G (operator worktree: BCC, AOA,
EveUnleashed, venvs, logs, cleave archives), /home 8.4G (AI histories),
/opt 5.7G, /var 2.2G.

## What migrates onto production BM

1. Tool layer ~30G (one native Kali superseded set, not both distros').
2. Live operator data ~15–20G AFTER archive triage (the 27G /root holds
   cleave archives, old logs, monster chat dirs already flagged for G:).
3. Model A-I-O set ~9G (chat 2.8 + embed 0.2 + Eve 4.1 + ollama 0.6 + HF 1.6).
4. Repos + one worktree ~10–15G (azazael + live worktree, not all history).
5. OS + swap + growth headroom ~25G.

Floor: 90G (tight, repeats today's squeeze). Comfortable: 150–180G.

## Enlarge recipe (P8 100.8G → ~180G)

No unallocated space exists, so the 80G must come from neighbors: shrink
C: by ~50G (leaves ~37G free — above the 10G backup floor but the new
minimum to watch) and E: by ~30G (leaves ~19G free; VHDX is sparse so
physical stays ~47G). Then extend P8 into the freed extent. All moves
happen Windows-side or from a live USB with P8 unmounted; snapshot the
VHDX + manifest first; expect grub re-repair (Redo-GrubRecovery.ps1 is
already on E:). P9 swap: keep, or fold into a swapfile and reclaim 5.5G.

## Open: P8 interior

The fixed partition's contents cannot be read from Windows (Unknown
type). Re-derive at first BM boot with the bm_capture kit
(tools/bm_capture: probe_tree + probe_pip + probe_env) before finalizing
the number — if P8 already holds a 60G native toolset, the 80G extension
covers growth; if it holds a bare install, 50G from C: alone suffices.
