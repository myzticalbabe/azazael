# =============================================================================
# Azazael Core Dockerfile - Python 3.14t Free-Threading + CD5 WAL Optimization
# =============================================================================
# Source: research/CROSS_DOMAIN.md sec.CD5 (June 11, 2026)
#
# Features:
#   - Python 3.14.0-slim-bookworm base (free-threading ready)
#   - Non-root azazael user (uid=1000, gid=1000)
#   - Read-only root filesystem compatible
#   - All dependencies installed in a single layer
#   - WAL-optimized SQLite configuration via env vars
# =============================================================================

FROM python:3.14.0-slim-bookworm AS base

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gosu \
        tini \
    ; \
    rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Create azazael user (uid=1000, gid=1000) for non-root execution
# ---------------------------------------------------------------------------
RUN set -eux; \
    groupadd -r azazael -g 1000; \
    useradd -r -g azazael -u 1000 -m -d /home/azazael -s /bin/bash azazael; \
    mkdir -p /persistent /data /app/output; \
    chown -R azazael:azazael /persistent /data /app/output /home/azazael

# ---------------------------------------------------------------------------
# Copy and install Python dependencies
# ---------------------------------------------------------------------------
COPY --chown=azazael:azazael requirements-3.14t.txt /tmp/requirements-3.14t.txt
RUN set -eux; \
    pip install --no-cache-dir -r /tmp/requirements-3.14t.txt; \
    rm -f /tmp/requirements-3.14t.txt

# ---------------------------------------------------------------------------
# Copy application code (ownership preserved for bind-mount override)
# ---------------------------------------------------------------------------
WORKDIR /app
COPY --chown=azazael:azazael . /app/

# ---------------------------------------------------------------------------
# Final stage: production image
# ---------------------------------------------------------------------------
FROM base AS production

# Switch to non-root user
USER azazael:azazael
WORKDIR /app

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
# CD5 split config: .db on persistent volume, WAL/SHM on tmpfs
ENV AZAZAEL_MEMORY_DIR=/persistent
ENV AZAZAEL_WAL_DIR=/data

# Python configuration
ENV PYTHONPATH=/app/azazael/src
ENV PYTHON_GIL=0

# Application paths
ENV AZAZAEL_WORKSPACE=/app
ENV AZAZAEL_OUTPUT_PATH=/app/output

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "azazael"]

# =============================================================================
# Metadata
# =============================================================================
LABEL org.opencontainers.image.title="Azazael Core"
LABEL org.opencontainers.image.description="Azazael AI Ecosystem - WAL-optimized SQLite with split tmpfs/volume"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2026-06-12"
