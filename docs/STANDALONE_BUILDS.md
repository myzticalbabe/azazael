# STANDALONE BUILDS — .exe Packaging (Python 3.15t; 3.14t retired)

**Created:** June 4, 2026 | **Build Tool:** Nuitka 4.1.2 (3.15t free-threading)
**Interpreter (2026-10-19):** `C:\Azazael\.venvs\py315t\Scripts\python.exe`. Commands below use that pinned path because bare `python` is not production.
**Updated:** June 4, 2026 — Concurrent build + environment alignment

---

## Build System

### Concurrent Build (Windows 11 + WSL2)

```bash
# Build ALL targets on BOTH platforms simultaneously:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --all

# Build specific tier:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --tier neural

# Build single target on specific platform:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --target metacognition --platform windows

# Verify Nuitka patches before building:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --verify

# List registered targets:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --list
```

### Environment Sync (pre-build requirement)

```bash
# Sync Windows 11 → WSL2 before building:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/sync_all.py --sync-to wsl2

# Full sync all environments:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/sync_all.py --sync-all

# Check sync status:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/sync_all.py --status
```

### Nuitka Configuration

| Platform | Python | Nuitka | Status |
|----------|--------|--------|--------|
| Windows 11 | 3.14.6t | 4.1.2 | Verified |
| WSL2 Ubuntu-26.04 | 3.14.6t | 4.1.2 | Verified |

**Patch script:** `docs/scripts/patch_nuitka_315t.py` — run `--verify` before any build.

### Build Strategy

```
Python 3.14t Source → patch_nuitka_315t.py --verify → Nuitka --standalone → .exe
                                                   ├─ Windows 11 (native)
                                                   └─ WSL2 (Linux ELF)
```

Key flags:
- `--standalone` — Bundle all dependencies
- `--assume-yes-for-downloads` — Non-interactive (CI-compatible)
- `--nofollow-import-to=psycopg2` — Exclude PostgreSQL dep
- `--include-package=CORE.WORMS.expansion` — Include worm modules
- `--output-filename=azazael-{name}.exe` — Consistent naming

---

## Worm-Specific Build Targets

### Neural Advancement Suite (5 .exe)

| Worm | Entry Point | .exe Name | Dependencies |
|------|------------|-----------|-------------|
| MetaCognitionWorm | `execute()` | `azazael-metacognition.exe` | CORE.worm_registry, CORE.local_memory |
| EvolutionEngine | `execute()` | `azazael-evolution.exe` | CORE.worm_registry, CORE.local_memory |
| GeneticOptimizer | `optimize()` | `azazael-genetic-optimizer.exe` | EvolutionEngine |
| DreamingModule | `run_dreaming_pipeline()` | `azazael-dreaming.exe` | CORE.local_memory |
| HypnagogicSynthesizer | `synthesize()` | `azazael-hypnagogic.exe` | None |

### Proposed New .exe Targets (7)

| Worm | .exe Name | Priority |
|------|-----------|----------|
| RaceConditionDetector | `azazael-race-detector.exe` | P0 |
| ErrorRecoveryOrchestrator | `azazael-recovery-orchestrator.exe` | P0 |
| SubAgentPoolManager | `azazael-subagent-pool.exe` | P1 |
| SessionStateManager | `azazael-session-state.exe` | P1 |
| CrossWormOptimizer | `azazael-cross-worm-optimizer.exe` | P2 |
| WormCompiler | `azazael-compiler.exe` | P2 |
| DockerOrchestrator | `azazael-docker-orchestrator.exe` | P3 |

### Monitoring Suite (8 .exe)

| Worm | .exe Name |
|------|-----------|
| SYSTEMZ | `azazael-systemz.exe` |
| NETWORXZ | `azazael-networxz.exe` |
| PROCESSZ | `azazael-processz.exe` |
| DISKZ | `azazael-diskz.exe` |
| CLOCKZ | `azazael-clockz.exe` |
| METRICZ | `azazael-metricz.exe` |
| DIAGNOSTIC_WORM | `azazael-diagnostic.exe` |
| NETWORK_DIAG | `azazael-network-diag.exe` |

### Security Suite (5 .exe)

| Worm | .exe Name |
|------|-----------|
| BINARY_ANALYSIS | `azazael-binary-analysis.exe` |
| ERROR_SCAN_WORM | `azazael-error-scan.exe` |
| HEALING_WORM | `azazael-healing.exe` |
| MORPHING_WORM_V2 | `azazael-morphing.exe` |
| REVERSE_TOOLS | `azazael-reverse-tools.exe` |

