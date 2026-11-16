#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Re-apply the 2026-11-09 bare-metal boot recovery (freebuff rows 48003/48007/48008),
  corrected 2026-11-13: the 11-12 version cloned {bootmgr} (a Windows Boot Manager
  object) and parked the phantom FIRST, demoting the real Ubuntu Firmware
  Application to second with a 1s timeout.
.DESCRIPTION
  Verifies, and if drifted repairs, the two Windows-side pieces of the dual boot:
   1. Firmware boot order: the REAL Ubuntu Firmware Application entry
      (header 'Firmware Application', path \EFI\ubuntu\shimx64.efi) leads
      {fwbootmgr} displayorder, timeout 5s. Any BCD-cloned 'Windows Boot
      Manager' object with an ubuntu description (e.g. {b7173bf3...}) is a
      phantom: deleted, never trusted, never recreated.
   2. The ESP stub \EFI\ubuntu\grub.cfg on p1: search-based probe (native
      hd0,gpt8 view + raw-map hd0,gpt2 VM view), Win11 chainload fallback.
      Current file is rotated to grub.cfg.bak1/.bak2 before any write.
  Run with -VerifyOnly to report drift without touching the BCD or the ESP
  (mounts the ESP read-only to check the stub, then dismounts). Run without
  flags to repair (one UAC prompt; BCD + ESP both require elevation).
  NEVER auto-creates a firmware entry from {bootmgr}: if no real Ubuntu
  Firmware Application exists, repair stops with efibootmgr instructions.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File Redo-GrubRecovery.ps1 -VerifyOnly
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File Redo-GrubRecovery.ps1
#>
param([switch]$VerifyOnly)

$ErrorActionPreference = 'Stop'
$ESP_GPT = '{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}'
$UBUNTU_STUB = 'EFI\ubuntu\grub.cfg'
$TIMEOUT_S = 5

function fail([string]$Message) {
    try { mountvol 'S:' /D 2>$null | Out-Null } catch {}
    throw $Message
}

function Get-FwEntries {
    $raw = bcdedit /enum '{fwbootmgr}' 2>&1 | Out-String
    $order = [regex]::Matches($raw, '\{[0-9a-f\-]{36}\}') |
        ForEach-Object { $_.Value } | Where-Object { $_ -ne '{fwbootmgr}' }
    $descs = @{}
    $headers = @{}
    foreach ($id in ($order | Select-Object -Unique)) {
        $d = bcdedit /enum $id 2>$null | Out-String
        $m = [regex]::Match($d, 'description\s+(.+)')
        if ($m.Success) { $descs[$id] = $m.Groups[1].Value.Trim() }
        $h = ($d -split "`r?`n" | Where-Object { $_.Trim() -ne '' } | Select-Object -First 1)
        if ($h) { $headers[$id] = $h.Trim() }
    }
    return @{ Order = @($order); Descriptions = $descs; Headers = $headers }
}

function Get-RealUbuntuFwId($fw) {
    foreach ($id in $fw.Order) {
        $hdr = $fw.Headers[$id]
        $desc = $fw.Descriptions[$id]
        if ($desc -match '(?i)^ubuntu$' -and $hdr -match 'Firmware Application') { return $id }
    }
    return $null
}

function Get-PhantomUbuntuIds($fw) {
    $out = @()
    foreach ($id in $fw.Order) {
        $hdr = $fw.Headers[$id]
        $desc = $fw.Descriptions[$id]
        if ($desc -match '(?i)^ubuntu$' -and $hdr -notmatch 'Firmware Application') {
            $out += $id
        }
    }
    return $out
}

function Get-EspWithUbuntu {
    if (Get-PSDrive -Name S -ErrorAction SilentlyContinue) {
        fail 'drive S: is already in use (a previous run may have leaked its ESP mount). Run: mountvol S: /D  then re-run.'
    }
    $esps = Get-Partition -DiskNumber 0 |
        Where-Object { $_.GptType -eq $ESP_GPT } |
        Sort-Object PartitionNumber
    foreach ($p in $esps) {
        $volPath = ($p | Get-Volume).Path
        if (-not $volPath) { continue }
        $letter = 'S'
        mountvol "${letter}:" $volPath | Out-Null
        if (Test-Path "${letter}:\$UBUNTU_STUB") {
            return @{ Letter = $letter; VolPath = $volPath;
                      Partition = $p.PartitionNumber }
        }
        mountvol "${letter}:" /D | Out-Null
    }
    return $null
}

$drift = @()

# ---- 1. firmware order -------------------------------------------------------
$esp = Get-EspWithUbuntu
$fw = Get-FwEntries
$realId = Get-RealUbuntuFwId $fw
$phantoms = @(Get-PhantomUbuntuIds $fw)

foreach ($ph in $phantoms) {
    $drift += "PHANTOM ubuntu BCD entry $ph is type '$($fw.Headers[$ph])', not a Firmware Application (BCD-only, firmware never boots it)"
    if (-not $VerifyOnly) {
        bcdedit /delete $ph | Out-Null
        Write-Host "fixed: deleted phantom ubuntu BCD entry $ph"
    }
}
if ($phantoms.Count -gt 0) {
    $fw = Get-FwEntries
    $realId = Get-RealUbuntuFwId $fw
}

