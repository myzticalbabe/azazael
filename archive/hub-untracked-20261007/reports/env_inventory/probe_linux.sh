#!/usr/bin/env bash
# Azazael environment probe (Linux side) — structured inventory emitter.
# Usage: bash probe_linux.sh   (runs inside WSL distro)
export LC_ALL=C

section() { echo ""; echo "### $1"; }

section OS
cat /etc/os-release 2>/dev/null | grep -E '^(NAME|VERSION_ID|PRETTY_NAME)='
uname -r
echo "kernel_arch=$(uname -m)"
echo "cpu_cores=$(nproc)"
free -m 2>/dev/null | awk '/Mem:/{print "mem_total_mb="$2" mem_avail_mb="$7}'

section PYTHON
echo "python3=$(python3 --version 2>&1)"
echo "python3_path=$(command -v python3)"
echo "pip3=$(python3 -m pip --version 2>&1)"
ls -1 /usr/bin/python3.* 2>/dev/null | tr '\n' ' '; echo ""
for py in python3.13 python3.14 python3.12 python3.11; do
  if command -v "$py" >/dev/null 2>&1; then echo "$py=$(command -v $py) $( $py --version 2>&1 )"; fi
done
echo "venvs:"
find /root /opt /srv -maxdepth 4 -name "pyvenv.cfg" -printf '%h\n' 2>/dev/null | head -30

section TOOLS
for t in gcc g++ clang make cmake pkg-config go cargo rustc node npm npx pnpm bun yarn docker podman ffmpeg ffprobe git git-lfs rsync ssh tmux screen ansible terraform kubectl helm java javac dotnet mono R sqlite3 psql mysql redis-cli nginx caddy chromium google-chrome firefox oil tclsh; do
  p="$(command -v "$t" 2>/dev/null || true)"
  if [ -n "$p" ]; then printf '%s=%s\n' "$t" "$p"; fi
done
echo "--- versions ---"
node --version 2>/dev/null | sed 's/^/node_version=/'
npm --version 2>/dev/null | sed 's/^/npm_version=/'
go version 2>/dev/null | sed 's/^/go_version=/'
cargo --version 2>/dev/null | sed 's/^/cargo_version=/'
gcc --version 2>/dev/null | head -1 | sed 's/^/gcc_version=/'
ffmpeg -version 2>/dev/null | head -1 | sed 's/^/ffmpeg_version=/'

section APT
echo "installed_count=$(dpkg -l 2>/dev/null | grep -c '^ii')"
echo "explicitly_installed=$(apt-mark showmanual 2>/dev/null | wc -l)"
apt-mark showmanual 2>/dev/null | sort | tr '\n' ' ' | head -c 6000; echo ""

section PIP
echo "pip_count=$(python3 -m pip list --format=freeze 2>/dev/null | wc -l)"
python3 -m pip list --format=freeze 2>/dev/null | sort

section NPM_GLOBAL
npm ls -g --depth=0 2>/dev/null | tail -n +2

section SERVICES
systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | awk '{print $1}' | head -30

section LISTEN
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | head -25

section DISK
df -h 2>/dev/null | grep -Ev '^(tmpfs|devtmpfs|efivarfs|none)' | head -20

section AZAZAEL
for d in /root/azazael /root/vermillion_lightfury /mnt/g/azazael_shared /mnt/c/Users/clint/azazael; do
  if [ -e "$d" ]; then echo "$d -> $(du -sh "$d" 2>/dev/null | cut -f1)"; else echo "$d -> MISSING"; fi
done
echo "mounts:"; ls -1 /mnt 2>/dev/null | tr '\n' ' '; echo ""
echo "g_mounted=$(mountpoint -q /mnt/g && echo yes || echo no)"
echo "e_mounted=$(mountpoint -q /mnt/e && echo yes || echo no)"
