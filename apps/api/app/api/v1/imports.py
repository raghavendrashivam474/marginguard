"""Import batch API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_import_batch_service
from app.api.exceptions import MarginGuardError, NotFoundError
from app.api.schemas.import_batch import ImportBatchResponse
from app.application.services.import_batch_service import ImportBatchService

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("/{import_id}", response_model=ImportBatchResponse)
async def get_import(
    import_id: UUID,
    service: ImportBatchService = Depends(get_import_batch_service),
) -> ImportBatchResponse:
    """Retrieve an import batch by ID."""
    batch = await service.get_by_id(import_id)
    if batch is None:
        raise NotFoundError("ImportBatch", str(import_id))
    return ImportBatchResponse.from_domain(batch)


@router.get("", response_model=list[ImportBatchResponse])
async def list_imports(
    page: int = 1,
    page_size: int = 20,
    service: ImportBatchService = Depends(get_import_batch_service),
) -> list[ImportBatchResponse]:
    """List all import batches (global cross-tenant prohibited)."""
    raise MarginGuardError(
        code="NOT_IMPLEMENTED",
        message="Use GET /api/v1/organizations/{org_id}/imports instead.",
        status_code=501,
    )
