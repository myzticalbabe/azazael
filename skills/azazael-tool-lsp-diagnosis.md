---
name: azazael-tool-lsp-diagnosis
description: lsp_diagnosis — LSP/language-server diagnostics for editor tooling. Use when hover/completion breaks or a language server fails to attach.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: false
---
# lsp_diagnosis

Location: `src/SCRIPTS/lsp_diagnosis.py`

## When to use
- Diagnose LSP attach failures or stale language-server state.
- Pair with COMPREHENSIVE_FIX (LSP repair) when editor tooling misbehaves.

## How to run
```
python src/SCRIPTS/lsp_diagnosis.py
```

## Notes
- Capability worm: `LspDiagnosisWorm` (TOOLBELTZ).
