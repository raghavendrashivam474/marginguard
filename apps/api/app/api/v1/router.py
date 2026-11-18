"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.imports import router as imports_router
from app.api.v1.org_imports import router as org_imports_router
from app.api.v1.organizations import router as organizations_router
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


router.include_router(organizations_router)
router.include_router(imports_router)
router.include_router(org_imports_router)
