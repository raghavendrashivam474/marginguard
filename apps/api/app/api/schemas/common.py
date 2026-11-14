"""MarginGuard API — common schemas.

Shared Pydantic models for error responses, pagination, and base types.
These implement the contracts defined in ADR-004 and contracts/schemas/common.schema.json.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Decimal serialization
# ---------------------------------------------------------------------------
class DecimalModel(BaseModel):
    """Base model that serializes Decimal fields as strings for JSON precision."""

    model_config = ConfigDict(
        json_encoders={Decimal: str},
    )


# ---------------------------------------------------------------------------
# Error response (ADR-004)
# ---------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    """Field-level validation error detail."""

    field: str | None = None
    issue: str


class ErrorBody(BaseModel):
    """Standard error body following the MarginGuard error envelope."""

    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Human-readable error description",
    )
    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="Field-level validation errors",
    )
    request_id: str | None = Field(
        default=None,
        description="Unique request identifier for tracing",
    )


class ErrorResponse(BaseModel):
    """Top-level error response wrapper."""

    error: ErrorBody


# ---------------------------------------------------------------------------
# Pagination (ADR-004)
# ---------------------------------------------------------------------------
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Items per page (max 100)"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope."""

    items: list[T]
    total: int = Field(ge=0, description="Total number of items")
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


# ---------------------------------------------------------------------------
# Shared field types
# ---------------------------------------------------------------------------
class TimestampMixin(BaseModel):
    """Mixin providing created_at / updated_at fields."""

    created_at: datetime
    updated_at: datetime


class CurrencyField(BaseModel):
    """Validates ISO 4217 currency codes."""

    currency: str = Field(
        ..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    )
