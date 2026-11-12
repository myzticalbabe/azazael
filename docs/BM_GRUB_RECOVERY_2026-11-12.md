# BM GRUB RECOVERY — redone 2026-11-12

**Status: staged, needs one elevated run + one reboot.**
Nothing below was executed with privilege from this session: `bcdedit` answers
`Access is denied` here, and the ESP has no drive letter, so the BCD and the
ESP are unreadable and unwritable without elevation. Everything that could be
done unelevated is done; the one remaining step is a human double-click.

## 1. What "again" restores (board rows 48003 / 48007 / 48008, 2026-11-09)

| piece | prior state | source |
|---|---|---|
| Firmware order | Ubuntu `shimx64.efi` leads `{fwbootmgr}` displayorder, timeout 1s | row 48007 |
| ESP layout | p1 (260 MB) holds `Microsoft` + `ubuntu`; p4 (977 MB) EMPTY spare | row 48007 |
| UBUNTU stub | `\EFI\ubuntu\grub.cfg`, 806 B, 3-item menu, live PARTUUID, Win11 chainload, 2 backups beside it | row 48008 |
| BM plan | `/etc/default/grub` menu 10 s + `quiet splash mem_sleep_default=deep`; `40_custom` main + fallback + Win11 chainload; `update-grub`, `grub-install` to `/boot/efi`, `efibootmgr` order; Secure Boot OFF | row 48003 |

## 2. What was re-verified today without elevation

- GPT layout unchanged: p8 = `0fc63daf-…` Linux filesystem 93.88 GiB,
  p9 = `0657fd6d-…` swap 5.16 GiB, p1 + p4 ESPs present, 1.336 MiB unallocated
  (`Get-Partition`, `Get-Disk` — numbers in the 2026-11-12 partition table).
- `mountvol` list: C:, E:, G: mounted; the ESPs/recovery volumes present with
  no mount points (expected).
- No `grub.cfg` backups on C: or E: — the 2 backups live on the ESP itself.
- Engram holds no grub detail (searched); PMB holds the three rows above.

## 3. The redo (you, one UAC approval)

Script: `C:/Azazael/azazael/tools/Redo-GrubRecovery.ps1`
(copy at `E:\Redo-GrubRecovery.ps1` next to the BM instructions).

1. Right-click PowerShell → **Run as administrator**:
   `powershell -ExecutionPolicy Bypass -File E:\Redo-GrubRecovery.ps1 -VerifyOnly`
   - Exit 0 = no drift: reboot straight to the grub menu.
   - Exit 1 = drift listed: re-run without `-VerifyOnly` to repair.
2. Repair run does, in order: ubuntu-first displayorder (only if drifted),
   bootmgr timeout 1 s (only if drifted), finds the ESP holding
   `\EFI\ubuntu\`, rotates `grub.cfg` → `.bak1` → `.bak2`, writes the
   delegate stub (`hd0,gpt8` → p8's own `grub.cfg`, Win11 chainload fallback),
   dismounts the ESP.
3. Reboot → grub menu → Ubuntu on p8. `E:\BM_INSTRUCTIONS.txt` is the BM side.

Design notes: the stub addresses `hd0,gpt8` directly instead of by UUID, so it
cannot go stale the way a PARTUUID string can — the layout it names was
re-measured today. If p8's own `grub.cfg` is ever missing, the Win11 entry
below the `configfile` line is the fallback, so the box always boots something.

## 4. If the menu does not appear

- Firmware boot menu key (ASUS: Esc/F8 at POST) → pick `ubuntu` by hand. If no
  ubuntu entry exists in NVRAM at all, the ESP write did not land — re-run the
  script and read its output; do not edit the ESP by hand.
- Secure Boot must stay OFF for the unsigned 26.04 shim (row 48003).
- The `ext4.vhdx` at `E:\Kali\` (112 GB, written today) is a WSL virtual disk,
  NOT the bare install — do not boot it, do not delete it while WSL uses it.
