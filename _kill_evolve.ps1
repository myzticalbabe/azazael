$targets = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*run_evolution_n*' -or $_.CommandLine -like '*evolution_cycle*' }
if (-not $targets) {
    Write-Output "none running"
    exit 0
}
foreach ($t in $targets) {
    Write-Output ("stopping pid=" + $t.ProcessId)
    try { Stop-Process -Id $t.ProcessId -Force -ErrorAction Stop } catch {
        Write-Output ("  failed: " + $_.Exception.Message)
    }
}
Start-Sleep -Seconds 2
$left = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*run_evolution_n*' -or $_.CommandLine -like '*evolution_cycle*' }
Write-Output ("remaining=" + @($left).Count)
