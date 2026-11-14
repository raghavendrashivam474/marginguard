"""MarginGuard domain enumerations.

These enumerations define the allowed values for domain entity attributes.
They live in the Domain layer and must not import any infrastructure framework.
"""

from enum import StrEnum


class ImportStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"


class FindingType(StrEnum):
    DUPLICATE_INVOICE = "duplicate_invoice"
    DUPLICATE_PAYMENT = "duplicate_payment"
    INVOICE_PAYMENT_MISMATCH = "invoice_payment_mismatch"
    PURCHASE_ORDER_PRICE_MISMATCH = "purchase_order_price_mismatch"
    UNMATCHED_PAYMENT = "unmatched_payment"


class FindingStatus(StrEnum):
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MatchType(StrEnum):
    INVOICE_TO_PAYMENT = "invoice_to_payment"
    INVOICE_TO_PURCHASE_ORDER = "invoice_to_purchase_order"
    PAYMENT_TO_INVOICE = "payment_to_invoice"


class MatchStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class RecordType(StrEnum):
    INVOICE = "invoice"
    PAYMENT = "payment"
    PURCHASE_ORDER = "purchase_order"
    SUPPLIER = "supplier"


class InvestigationStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CONCLUDED = "concluded"
