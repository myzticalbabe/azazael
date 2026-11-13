# Run Windows + bare-metal Ubuntu AT THE SAME TIME
Date: 2026-11-12. Box: Windows 11 Home (no Hyper-V), Disk0 internal SSD,
p1 = ESP, p8 = Ubuntu root 93.88 GiB, p9 = swap. Secure Boot already OFF.

## The idea (one sentence)
Windows keeps running as the host; the PHYSICAL Ubuntu partition (p8) boots
inside a VirtualBox VM window from the real disk -- no reboot, no copy, both
alive. Rebooting is never required to switch.

## Why VirtualBox (not Hyper-V, not a copy)
- Win11 Home has no Hyper-V. Hyper-V raw-disk needs the WHOLE disk offline,
  impossible on the boot disk anyway.
- VirtualBox maps SINGLE partitions (p1 + p8 only), leaving C: untouched.
- WSL `--mount` gives file access only, not a running Ubuntu. A copy of p8
  is a second machine to maintain -- the point here is ONE Ubuntu.

## HARD RULES (break one = corrupt p8)
1. NEVER boot p8 natively while the VM is open. One owner at a time.
2. Disable Windows Fast Startup (Control Panel > Power > lid/buttons) and
   never hibernate/sleep EITHER side while the VM runs.
3. NO snapshots on the raw disk (VirtualBox: VM Settings > uncheck/live Guru
   warns you -- raw VMDKs can't snapshot; keep it that way).
4. Shut the VM down FULLY (power off inside Ubuntu) before any native boot.
5. First native boot after VM use may run fsck -- let it finish.

## Setup, step by step
1. Install VirtualBox 7.x for Windows hosts (admin). Defaults are fine.
   Download Super Grub2 Disk ISO (supergrubdisk.org) to E:\ (boot helper,
   used in step 5).
2. Confirm the disk (admin cmd -- READ ONLY):
   diskpart > list disk   (Disk0 = internal SSD, ~953 GB Samsung -- match size)
   > list partition  (expect 10 partitions; p1 System/260MB, p8 ~93.9GB)
   > exit
3. Create the raw-partition VMDK (admin cmd, ONE line):
   "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" internalcommands
   createrawvmdk -filename "E:\BM-p8.vmdk" -rawdisk \\.\PhysicalDrive0
   -partitions 1,8
   This maps ONLY the ESP (p1) and Ubuntu root (p8). C: is not mapped and
   cannot be touched by the VM. The .vmdk is 2 KB -- it holds pointers, no data.
4. New VM: Type Linux, Version Ubuntu (64-bit), 4096 MB RAM, 2 CPUs,
   attach E:\BM-p8.vmdk as SATA port 0, attach the Super Grub2 ISO as IDE.
   System > Motherboard: CHECK "Enable EFI (special OSes only)".
   Network: NAT (first boot), Audio: off.
5. Start the VM from the ISO: Super Grub2 > Detect and show boot methods >
   pick the Ubuntu entry on the ~93 GB disk. Log in. (Why the ISO: the VM
   sees only 2 partitions so p8 looks like (hd0,gpt2), and VirtualBox EFI
   defaults to EFI/BOOT/bootx64.efi -- the ISO sidesteps both on day one.)
6. Make VM boots ISO-free (inside the VM's Ubuntu, once):
   sudo mkdir -p /boot/efi/EFI/BOOT
   sudo cp /boot/efi/EFI/ubuntu/grubx64.efi /boot/efi/EFI/BOOT/bootx64.efi
   sudo cp /boot/efi/EFI/ubuntu/grub.cfg   /boot/efi/EFI/BOOT/grub.cfg
   The ESP stub was rewritten 2026-11-12 to probe (hd0,gpt8) THEN (hd0,gpt2),
   so this same grub.cfg boots the native view AND the VM view. Native boot
   is untouched (NVRAM still points at \EFI\ubuntu\shimx64.efi).
7. Detach the ISO (VM Settings > Storage > remove disk), snapshots stay OFF.
   Normal use from here: start VM = Ubuntu window beside Windows.

## What changes inside Ubuntu (first VM boot only, automatic)
- New virtual NIC -> new DHCP lease; interface name may differ (enp0s3).
  Netplan/systemd handles it; static IPs set on bare metal will NOT apply.
- Disk appears as /dev/sda (UUIDs identical, so /etc/fstab mounts right).
- p9 swap is NOT mapped -> VM runs swapless. Add a swapfile later if
  needed (fallocate -l 4G /swapfile ...), it lives on p8, harmless native.
- First native boot afterwards: possible fsck + "new hardware" one-time
  settle. Normal.

## Zero-risk alternative (files only, no VM)
Admin PowerShell, read-only:
  wsl --mount \\.\PHYSICALDRIVE0 --partition 8 --type ext4 --options ro
Read p8 at /mnt/wsl/PHYSICALDRIVE0p8 from any WSL distro. Read-only = it
cannot corrupt anything. Release with: wsl --unmount \\.\PHYSICALDRIVE0

## Reversed setup (BM host + Windows-in-VM): OUT OF SCOPE
Needs KVM, IOMMU groups, GPU passthrough and Windows reactivation on
virtual hardware. Documented as not-worth-it for this box.

## Undo (back to pure dual boot)
Power off VM > delete VM in VirtualBox > delete E:\BM-p8.vmdk (2 KB of
pointers, zero user data) > optionally delete the EFI/BOOT fallback files
from step 6. Native grub menu, entries and timeout are exactly as left by
the 2026-11-12 recovery (ubuntu first, timeout 1s).

## If the VM cannot see the disk
- VBoxManage "access denied": rerun that ONE command from an ADMIN prompt.
- Windows mounted the ESP (S:) during recovery and never released it:
  admin cmd > mountvol S: /D > retry. (Redo-GrubRecovery.ps1 dismounts on
  success; a crashed run can leak it.)
- p8 locked: WSL --mount still holding it > wsl --unmount first.
