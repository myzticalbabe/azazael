# AZAZAEL — Multi-Platform Deployment TODO (3.14t-era title; production is 3.15t)

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project;
> production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only
> sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Deployment
> commands below describe the 2026-06 state.

**Created:** June 4, 2026 | **Version:** 1.0.0
**Scope:** Windows 11 · WSL2 Ubuntu 26.04 · Bare Metal Ubuntu 26.04 · Kali Linux

---

## Platform Matrix

| Platform | Status | Python | Free-Threading | Worms | G: Drive | CI |
|----------|--------|--------|---------------|-------|----------|-----|
| **Windows 11** | 🟢 Active | 3.14.5t | ✅ GIL-disabled | 88 | ✅ Mounted | 🟡 Partial |
| **WSL2 Ubuntu 26.04** | 🟡 Explored | 3.14.5 | ✅ Native | ? | ✅ /mnt/g/ | 🔴 None |
| **Bare Metal Ubuntu 26.04** | 🔴 Not started | — | — | — | 🔴 NFS/SMB | 🔴 None |
| **Kali Linux** | 🔴 Not started | — | — | — | 🔴 NFS/SMB | 🔴 None |

---

## Platform-Specific TODOs

### 🔴 Windows 11 (Current Primary)

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Complete Lessons 1-10 from MASTER_TASKS.md | P1 | 🟡 5/10 done | Lessons 6-10 remaining |
| Run full worm discovery (88 worms) | P1 | 🟢 Done | 88 worms, 17 categories |
| CurativePool tests (37/37) | P1 | 🟢 Done | tests/test_curative_pool.py |
| Neural advancement tests | P1 | 🔴 None | tests/test_neural_advancement.py |
| HydraBridge integration test | P1 | 🔴 None | tests/test_hydra_bridge.py |
| GOSP CI pipeline | P2 | 🟡 Created | Never executed |
| Nuitka standalone .exe builds | P2 | 🔴 None | azazael-standalone skill |
| Sync with WSL canonical | P0 | 🔴 Not started | /root/azazael/ is canonical v1.1.0 |
| Rust toolchain (cargo workspace) | P3 | 🔴 Not started | G:/source-of-truth/crates/ |

### 🟡 WSL2 Ubuntu 26.04 (Canonical Source)

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Audit /root/azazael/src/ vs Windows src/ | P0 | 🔴 Not synced | WSL has v1.1.0, Windows has latest |
| Install Rust toolchain | P2 | 🔴 Missing | No rustc/cargo |
| Set up CI for WSL | P2 | 🔴 None | GitHub Actions WSL runner |
| Build llama.cpp | P2 | 🔴 Not built | GGUF models present, build dir empty |
| Verify worm count matches | P0 | 🔴 Unknown | 88 on Windows, ? on WSL |
| Run test suite | P1 | 🔴 Not run | Python 3.14.5 available |
| Mount G: drive for shared state | P1 | 🟢 Done | /mnt/g/ accessible |
| 21 workspace projects | P2 | 🟡 Present | Needs audit for compatibility |
| doctoral-thesis-engine | P0 | 🔴 Unexplored | GOSP codebase may be here |
| gossamer-oxford-parser | P0 | 🔴 Unexplored | GOSP parser may be here |

### 🔴 Bare Metal Ubuntu 26.04

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Install Python 3.14.5t | P0 | 🔴 Not started | DeadSnakes PPA or compile from source |
| Clone azazael from G: drive or git | P0 | 🔴 Not started | Need git remote or rsync |
| Mount G: drive (NFS/SMB) | P0 | 🔴 Not started | smbclient or NFS mount |
| Install system deps (numpy, torch, tkinter) | P1 | 🔴 Not started | apt-get build-deps |
| Set up Rust toolchain | P2 | 🔴 Not started | rustup default stable |
| Configure free-threading | P0 | 🔴 Not started | --disable-gil compile flag |
| Set up CI (GitHub Actions bare-metal runner) | P2 | 🔴 Not started | Self-hosted runner |
| Performance benchmarking | P3 | 🔴 Not started | Native vs WSL2 vs Windows |
| Systemd service for AZAZAEL daemon | P3 | 🔴 Not started | /etc/systemd/system/azazael.service |
| Network accessibility (PAMS, llama-server) | P1 | 🔴 Not started | Firewall rules, port forwarding |

