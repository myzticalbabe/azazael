---
name: azazael-powershell-escape
description: Safe PowerShell command patterns from basher/Git Bash — avoid cmdlet escaping, $variable mangling, and parser errors.
metadata:
  category: quality
  project: azazael
---

# Azazael PowerShell Escape — Safe Commands from Git Bash

## Problem

Git Bash (MSYS2) interprets `$`, `{`, `}`, `|`, `%`, and other special characters
BEFORE they reach PowerShell. Complex one-liners fail with parser errors:
```
Unexpected token 'files' in expression or statement.
Missing closing '})' in expression.
Missing closing '}' in statement block or type definition.
```

## The Rule

**For any PowerShell command longer than a simple path query, write to a `.ps1` file.**

## Patterns

### ❌ NEVER — Complex one-liners in basher
```python
# FAILS: $variables, {}, and -f operators get mangled
basher(params={
    command: 'powershell -Command "if (Test-Path $path) { $size = (Get-ChildItem $path | Measure-Object -Property Length -Sum).Sum; Write-Output ($size / 1MB) }"'
})
```

### ✅ ALWAYS — Write to .ps1 temp file
```python
write_file(path="_check.ps1", content="
if (Test-Path 'C:/Users/clint/Desktop') {
    $items = Get-ChildItem 'C:/Users/clint/Desktop' -File
    Write-Output ('Files: ' + $items.Count)
}
")
basher(params={command: "powershell -File _check.ps1 && del _check.ps1"})
```

### ✅ Simple queries — Single command, no variables
```python
# OK: Simple path check without $ variables
basher(params={command: "powershell -Command \"Test-Path 'G:\\'\" 2>&1"})

# OK: Single cmdlet with no interpolation
basher(params={command: "powershell -Command \"Get-ChildItem 'C:\\Users\\clint\\Desktop\\CAIN_panels' -Name\" 2>&1"})
```

### ✅ Alternative — Use Python instead of PowerShell
```python
# Python pathlib is safer and more portable
write_file(path="_check.py", content="
from pathlib import Path
desktop = Path.home() / 'Desktop'
items = list(desktop.glob('*.png'))
print(f'Found {len(items)} PNGs')
")
basher(params={command: "python _check.py && del _check.py"})
```

## Quick Reference

| Do This | Instead of This |
|---------|-----------------|
| Write `.ps1` file, then `powershell -File _tmp.ps1` | Inline `-Command` with `$vars` |
| Use Python pathlib for file ops | PowerShell `Get-ChildItem` |
| Use `cmd.exe //c` for Windows native commands | Direct `cmd.exe` or `robocopy` calls |
| Forward slashes in paths: `C:/Users/...` | Backslashes: `C:\Users\...` |

## Related Skills
- `azazael-error-prevention` — Anti-pattern #1 (nested quotes in basher)
- `azazael-crossplat-fileops` — Cross-platform file operations
- `azazael-startup` — Loads this skill at session start
