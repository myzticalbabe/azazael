# Tool Categories & Groupings

> Inventory of every tool in the ecosystem, grouped by function.
> Updated August 23, 2026.

## Legend
- **INSTALLED** — present on this system (binaries, CLIs, or cloned source)
- **STAGED** — callable skill generated, tool install pending
- **MISSING** — not installed
- Skill prefixes: `azazael-pkg-*` (Kali 3.13 packages), `azazael-pkg314t-*` (3.14t packages — RETIRED 2026-10-19, archived), `azazael-bin-*` (binary tools)

---

## 1. Reconnaissance & Attack Surface (9 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| nmap | INSTALLED | azazael-bin-nmap | Network discovery, port scanning, service/OS detection |
| nuclei | INSTALLED | azazael-bin-nuclei | Template-based vulnerability scanning (ProjectDiscovery) |
| subfinder | INSTALLED | azazael-bin-subfinder | Passive subdomain enumeration |
| amass | INSTALLED | azazael-bin-amass | OWASP attack-surface mapping |
| dnsx | INSTALLED | azazael-bin-dnsx | Fast DNS resolution / record enumeration |
| naabu | INSTALLED | azazael-bin-naabu | Fast port scanner (ProjectDiscovery) |
| httpx-pd | INSTALLED | azazael-bin-httpx | HTTP probing, tech detection (Go binary, avoids Python httpx clash) |
| katana | INSTALLED | azazael-bin-katana | Crawler / spider (ProjectDiscovery) |
| dnsrecon | STAGED | azazael-pkg-dnsrecon | DNS enumeration (Python) |

## 2. Web Application Testing & Fuzzing (5 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| sqlmap | INSTALLED | azazael-bin-sqlmap | Automated SQL injection & DB takeover |
| ffuf | INSTALLED | azazael-bin-ffuf | Fast web fuzzer (dirs, vhosts, params) |
| gobuster | INSTALLED | azazael-bin-gobuster | Directory / DNS subdomain brute-force |
| feroxbuster | INSTALLED | azazael-bin-feroxbuster | Recursive content discovery |
| nuclei (web templates) | INSTALLED | azazael-bin-nuclei | HTTP exposure scanning (see §1) |

## 3. Credential Cracking (2 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| hashcat | INSTALLED | azazael-bin-hashcat | GPU-accelerated hash cracking (300+ modes) |
| john | INSTALLED | azazael-bin-john | John the Ripper, offline password cracking |

## 4. Secret Detection & Code Security (2 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| gitleaks | INSTALLED | azazael-bin-gitleaks | Scan git repos for leaked secrets |
| trufflehog | INSTALLED | azazael-bin-trufflehog | Credential discovery across repos/files/APIs |

## 5. Traffic Interception & Proxying (1 tool)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| mitmproxy | INSTALLED | azazael-bin-mitmproxy | Interactive HTTPS MITM proxy (fixed: 3.13 shebang) |

## 6. OSINT — Username & Social (6 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| sherlock | INSTALLED | azazael-bin-sherlock | Username search across social platforms |
| maigret | INSTALLED | azazael-bin-maigret | Username OSINT across 3,000+ sites |
| social-analyzer | INSTALLED (clone) | azazael-bin-social-analyzer | Social media analysis + web UI |
| osintgram | INSTALLED (clone) | azazael-bin-osintgram | Instagram OSINT via public API |
| ghunt | INSTALLED (clone) | azazael-bin-ghunt | Google account OSINT (cookie-based) |
| phoneinfoga | INSTALLED | azazael-bin-phoneinfoga | Phone number OSINT & footprinting |

## 7. OSINT — Domain, Email & Correlation (3 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| theHarvester | INSTALLED | azazael-bin-theharvester | Email/subdomain/hostname enumeration |
| spiderfoot | INSTALLED | azazael-bin-spiderfoot | Automated OSINT correlation, 200+ sources |
| Moriarty-Project | INSTALLED (clone) | — | OSINT collection framework |

## 8. AI / ML — Local Inference (5 tools)

