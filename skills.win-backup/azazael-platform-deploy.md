---
name: azazael-platform-deploy
description: Cross-platform AZAZAEL 3.14t deployment — Windows 11, WSL2 Ubuntu, Bare Metal Ubuntu, Kali Linux. Setup, sync, path resolution, and validation per platform.
metadata:
  category: infrastructure
  project: azazael
  auto_load: true
---

# azazael-platform-deploy

## Description
Cross-platform AZAZAEL 3.14t deployment skill. Covers Windows 11, WSL2 Ubuntu 26.04, Bare Metal Ubuntu 26.04, and Kali Linux. Use when setting up AZAZAEL on a new platform, syncing between platforms, or debugging cross-platform issues.

## Load When
- Setting up AZAZAEL on any platform for the first time
- Syncing code between Windows ↔ WSL2 ↔ Linux
- Debugging import errors, path issues, or case sensitivity problems
- Configuring CI/CD for multi-platform testing
- Mounting G: drive for shared state

## Platform-Specific Setup

### Windows 11
```powershell
# Python 3.14t with free-threading
C:\Python314t\python.exe --version
python -c "import sys; print(hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"

# Path setup
set AZAZAEL_ROOT=C:\Users\clint\azazael
set PYTHONPATH=%AZAZAEL_ROOT%\src

# G: drive (should already be mounted)
dir G:\source-of-truth\

# Rust toolchain (for GOSP)
rustup default stable-x86_64-pc-windows-msvc
```

### WSL2 Ubuntu 26.04
```bash
# Python 3.14t (pre-installed on Ubuntu 26.04)
python3 --version  # Should show 3.14.5

# Mount G: drive (automatic via WSL2 /mnt/g/)
ls /mnt/g/source-of-truth/

# Set up project
export AZAZAEL_ROOT=/root/azazael
cd $AZAZAEL_ROOT

# Verify free-threading
python3 -c "import sys; print(hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"
```

### Bare Metal Ubuntu 26.04
```bash
# Install Python 3.14t from source (needed for free-threading)
sudo apt-get update
sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Download and build Python 3.14 with free-threading
wget https://www.python.org/ftp/python/3.14.5/Python-3.14.5.tar.xz
tar -xf Python-3.14.5.tar.xz
cd Python-3.14.5
./configure --disable-gil --enable-optimizations --prefix=/usr/local/python314t
make -j$(nproc)
sudo make install

# Verify
/usr/local/python314t/bin/python3 -c "import sys; print(hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"

# Mount G: drive (NFS or SMB)
sudo apt-get install -y nfs-common  # or cifs-utils
sudo mkdir -p /mnt/g
sudo mount -t cifs //server/share /mnt/g -o username=user,password=pass,vers=3.0
```

### Kali Linux
```bash
# Kali-specific: Python 3.14t
# Same source build as Ubuntu, plus security tools
sudo apt-get install -y python3-tk python3-dev

# Install security tools integration
sudo apt-get install -y nmap wireshark aircrack-ng metasploit-framework

# Configure firewall for AZAZAEL
sudo ufw allow 8420/tcp   # PAMS
sudo ufw allow 18080/tcp  # llama-server
sudo ufw allow 8080/tcp   # Web dashboard

# AppArmor (optional but recommended)
sudo apt-get install -y apparmor apparmor-utils
```

## Cross-Platform Path Resolution

```python
from pathlib import Path
import os, sys, platform

def get_project_root():
    """Cross-platform project root resolution."""
    # Check environment variable
    for var in ('AZAZAEL_ROOT', 'Azazael_ROOT'):
        if var in os.environ:
            return Path(os.environ[var])

    # Auto-detect from common locations
    candidates = [
        Path.home() / 'azazael',
        Path.home() / 'Azazael',
        Path('/root/azazael'),
        Path('/home/clint/azazael'),
    ]
    for c in candidates:
        if (c / 'src' / 'CORE').exists():
            return c

    # Fallback: current directory
    return Path.cwd()

def get_g_drive():
    """Cross-platform G: drive resolution."""
    if platform.system() == 'Windows':
        p = Path('G:/')
    elif Path('/mnt/g').exists():
        p = Path('/mnt/g')
    elif Path('/media/g').exists():
        p = Path('/media/g')
    else:
        return None

    return p if p.exists() else None
```

## Sync Commands

```bash
# WSL2 → Windows (from WSL)
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    /root/azazael/ /mnt/c/Users/clint/azazael/

# WSL2 → Bare Metal
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
    /root/azazael/ user@bare-metal:/home/clint/azazael/

# WSL2 → Kali
rsync -avz --exclude='__pycache__' --exclude='*.pyc' \
    /root/azazael/ root@kali:/root/azazael/

# G: drive state sync
rsync -avz /root/azazael/output/ /mnt/g/source-of-truth/state/wsl/output/
```

## Validation Checklist

After deploying to any platform, run:

```bash
# 1. Free-threading check
python3 -c "import sys; print('FT:', hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"

# 2. Import check
cd $AZAZAEL_ROOT
python3 -c "import sys; sys.path.insert(0,'src'); from CORE.worm_registry import WORM_REGISTRY; print('Worms:', len(WORM_REGISTRY))"

# 3. G: drive check
python3 -c "from CORE.paths import get_g_drive; print('G:', get_g_drive())"

# 4. Syntax check all Python files
find src -name "*.py" -exec python3 -m py_compile {} \;

# 5. Run test suite
python3 -m pytest tests/ -v --tb=short
```

## Related Documents
- PLATFORM_DEPLOYMENT.md — Multi-platform TODO matrix
- LESSONS_PLATFORM.md — 10 platform-specific lessons
- MEMORIES_PLATFORM.md — Cross-platform anti-patterns
- PROJECT_STRUCTURES.md — Directory templates per platform
- RUST_CONVERSION_PLAN.md — Rust conversion strategy
