# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app
ENV PYTHONPATH=/app

# --- Dependency Installation ---
# This section is structured to maximize Docker cache efficiency.
# First, install uv, our package manager.
# This layer will be cached unless the base image changes.
RUN pip install uv

# Next, copy only the dependency definition files.
# This layer is only invalidated if you change your dependencies in pyproject.toml.
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv pip install.
# This creates a cached layer with all your dependencies installed.
RUN uv pip install --system -e .

# --- Application Code ---
# Finally, copy your application code.
# This is the most frequently changing part, so it comes last.
# Now, when you change your code, only this layer and subsequent ones will be rebuilt.
COPY app/ .

# Set the command to run your pipeline
ENTRYPOINT ["python", "main.py"]
