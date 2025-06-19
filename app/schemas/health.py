from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: datetime
    version: str
    environment: str


class SystemInfo(BaseModel):
    """System information schema."""

    python_version: str
    platform: str
    dependencies: dict[str, str]


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with system info."""

    status: str
    timestamp: datetime
    version: str
    environment: str
    system_info: SystemInfo
    checks: dict[str, Any]
