"""API v1 routes."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/health")
async def health_check_v1() -> dict:
    """Versioned health check endpoint."""
    return {
        "status": "healthy",
        "service": "marginguard-api",
        "version": settings.APP_VERSION,
    }
