FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install pre-commit
RUN pip install --no-cache-dir pre-commit

# Install additional development tools
RUN pip install --no-cache-dir \
    black \
    ruff \
    mypy \
    pytest \
    pytest-cov \
    pytest-asyncio \
    httpx

# Set up pre-commit hooks
RUN pre-commit install-hooks

# Create workspace directory
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1
