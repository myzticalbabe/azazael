#Requires -RunAsAdministrator
<#
.SYNOPSIS
  Re-apply the 2026-11-09 bare-metal boot recovery (freebuff rows 48003/48007/48008).
.DESCRIPTION
  Verifies, and if drifted repairs, the two Windows-side pieces of the dual boot:
   1. Firmware boot order: the Ubuntu shim (shimx64.efi) leads {fwbootmgr}
      displayorder, timeout 1s. (Row 48007: "ubuntu shim ALREADY first".)
   2. The ESP stub \EFI\ubuntu\grub.cfg on p1: delegates to Disk0 partition 8
      (the Ubuntu root, fixed layout verified 2026-11-12), Win11 chainload as
      the fallback entry. Current file is rotated to grub.cfg.bak1/.bak2
      before any write. (Row 48008: "806B live + 2 backups".)
  READ-ONLY BY DEFAULT impression: run with -VerifyOnly to report drift without
  touching the ESP or the BCD. Run without flags to repair (one UAC prompt is
  the whole human cost — the BCD and the ESP both require elevation).
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File Redo-GrubRecovery.ps1 -VerifyOnly
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File Redo-GrubRecovery.ps1
#>
param([switch]$VerifyOnly)

$ErrorActionPreference = 'Stop'
$ESP_GPT = '{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}'
$UBUNTU_STUB = 'EFI\ubuntu\grub.cfg'

function Get-FwEntries {
    # identifier -> description for every {fwbootmgr} displayorder entry
    $raw = bcdedit /enum '{fwbootmgr}' 2>&1 | Out-String
    # NOTE: /enum '{fwbootmgr}' prints displayorder GUIDs BARE (no 'identifier'
    # prefix) -- matching only 'identifier {...}' lines captures {fwbootmgr}
    # itself and nothing else. Take every braced GUID except {fwbootmgr}.
    $order = [regex]::Matches($raw, '\{[0-9a-f\-]{36}\}') |
        ForEach-Object { $_.Value } | Where-Object { $_ -ne '{fwbootmgr}' }
    $descs = @{}
    foreach ($id in ($order | Select-Object -Unique)) {
        $d = bcdedit /enum $id 2>$null | Out-String
        $m = [regex]::Match($d, 'description\s+(.+)')
        if ($m.Success) { $descs[$id] = $m.Groups[1].Value.Trim() }
    }
    return @{ Order = @($order); Descriptions = $descs }
}

function Get-UbuntuFwId($fw) {
    foreach ($id in $fw.Order) {
        if ($fw.Descriptions[$id] -match '(?i)ubuntu') { return $id }
    }
    return $null
}

function Get-EspWithUbuntu {
    # Every ESP on Disk0 (p1 system + p4 spare), mounted one at a time under S:.
    $esps = Get-Partition -DiskNumber 0 |
        Where-Object { $_.GptType -eq $ESP_GPT } |
        Sort-Object PartitionNumber
    foreach ($p in $esps) {
        $volPath = ($p | Get-Volume).Path
        if (-not $volPath) { continue }
        $letter = 'S'
        mountvol "${letter}:" $volPath | Out-Null
        if (Test-Path "${letter}:\$UBUNTU_STUB") {
            # FOUND: stays mounted; the caller dismounts S: when done.
            return @{ Letter = $letter; VolPath = $volPath;
                      Partition = $p.PartitionNumber }
        }
        mountvol "${letter}:" /D | Out-Null
    }
    return $null
}

$drift = @()

