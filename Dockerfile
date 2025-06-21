# ───────────────────────────────────────────────────────────────
# 1. Base image: uv + Python 3.11 already installed
#    (tags: {version}-python3.11-bookworm-slim, python3.11-bookworm-slim, …)
# ───────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# ───────────────────────────────────────────────────────────────
# 2. Runtime setup
# ───────────────────────────────────────────────────────────────
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Tell uv to install straight into the system interpreter
    UV_SYSTEM_PYTHON=1

# ───────────────────────────────────────────────────────────────
# 3. Dependency layer  (maximises Docker cache)
#    – uv’s pip shim is a 100 % drop-in for pip
# ───────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN uv pip install --system --requirement requirements.txt --no-cache-dir

# ───────────────────────────────────────────────────────────────
# 4. Application code
# ───────────────────────────────────────────────────────────────
COPY app/ .

# ───────────────────────────────────────────────────────────────
# 5. Entrypoint
# ───────────────────────────────────────────────────────────────
ENTRYPOINT ["python", "main.py"]
