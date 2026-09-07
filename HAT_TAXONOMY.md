# Tool Codification — White Hat / Red Hat / Cerulean Hat (Blue)

Rule: every tool is deemed White Hat or Red Hat below, or it SHALL BE
Cerulean Hat (Blue) by default. No other designations are used in this file.

Surveyed 2026-09-06 on this workstation (Windows 11, Intel Arc 140T).
Statuses: PRESENT + USED, PRESENT idle, ABSENT.

## WHITE HAT (defensive, compliance, constructive, audit)
| Tool | Status | Role in this investigation |
|------|--------|----------------------------|
| graphify 0.9.55 | PRESENT + USED | Knowledge-graph extraction over 84-file corpus; graph.json (39 nodes/16 edges/23 communities) + report built |
| harvester.py (Qwen2.5-1.5B) | PRESENT + USED | 114/114 file summaries banked, real case numbers recovered |
| research_analyzer.py | PRESENT + USED | Deep-analysis passes (shallow on 1.5B, pipeline proven) |
| DirectMemory | PRESENT + USED | Canonical session/audit ledger; all findings banked + verified |
| PAMS / friday-memory :21434 | PRESENT idle | Cross-session memory + FTS search surface |
| llama-server (Jan b9967 Vulkan) | PRESENT + USED | Local GPU inference; served gemma/Qwen runs |
| git + compliance scanner hook | PRESENT + USED | 6 reconciling commits; gate baselined to WARNING+ (proven both directions) |
| curl.exe | PRESENT + USED | Endpoint verification for every server brought up |
| sqlite3 / DB tooling | PRESENT + USED | DirectMemory forensics, vacuum (1233->923 MB, lossless PASS), session sweeper (10,928 closed) |
| EFAST 5500Search (public) | USED (procedure) | Retrieval memo written: EIN path, no login, Schedule C drilldown |
| RTK process (PA) | USED (draft) | CAP-dispositions request drafted + HELD, unsent |

### Kali audit arsenal — deemed WHITE HAT (authorized use)
Hat follows authorization and intent, not the binary. All PRESENT in the
kali-linux WSL2 distro (verified: full sweep + path checks); skill docs may
exist for some. No action executed here.
| Tool | Status | Role under authorization |
|------|--------|---------------------------|
| nmap | White Hat — PRESENT (Kali WSL) | Port/service discovery |
| naabu | White Hat — PRESENT (Kali WSL) | Port/service discovery |
| rustscan | White Hat — PRESENT (Kali WSL) | Port/service discovery |
| masscan | White Hat — PRESENT (Kali WSL) | Port/service discovery |
| nuclei | White Hat — PRESENT (Kali WSL) | Vulnerability scanning |
| nikto | White Hat — PRESENT (Kali WSL) | Vulnerability scanning |
| wpscan | White Hat — PRESENT (Kali WSL) | Vulnerability scanning |
| wapiti3 | White Hat — PRESENT (Kali WSL) | Vulnerability scanning |
| ffuf | White Hat — PRESENT (Kali WSL) | Content discovery / fuzzing |
| gobuster | White Hat — PRESENT (Kali WSL) | Content discovery / fuzzing |
| feroxbuster | White Hat — PRESENT (Kali WSL) | Content discovery / fuzzing |
| dirb | White Hat — PRESENT (Kali WSL) | Content discovery / fuzzing |
| dnsx | White Hat — PRESENT (Kali WSL) | DNS/subdomain enumeration |
| subfinder | White Hat — PRESENT (Kali WSL) | DNS/subdomain enumeration |
| amass | White Hat — PRESENT (Kali WSL) | DNS/subdomain enumeration |
| dnsgen | White Hat — PRESENT (Kali WSL) | DNS/subdomain enumeration |
| theHarvester | White Hat — PRESENT (Kali WSL) | OSINT: emails, usernames, breach data |
| sherlock | White Hat — PRESENT (Kali WSL) | OSINT: emails, usernames, breach data |
| maigret | White Hat — PRESENT (Kali WSL) | OSINT: emails, usernames, breach data |
| phoneinfoga | White Hat — PRESENT (Kali WSL) | OSINT: phone numbers |
| holehe | White Hat — PRESENT (Kali WSL) | OSINT: account/breach checks |
| h8mail | White Hat — PRESENT (Kali WSL) | OSINT: account/breach checks |
| trufflehog | White Hat — PRESENT (Kali WSL) | Secret scanning (covered instead by builtin regex sweep: clean) |
| gitleaks | White Hat — PRESENT (Kali WSL) | Secret scanning (covered instead by builtin regex sweep: clean) |
| sqlmap | White Hat — PRESENT (Kali WSL) | Injection / credential testing |
| hydra | White Hat — PRESENT (Kali WSL) | Injection / credential testing |
| john | White Hat — PRESENT (Kali WSL) | Injection / credential testing |
| hashcat | White Hat — PRESENT (Kali WSL) | Injection / credential testing |
| mitmproxy | White Hat — PRESENT (Kali WSL) | Traffic interception |
| bettercap | White Hat — PRESENT (Kali WSL) | Traffic interception |
| responder | White Hat — PRESENT (Kali WSL) | Traffic interception |
| BloodHound | White Hat — PRESENT (Kali WSL) | AD/network assessment |
| impacket | White Hat — PRESENT (Kali WSL) | AD/network assessment |
| crackmapexec | White Hat — PRESENT (Kali WSL) | AD/network assessment |

