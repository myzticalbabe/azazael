# PATH FORWARD — Roadmap: Pure Python & Desktop Standalone

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project; production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m`. Statements below describe the state on the date of this record — in particular, "Python 3.14t already installed as default `python`" is no longer true.

> *Generated: June 2, 2026*
> *Phase: Post-Codebase-Audit Planning*
> *Horizon: Q3-Q4 2026*

---

## EXECUTIVE SUMMARY

The AZAZAEL ecosystem spans **4 active projects**, **4 partially-operational projects**, and **3 deprecated projects** across Windows 11 and WSL2. The core framework (`azazael/`) contains 45+ modules and 76 worms. Desktop apps include 51 Nuitka-built EXEs. This roadmap defines the path to:

1. **Pure Python excellence** — Production-grade testing, error handling, documentation
2. **Desktop standalone maturity** — Cross-platform, auto-updating, unified launcher
3. **Integration** — WSL bridge, memory sync, VL pipeline unification

---

## PHASE 1: PURE PYTHON FOUNDATION (Weeks 1-4)

### Week 1: Testing Infrastructure
| Task | Effort | Dependencies |
|------|--------|-------------|
| Create `tests/` directories in all projects | 1h | None |
| Write `conftest.py` with shared fixtures | 2h | None |
| Add pytest-cov to `pyproject.toml` | 30m | None |
| Write unit tests for `circuit_breaker.py` | 3h | None |
| Write unit tests for `local_memory.py` | 2h | None |
| Create GitHub Actions CI config | 1h | None |

### Week 2: Error Handling & Resilience
| Task | Effort | Dependencies |
|------|--------|-------------|
| Centralized retry with exponential backoff | 4h | Week 1 tests |
| Dead letter queue implementation | 3h | Week 1 tests |
| Structured JSON logging (logging.conf) | 2h | None |
| Graceful degradation in all Vault endpoints | 3h | None |
| Circuit breaker integration with HTTP calls | 2h | Week 1 tests |

### Week 3: Type Hints & Documentation
| Task | Effort | Dependencies |
|------|--------|-------------|
| Type-hint `CORE/*.py` (45 modules) | 8h | None |
| Type-hint `CORE/WORMS/*.py` (76 worms) | 12h | None |
| Add JSDoc to Vault `index.html` | 2h | None |
| Generate API reference from docstrings | 1h | None |
| Create architecture diagrams (Mermaid) | 3h | None |
| Write user guide | 4h | Week 3 docs |

### Week 4: Performance & Configuration
| Task | Effort | Dependencies |
|------|--------|-------------|
| Centralized YAML config system | 4h | None |
| Profile Vault graph loading | 2h | None |
| Optimize Vault search caching | 2h | Profile results |
| WORM execution optimization | 4h | Config system |
| Benchmark suite creation | 2h | None |

---

## PHASE 2: DESKTOP STANDALONE MATURITY (Weeks 5-8)

### Week 5: Vault Enhancements
| Task | Effort | Dependencies |
|------|--------|-------------|
| Visual diff improvements (inline/side-by-side) | 4h | None |
| Keyboard shortcuts (Ctrl+S, Ctrl+F, Escape, Arrows) | 2h | None |
| Settings panel (UI preferences) | 3h | None |
| Tab persistence across sessions | 2h | Settings panel |
| Graph layout presets | 2h | None |

### Week 6: Nuitka & Cross-Platform
| Task | Effort | Dependencies |
|------|--------|-------------|
| Verify Nuitka with Python 3.14 free-threading | 4h | Python 3.14t installed |
| Rebuild all 51 EXEs with optimizations | 8h | Nuitka verification |
| Linux build pipeline (WSL2) | 4h | Week 6 builds |
| macOS build pipeline (cross-compile) | 4h | Linux pipeline |
| Test all EXEs on clean Windows 11 | 4h | Rebuilds |

### Week 7: Unified Launcher
| Task | Effort | Dependencies |
|------|--------|-------------|
| Design single-entry-point launcher | 2h | None |
| Implement launcher with subprocess management | 4h | Design |
| Add service discovery (port scanning) | 3h | Launcher |
| System tray integration | 4h | Launcher |
| Startup-on-boot option | 2h | System tray |

### Week 8: Auto-Updater & MSI Installer
| Task | Effort | Dependencies |
|------|--------|-------------|
| Version manifest system | 2h | None |
| GitHub Releases integration | 3h | Manifest |
| Delta update mechanism | 4h | Version system |
| MSI/InnoSetup installer creation | 4h | Launcher |
| Installer testing on clean VM | 2h | Installer |

---

## PHASE 3: INTEGRATION & VL UNIFICATION (Weeks 9-12)

### Week 9: WSL Bridge
| Task | Effort | Dependencies |
|------|--------|-------------|
| WSL2 file system watcher | 3h | None |
| Bidirectional file sync | 4h | Watcher |
| WSL process management from Windows | 3h | None |
| Cross-platform clipboard sharing | 2h | None |

### Week 10: Memory Sync
| Task | Effort | Dependencies |
|------|--------|-------------|
| Cross-project memory store synchronization | 4h | None |
| PAMS → LocalMemory bridge | 3h | None |
| Unified search across all memory stores | 3h | Sync |
| Memory deduplication | 2h | Sync |

### Week 11: VL Pipeline Unification
| Task | Effort | Dependencies |
|------|--------|-------------|
| Unified VL inference interface | 4h | None |
| Model registry service | 3h | Unified interface |
| Batch inference pipeline | 4h | Model registry |
| Result caching layer | 2h | Pipeline |

### Week 12: Polish & Release
| Task | Effort | Dependencies |
|------|--------|-------------|
| End-to-end integration testing | 4h | All of Phase 3 |
| Performance benchmarking | 2h | Integration tests |
| Documentation final review | 3h | All docs |
| Release v4.0.0 | 1h | Everything above |
| Blog/announcement | 2h | Release |

---

## RESOURCE REQUIREMENTS

### Tools
| Tool | Purpose | Status |
|------|---------|--------|
| pytest + pytest-cov | Testing | ❌ Need install |
| mypy | Type checking | ❌ Need install |
| Nuitka | EXE building | ✅ Installed (Python 3.14t, patched via patch_nuitka_314t.py) |
| InnoSetup/NSIS | Windows installer | ❌ Need install |
| GitHub Actions | CI/CD | ✅ Repository exists |
| Python 3.14t | Free-threading | ✅ Already installed (default `python`) |

### Python 3.14 Free-Threading Setup (already done)
```bash
# Verify (may need to reinstall psutil for cp314t wheel)
pip install --force-reinstall --no-deps psutil

# Verify
python -c "import sys; print(sys.version); print('Free-threaded:', not sys._is_gil_enabled())"
# Expected: 3.14.5 ... Free-threaded: True

# Apply Nuitka 3.14t patches
python azazael/docs/scripts/patch_nuitka_314t.py --apply

# Test rebuild of simple module
python -m nuitka --standalone --onefile vault_server.py
```

---

## RISK ASSESSMENT

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Python 3.14t compatibility issues | High | Medium | Test early, run patch_nuitka_314t.py before builds |
| Nuitka build failures | Medium | Medium | Incremental rebuild strategy |
| WSL2 cross-platform issues | Medium | Low | Container-based testing |
| MSI installer complexity | Low | Medium | NSIS as simpler alternative |
| Scope creep | Medium | High | Strict phase gating |

---

## SUCCESS METRICS

| Metric | Current | Target (v4.0) |
|--------|---------|---------------|
| Test coverage | 0% | >80% |
| Type hint coverage | ~50% | >90% |
| Documentation coverage | ~60% | >95% |
| Crash recovery | ❌ None | ✅ Auto-recover |
| Startup time | ~5s | <2s |
| EXE count verified working | 51 | 51+ (all tested) |
| Cross-platform | Windows only | Windows + WSL2 |
| Install/uninstall | Manual | MSI installer |

---

## APPENDIX: QUICK-START COMMANDS

```bash
# === Phase 1: Testing ===
cd ~/azazael
pip install pytest pytest-cov mypy
pytest tests/ --cov=CORE --cov-report=html

# === Phase 1: Type checking ===
mypy src/CORE --strict

# === Phase 2: Nuitka rebuild ===
cd ~/Desktop/AZAZAEL_Standalone
python3.14t -m nuitka --standalone --onefile --python-flag=free-threading vault_server.py

# === Phase 3: Integration ===
# WSL bridge test
wsl bash -c "echo 'WSL ready'"

# Memory sync test
python -c "from CORE.local_memory import get_memory_store; ms = get_memory_store(); print(ms.recall_recent(5))"
```

---

*Roadmap generated by AZAZAEL Codebuff — v4.0.0 target*