### 🔴 Kali Linux

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Install Python 3.14.5t | P0 | 🔴 Not started | Kali rolling, may need source compile |
| Clone azazael | P0 | 🔴 Not started | git clone or rsync |
| Security audit of worm execution | P0 | 🔴 Not started | Kali's security tooling advantage |
| Mount G: drive (NFS/SMB) | P1 | 🔴 Not started | smbclient mount |
| Penetration testing worms | P2 | 🔴 Not started | VulnScanner, PortAuditor, FirewallAudit |
| Network analysis worms | P2 | 🔴 Not started | NETWORXZ, PacketCapture |
| Forensic analysis integration | P3 | 🔴 Not started | Autopsy, Volatility integration |
| Set up CI | P3 | 🔴 Not started | Optional |

---

## Shared Infrastructure TODOs

### Git & Version Control

| Task | Priority | Status |
|------|----------|--------|
| Establish canonical git remote (GitHub/GitLab) | P0 | 🔴 |
| Branch strategy: main (stable), develop (WIP), platform/* branches | P1 | 🔴 |
| .gitattributes for Windows/Linux line endings | P1 | 🔴 |
| Pre-commit hooks: py_compile, worm discovery, test suite | P2 | 🔴 |

### G: Drive as Source of Truth

| Task | Priority | Status |
|------|----------|--------|
| MANIFEST.json tracks all platform deployments | P1 | 🟡 Created |
| Per-platform state directories (G:/state/windows/, G:/state/wsl/, etc.) | P1 | 🔴 |
| Shared model registry (G:/models/) | P2 | 🔴 |
| Shared worm output directory (G:/output/) | P2 | 🔴 |
| CI artifacts stored on G: drive | P2 | 🟡 Partial |

### Cross-Platform Path Resolution

| Task | Priority | Status |
|------|----------|--------|
| `get_project_root()` works on all platforms | P0 | 🟡 Windows only |
| `get_g_drive()` resolves on all platforms | P0 | 🟡 Windows + WSL2 |
| Path separators: use pathlib.Path exclusively | P1 | 🔴 |
| Line endings: .gitattributes text=auto | P2 | 🔴 |
| Case sensitivity: Linux is case-sensitive, Windows is not | P0 | 🟡 Known |

### Cross-Platform CI/CD

| Task | Priority | Status |
|------|----------|--------|
| GitHub Actions matrix: windows-latest, ubuntu-26.04, kali-latest | P2 | 🔴 |
| Nightly worm discovery + test suite on all platforms | P2 | 🔴 |
| G: drive health check (daily) | P1 | 🟡 Created |
| Cross-platform Nuitka builds | P3 | 🔴 |
| Docker-based CI for consistency | P3 | 🔴 |

---

## Migration Plan

### Phase 1: Stabilize Windows (Current)
- Complete Lessons 1-10
- All 88 worms tested
- CurativePool + neural advancements validated

### Phase 2: Sync WSL2 (Week 1-2)
- Compare /root/azazael/ (v1.1.0) with Windows (latest)
- Merge divergent changes
- Run full test suite on WSL
- Establish WSL as canonical development environment

### Phase 3: Bare Metal Ubuntu (Week 2-4)
- Install Python 3.14.5t from source (--disable-gil)
- Clone from synced WSL repository
- Performance benchmark vs WSL2 vs Windows
- Systemd service for daemon mode

### Phase 4: Kali Linux (Week 4-6)
- Install Python 3.14.5t
- Clone from canonical repository
- Security-focused worm execution
- Penetration testing integration

---

## Success Criteria Per Platform

### Windows 11
- [ ] 88 worms discovered in <10s
- [ ] 37/37 CurativePool tests passing
- [ ] All neural advancements functional
- [ ] HydraBridge v2.0.0 pipeline runs end-to-end
- [ ] Nuitka .exe builds for all standalone tools

### WSL2 Ubuntu 26.04
- [ ] 88 worms discovered in <5s (Linux FS perf advantage)
- [ ] Test suite passes identically to Windows
- [ ] llama.cpp built and serving models
- [ ] G: drive accessible for shared state

### Bare Metal Ubuntu 26.04
- [ ] Python 3.14.5t free-threading confirmed
- [ ] 88 worms discovered, all tests pass
- [ ] Performance benchmarks show native Linux advantage
- [ ] Systemd service auto-starts AZAZAEL

### Kali Linux
- [ ] 88 worms discovered
- [ ] Security worms (VulnScanner, PortAuditor, FirewallAudit) validated
- [ ] Network analysis worms functional
- [ ] Penetration testing integration demonstrated