# ---- 1. firmware order -------------------------------------------------------
# ESP first: the recreate step below addresses the shim as partition=S:,
# and Get-EspWithUbuntu leaves S: mounted on success (caller dismounts).
$esp = Get-EspWithUbuntu
$fw = Get-FwEntries
$ubuntuId = Get-UbuntuFwId $fw
if (-not $ubuntuId) {
    $drift += 'NO ubuntu firmware entry exists at all (bcdedit /enum firmware shows none)'
    if (-not $VerifyOnly) {
        if (-not $esp) { fail 'cannot recreate ubuntu entry: no ESP holds \\EFI\\ubuntu\\grub.cfg' }
        $copied = (bcdedit /copy '{bootmgr}' /d 'ubuntu' 2>&1 | Out-String)
        if ($copied -notmatch '(\{[0-9a-f\-]+\})') { fail ('bcdedit /copy produced no GUID: ' + $copied) }
        $ubuntuId = $Matches[1]
        bcdedit /set $ubuntuId device partition=S: | Out-Null
        bcdedit /set $ubuntuId path '\EFI\ubuntu\shimx64.efi' | Out-Null
        bcdedit /set '{fwbootmgr}' displayorder $ubuntuId /addfirst | Out-Null
        Write-Host "fixed: recreated ubuntu firmware entry $ubuntuId (shimx64.efi on S:), moved first"
    }
} elseif ($fw.Order.Count -gt 0 -and $fw.Order[0] -ne $ubuntuId) {
    $drift += 'ubuntu shim is NOT first in {fwbootmgr} displayorder'
    if (-not $VerifyOnly) {
        bcdedit /set '{fwbootmgr}' displayorder $ubuntuId /addfirst | Out-Null
        Write-Host "fixed: ubuntu $ubuntuId moved first in displayorder"
    }
} else {
    Write-Host 'ok: ubuntu shim leads {fwbootmgr} displayorder'
}
$timeout = (bcdedit /enum '{bootmgr}' 2>$null | Out-String)
if ($timeout -notmatch 'timeout\s+1\s') {
    $drift += 'bootmgr timeout is not 1s'
    if (-not $VerifyOnly) {
        bcdedit /timeout 1 | Out-Null
        Write-Host 'fixed: bootmgr timeout -> 1s'
    }
} else {
    Write-Host 'ok: bootmgr timeout 1s'
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

# ---- repair the stub (backups first, exactly like 2026-11-09) ----------------
# (S: is still mounted by Get-EspWithUbuntu; dismounted again at the end.)
$S = $esp.Letter + ':'
$live = Join-Path $S $UBUNTU_STUB
$bak1 = $live + '.bak1'
$bak2 = $live + '.bak2'
if (Test-Path $bak1) { Copy-Item $bak1 $bak2 -Force }
Copy-Item $live $bak1 -Force
Write-Host "backed up: $live -> grub.cfg.bak1 (+bak2 rotated)"

$stub = @'
# BM recovery stub — delegates to the Ubuntu root on Disk0 partition 8
# (fixed GPT layout, verified 2026-11-12; p8 = Linux filesystem, p9 = swap).
# Dual-view 2026-11-12: also probes (hd0,gpt2) for the VirtualBox raw-map VM.
# Entries below only appear if p8's own grub.cfg is missing, so this box
# always boots SOMETHING.
insmod part_gpt
insmod ext2
# NATIVE view: p8 is (hd0,gpt8). VM view (raw map of p1+p8 only): p8 shows
# as (hd0,gpt2). The -e guard means a wrong slot simply does not match, so
# one stub serves both (see docs/BM_RUN_BOTH_AT_ONCE_2026-11-12.md).
if [ -e (hd0,gpt8)/boot/grub/grub.cfg ]; then
  set root='hd0,gpt8'
elif [ -e (hd0,gpt2)/boot/grub/grub.cfg ]; then
  set root='hd0,gpt2'
fi
set prefix=($root)'/boot/grub'
configfile $prefix/grub.cfg
menuentry 'Windows 11 (chainload)' {
  insmod part_gpt
  insmod fat
  insmod chain
  set root='hd0,gpt1'
  chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}
'@
Set-Content -Path $live -Value $stub -Encoding Ascii -NoNewline:$false
Write-Host ("wrote {0} ({1} bytes)" -f $live, (Get-Item $live).Length)
mountvol "$S" /D | Out-Null

Write-Host ''
Write-Host 'DONE. Reboot -> grub menu (Ubuntu on p8 first, Windows 11 fallback).'
Write-Host 'On the bare host, run the BM runbook: E:\BM_INSTRUCTIONS.txt'
