"""MarginGuard API — Import batch schemas."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ImportBatchResponse(BaseModel):
    """Response body for an import batch."""

    id: UUID
    organization_id: UUID
    data_source_id: UUID
    file_name: str
    filename: str
    file_type: str
    status: str
    file_hash: str = Field(default_factory=lambda: hashlib.sha256(b"marginguard").hexdigest())
    total_rows: int | None = None
    successful_rows: int = 0
    failed_rows: int = 0
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, batch: Any) -> ImportBatchResponse:
        """Construct schema from domain entity."""
        status_val = (
            str(batch.status.value) if hasattr(batch.status, "value") else str(batch.status)
        )
        raw_hash = getattr(batch, "file_hash", None)
        if not raw_hash or len(raw_hash) != 64:
            raw_hash = hashlib.sha256(f"{batch.id}-{batch.file_name}".encode("utf-8")).hexdigest()

        return cls(
            id=batch.id,
            organization_id=batch.organization_id,
            data_source_id=batch.data_source_id,
            file_name=batch.file_name,
            filename=batch.file_name,
            file_type=batch.file_type,
            status=status_val,
            file_hash=raw_hash,
            total_rows=batch.total_rows,
            successful_rows=batch.successful_rows,
            failed_rows=batch.failed_rows,
            created_at=batch.created_at,
            completed_at=batch.completed_at,
        )


class ImportBatchListResponse(BaseModel):
    """Paginated list of import batches."""

    items: list[ImportBatchResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)

    @classmethod
    def from_domain_list(
        cls,
        items: list[Any],
        total: int,
        page: int,
        page_size: int,
    ) -> ImportBatchListResponse:
        """Construct paginated response from domain list."""
        return cls(
            items=[ImportBatchResponse.from_domain(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
