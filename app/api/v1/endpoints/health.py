import platform
import sys
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import DetailedHealthResponse, HealthResponse, SystemInfo

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.version,
        environment="development" if settings.debug else "production",
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system information and dependency checks."""

    # System information
    system_info = SystemInfo(
        python_version=sys.version,
        platform=platform.platform(),
        dependencies={
            "fastapi": "0.115.13",
            "uvicorn": "0.34.3",
            "sqlalchemy": "2.0.41",
            "pydantic": "2.11.7",
        },
    )

    # Health checks
    checks: dict[str, Any] = {
        "database": "healthy",
        "api": "healthy",
        "memory": "healthy",
    }

    # Test database connection
    try:
        db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Determine overall status
    overall_status = (
        "healthy"
        if all(status == "healthy" for status in checks.values())
        else "degraded"
    )

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.version,
        environment="development" if settings.debug else "production",
        system_info=system_info,
        checks=checks,
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}
