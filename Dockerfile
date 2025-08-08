# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY mcp.json ./
COPY local_filesystem_mcp ./local_filesystem_mcp

# Install the package
RUN pip install --upgrade pip && pip install .

# Default env: the user should override MCP_FS_ALLOWED_DIRS at runtime
ENV MCP_FS_ALLOWED_DIRS="/data"

# Optional mount point for host files
VOLUME ["/data"]

EXPOSE 3000

# Command to run the MCP server
CMD ["python", "-m", "local_filesystem_mcp.server"]


