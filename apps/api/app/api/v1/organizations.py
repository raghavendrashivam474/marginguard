"""Organization API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_organization_service
from app.api.exceptions import NotFoundError
from app.api.schemas.organization import OrganizationCreate, OrganizationResponse
from app.application.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    body: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    """Create a new organization."""
    org = await service.create(
        name=body.name,
        currency=body.currency,
        legal_name=body.legal_name,
    )
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    page: int = 1,
    page_size: int = 20,
    service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationResponse]:
    """List all organizations."""
    orgs = await service.list_all(page=page, page_size=page_size)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: UUID,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationResponse:
    """Retrieve an organization by ID."""
    org = await service.get_by_id(organization_id)
    if org is None:
        raise NotFoundError("Organization", str(organization_id))
    return OrganizationResponse.model_validate(org)
