# =============================================================================
# Dockerfile — AZAZAEL Production Container
# =============================================================================
# Build:  docker build -t azazael .
# Run:    docker run -p 18420:18420 -v G:/:/archive azazael
# =============================================================================

FROM python:3.14-slim

LABEL org.opencontainers.image.title="AZAZAEL"
LABEL org.opencontainers.image.description="Multi-agent worm orchestration ecosystem"
LABEL org.opencontainers.image.version="1.0.0"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash azazael

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application (build from project root: docker build -f azazael/Dockerfile .)
COPY --chown=azazael:azazael azazael/src ./azazael/src
COPY --chown=azazael:azazael azazael/azazael.yaml ./
COPY --chown=azazael:azazael azazael/requirements.txt ./

# Create data directories
RUN mkdir -p /app/data /app/output /archive && \
    chown -R azazael:azazael /app/data /app/output

USER azazael

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('localhost',18420)); print(s.recv(8192).decode()); s.close()" || exit 1

# Expose health endpoint + Prometheus metrics
EXPOSE 18420 18421

ENTRYPOINT ["python", "-m", "azazael.src.CORE.health_server"]
