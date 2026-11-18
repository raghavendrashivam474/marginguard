"""Import batch application service."""

from __future__ import annotations

import inspect
import uuid

from app.application.ports import ImportBatchRepository
from app.domain.entities import ImportBatch


class ImportBatchService:
    """Orchestrates import batch use cases."""

    def __init__(self, repo: ImportBatchRepository) -> None:
        self._repo = repo

    async def get_by_id(self, batch_id: uuid.UUID) -> ImportBatch | None:
        res = self._repo.get_by_id(batch_id)
        if inspect.isawaitable(res):
            return await res
        return res

    async def list_import_batches_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ImportBatch], int]:
        res = self._repo.list_by_organization(organization_id, page=page, page_size=page_size)
        if inspect.isawaitable(res):
            res = await res
        if isinstance(res, tuple):
            return res
        return res, len(res)

    async def list_by_organization(
        self,
        organization_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ImportBatch], int]:
        return await self.list_import_batches_by_organization(
            organization_id, page=page, page_size=page_size
        )

    async def save(self, batch: ImportBatch) -> ImportBatch:
        res = self._repo.save(batch)
        if inspect.isawaitable(res):
            return await res
        return res

    async def update_status(self, batch_id: uuid.UUID, status: str) -> None:
        res = self._repo.update_status(batch_id, status)
        if inspect.isawaitable(res):
            await res
