# ────────────────────────────────────────────────
# 1. Base image
# ────────────────────────────────────────────────
FROM python:3.11-slim

# Work inside /app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ────────────────────────────────────────────────
# 2. Install uv (and tiny curl helper)
#    – the script drops a single statically-linked
#      binary into /usr/local/bin/uv
# ────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && curl -Ls https://astral.sh/uv/install.sh | sh \
 && apt-get purge -y --auto-remove curl \
 && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────
# 3. Dependency layer (maximises Docker cache)
#    – uv pip install works 100 % drop-in for pip
#      Use --system to install into the image’s
#      site-packages instead of creating a venv
# ────────────────────────────────────────────────
COPY requirements.txt .
RUN uv pip install --system --requirement requirements.txt --no-cache-dir

# ────────────────────────────────────────────────
# 4. Application code
# ────────────────────────────────────────────────
COPY app/ .

# ────────────────────────────────────────────────
# 5. Entrypoint
# ────────────────────────────────────────────────
ENTRYPOINT ["python", "main.py"]
