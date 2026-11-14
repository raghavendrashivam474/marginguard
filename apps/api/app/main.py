"""MarginGuard API - application entry point."""

from fastapi import FastAPI

from app.api.exceptions import register_exception_handlers
from app.api.v1.router import router as v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-assisted financial leakage detection and investigation API.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register standardized exception handlers (ADR-004)
register_exception_handlers(app)

app.include_router(v1_router)


@app.get("/health", tags=["root"])
async def health_check() -> dict:
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": "marginguard-api",
        "version": settings.APP_VERSION,
    }
