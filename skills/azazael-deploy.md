---
name: azazael-deploy
description: Azazael deployment — Docker, CLI packaging, scheduled runs, G:/ archive, production readiness. Load for deployment tasks.
metadata:
  category: planning
  project: azazael
---
# Azazael Deployment
## Current Deployment State
Azazael runs as a Python CLI application from `C:/Users/clint/azazael/`. No containerization, no scheduling, no CI/CD pipeline — yet. All PRODUCTION_TODO.md deployment items are open.
## Dependencies
| Package | Purpose | Required? |
|---------|---------|-----------|
| Python 3.10+ | Runtime | Required |
| Pillow | Image processing (CODEX frames) | Required for CODEX |
| psutil | System monitoring (SystemZ, PROCESSZ) | Required for monitoring |
| ffmpeg | Video encoding (CODEX output) | Required for CODEX |
| tkinter | GUI popups (optional) | Optional |
## Entry Points
| Script | Purpose | How to Run |
|--------|---------|-----------|
| `python src/CORE/WORMS/CLUSTERWORMS.py --popup` | GUI cluster manager | Interactive |
| `python src/CORE/WORMS/CLUSTERWORMS.py --discover` | List all Nature categories | CLI |
| `python src/CORE/WORMS/CLUSTERWORMS.py --build-nature security --execute` | Run a Nature cluster | CLI |
| `python src/CORE/WORMS/METACLUSTER.py --orchestrate` | Full ecosystem orchestration | CLI |
| `python src/CORE/WORMS/CONCURRENCY.py --ecosystem` | Parallel full ecosystem | CLI |
## CLI Packaging (Planned)
### Unified CLI
```python
# Proposed: azazael-cli (not yet built)
$ azazael scan --nature security
$ azazael orchestrate --all
$ azazael status
$ azazael codex --output G:/videos/
```
### Package Structure (Planned)
azazael/
setup.py                  # Package config
requirements.txt          # Dependencies
azazael_cli/
__init__.py
main.py                 # Unified CLI entry
commands/
scan.py               # --scan
orchestrate.py        # --orchestrate
codex.py              # CODEX video
status.py             # --status
## Docker (Planned)
### Dockerfile
```dockerfile
FROM python:3.14t-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY azazael/ ./azazael/
# Non-root user
RUN useradd -m azazael && chown -R azazael:azazael /app
USER azazael
ENTRYPOINT ["python", "-m", "azazael_cli"]
### docker-compose.yml (Planned)
```yaml
version: "3.8"
services:
azazael:
build: .
volumes:
- ./data:/app/data
- G:/azazael_archive:/archive  # G:/ archive mount
environment:
- AZAZAEL_ROOT=/app
- AZAZAEL_ARCHIVE=/archive
restart: unless-stopped
## Scheduled Runs (Planned)
### Windows Task Scheduler
```powershell
# Run full ecosystem scan every 4 hours
$action = New-ScheduledTaskAction -Execute "python" `
-Argument "C:/Users/clint/src/CORE/WORMS/METACLUSTER.py --orchestrate"
$trigger = New-ScheduledTaskTrigger -Daily -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 4)
Register-ScheduledTask -TaskName "AzazaelEcosystem" -Action $action -Trigger $trigger
### Cron (Linux)
```cron
# Full ecosystem scan every 6 hours
0 */6 * * * cd /app && python src/CORE/WORMS/METACLUSTER.py --orchestrate >> /var/log/azazael.log 2>&1
# Security audit daily at 3am
0 3 * * * cd /app && python src/CORE/WORMS/CLUSTERWORMS.py --build-nature security --execute
## G:/ Archive Integration
The CODEX system writes to `G:/` drive:
- `G:/azazael_videos/` — CODEX video output
- `G:/azazael_frames/` — Raw frame captures
- `G:/azazael_archive/` — Cold storage (ColdArchivist target)
These paths are hardcoded in some worms. For Docker deployment, mount G:/ as a volume.
### Path Resolution
from CORE.config import get_project_root, get_g_drive
project_root = get_project_root()  # C:/Users/clint/azazael/
g_drive = get_g_drive()            # G:/ or fallback
## Deployment Priorities (from PRODUCTION_TODO.md)
| Priority | Item | Effort | Status |
|----------|------|--------|--------|
| High | Unified CLI entry point | M | Not started |
| High | requirements.txt with pinned versions | S | Not started |
| Medium | Dockerfile + docker-compose.yml | M | Not started |
| Medium | Scheduled runs (Task Scheduler / cron) | S | Not started |
| Low | CI/CD pipeline (GitHub Actions) | L | Not started |
| Low | PyPI package publication | M | Not started |
## Related Skills
- `azazael-production` — Full 12-section production roadmap
- `azazael-environment` — Python 3.10+/3.14t, dependency setup
- `azazael-paths` — Path resolution system, get_project_root, get_g_drive
- `azazael-git` — Git conventions, pre-commit checklist
Azazael runs as a Python CLI application from `C:/Azazael/azazael/`. No containerization, no scheduling, no CI/CD pipeline — yet. All PRODUCTION_TODO.md deployment items are open.
COPY requirements-3.15t.txt .
RUN pip install --no-cache-dir -r requirements-3.15t.txt
project_root = get_project_root()  # C:/Azazael/azazael/