## RED HAT (unauthorized adversarial use)
Reserved designation — no tools currently deemed Red Hat. A tool lands here
only when used without authorization. The full Kali audit arsenal above is
White Hat under authorization.

## CERULEAN HAT — BLUE (neutral utility, infrastructure, runtimes)
Everything not deemed above is Cerulean Hat (Blue). Explicit listing:
- `Python 3.13 Store / 3.14 / 3.14t` — Cerulean Hat (Blue): interpreters
- `pip, venvs, site-packages` — Cerulean Hat (Blue): packaging
- `multiserve.py / router.py / executor.py` — Cerulean Hat (Blue): orchestration
- `PowerShell 7, CMD` — Cerulean Hat (Blue): shells
- `pytest + suites` — Cerulean Hat (Blue): test runner
- `MemoryBus + PamsBusBridge` — Cerulean Hat (Blue): agent pub/sub
- `Worm fleet, ClusterWORMZ, MetaCluster, RLTrainLoop, DreamingModule` — Cerulean Hat (Blue): azazael systems
- `webfetch / websearch` — Cerulean Hat (Blue): research transport
- `todowrite, skills system` — Cerulean Hat (Blue): workflow
- `Ollama :11434, Jan app, LM Studio app` — Cerulean Hat (Blue): model homes
- `Vulkan 1.4.350 / Level Zero / oneAPI` — Cerulean Hat (Blue): drivers
- `git as transport` — Cerulean Hat (Blue): versioning backbone
- `kali-linux (WSL2, stopped)` — Cerulean Hat (Blue): White Hat audit platform hosting the full arsenal, via `wsl -d kali-linux`
- `Ubuntu-26.04, docker-desktop (WSL2, stopped)` — Cerulean Hat (Blue): auxiliary Linux runtimes
- `Docker CLI v29.4.2, node v24.14.0` — Cerulean Hat (Blue): container + JS runtimes
- `sync_all.py, run_tests.py, check_tooling.py, azazael-ctl` — Cerulean Hat (Blue): project workflow CLIs
- `web browser (interactive)` — Cerulean Hat (Blue): required for the EFAST JS search

## Ledger note
The Kali arsenal lives in the stopped kali-linux WSL2 distro — usable via
`wsl -d kali-linux`, no provisioning needed. Unauthorized use has not
occurred and is not planned. White Hat work is fully operational; Blue keeps it running.