if (-not $realId) {
    $drift += 'NO real Ubuntu Firmware Application entry exists (will NOT clone {bootmgr}: recreate from Linux via efibootmgr, or firmware setup, then re-run)'
    if (-not $VerifyOnly) {
        Write-Host 'repair blocked: refusing to fabricate a firmware entry from {bootmgr}.'
        Write-Host 'from Ubuntu live media: efibootmgr -c -d /dev/nvme0n1 -p 1 -L ubuntu -l \EFI\ubuntu\shimx64.efi'
    }
} elseif ($fw.Order.Count -gt 0 -and $fw.Order[0] -ne $realId) {
    $drift += 'real Ubuntu Firmware Application entry is NOT first in {fwbootmgr} displayorder'
    if (-not $VerifyOnly) {
        bcdedit /set '{fwbootmgr}' displayorder $realId /addfirst | Out-Null
        Write-Host "fixed: real ubuntu $realId moved first in displayorder"
    }
} else {
    Write-Host 'ok: real Ubuntu Firmware Application entry leads {fwbootmgr} displayorder'
}

# ---- timeouts (both menus need an intervention window) -----------------------
$fwTimeout = $null
$m1 = [regex]::Match((bcdedit /enum '{fwbootmgr}' 2>$null | Out-String), 'timeout\s+(\d+)')
if ($m1.Success) { $fwTimeout = [int]$m1.Groups[1].Value }
$bootTimeout = $null
$m2 = [regex]::Match((bcdedit /enum '{bootmgr}' 2>$null | Out-String), 'timeout\s+(\d+)')
if ($m2.Success) { $bootTimeout = [int]$m2.Groups[1].Value }
if ($fwTimeout -ne $TIMEOUT_S) {
    $drift += "fwbootmgr timeout is ${fwTimeout}s, want ${TIMEOUT_S}s"
    if (-not $VerifyOnly) {
        bcdedit /set '{fwbootmgr}' timeout $TIMEOUT_S | Out-Null
        Write-Host "fixed: fwbootmgr timeout -> ${TIMEOUT_S}s"
    }
} else {
    Write-Host "ok: fwbootmgr timeout ${TIMEOUT_S}s"
}
if ($bootTimeout -ne $TIMEOUT_S) {
    $drift += "bootmgr timeout is ${bootTimeout}s, want ${TIMEOUT_S}s"
    if (-not $VerifyOnly) {
        bcdedit /timeout $TIMEOUT_S | Out-Null
        Write-Host "fixed: bootmgr timeout -> ${TIMEOUT_S}s"
    }
} else {
    Write-Host "ok: bootmgr timeout ${TIMEOUT_S}s"
}

# ---- 2. ESP stub --------------------------------------------------------------
if (-not $esp) {
    $drift += 'NO ESP on Disk0 holds \EFI\ubuntu\grub.cfg (checked every ESP partition)'
    if (-not $VerifyOnly) {
        Write-Host 'repair needs a target: mount the Ubuntu ESP and re-run'
    }
} else {
    Write-Host ("ok: \EFI\ubuntu\grub.cfg lives on ESP partition p{0} ({1})" -f
        $esp.Partition, $esp.VolPath)
}

if ($VerifyOnly -or -not $esp) {
    Write-Host ''
    if ($drift.Count -eq 0) { Write-Host 'VERIFY: no drift. Reboot lands on the grub menu.' }
    else { Write-Host 'VERIFY: drift found:'; $drift | ForEach-Object { Write-Host "  - $_" } }
    if ($esp) { mountvol 'S:' /D | Out-Null }
    if ($drift.Count -gt 0) { exit 1 } else { exit 0 }
}

# ---- repair the stub (backups first) ------------------------------------------
try {
    $S = $esp.Letter + ':'
    $live = Join-Path $S $UBUNTU_STUB
    if (-not (Test-Path $live)) { fail "ESP stub vanished mid-run: $live" }
    $bak1 = $live + '.bak1'
    $bak2 = $live + '.bak2'
    if (Test-Path $bak1) { Copy-Item $bak1 $bak2 -Force }
    Copy-Item $live $bak1 -Force
    if (-not (Test-Path $bak1)) { fail 'backup failed: grub.cfg.bak1 not written' }
    Write-Host "backed up: $live -> grub.cfg.bak1 (+bak2 rotated)"

    $stub = @'
# BM recovery stub - delegates to the Ubuntu root on Disk0 partition 8
# (fixed GPT layout, verified 2026-11-12; p8 = Linux filesystem, p9 = swap).
# Dual-view 2026-11-12: native p8 is (hd0,gpt8); VirtualBox raw map of p1+p8
# shows p8 as (hd0,gpt2). search --file finds whichever view is live; if no
# view carries p8 grub.cfg the menu below still boots Windows.
insmod part_gpt
insmod ext2
insmod search
set root=''
search --no-floppy --file /boot/grub/grub.cfg --hint='hd0,gpt8' --set=root
if [ -z "$root" ]; then
  search --no-floppy --file /boot/grub/grub.cfg --hint='hd0,gpt2' --set=root
fi
if [ -n "$root" ]; then
  set prefix=($root)/boot/grub
  configfile $prefix/grub.cfg
fi
menuentry 'Windows 11 (chainload)' {
  insmod part_gpt
  insmod fat
  insmod chain
  set root='hd0,gpt1'
  chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}
'@
    Set-Content -Path $live -Value $stub -Encoding Ascii -NoNewline:$false
    $len = (Get-Item $live).Length
    if ($len -lt 100) { fail "write looks truncated: $live is ${len} bytes" }
    Write-Host ("wrote {0} ({1} bytes)" -f $live, $len)
}
finally {
    mountvol "$S" /D | Out-Null
}

Write-Host ''
Write-Host 'DONE. Reboot -> grub menu (Ubuntu on p8 first, Windows 11 fallback).'
Write-Host 'On the bare host, run the BM runbook: E:\BM_INSTRUCTIONS.txt'
