import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, users
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    logger.info(f"👋 Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(users.router, prefix="/api/v1", tags=["users"])

    return app


app = create_app()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/api/v1/health",
    }


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.version,
        "environment": settings.environment,
    }


# Ping endpoint
@app.get("/api/v1/ping")
async def ping():
    """Simple ping endpoint for load balancer health checks."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.host, port=settings.port, reload=settings.debug
    )
