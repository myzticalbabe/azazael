# Skill Gap Analysis — August 23, 2026

> Systematic audit of all 1,203 skills (1,174 canonical + 29 staged bin) for gaps,
> plus web-researched newer open-source capabilities to fill them.

## Audit method

1. **Structural audit** — frontmatter validity, name==filename, category/description presence, EXECUTE/Notes section presence (1,203 skills)
2. **Binary existence check** — every CLI token in EXECUTE blocks resolved via `which` + Python import fallback (746 skills with CLI refs)
3. **Python import check** — package modules importable in the declared interpreter (428 sampled)
4. **Coverage check** — all installed security/OSINT binaries on the system cross-referenced against skill coverage (418 candidates scanned)

## Structural findings

| Check | Result |
|-------|--------|
| Skills structurally clean | **1,190 / 1,203** |
| Legacy-format skills (no YAML) | 10 without category marker (codex-studio, codex-video, curative, eve-unleashed, mypy-fix-patterns, packaging, python3.14-ml, standalone-audit, standalone, sync-kali) |
| Filename≠frontmatter (pre-existing legacy) | 3 (`azazael_314t_master`, `azazael_314t_optimum`, `azazael_insights_2026-05-28`) |

## Binary gap check — skills referencing missing binaries

### Category 1: Broken reference in skill (install pending) — 5 skills
| Skill | Missing binary | Status |
|-------|---------------|--------|
| azazael-bin-llama-cpp | llama-cli, llama-server | needs cmake |
| azazael-bin-open-webui | open-webui | pip installable |
| azazael-bin-vllm | vllm | GPU-oriented, CPU-only box |
| azazael-bin-social-analyzer | social-analyzer (CLI wrapper) | cloned at /root/osint-tools, no bin symlink |
| azazael-bin-ollama | (resolved — see GPU work) | ✅ GPU-accelerated on Intel Arc |

### Category 2: Installed binaries with NO skill at all — highest-value gap
The Kali box has **~20 major tools installed with zero callable skills**:

| Tool | Purpose | Priority |
|------|---------|----------|
| masscan | Internet-scale port scanning | HIGH |
| rustscan | Ultra-fast port scanner (Rust) | HIGH |
| trivy | Container/fs/iac vulnerability scanner | HIGH |
| syft | SBOM generation | HIGH |
| tshark | Wireshark CLI packet analysis | HIGH |
| snort | IDS/IPS | HIGH |
| bettercap | MITM framework | MED |
| responder | LLMNR/NBT-NS/mDNS poisoning | MED |
| hydra | Online password cracking | MED |
| nikto | Web server scanner | MED |
| dirb / dirbuster | Web directory brute-force | MED |
| exiftool | Metadata extraction (OSINT) | HIGH |
| foremost | File carving / recovery | MED |
| seclists | Wordlists (data, not binary) | MED |
| wpscan | WordPress scanner | MED |
| joomscan | Joomla scanner | LOW |
| kerberoast / rubeus | AD attacks | LOW (impacket covers) |
| massdns | DNS brute-force | LOW |
| altdns / subjack / gospider / hakrawler / waybackurls / arjun / paramspider / dnsgen | Recon suite (already in pkg skills? check) | MED |
| tookie-osint | AI-powered OSINT agent (found in research) | MED |

### Category 3: Import-only gaps (module installed, CLI missing) — 20 skills, OK by design
e.g. crackmapexec→cme importable, dotenv, tldextract, ulid, faker, typer, wheel, xattr — these are Python-API skills; verified importable. **No action.**

### Category 4: Real import failures — 5
- `azazael-pkg-distorm3` — `import distorm3` fails on 3.13 (not installed? distorm3 ships via pypi; check)
- `azazael-pkg-ghp-import` — malformed doc (description text parsed as import)
- `azazael-pkg-google` — `protobuf` import fails (google package needs protobuf dep)
- `azazael-pkg-xdg` — `pyxdg` module name mismatch (real module is `xdg`)

---

## Web research — newer open-source capabilities (2026 landscape)

### OSINT additions worth installing
| Project | What it adds | Install |
|---------|-------------|---------|
| **tookie-osint** | AI-powered OSINT agent w/ MCP + CLI (already on system!) | present |
| **blackbird** | Username search across 100+ sites (Sherlock/Maigret alternative) | pip |
| **h8mail** | Email breach OSINT | pip |
| **socialscan** | Checks email/username availability (already pkg skill) | ✅ covered |
| **whatsmyname** | Universal username enumeration | pip |
| **PhoneInfoga 2.x** | Already installed ✅ | present |
| **SpiderFoot** | Already installed ✅ | present |

### AI/ML additions (self-hosted, 2026)
| Project | What it adds | Notes |
|---------|-------------|-------|
| **ollama 0.32+** | Local LLM serving | ✅ GPU-accelerated on Arc 140T |
| **llama.cpp** | GGUF inference engine | needs cmake |
| **Open WebUI** | Chat UI for Ollama | pip |
| **LangGraph** | Agent orchestration framework | pip (CPU OK) |
| **Mem0** | AI memory layer | pip |
| **vLLM / SGLang** | High-throughput serving | GPU-only, low priority on CPU box |
| **CrewAI / AutoGen / OpenClaw** | Agent frameworks (100k+ stars) | CPU OK |

### Security tooling additions
| Project | What it adds | Notes |
|---------|-------------|-------|
| **semgrep** | SAST (best open-source per 2026 reviews) | pip |
| **bandit** | Python SAST | pip |
| **grype** | Container vuln scanning (Anchore) | binary |
| **falco** | Runtime security | container-centric |
| **kube-bench** | K8s CIS benchmarks | container-centric |
| **wazuh** | Full SIEM/XDR | heavy, server |
| **zeek** | Network analysis framework | apt |
| **suricata** | High-perf IDS/IPS | apt |
| **malcolm** | Network traffic analysis (PCAP) | docker |

### Media forensics additions (fits CODEX/CAIN work)
| Project | What it adds | Notes |
|---------|-------------|-------|
| **ffmpeg** | THE critical missing dependency (codex, cain-pipeline, cain-video reference it but NOT installed!) | apt — CRITICAL |
| **quevidkit** | Forensic video tampering analysis toolkit | git |
| **Audiopsy** | Forensic audio analysis | git |
| **exiftool** | Metadata extraction (installed, no skill) | binary |

### Password cracking additions
| Project | What it adds | Notes |
|---------|-------------|-------|
| **Name-That-Hash** | Hash type identification (nicer than hashid) | pip |
| **SecLists** | Wordlists (installed? verify) | apt/data |

---

## Priority action list

1. **CRITICAL: Install ffmpeg** — 3 core skills (codex, cain-pipeline, cain-video) reference it; it's absent. `apt install ffmpeg`
2. **HIGH: Generate skills for installed-but-uncovered binaries** — masscan, trivy, syft, tshark, snort, bettercap, responder, hydra, nikto, dirb, exiftool, foremost, seclists, wpscan (→ `azazael-bin-*` staged)
3. **MED: Fix 10 legacy skills missing category marker** — add `metadata: category:` block
4. **MED: Install remaining AI/ML** — cmake + llama.cpp, open-webui, semgrep, bandit, grype
5. **LOW: Install OSINT additions** — blackbird, h8mail, whatsmyname, Name-That-Hash
6. **LOW: Fix 5 import failures** — distorm3, ghp-import doc, google/protobuf, xdg→pyxdg naming
