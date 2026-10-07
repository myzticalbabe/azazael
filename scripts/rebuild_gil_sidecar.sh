#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Rebuild the Azazael GIL sidecar from scratch.      created 2026-09-30
# ---------------------------------------------------------------------------
# The Ubuntu pillar's primary interpreter is CPython 3.14 free-threaded
# (cpython-314t), which only accepts cp314t wheels. Frameworks with no
# free-threaded wheel (tensorflow, tf2onnx, orjson, langchain, chromadb, polars,
# ray, spacy) run in this same-version GIL sidecar instead.
#
# This script is idempotent and re-runnable. Nothing here compiles Python: the
# interpreter comes prebuilt from astral-sh/python-build-standalone, so a
# rebuild takes about a minute plus the pip installs.
#
# Usage:
#   bash scripts/rebuild_gil_sidecar.sh                 # rebuild if missing
#   GIL_VERSION=3.14.8 bash scripts/rebuild_gil_sidecar.sh   # different patch
#
# Verified 2026-09-30 against cpython-3.14.7+20260929.
# ---------------------------------------------------------------------------
set -euo pipefail

GIL_VERSION="${GIL_VERSION:-3.14.7}"
GIL_PREFIX="${GIL_PREFIX:-/usr/local/python3147-gil}"
VENV="${VENV:-/root/venv-314-gil}"
PREBUILT_SP="${PREBUILT_SP:-/usr/local/lib/python3.14/site-packages}"
ENTRYPOINT="${ENTRYPOINT:-/usr/local/bin/python3.14-gil}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

note() { printf '\033[36m[gil-sidecar]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[gil-sidecar] WARN:\033[0m %s\n' "$*"; }

# A GIL build aborts when PYTHON_GIL=0 is exported (the free-threaded launcher
# sets it in ~/.bashrc), so it is cleared for every interpreter invocation here.
unset PYTHON_GIL

# ── 1. resolve the prebuilt interpreter ────────────────────────────────────
if [ -x "$GIL_PREFIX/bin/python3.14" ]; then
    note "interpreter already present: $GIL_PREFIX"
else
    note "resolving python-build-standalone release for $GIL_VERSION"
    TAG="$(curl -fsSL https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest \
           | tr ',' '\n' | grep -oE '"tag_name": *"[^"]*"' | head -1 | grep -oE '[0-9]{8}')"
    [ -n "$TAG" ] || { warn "could not resolve release tag"; exit 1; }
    ASSET="cpython-${GIL_VERSION}%2B${TAG}-x86_64-unknown-linux-gnu-install_only.tar.gz"
    URL="https://github.com/astral-sh/python-build-standalone/releases/download/${TAG}/${ASSET}"
    note "downloading $ASSET"
    mkdir -p "$GIL_PREFIX"
    TMP="$(mktemp -d)"
    curl -fsSL -o "$TMP/cpython.tar.gz" "$URL"
    tar -xzf "$TMP/cpython.tar.gz" -C "$GIL_PREFIX" --strip-components=1
    rm -rf "$TMP"
    note "installed $("$GIL_PREFIX/bin/python3.14" -VV | head -1)"
fi
"$GIL_PREFIX/bin/python3.14" -c \
    'import sysconfig; assert not sysconfig.get_config_var("Py_GIL_DISABLED"), "not a GIL build"' \
    || { warn "prefix is not a GIL build"; exit 1; }

# ── 2. venv ────────────────────────────────────────────────────────────────
if [ -x "$VENV/bin/python" ]; then
    note "venv already present: $VENV"
else
    note "creating venv $VENV"
    "$GIL_PREFIX/bin/python3.14" -m venv "$VENV"
fi

# Wrapper that clears the fatal PYTHON_GIL flag, for interactive use.
cat > "$VENV/bin/py" <<'PYWRAP'
#!/bin/bash
unset PYTHON_GIL
exec "$(dirname "$0")/python" "$@"
PYWRAP
chmod +x "$VENV/bin/py"

# ── 3. reuse the prebuilt ML stack (holds the local tensorflow build) ──────
if [ -d "$PREBUILT_SP" ]; then
    note "wiring prebuilt site-packages: $PREBUILT_SP"
    printf '%s\n' "$PREBUILT_SP" > "$VENV/lib/python3.14/site-packages/zzz_prebuilt_gil.pth"
else
    warn "$PREBUILT_SP absent: tensorflow/torch/keras/jax will not be importable"
fi

# ── 4. install the sidecar requirements ────────────────────────────────────
if [ -f "$HERE/requirements-gil.txt" ]; then
    note "pip install -r requirements-gil.txt"
    "$VENV/bin/python" -m pip install --no-input --disable-pip-version-check \
        -r "$HERE/requirements-gil.txt" || warn "some packages failed; see output above"
else
    warn "requirements-gil.txt not found under $HERE"
fi

# ── 5. stable entry point ──────────────────────────────────────────────────
cat > "$ENTRYPOINT" <<ENTRY
#!/bin/bash
# Azazael GIL compatibility environment (CPython ${GIL_VERSION}, GIL enabled).
unset PYTHON_GIL
exec ${VENV}/bin/python "\$@"
ENTRY
chmod +x "$ENTRYPOINT"
note "entry point: $ENTRYPOINT"

# ── 6. verify ──────────────────────────────────────────────────────────────
note "verifying"
"$ENTRYPOINT" - <<'CHECK'
import sys, sysconfig
print("python", sys.version.split()[0], "| GIL-disabled =", bool(sysconfig.get_config_var("Py_GIL_DISABLED")))
for mod in ("tensorflow", "torch", "keras", "polars", "ray", "spacy",
            "chromadb", "langchain", "orjson", "tf2onnx"):
    try:
        m = __import__(mod)
        print(f"  OK   {mod:12s} {getattr(m, '__version__', '')}")
    except Exception as exc:
        print(f"  FAIL {mod:12s} {type(exc).__name__}: {exc}")
CHECK
note "done"
