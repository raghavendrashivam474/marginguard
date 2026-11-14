"""MarginGuard domain entities.

Entities are domain objects with identity (UUID). They represent the core
business concepts of MarginGuard and must not import any infrastructure
framework (no FastAPI, no SQLAlchemy, no Pydantic).

These are plain Python dataclasses. ORM models in the Infrastructure layer
will mirror these structures but add persistence concerns.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums import (
    FindingStatus,
    FindingType,
    ImportStatus,
    InvestigationStatus,
    MatchStatus,
    MatchType,
    RecordType,
    Severity,
)


@dataclass(slots=True)
class Organization:
    """The business using MarginGuard. Tenant boundary for data isolation."""

    id: UUID
    name: str
    currency: str  # ISO 4217
    created_at: datetime
    updated_at: datetime
    legal_name: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Organization name must not be empty")
        if len(self.currency) != 3 or self.currency != self.currency.upper():
            raise ValueError(f"Invalid currency code: {self.currency!r}")


@dataclass(slots=True)
class DataSource:
    """Origin of imported business records."""

    id: UUID
    organization_id: UUID
    source_type: str
    source_name: str
    created_at: datetime


@dataclass(slots=True)
class ImportBatch:
    """A single import operation with lifecycle tracking."""

    id: UUID
    organization_id: UUID
    data_source_id: UUID
    file_name: str
    file_type: str
    status: ImportStatus
    created_at: datetime
    total_rows: int | None = None
    successful_rows: int = 0
    failed_rows: int = 0
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.successful_rows < 0 or self.failed_rows < 0:
            raise ValueError("Row counts must be non-negative")
        if self.total_rows is not None:
            if self.successful_rows + self.failed_rows > self.total_rows:
                raise ValueError("successful + failed rows cannot exceed total")


@dataclass(slots=True)
class Supplier:
    """A vendor or supplier the organization transacts with."""

    id: UUID
    organization_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    external_reference: str | None = None
    tax_identifier: str | None = None


@dataclass(slots=True)
class PurchaseOrder:
    """A purchase order issued by the organization."""

    id: UUID
    organization_id: UUID
    supplier_id: UUID
    external_reference: str
    order_date: date
    currency: str
    total_amount: Decimal
    status: str
    created_at: datetime

    def __post_init__(self) -> None:
        if self.total_amount < 0:
            raise ValueError("total_amount must be non-negative")


@dataclass(slots=True)
class Invoice:
    """An invoice received from a supplier."""

    id: UUID
    organization_id: UUID
    supplier_id: UUID
    external_reference: str
    invoice_date: date
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    purchase_order_id: UUID | None = None
    due_date: date | None = None

    def __post_init__(self) -> None:
        if self.subtotal < 0:
            raise ValueError("subtotal must be non-negative")
        if self.tax_amount < 0:
            raise ValueError("tax_amount must be non-negative")
        if self.total_amount < 0:
            raise ValueError("total_amount must be non-negative")
        expected_total = self.subtotal + self.tax_amount
        if self.total_amount != expected_total:
            raise ValueError(
                f"total_amount ({self.total_amount}) must equal "
                f"subtotal + tax_amount ({expected_total})"
            )


@dataclass(slots=True)
class Payment:
    """A payment made by the organization."""

    id: UUID
    organization_id: UUID
    payment_date: date
    currency: str
    amount: Decimal
    created_at: datetime
    supplier_id: UUID | None = None
    external_reference: str | None = None
    payment_method: str | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")


@dataclass(slots=True)
class Match:
    """A proposed or established relationship between two financial records."""

    id: UUID
    organization_id: UUID
    match_type: MatchType
    source_record_type: RecordType
    source_record_id: UUID
    target_record_type: RecordType
    target_record_id: UUID
    matched_amount: Decimal
    matching_method: str
    confidence: float
    status: MatchStatus
    created_at: datetime

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.matched_amount <= 0:
            raise ValueError("matched_amount must be positive")
        if self.source_record_id == self.target_record_id:
            raise ValueError("source and target records must be different")


@dataclass(slots=True)
class Finding:
    """A potential financial discrepancy detected by the reconciliation engine."""

    id: UUID
    organization_id: UUID
    finding_type: FindingType
    severity: Severity
    status: FindingStatus
    title: str
    description: str
    amount_at_risk: Decimal
    currency: str
    confidence: float
    rule_id: str
    rule_version: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.amount_at_risk < 0:
            raise ValueError("amount_at_risk must be non-negative")


@dataclass(slots=True)
class Evidence:
    """Structured supporting information behind a finding."""

    id: UUID
    organization_id: UUID
    finding_id: UUID
    evidence_type: str
    source_record_type: RecordType
    source_record_id: UUID
    description: str
    created_at: datetime
    calculation_details: dict | None = None


@dataclass(slots=True)
class Investigation:
    """Human review process for a finding."""

    id: UUID
    organization_id: UUID
    finding_id: UUID
    status: InvestigationStatus
    created_at: datetime
    updated_at: datetime
    review_notes: str | None = None
