# BM BASEMENT RUNBOOK — read this on the bare host

**You are on bare metal when `cat /proc/version` says Linux and does NOT say
`microsoft`.** WSL says `microsoft`; this runbook is not for WSL.

## 0. Prove the host (2 minutes, decides everything after)

```
lsblk -f                          # expect sda/nvme p8 ext4 mounted on /, p9 swap
cat /proc/version                 # must NOT contain "microsoft"
efibootmgr -v                     # ubuntu entry exists; note the BootOrder
mokutil --sb-state                # expect "SecureBoot disabled"
lspci -k | grep -A3 -i xe         # expect kernel driver bound (no force_probe)
ls /dev/accel/accel0 2>&1         # expect it exists
ls /mnt /media                    # look for the E: NTFS volume (exFAT/NTFS "Kali")
```

If E: is visible, mount it and copy these instructions home — this file also
lives at `E:\BM_INSTRUCTIONS.txt` on the Windows side:
`sudo mkdir -p /mnt/e && sudo mount -t ntfs3 /dev/<E-partition> /mnt/e`
(find `<E-partition>` in the `lsblk -f` output: 96.9 GiB NTFS, label "Kali").

Record the p8 filesystem UUID now — it is the value future grub stubs need:
`lsblk -f` → UUID of the p8 ext4 volume. Write it here: `P8_UUID=________`.

## 1. Restore grub from the BM side (so the menu survives Windows Update)

```
sudo nano /etc/default/grub
#   GRUB_TIMEOUT_STYLE=menu
#   GRUB_TIMEOUT=10
#   GRUB_CMDLINE_LINUX_DEFAULT="quiet splash mem_sleep_default=deep"
sudo nano /etc/grub.d/40_custom
#   main entry (Ubuntu on p8) + fallback entry + Win11 chainload entry
#   (chainload: insmod part_gpt fat chain; set root='hd0,gpt1';
#    chainloader /EFI/Microsoft/Boot/bootmgfw.efi)
sudo update-grub
sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi \
  --bootloader-id=ubuntu --recheck
sudo efibootmgr -o <ubuntu-num>,<windows-num>   # ubuntu first, from efibootmgr -v
```

Reboot once and confirm the menu appears with Ubuntu first, Windows available.

## 2. Bring up the dev stack (Wave 5 of the conformity roadmap)

```
git clone https://github.com/myzticalbabe/azazael ~/azazael   # ~1.1 GiB pack
cd ~/azazael && git checkout azazael-intel-ultra-9-evo
```

**Python 3.16t** (free-threaded — the ONLY interpreter this stack runs on):
```
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev libncurses-dev libffi-dev liblzma-dev
# build CPython 3.16 from source with --disable-gil, then:
python3.16 -m venv ~/.venvs/py316t
~/.venvs/py316t/bin/python -c "import sys; print(sys._is_gil_enabled())"
# must print False. Anything else is not the native interpreter — stop here.
```

**Engram** (the MCP memory server; the tree carries the Windows `.exe` only):
```
GOOS=linux GOARCH=amd64 go build -o ~/bin/engram <engram-source>
# blocker if the engram source is not at hand — do not substitute the exe
```

**Secrets** (never in a repo): create `~/.pmb/daemon.token` and a `0600` env
file carrying the pmb bearer token + provider API keys; point every unit at it
with `EnvironmentFile=`.

**Systemd units** (`~/.config/systemd/user/`, then
`systemctl --user daemon-reload && enable --now` each): pmb daemon (`:8765`),
floor proxy (`:8766`, started after the daemon, `Restart=always`), pams
launcher, supervisor, `krampus_mcp.py`. Order matters: proxy waits on daemon
(`PMB_UPSTREAM_WAIT=30`, same as the Windows logon wiring).

## 3. Prove it (the run that closes the loop)

```
~/azazael/tools/mcp_startup_gate.py            # expect PASS=9, WARN=1 at most
~/azazael/tools/krampus_conformance.py         # expect PASS, 3 lanes, 0 gaps
~/.venvs/py316t/bin/python tools/krampus_mcp.py --selftest   # 15 tools, 0 problems
```

Then the one reading Windows can never produce — run the metal probe and
confirm `is_bare_kernel: true`:
`krampus_metal_probe(all)` → `via` names a real path (local/ssh/vsock),
**not** `none-bare (confined to virtual kernel)`.
Record the full outputs; a claim without its command is a recollection.

## 4. Report back

`pathfinder SOIL=bare-metal-linux` (row 48003's words): post the gate line,
the conformance line, and the metal_probe line to the board. If anything in
§0 fails (no accel0, SecureBoot enabled, p8 UUID missing), stop and report
that instead — do not build the stack on a host that has not proven itself.