| Tool | Status | Skill | Purpose |
|------|--------|-------|---------|
| ollama | INSTALLED (WSL + Windows) | azazael-bin-ollama | Local LLM serving — **GPU-accelerated on Intel Arc 140T via Vulkan** (27/27 & 17/17 layers offloaded) |
| llama.cpp | MISSING (needs cmake) | azazael-bin-llama-cpp | GGUF inference engine (llama-cli / llama-server) |
| open-webui | MISSING | azazael-bin-open-webui | Self-hosted chat web UI |
| vllm | MISSING (CPU-only box) | azazael-bin-vllm | High-throughput serving (PagedAttention) |
| sglang | MISSING (CPU-only box) | azazael-bin-sglang | Fast LLM/VLM serving framework |

## 9. OSINT / Analysis Packages (Python, Kali 3.13 — `azazael-pkg-*`)

Key highlights of the 968 package skills:
- **Recon**: shodan, censys, dnsrecon, dnspython, recon-ng
- **OSINT**: theHarvester (pkg), sherlock (pkg), socialscan, holehe, twint, instaloader
- **Exploitation**: impacket, netexec (nxc), metasploit libs, paramiko, pwntools
- **Forensics**: volatility3, capstone, pefile, pycryptodome
- **Network**: scapy, pyshark, requests, aiohttp
- **Crypto**: cryptography, pycryptodome, gmpy2
- **Stubs**: ~300 `types-*` typing stubs

## 10. Azazael / 3.14t Environment Packages (`azazael-pkg314t-*`, 74 skills)

| Group | Tools |
|-------|-------|
| Core Azazael | azazael-core 3.1.0, torbot 4.3.0 |
| Build/Dev | mypy, pyright, nuitka, autoflake, ruff, pytest, wheel, setuptools |
| ML | numpy, scipy, scikit-learn, pandas, torch (CPU), transformers, onnx |
| AI tooling | yt-dlp, openai, anthropic, tiktoken |
| Runtime | psutil, gevent, uvloop, orjson, httpx |

## 11. Project Core Skills (132, category-grouped)

- **architecture (22)** — clusters, registry, worms*, paths, files, separation, state-machine, parallel, dual-ledger
- **system (11)** — system-startup, direct-memory, mandates, sop, pre-action-gate, sentinel-gate, verifiable-truth, compliance-orchestrator, toolkit, orchestration
- **process (14)** — error-prevention, inference-protocol, ml-platforms, sync-patterns, tools, utilities, catalog-maintenance, shims, dedup
- **devtools (8)** — devtools-index, console, elements, network, performance, sources, coverage, audit
- **codex (7)** — codex, cain-pipeline, cain-template, neural-architecture, neural-pipeline, training-pipeline
- **workflow (6)** — startup, environment, eleven-followups, operating-protocols, parallel-execution
- **fixes (6)** — fix-python-314t, fix-gitbash-paths, fix-file-operations, fix-data-recording, error-index
- **quality (5)** — audit-infrastructure, error-resolution, session-recording, crossplat-fileops
- **planning (4)** — deploy, production, desktop-projects, full-wiring
- **conventions (4)** — conventions, git, mermaid, threading
- **algorithm (4)** — autodiff-forward/backprop/higher-order/gradient
- **environment (3)** — azazael_314t_master/optimum, azazael_insights
- **infrastructure (2)** — secrets-manager, sync-wsl
- **misc (remaining)** — testing, mypy, pyright, autoflake, exe-build, pams-memory, compliance-infrastructure, algorithmic-respawn

---

## Summary

| Group | Count |
|-------|-------|
| Recon & attack surface | 9 |
| Web testing & fuzzing | 5 |
| Credential cracking | 2 |
| Secret detection | 2 |
| Traffic interception | 1 |
| OSINT username/social | 6 |
| OSINT domain/email/correlation | 3 |
| AI/ML local inference | 5 |
| Kali package skills | 968 |
| 3.14t package skills | 74 |
| Core project skills | 132 |
| **Total tools/skills** | **1,207** |

## Remaining installs (AI/ML, CPU-bound)

- llama.cpp — needs cmake (missing on system)
- open-webui — pip installable
- vllm / sglang — GPU-oriented; CPU-only hardware makes them low priority
