"""Organization imports routes for file upload and import batch listings."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.dependencies import get_import_batch_service, get_ingestion_service
from app.api.schemas.import_batch import ImportBatchListResponse, ImportBatchResponse
from app.application.services.import_batch_service import ImportBatchService
from app.application.services.ingestion_service import IngestionService

router = APIRouter()


@router.post(
    "/organizations/{organization_id}/imports",
    response_model=ImportBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_import_upload(
    organization_id: UUID,
    file: UploadFile = File(...),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> ImportBatchResponse:
    """Upload a CSV or XLSX financial data file for an organization."""
    content = await file.read()
    filename = file.filename or "upload.csv"

    try:
        batch = await ingestion_service.ingest_file(
            organization_id=organization_id,
            filename=filename,
            content=content,
        )
        return ImportBatchResponse.from_domain(batch)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/organizations/{organization_id}/imports",
    response_model=ImportBatchListResponse,
)
async def list_organization_imports(
    organization_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ImportBatchService = Depends(get_import_batch_service),
) -> ImportBatchListResponse:
    """List all import batches belonging to a specific organization."""
    batches, total = await service.list_import_batches_by_organization(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
    )
    return ImportBatchListResponse.from_domain_list(
        items=batches,
        total=total,
        page=page,
        page_size=page_size,
    )
