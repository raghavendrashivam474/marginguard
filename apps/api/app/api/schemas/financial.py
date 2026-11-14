"""MarginGuard API — Financial record schemas.

Pydantic models for Supplier, PurchaseOrder, Invoice, and Payment.
Monetary values are serialized as strings to preserve Decimal precision.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------
class SupplierResponse(BaseModel):
    id: UUID
    organization_id: UUID
    external_reference: str | None
    name: str
    tax_identifier: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Purchase Order
# ---------------------------------------------------------------------------
class PurchaseOrderResponse(BaseModel):
    id: UUID
    organization_id: UUID
    supplier_id: UUID
    external_reference: str
    order_date: date
    currency: str
    total_amount: Decimal
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------
class InvoiceResponse(BaseModel):
    id: UUID
    organization_id: UUID
    supplier_id: UUID
    purchase_order_id: UUID | None
    external_reference: str
    invoice_date: date
    due_date: date | None
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------
class PaymentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    supplier_id: UUID | None
    external_reference: str | None
    payment_date: date
    currency: str
    amount: Decimal
    payment_method: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
