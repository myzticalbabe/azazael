# PROJECT_STRUCTURES — Multi-Platform Directory Templates

**Created:** June 4, 2026 | **Platforms:** Windows 11 · WSL2 · Ubuntu 26.04 · Kali Linux

---

## Windows 11 Structure

```
C:\Users\clint\azazael\
├── src/
│   ├── CORE/
│   │   ├── WORMS/           # 88 worm implementations
│   │   │   └── expansion/   # 15 expansion modules
│   │   ├── Agent.py
│   │   ├── agent_registry.py
│   │   ├── worm_registry.py
│   │   ├── local_memory.py
│   │   ├── web_dashboard.py
│   │   └── paths.py
│   ├── ORCHESTRATION/
│   │   ├── HYDRA.py
│   │   ├── HORUS.py
│   │   ├── hydra_bridge.py
│   │   └── ml_platforms/
│   ├── META/
│   │   └── MetaWormSpawner.py  # CurativePool
│   ├── CODEX/
│   ├── HYDRA/
│   └── UTILITIES/
├── tests/
│   ├── test_curative_pool.py
│   └── test_neural_advancement.py  # TO CREATE
├── scripts/
├── skills/
├── docs/
├── MASTER_TASKS.md
├── PLATFORM_DEPLOYMENT.md
├── LESSONS_NEURAL_ADVANCEMENT.md
├── LESSONS_PLATFORM.md
└── MEMORIES_PLATFORM.md

G:\source-of-truth\
├── MANIFEST.json
├── azazael/                   # Windows mirror
├── GOSP/                      # GOSP Rust + Python
├── crates/                    # Future Rust workspace
├── state/
│   ├── windows/
│   ├── wsl/
│   ├── ubuntu/
│   └── kali/
└── models/
```

---

## WSL2 Ubuntu 26.04 Structure

```
/root/azazael/                  # Canonical v1.1.0 (SYNC WITH WINDOWS)
├── src/
│   ├── CORE/
│   ├── ORCHESTRATION/
│   ├── META/
│   ├── CODEX/
│   ├── HYDRA/
│   ├── UTILITIES/
│   ├── AZAZAEL_TOOLKIT/
│   ├── CLI/
│   └── CHANGELOG_GENERATOR.py
├── tests/
├── scripts/
├── docs/
├── config/
├── data/
├── build/
├── output/
├── pyproject.toml              # azazael v1.1.0
└── MEMORY_PROTOCOL.md

/root/workspace/projects/       # 21 sub-projects
├── azazael/                    # Workspace link to /root/azazael/
├── doctoral-thesis-engine/     # GOSP DoctoralThesisEngine
├── gossamer-oxford-parser/     # GOSP Parser
├── eve-unleashed/
├── codex/                      # azazael-codex v2.0.0
├── pams/                       # azazael-pams v1.0.0
├── llama-server/               # azazael-llama-server v1.0.0
├── onnx-runtime/
├── tensorflow/
├── vision-language/
├── graph-vault/
├── performance-monitor/
├── all-into-one/
├── shared/
├── python-3145t/
├── openmono/
├── openmono-igpu/
├── openmono-rust/
├── openmono-go-bridge/
└── open-interpreter/

/home/clint/llama.cpp/          # LLM inference
/home/clint/openmono.ai/        # .NET + LLM solution
```

---

## Bare Metal Ubuntu 26.04 Structure (Target)

```
/home/clint/azazael/            # Primary deployment
├── src/                        # (Synced from canonical)
├── tests/
├── scripts/
├── docs/
├── config/
│   └── azazael.yaml            # Platform-specific config
├── output/                     # Worm output
├── logs/                       # Systemd logs
└── pyproject.toml

/etc/systemd/system/
└── azazael.service             # Daemon service

/mnt/g/                         # NFS/SMB mount for shared state
├── source-of-truth/
└── state/ubuntu/

/opt/models/                    # Local model cache
├── gguf/                       # llama.cpp models
└── onnx/                       # ONNX runtime models
```

---

## Kali Linux Structure (Target)

```
/root/azazael/                  # Security-focused deployment
├── src/                        # (Synced from canonical)
├── tests/
├── scripts/
├── docs/
├── config/
│   └── azazael.yaml            # Kali-specific: security flags
├── output/
│   └── scans/                  # VulnScanner output
├── logs/
└── pyproject.toml

/etc/apparmor.d/
└── usr.bin.python3.14          # AppArmor profile

/etc/ufw/
└── user.rules                  # Firewall: ports 8420, 18080, 8080

/root/tools/                    # Kali security tools
├── vulnscanner -> ../azazael/src/CORE/WORMS/expansion/security.py
├── portauditor -> .../
└── pentest -> .../
```

---

## Sync Strategy

```
Canonical Source
    │
    ├── /root/azazael/ (WSL2) ── Primary development
    │       │
    │       ├── rsync → C:\Users\clint\azazael\ (Windows)
    │       ├── rsync → bare-metal:/home/clint/azazael/
    │       └── rsync → kali:/root/azazael/
    │
    └── G:/source-of-truth/ ── Shared state + CI artifacts
            │
            ├── state/windows/
            ├── state/wsl/
            ├── state/ubuntu/
            └── state/kali/

Sync command:
    rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
        /root/azazael/ /mnt/c/Users/clint/azazael/
```
