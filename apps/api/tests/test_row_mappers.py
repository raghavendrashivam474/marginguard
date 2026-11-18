from decimal import Decimal
import pytest

from app.application.services.csv_reader import ParsedCsvRow
from app.application.services.row_mappers import (
    DocumentCategory,
    SupplierRowMapper,
    PurchaseOrderRowMapper,
    InvoiceRowMapper,
    PaymentRowMapper,
    detect_document_category,
    parse_decimal,
    parse_date,
    validate_currency,
)


def test_detect_document_category():
    assert detect_document_category(["supplier_id", "vendor_name", "tax_id"]) == DocumentCategory.SUPPLIER
    assert detect_document_category(["po_number", "vendor_id", "total_amount"]) == DocumentCategory.PURCHASE_ORDER
    assert detect_document_category(["invoice_number", "issue_date", "total_amount"]) == DocumentCategory.INVOICE
    assert detect_document_category(["payment_number", "invoice_id", "amount"]) == DocumentCategory.PAYMENT
    assert detect_document_category(["unknown_col_1", "unknown_col_2"]) is None


def test_validation_helpers():
    # Decimal
    val, err = parse_decimal("123.45", "test_field", 1)
    assert val == Decimal("123.45")
    assert err is None

    val, err = parse_decimal("$1,234.5678", "test_field", 1)
    assert val == Decimal("1234.5678")
    assert err is None

    val, err = parse_decimal("abc", "test_field", 1)
    assert val is None
    assert err is not None
    assert err.field_name == "test_field"

    # Date
    from datetime import date
    val, err = parse_date("2026-03-15", "date_field", 1)
    assert val == date(2026, 3, 15)
    assert err is None

    val, err = parse_date("03/15/2026", "date_field", 1)
    assert val == date(2026, 3, 15)
    assert err is None

    val, err = parse_date("invalid-date", "date_field", 1)
    assert val is None
    assert err is not None

    # Currency
    err = validate_currency("USD", "currency", 1)
    assert err is None

    err = validate_currency("eur", "currency", 1)
    assert err is None

    err = validate_currency("US", "currency", 1)
    assert err is not None


def test_supplier_row_mapper():
    mapper = SupplierRowMapper()
    parsed_row = ParsedCsvRow(
        source_row_number=2,
        data={"vendor_name": "Acme Corp", "tax_id": "TX-12345", "currency": "USD"},
        raw_values=["Acme Corp", "TX-12345", "USD"],
        original_data={"vendor_name": "Acme Corp", "tax_id": "TX-12345", "currency": "USD"},
    )
    supplier, errs = mapper.map_row(parsed_row, import_batch_id="batch-001")
    assert errs == []
    assert supplier is not None
    assert supplier.name == "Acme Corp"
    assert supplier.tax_identifier == "TX-12345"
    assert supplier.import_batch_id == "batch-001"
    assert supplier.source_row_number == 2


def test_purchase_order_row_mapper():
    mapper = PurchaseOrderRowMapper()
    parsed_row = ParsedCsvRow(
        source_row_number=5,
        data={
            "po_number": "PO-1001",
            "vendor_id": "00000000-0000-0000-0000-000000000001",
            "issue_date": "2026-01-10",
            "total_amount": "1500.50",
            "currency": "USD",
        },
        raw_values=["PO-1001", "00000000-0000-0000-0000-000000000001", "2026-01-10", "1500.50", "USD"],
        original_data={"po_number": "PO-1001"},
    )
    po, errs = mapper.map_row(parsed_row, import_batch_id="batch-001")
    assert errs == []
    assert po is not None
    assert po.external_reference == "PO-1001"
    assert po.total_amount == Decimal("1500.50")
    assert po.import_batch_id == "batch-001"
    assert po.source_row_number == 5


def test_invoice_row_mapper():
    mapper = InvoiceRowMapper()
    parsed_row = ParsedCsvRow(
        source_row_number=10,
        data={
            "invoice_number": "INV-2026-001",
            "vendor_id": "00000000-0000-0000-0000-000000000001",
            "issue_date": "2026-02-01",
            "due_date": "2026-03-01",
            "subtotal": "1000.00",
            "tax_amount": "100.00",
            "total_amount": "1100.00",
            "currency": "EUR",
            "status": "APPROVED",
        },
        raw_values=["INV-2026-001"],
        original_data={"invoice_number": "INV-2026-001"},
    )
    inv, errs = mapper.map_row(parsed_row, import_batch_id="batch-002")
    assert errs == []
    assert inv is not None
    assert inv.external_reference == "INV-2026-001"
    assert inv.subtotal == Decimal("1000.00")
    assert inv.tax_amount == Decimal("100.00")
    assert inv.total_amount == Decimal("1100.00")
    assert inv.status == "APPROVED"
    assert inv.import_batch_id == "batch-002"
    assert inv.source_row_number == 10


def test_payment_row_mapper():
    mapper = PaymentRowMapper()
    parsed_row = ParsedCsvRow(
        source_row_number=12,
        data={
            "payment_number": "PAY-999",
            "invoice_id": "00000000-0000-0000-0000-000000000002",
            "payment_date": "2026-02-15",
            "amount": "1100.00",
            "currency": "EUR",
            "payment_method": "ACH",
        },
        raw_values=["PAY-999"],
        original_data={"payment_number": "PAY-999"},
    )
    pym, errs = mapper.map_row(parsed_row, import_batch_id="batch-002")
    assert errs == []
    assert pym is not None
    assert pym.external_reference == "PAY-999"
    assert pym.amount == Decimal("1100.00")
    assert pym.payment_method == "ACH"
    assert pym.import_batch_id == "batch-002"
    assert pym.source_row_number == 12


def test_row_validation_error_aggregation():
    mapper = SupplierRowMapper()
    parsed_row = ParsedCsvRow(
        source_row_number=3,
        data={"vendor_name": "", "currency": "INVALID_CURRENCY_CODE"},
        raw_values=["", "INVALID_CURRENCY_CODE"],
        original_data={"vendor_name": ""},
    )
    supplier, errs = mapper.map_row(parsed_row, import_batch_id="batch-001")
    assert supplier is None
    assert len(errs) >= 2
    err_fields = [e.field_name for e in errs]
    assert "vendor_name" in err_fields
    assert "currency" in err_fields
