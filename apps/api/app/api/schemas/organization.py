"""MarginGuard API — Organization schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    """Request body for creating an organization."""

    name: str = Field(..., min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    currency: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class OrganizationResponse(BaseModel):
    """Response body for an organization."""

    id: UUID
    name: str
    legal_name: str | None
    currency: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
