# ─────────────────────────────────────────────────────────────
# 1. Base image
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Work inside /app
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ─────────────────────────────────────────────────────────────
# 2. Install OS packages (optional, uncomment if you need them)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# 3. Dependency layer
#    – copy requirements.txt first to maximise Docker cache
# ─────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────
# 4. Application code
# ─────────────────────────────────────────────────────────────
COPY app/ .

# ─────────────────────────────────────────────────────────────
# 5. Entrypoint
# ─────────────────────────────────────────────────────────────
ENTRYPOINT ["python", "main.py"]
