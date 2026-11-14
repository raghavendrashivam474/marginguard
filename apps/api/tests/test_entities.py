"""Tests for domain entity invariants.

Verifies that business rules defined in the domain model are enforced
at construction time, independent of any persistence layer.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities import (
    Finding,
    ImportBatch,
    Invoice,
    Match,
    Organization,
    Payment,
)
from app.domain.enums import (
    FindingStatus,
    FindingType,
    ImportStatus,
    MatchStatus,
    MatchType,
    RecordType,
    Severity,
)

NOW = datetime.now(timezone.utc)
TODAY = date.today()
ORG_ID = uuid4()
SUP_ID = uuid4()


class TestOrganization:
    def test_valid(self) -> None:
        org = Organization(
            id=uuid4(), name="Test Corp", currency="INR",
            created_at=NOW, updated_at=NOW,
        )
        assert org.name == "Test Corp"

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            Organization(
                id=uuid4(), name="   ", currency="INR",
                created_at=NOW, updated_at=NOW,
            )

    def test_rejects_invalid_currency(self) -> None:
        with pytest.raises(ValueError, match="Invalid currency"):
            Organization(
                id=uuid4(), name="Test", currency="inr",
                created_at=NOW, updated_at=NOW,
            )


class TestInvoice:
    def test_valid(self) -> None:
        inv = Invoice(
            id=uuid4(), organization_id=ORG_ID, supplier_id=SUP_ID,
            external_reference="INV-001", invoice_date=TODAY,
            currency="INR", subtotal=Decimal("1000"),
            tax_amount=Decimal("180"), total_amount=Decimal("1180"),
            created_at=NOW,
        )
        assert inv.total_amount == Decimal("1180")

    def test_rejects_mismatched_total(self) -> None:
        with pytest.raises(ValueError, match="must equal"):
            Invoice(
                id=uuid4(), organization_id=ORG_ID, supplier_id=SUP_ID,
                external_reference="INV-002", invoice_date=TODAY,
                currency="INR", subtotal=Decimal("1000"),
                tax_amount=Decimal("180"), total_amount=Decimal("999"),
                created_at=NOW,
            )

    def test_rejects_negative_subtotal(self) -> None:
        with pytest.raises(ValueError, match="subtotal"):
            Invoice(
                id=uuid4(), organization_id=ORG_ID, supplier_id=SUP_ID,
                external_reference="INV-003", invoice_date=TODAY,
                currency="INR", subtotal=Decimal("-100"),
                tax_amount=Decimal("0"), total_amount=Decimal("-100"),
                created_at=NOW,
            )


class TestPayment:
    def test_valid(self) -> None:
        pay = Payment(
            id=uuid4(), organization_id=ORG_ID,
            payment_date=TODAY, currency="INR",
            amount=Decimal("5000"), created_at=NOW,
        )
        assert pay.amount == Decimal("5000")

    def test_rejects_zero_amount(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            Payment(
                id=uuid4(), organization_id=ORG_ID,
                payment_date=TODAY, currency="INR",
                amount=Decimal("0"), created_at=NOW,
            )

    def test_rejects_negative_amount(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            Payment(
                id=uuid4(), organization_id=ORG_ID,
                payment_date=TODAY, currency="INR",
                amount=Decimal("-100"), created_at=NOW,
            )


class TestImportBatch:
    def test_valid(self) -> None:
        batch = ImportBatch(
            id=uuid4(), organization_id=ORG_ID,
            data_source_id=uuid4(), file_name="test.csv",
            file_type="csv", status=ImportStatus.PENDING,
            created_at=NOW,
        )
        assert batch.successful_rows == 0

    def test_rejects_row_overflow(self) -> None:
        with pytest.raises(ValueError, match="cannot exceed"):
            ImportBatch(
                id=uuid4(), organization_id=ORG_ID,
                data_source_id=uuid4(), file_name="test.csv",
                file_type="csv", status=ImportStatus.COMPLETED,
                created_at=NOW, total_rows=10,
                successful_rows=8, failed_rows=5,
            )


class TestMatch:
    def test_valid(self) -> None:
        src = uuid4()
        tgt = uuid4()
        m = Match(
            id=uuid4(), organization_id=ORG_ID,
            match_type=MatchType.INVOICE_TO_PAYMENT,
            source_record_type=RecordType.INVOICE,
            source_record_id=src,
            target_record_type=RecordType.PAYMENT,
            target_record_id=tgt,
            matched_amount=Decimal("1000"),
            matching_method="exact", confidence=0.95,
            status=MatchStatus.PROPOSED, created_at=NOW,
        )
        assert m.confidence == 0.95

    def test_rejects_same_source_target(self) -> None:
        same_id = uuid4()
        with pytest.raises(ValueError, match="must be different"):
            Match(
                id=uuid4(), organization_id=ORG_ID,
                match_type=MatchType.INVOICE_TO_PAYMENT,
                source_record_type=RecordType.INVOICE,
                source_record_id=same_id,
                target_record_type=RecordType.PAYMENT,
                target_record_id=same_id,
                matched_amount=Decimal("100"),
                matching_method="exact", confidence=0.9,
                status=MatchStatus.PROPOSED, created_at=NOW,
            )

    def test_rejects_invalid_confidence(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            Match(
                id=uuid4(), organization_id=ORG_ID,
                match_type=MatchType.INVOICE_TO_PAYMENT,
                source_record_type=RecordType.INVOICE,
                source_record_id=uuid4(),
                target_record_type=RecordType.PAYMENT,
                target_record_id=uuid4(),
                matched_amount=Decimal("100"),
                matching_method="exact", confidence=1.5,
                status=MatchStatus.PROPOSED, created_at=NOW,
            )
