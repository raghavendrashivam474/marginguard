"""
Canonical Domain Mappers, Template Detector, and Row Validators for Ingestion.
Enforces strict schema rules, numeric precision (Decimal), ISO 4217 currencies,
and maps incoming parsed CSV rows into domain entities with provenance.
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import NAMESPACE_OID, UUID, uuid4, uuid5

from app.application.services.csv_reader import ParsedCsvRow
from app.domain.entities import Invoice, Payment, PurchaseOrder, Supplier


class DocumentCategory:
    SUPPLIER = "supplier"
    PURCHASE_ORDER = "purchase_order"
    INVOICE = "invoice"
    PAYMENT = "payment"


class RowValidationError:
    def __init__(
        self,
        source_row_number: int,
        field_name: str,
        error_code: str,
        message: str,
        original_value: Any = None,
    ) -> None:
        self.source_row_number = source_row_number
        self.field_name = field_name
        self.error_code = error_code
        self.message = message
        self.original_value = original_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_row_number": self.source_row_number,
            "field_name": self.field_name,
            "error_code": self.error_code,
            "message": self.message,
            "original_value": str(self.original_value) if self.original_value is not None else None,
        }


def detect_document_category(headers: list[str]) -> str | None:
    """Detect document type based on header clues."""
    hdr_set = {h.lower().strip() for h in headers}

    if (
        "invoice_number" in hdr_set
        or "invoice_no" in hdr_set
        or "subtotal_amount" in hdr_set
        or "subtotal" in hdr_set
    ):
        return DocumentCategory.INVOICE
    if "po_number" in hdr_set or "order_date" in hdr_set:
        return DocumentCategory.PURCHASE_ORDER
    if "payment_reference" in hdr_set or "payment_number" in hdr_set or "payment_date" in hdr_set:
        return DocumentCategory.PAYMENT
    if (
        "supplier_code" in hdr_set
        or "supplier_name" in hdr_set
        or "vendor_name" in hdr_set
        or "supplier_id" in hdr_set
        or "tax_id" in hdr_set
    ):
        return DocumentCategory.SUPPLIER

    return None


ISO_4217_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "CAD",
    "AUD",
    "JPY",
    "CHF",
    "CNY",
    "INR",
    "BRL",
    "SEK",
    "NZD",
    "MXN",
    "SGD",
    "HKD",
    "NOK",
    "KRW",
    "TRY",
    "ZAR",
    "AED",
}


def parse_decimal(
    val: str, field_name: str, row_num: int
) -> tuple[Decimal | None, RowValidationError | None]:
    """Parse strict Decimal without floating-point conversion, handling optional $ and commas."""
    if not val or not str(val).strip():
        return None, RowValidationError(
            source_row_number=row_num,
            field_name=field_name,
            error_code="MISSING_VALUE",
            message=f"Field '{field_name}' is required.",
            original_value=val,
        )

    cleaned = str(val).strip().replace("$", "").replace(",", "")
    try:
        dec = Decimal(cleaned)
        return dec, None
    except InvalidOperation:
        return None, RowValidationError(
            source_row_number=row_num,
            field_name=field_name,
            error_code="INVALID_MONETARY_VALUE",
            message=f"Field '{field_name}' must be a valid monetary decimal, got '{val}'.",
            original_value=val,
        )


def parse_date(
    val: str, field_name: str, row_num: int, required: bool = True
) -> tuple[date | None, RowValidationError | None]:
    """Parse string date into python date object.
    If required is False and value is missing, returns current UTC date.
    """
    if not val or not str(val).strip():
        if not required:
            return datetime.utcnow().date(), None
        return None, RowValidationError(
            source_row_number=row_num,
            field_name=field_name,
            error_code="MISSING_VALUE",
            message=f"Field '{field_name}' is required.",
            original_value=val,
        )

    s = str(val).strip()
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in date_formats:
        try:
            parsed_dt = datetime.strptime(s, fmt).date()
            return parsed_dt, None
        except ValueError:
            continue

    return None, RowValidationError(
        source_row_number=row_num,
        field_name=field_name,
        error_code="INVALID_DATE_FORMAT",
        message=f"Field '{field_name}' must be a valid date, got '{val}'.",
        original_value=val,
    )


def validate_currency(val: str, field_name: str, row_num: int) -> RowValidationError | None:
    """Validate currency against ISO 4217 codes."""
    if not val or not str(val).strip():
        return None  # Currency optional or defaults to USD

    c_code = str(val).strip().upper()
    if c_code not in ISO_4217_CURRENCIES:
        return RowValidationError(
            source_row_number=row_num,
            field_name=field_name,
            error_code="INVALID_CURRENCY_CODE",
            message=f"Field '{field_name}' contains invalid ISO 4217 currency code '{val}'.",
            original_value=val,
        )
    return None


def parse_vendor_uuid(vendor_id_raw: str | None) -> UUID:
    """Parse UUID or generate deterministic UUID from raw string vendor code."""
    if not vendor_id_raw or not vendor_id_raw.strip():
        return uuid4()
    cleaned = vendor_id_raw.strip()
    try:
        return UUID(cleaned)
    except ValueError:
        return uuid5(NAMESPACE_OID, cleaned)


class SupplierRowMapper:
    def map_row(
        self, parsed_row: ParsedCsvRow, import_batch_id: str, organization_id: UUID | None = None
    ) -> tuple[Supplier | None, list[RowValidationError]]:
        row_num = parsed_row.source_row_number
        data = parsed_row.data
        errors: list[RowValidationError] = []

        name = data.get("supplier_name") or data.get("vendor_name") or data.get("name")
        if not name or not name.strip():
            errors.append(
                RowValidationError(
                    source_row_number=row_num,
                    field_name="vendor_name",
                    error_code="MISSING_VALUE",
                    message="Supplier name is required.",
                    original_value=name,
                )
            )

        currency = data.get("currency") or data.get("default_currency") or "USD"
        curr_err = validate_currency(currency, "currency", row_num)
        if curr_err:
            errors.append(curr_err)

        if errors:
            return None, errors

        tax_id = data.get("tax_identifier") or data.get("tax_id") or data.get("tax_number")
        ext_ref = (
            data.get("supplier_id") or data.get("external_reference") or data.get("supplier_code")
        )
        now = datetime.utcnow()

        supplier = Supplier(
            id=uuid4(),
            organization_id=organization_id or uuid4(),
            name=name.strip(),
            tax_identifier=tax_id.strip() if tax_id else None,
            external_reference=ext_ref.strip() if ext_ref else None,
            created_at=now,
            updated_at=now,
            import_batch_id=import_batch_id,
            source_row_number=row_num,
            original_data=parsed_row.original_data,
        )
        return supplier, []


class PurchaseOrderRowMapper:
    def map_row(
        self, parsed_row: ParsedCsvRow, import_batch_id: str, organization_id: UUID | None = None
    ) -> tuple[PurchaseOrder | None, list[RowValidationError]]:
        row_num = parsed_row.source_row_number
        data = parsed_row.data
        errors: list[RowValidationError] = []

        po_number = (
            data.get("po_number") or data.get("order_number") or data.get("external_reference")
        )
        if not po_number or not po_number.strip():
            errors.append(
                RowValidationError(
                    source_row_number=row_num,
                    field_name="po_number",
                    error_code="MISSING_VALUE",
                    message="Purchase order number is required.",
                    original_value=po_number,
                )
            )

        vendor_id_raw = data.get("supplier_id") or data.get("vendor_id")
        vendor_uuid = parse_vendor_uuid(vendor_id_raw)

        issue_date_raw = data.get("order_date") or data.get("issue_date") or data.get("po_date")
        issue_date, date_err = parse_date(
            issue_date_raw or "", "issue_date", row_num, required=False
        )
        if date_err:
            errors.append(date_err)

        total_amount_raw = data.get("total_amount") or data.get("amount")
        total_amount, amount_err = parse_decimal(total_amount_raw or "", "total_amount", row_num)
        if amount_err:
            errors.append(amount_err)

        currency = data.get("currency") or "USD"
        curr_err = validate_currency(currency, "currency", row_num)
        if curr_err:
            errors.append(curr_err)

        if errors:
            return None, errors

        po = PurchaseOrder(
            id=uuid4(),
            organization_id=organization_id or uuid4(),
            supplier_id=vendor_uuid,
            external_reference=po_number.strip(),
            order_date=issue_date,  # type: ignore[arg-type]
            currency=currency.strip().upper(),
            total_amount=total_amount,  # type: ignore[arg-type]
            status="ISSUED",
            created_at=datetime.utcnow(),
            import_batch_id=import_batch_id,
            source_row_number=row_num,
            original_data=parsed_row.original_data,
        )
        return po, []


class InvoiceRowMapper:
    def map_row(
        self, parsed_row: ParsedCsvRow, import_batch_id: str, organization_id: UUID | None = None
    ) -> tuple[Invoice | None, list[RowValidationError]]:
        row_num = parsed_row.source_row_number
        data = parsed_row.data
        errors: list[RowValidationError] = []

        inv_num = (
            data.get("invoice_number") or data.get("invoice_no") or data.get("external_reference")
        )
        if not inv_num or not inv_num.strip():
            errors.append(
                RowValidationError(
                    source_row_number=row_num,
                    field_name="invoice_number",
                    error_code="MISSING_VALUE",
                    message="Invoice number is required.",
                    original_value=inv_num,
                )
            )

        vendor_id_raw = data.get("supplier_id") or data.get("vendor_id")
        vendor_uuid = parse_vendor_uuid(vendor_id_raw)

        issue_date_raw = data.get("issue_date") or data.get("invoice_date")
        issue_date, date_err = parse_date(
            issue_date_raw or "", "issue_date", row_num, required=False
        )
        if date_err:
            errors.append(date_err)

        due_date_raw = data.get("due_date")
        due_date = None
        if due_date_raw and due_date_raw.strip():
            due_date, due_err = parse_date(due_date_raw, "due_date", row_num, required=False)
            if due_err:
                errors.append(due_err)

        subtotal_raw = data.get("subtotal") or data.get("subtotal_amount")
        subtotal = Decimal("0.0000")
        if subtotal_raw and subtotal_raw.strip():
            parsed_sub, sub_err = parse_decimal(subtotal_raw, "subtotal", row_num)
            if sub_err:
                errors.append(sub_err)
            elif parsed_sub is not None:
                subtotal = parsed_sub

        tax_raw = data.get("tax_amount") or data.get("tax")
        tax_amt = Decimal("0.0000")
        if tax_raw and tax_raw.strip():
            parsed_tax, tax_err = parse_decimal(tax_raw, "tax_amount", row_num)
            if tax_err:
                errors.append(tax_err)
            elif parsed_tax is not None:
                tax_amt = parsed_tax

        total_raw = data.get("total_amount") or data.get("total")
        total_amt, total_err = parse_decimal(total_raw or "", "total_amount", row_num)
        if total_err:
            errors.append(total_err)

        if subtotal == Decimal("0.0000") and total_amt is not None:
            subtotal = total_amt - tax_amt

        currency = data.get("currency") or "USD"
        curr_err = validate_currency(currency, "currency", row_num)
        if curr_err:
            errors.append(curr_err)

        status = data.get("status") or "PENDING"

        if errors:
            return None, errors

        invoice = Invoice(
            id=uuid4(),
            organization_id=organization_id or uuid4(),
            supplier_id=vendor_uuid,
            external_reference=inv_num.strip(),
            invoice_date=issue_date,  # type: ignore[arg-type]
            due_date=due_date,
            currency=currency.strip().upper(),
            subtotal=subtotal,
            tax_amount=tax_amt,
            total_amount=total_amt,  # type: ignore[arg-type]
            status=status.strip().upper(),
            created_at=datetime.utcnow(),
            import_batch_id=import_batch_id,
            source_row_number=row_num,
            original_data=parsed_row.original_data,
        )
        return invoice, []


class PaymentRowMapper:
    def map_row(
        self, parsed_row: ParsedCsvRow, import_batch_id: str, organization_id: UUID | None = None
    ) -> tuple[Payment | None, list[RowValidationError]]:
        row_num = parsed_row.source_row_number
        data = parsed_row.data
        errors: list[RowValidationError] = []

        pym_num = (
            data.get("payment_number") or data.get("payment_reference") or data.get("reference")
        )
        if not pym_num or not pym_num.strip():
            errors.append(
                RowValidationError(
                    source_row_number=row_num,
                    field_name="payment_number",
                    error_code="MISSING_VALUE",
                    message="Payment reference/number is required.",
                    original_value=pym_num,
                )
            )

        invoice_id_raw = data.get("invoice_id")
        inv_uuid = parse_vendor_uuid(invoice_id_raw) if invoice_id_raw else None

        pym_date_raw = data.get("payment_date") or data.get("date")
        pym_date, date_err = parse_date(pym_date_raw or "", "payment_date", row_num, required=False)
        if date_err:
            errors.append(date_err)

        amount_raw = data.get("amount") or data.get("total_amount")
        amount, amt_err = parse_decimal(amount_raw or "", "amount", row_num)
        if amt_err:
            errors.append(amt_err)

        currency = data.get("currency") or "USD"
        curr_err = validate_currency(currency, "currency", row_num)
        if curr_err:
            errors.append(curr_err)

        payment_method = data.get("payment_method") or "ACH"

        if errors:
            return None, errors

        payment = Payment(
            id=uuid4(),
            organization_id=organization_id or uuid4(),
            invoice_id=inv_uuid,
            external_reference=pym_num.strip(),
            payment_date=pym_date,  # type: ignore[arg-type]
            currency=currency.strip().upper(),
            amount=amount,  # type: ignore[arg-type]
            payment_method=payment_method.strip().upper(),
            created_at=datetime.utcnow(),
            import_batch_id=import_batch_id,
            source_row_number=row_num,
            original_data=parsed_row.original_data,
        )
        return payment, []