### Infrastructure Suite (6 .exe)

| Worm | .exe Name |
|------|-----------|
| CLUSTERWORMS | `azazael-clusterworms.exe` |
| METACLUSTER | `azazael-metacluster.exe` |
| WORM_FLEET | `azazael-worm-fleet.exe` |
| CONCURRENCY | `azazael-concurrency.exe` |
| SMARTDISK | `azazael-smartdisk.exe` |
| OS_CONGRUENCY | `azazael-os-congruency.exe` |

### ML/AI Suite (5 .exe)

| Worm | .exe Name |
|------|-----------|
| SYSTEMZ_ML | `azazael-systemz-ml.exe` |
| WORMZ_ML | `azazael-wormz-ml.exe` |
| CAIN_WORM | `azazael-cain.exe` |
| OMNI_WORM_V2 | `azazael-omni.exe` |
| CODEX_TOOLS | `azazael-codex-tools.exe` |

### Expansion Suite (12 .exe)

| Worm | .exe Name |
|------|-----------|
| DatabaseMonitorWorm | `azazael-db-monitor.exe` |
| ScheduledDbMonitorWorm | `azazael-scheduled-db-monitor.exe` |
| BackupWorm | `azazael-backup.exe` |
| ConfigValidator | `azazael-config-validator.exe` |
| ContainerManager | `azazael-container-manager.exe` |
| MigrationEngine | `azazael-migration-engine.exe` |
| CommunicationBus | `azazael-communication-bus.exe` |
| LearningPipeline | `azazael-learning-pipeline.exe` |
| ProfilingEngine | `azazael-profiling-engine.exe` |
| TelemetryCollector | `azazael-telemetry-collector.exe` |
| VisualizationEngine | `azazael-visualization-engine.exe` |
| SecurityAuditor | `azazael-security-auditor.exe` |

---

## Build Commands (per worm)

### Example: MetaCognitionWorm
```bash
"C:/Azazael/.venvs/py315t/Scripts/python.exe" -m nuitka \
    --standalone \
    --output-dir=build/standalone \
    --output-filename=azazael-metacognition.exe \
    --include-package=CORE \
    --include-package=CORE.WORMS.expansion \
    --script=src/CORE/WORMS/expansion/meta_cognition.py
```

### Example: EvolutionEngine
```bash
"C:/Azazael/.venvs/py315t/Scripts/python.exe" -m nuitka \
    --standalone \
    --output-dir=build/standalone \
    --output-filename=azazael-evolution.exe \
    --include-package=CORE \
    --include-package=CORE.WORMS.expansion \
    --script=src/CORE/WORMS/expansion/evolution.py
```

### Batch Build (all 39)
```bash
# Concurrent build across Windows + WSL2:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_concurrent.py --all

# Legacy single-platform build:
"C:/Azazael/.venvs/py315t/Scripts/python.exe" scripts/build_all_standalone.py --targets all --output build/standalone/
```

---

## Environment Alignment

**5 environments must stay in sync:**
1. Windows 11 (`C:\Users\clint\azazael`) — primary dev
2. WSL2 (`/root/azazael`) — Linux build target
3. Desktop (`C:\Users\clint\Desktop\AZAZAEL_Standalone`) — 52 .exe release artifacts
4. G: source-of-truth (`G:\source-of-truth\azazael`) — canonical archive
5. G: AZAZAEL_ROOT (`G:\AZAZAEL\AZAZAEL_ROOT`) — primary archive

See `docs/ENVIRONMENT_ALIGNMENT.md` for full sync procedures.

---

## Known Limitations

1. **Nuitka 3.14t patch required** — Run `docs/scripts/patch_nuitka_315t.py --verify` before building.
2. **Tkinter dependency** — GUI worms require `--enable-plugin=tk-inter`.
3. **SQLite bundling** — Worms using LocalMemoryStore need `sqlite3.dll` bundled.
4. **GPU dependencies** — ML worms (SYSTEMZ_ML, WORMZ_ML) may need CUDA DLLs.
5. **Cross-platform** — .exe builds are Windows-only. WSL2 builds produce Linux ELF binaries.
6. **Package path resolution** — Nuitka resolves packages relative to Python path. Use `sys.path.insert(0, 'src')` in entry scripts or `--include-plugin-directory=src`.
