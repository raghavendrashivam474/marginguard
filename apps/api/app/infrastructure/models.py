"""MarginGuard infrastructure — SQLAlchemy ORM models.

These models map domain entities to PostgreSQL tables. They live in the
Infrastructure layer and are the only place that imports SQLAlchemy.

Design decisions (see ADR-005, data-model.md):
- UUID primary keys (Python-side default for cross-DB compatibility)
- NUMERIC(18,4) for all monetary columns
- TIMESTAMPTZ for all timestamps
- CHECK constraints matching the data model specification
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    CHAR,
    JSON,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Real,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Base(DeclarativeBase):
    """Shared declarative base for all MarginGuard ORM models."""

    pass


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------
class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    # Relationships
    data_sources: Mapped[list["DataSourceModel"]] = relationship(
        back_populates="organization"
    )
    import_batches: Mapped[list["ImportBatchModel"]] = relationship(
        back_populates="organization"
    )
    suppliers: Mapped[list["SupplierModel"]] = relationship(
        back_populates="organization"
    )


# ---------------------------------------------------------------------------
# DataSource
# ---------------------------------------------------------------------------
class DataSourceModel(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    organization: Mapped["OrganizationModel"] = relationship(
        back_populates="data_sources"
    )
    import_batches: Mapped[list["ImportBatchModel"]] = relationship(
        back_populates="data_source"
    )

    __table_args__ = (
        Index("ix_data_sources_organization_id", "organization_id"),
    )


# ---------------------------------------------------------------------------
# ImportBatch
# ---------------------------------------------------------------------------
class ImportBatchModel(Base):
    __tablename__ = "import_batches"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    data_source_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("data_sources.id"),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )
    total_rows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    successful_rows: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    failed_rows: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    organization: Mapped["OrganizationModel"] = relationship(
        back_populates="import_batches"
    )
    data_source: Mapped["DataSourceModel"] = relationship(
        back_populates="import_batches"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','processing','completed',"
            "'partially_completed','failed')",
            name="ck_import_batches_status",
        ),
        CheckConstraint(
            "successful_rows >= 0 AND failed_rows >= 0",
            name="ck_import_batches_row_counts",
        ),
        Index("ix_import_batches_organization_id", "organization_id"),
        Index("ix_import_batches_status", "status"),
    )


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------
class SupplierModel(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_identifier: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    organization: Mapped["OrganizationModel"] = relationship(
        back_populates="suppliers"
    )

    __table_args__ = (
        Index("ix_suppliers_organization_id", "organization_id"),
        Index("ix_suppliers_name", "name"),
    )


# ---------------------------------------------------------------------------
# PurchaseOrder
# ---------------------------------------------------------------------------
class PurchaseOrderModel(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    external_reference: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    total_amount: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0", name="ck_purchase_orders_total_amount"
        ),
        UniqueConstraint(
            "organization_id",
            "external_reference",
            name="uq_purchase_orders_org_ref",
        ),
        Index("ix_purchase_orders_organization_id", "organization_id"),
        Index("ix_purchase_orders_supplier_id", "supplier_id"),
    )


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------
class InvoiceModel(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=False,
    )
    purchase_order_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("purchase_orders.id"),
        nullable=True,
    )
    external_reference: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    subtotal: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    tax_amount: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_invoices_subtotal"),
        CheckConstraint("tax_amount >= 0", name="ck_invoices_tax_amount"),
        CheckConstraint("total_amount >= 0", name="ck_invoices_total_amount"),
        Index("ix_invoices_organization_id", "organization_id"),
        Index("ix_invoices_supplier_id", "supplier_id"),
        Index("ix_invoices_external_reference", "external_reference"),
    )


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=True,
    )
    external_reference: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    amount: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    payment_method: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount"),
        Index("ix_payments_organization_id", "organization_id"),
        Index("ix_payments_supplier_id", "supplier_id"),
    )


# ---------------------------------------------------------------------------
# Match
# ---------------------------------------------------------------------------
class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    match_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_record_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    target_record_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    target_record_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    matched_amount: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    matching_method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Real, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="proposed"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_matches_confidence",
        ),
        CheckConstraint(
            "matched_amount > 0", name="ck_matches_matched_amount"
        ),
        CheckConstraint(
            "source_record_id != target_record_id",
            name="ck_matches_different_records",
        ),
        Index("ix_matches_organization_id", "organization_id"),
        Index(
            "ix_matches_source",
            "source_record_type",
            "source_record_id",
        ),
        Index(
            "ix_matches_target",
            "target_record_type",
            "target_record_id",
        ),
    )


# ---------------------------------------------------------------------------
# Finding
# ---------------------------------------------------------------------------
class FindingModel(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    finding_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="detected"
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount_at_risk: Mapped[float] = mapped_column(
        Numeric(18, 4, asdecimal=True), nullable=False
    )
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    confidence: Mapped[float] = mapped_column(Real, nullable=False)
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    evidence: Mapped[list["EvidenceModel"]] = relationship(
        back_populates="finding", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_findings_confidence",
        ),
        CheckConstraint(
            "amount_at_risk >= 0", name="ck_findings_amount_at_risk"
        ),
        Index("ix_findings_organization_id", "organization_id"),
        Index("ix_findings_status", "status"),
        Index("ix_findings_finding_type", "finding_type"),
        Index("ix_findings_severity", "severity"),
    )


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
class EvidenceModel(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    finding_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_record_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    calculation_details: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )

    finding: Mapped["FindingModel"] = relationship(
        back_populates="evidence"
    )

    __table_args__ = (
        Index("ix_evidence_finding_id", "finding_id"),
        Index("ix_evidence_organization_id", "organization_id"),
    )


# ---------------------------------------------------------------------------
# Investigation
# ---------------------------------------------------------------------------
class InvestigationModel(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=_new_uuid
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    finding_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("findings.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="open"
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('open','in_progress','concluded')",
            name="ck_investigations_status",
        ),
        Index("ix_investigations_finding_id", "finding_id"),
        Index("ix_investigations_organization_id", "organization_id"),
    )
