# Azazael Ubuntu 26.04 Bare Metal Install Guide (E:\ Drive)

## Overview
- **Target Drive**: E:\
- **OS**: Ubuntu 26.04 (Resolute Raccoon) - Development Branch
- **Python**: 3.14.2
- **Purpose**: AI/ML Development with Intel iGPU + NPU

---

## Pre-Installation Checklist

### Files on F:\AZAZAEL_BOOT\
| File/Folder | Description |
|-------------|-------------|
| `iso/` | Ubuntu 26.04 ISO |
| `drivers/` | Intel GPU/NPU drivers |
| `python-wheels/` | Python packages |
| `scripts/` | Post-install scripts |
| `docs/` | Documentation |

---

## Step 1: Download Ubuntu 26.04 ISO

### Option A: Direct Download
```powershell
# Download Ubuntu 26.04 Desktop ISO
$isoUrl = "https://cdimages.ubuntu.com/daily-live/current/resolute-desktop-amd64.iso"
$isoFile = "F:\AZAZAEL_BOOT\iso\ubuntu-26.04-desktop-amd64.iso"

Invoke-WebRequest -Uri $isoUrl -OutFile $isoFile -UseBasicParsing
```

### Option B: Use Pre-Downloaded ISO
If you already have the ISO, copy it to:
```
F:\AZAZAEL_BOOT\iso\ubuntu-26.04-desktop-amd64.iso
```

---

## Step 2: Create Bootable USB

### Windows - Using Rufus
1. Download Rufus: https://rufus.ie/
2. Open Rufus
3. Select ISO: `F:\AZAZAEL_BOOT\iso\ubuntu-26.04-desktop-amd64.iso`
4. Device: Your USB drive (16GB+)
5. Partition scheme: GPT
6. Target system: UEFI
7. Click START

### Windows - Using Ventoy
1. Download Ventoy: https://www.ventoy.net/
2. Install Ventoy to USB
3. Copy ISO to USB

---

## Step 3: Boot from USB

1. Restart computer
2. Enter BIOS/UEFI (usually F2, F12, Del)
3. Disable Secure Boot
4. Set USB as first boot priority
5. Save and exit
6. Boot from USB

---

## Step 4: Ubuntu Installation

### Boot Menu
1. Select "Try or Install Ubuntu"
2. Choose "Install Ubuntu"

### Installation Steps
1. **Language**: English
2. **Keyboard**: English (US)
3. **Updates**: "Normal installation"
4. **Installation type**: "Something else"
5. **Partition**:
   - Select E:\ drive
   - Create partitions:
     - `/boot/efi` - 1GB (EFI System)
     - `/` - 50GB+ (Root)
     - `swap` - 16GB (if < 32GB RAM)
     - `/home` - Remaining (Home)
6. **User**:
   - Name: ubuntu
   - Computer: azazael
   - Username: ubuntu
   - Password: [your password]
7. **Complete installation**

---

## Step 5: Post-Installation Setup

### Copy Files from USB
```bash
# After first boot, copy files from USB
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
cp -r /mnt/usb/AZAZAEL_BOOT/* ~/
```

### Run Post-Install Script
```bash
cd ~/scripts
sudo chmod +x post_install.sh
sudo bash post_install.sh
```

---

## Step 6: Verify Installation

### Test Python
```bash
source ~/azazael_venv/bin/activate
python --version
python -c "import torch, transformers, nltk, openvino; print('All OK!')"
```

### Test Hardware Acceleration
```bash
# Check Intel GPU
clinfo | grep -i "intel"

# Check OpenVINO devices
python -c "from openvino.runtime import Core; print(Core().available_devices)"
```

---

## Hardware Support

| Component | Status | Driver |
|-----------|--------|--------|
| Intel iGPU | ✓ Supported | intel-opencl-icd |
| Intel NPU | ✓ Supported | intel-npu-driver |
| CPU | ✓ Supported | Default |
| RAM | ✓ Supported | Default |

---

## Troubleshooting

### No GPU/NPU Detected
```bash
# Reinstall Intel drivers
sudo apt install --reinstall intel-opencl-icd
sudo reboot
```

### Python 3.14 Not Found
```bash
# Check installation
which python3.14
python3.14 --version
```

---

## Files Included

### F:\AZAZAEL_BOOT\iso\
- ubuntu-26.04-desktop-amd64.iso (download required)

### F:\AZAZAEL_BOOT\drivers\
- Intel Graphics Driver (download links in download_drivers.sh)

### F:\AZAZAEL_BOOT\python-wheels\
- All Python packages for offline install

### F:\AZAZAEL_BOOT\scripts\
- post_install.sh - Automated post-install script

---

## Quick Commands Reference

```bash
# Activate venv
source ~/azazael_venv/bin/activate

# Install package
pip install <package>

# Check GPU
clinfo

# Check NPU
dmesg | grep -i npu

# Update all
sudo apt update && sudo apt upgrade -y
```

---

**Generated**: 2026-02-15
