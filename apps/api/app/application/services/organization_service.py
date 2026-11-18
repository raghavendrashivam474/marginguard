"""Organization application service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.application.ports import OrganizationRepository
from app.domain.entities import Organization


class OrganizationService:
    """Orchestrates organization use cases."""

    def __init__(self, repo: OrganizationRepository) -> None:
        self._repo = repo

    async def create(
        self,
        name: str,
        currency: str,
        legal_name: str | None = None,
    ) -> Organization:
        now = datetime.now(timezone.utc)
        org = Organization(
            id=uuid.uuid4(),
            name=name.strip(),
            currency=currency.upper(),
            legal_name=legal_name,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.save(org)

    async def get_by_id(self, organization_id: uuid.UUID) -> Organization | None:
        return await self._repo.get_by_id(organization_id)

    async def list_all(self, *, page: int = 1, page_size: int = 20) -> list[Organization]:
        return await self._repo.list_all(page=page, page_size=page_size)
