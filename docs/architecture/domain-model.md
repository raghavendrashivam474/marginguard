# Domain Model

**Project:** MarginGuard
**Sprint:** MG-S0.2
**Status:** Accepted
**Last Updated:** 2025-11-14
**ADR Reference:** ADR-003

---

## 1. Purpose

This document defines the canonical domain vocabulary for MarginGuard. Every developer, contract, database model, and API schema must use the same entity names, attribute names, and business rules defined here.

If a term is ambiguous, this document is the authoritative source.

---

## 2. Architectural Position

The domain model lives in the **Domain layer** (`app/domain/`). It must not import FastAPI, SQLAlchemy, Pydantic, or any infrastructure framework. Domain entities are plain Python dataclasses or value objects.

```text
Domain ──▶ no external dependencies
Application ──▶ Domain
Infrastructure ──▶ Domain + Application (ports)
Interfaces ──▶ Application + Domain
```

---

## 3. Entity Catalogue

### 3.1 Organization

**Purpose:** Represents the business using MarginGuard. Acts as the tenant boundary for all data isolation.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `name` | str | Yes | Display name |
| `legal_name` | str \| None | No | Formal registered name |
| `currency` | Currency | Yes | ISO 4217 code (e.g. `INR`, `USD`) |
| `created_at` | datetime | Yes | UTC, timezone-aware |
| `updated_at` | datetime | Yes | UTC, timezone-aware |

**Invariants:**
- An organization must have exactly one base currency.
- `name` must not be empty or whitespace-only.
- `currency` must be a valid ISO 4217 code.

**Relationships:**
- Has many DataSources, ImportBatches, Suppliers, PurchaseOrders, Invoices, Payments, Findings, Evidence records, Investigations.

---

### 3.2 DataSource

**Purpose:** Represents the origin of imported business records (e.g. "Tally Export", "Manual CSV Upload").

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `source_type` | str | Yes | e.g. `csv`, `excel`, `erp_export`, `accounting_export` |
| `source_name` | str | Yes | Human-readable label |
| `created_at` | datetime | Yes | UTC |

**Invariants:**
- Must belong to exactly one organization.
- `source_type` is an open enumeration (new types can be added without schema changes).

**Relationships:**
- Belongs to one Organization.
- Has many ImportBatches.

---

### 3.3 ImportBatch

**Purpose:** Represents a single import operation with lifecycle tracking.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `data_source_id` | UUID | Yes | FK → DataSource |
| `file_name` | str | Yes | Original file name |
| `file_type` | str | Yes | e.g. `csv`, `xlsx` |
| `status` | ImportStatus | Yes | See statuses below |
| `total_rows` | int \| None | No | Set when processing begins |
| `successful_rows` | int | Yes | Default 0 |
| `failed_rows` | int | Yes | Default 0 |
| `created_at` | datetime | Yes | UTC |
| `completed_at` | datetime \| None | No | Set when status reaches terminal state |

**Statuses:** `pending` → `processing` → `completed` | `partially_completed` | `failed`

**Invariants:**
- `successful_rows + failed_rows <= total_rows` when `total_rows` is set.
- `completed_at` must be set when status is `completed`, `partially_completed`, or `failed`.
- `completed_at` must be None when status is `pending` or `processing`.

**Relationships:**
- Belongs to one Organization and one DataSource.
- Associated with imported records via source provenance fields.

---

### 3.4 Supplier

**Purpose:** Represents a vendor or supplier that the organization transacts with.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `external_reference` | str \| None | No | Supplier ID from source system |
| `name` | str | Yes | Display name |
| `tax_identifier` | str \| None | No | GSTIN, VAT number, etc. |
| `created_at` | datetime | Yes | UTC |
| `updated_at` | datetime | Yes | UTC |

**Invariants:**
- Supplier names are **not** globally unique. Two different organizations may have suppliers with the same name. Even within one organization, name alone is not a reliable unique key.
- `external_reference` uniqueness is scoped to `(organization_id, external_reference)` when non-null.

**Relationships:**
- Belongs to one Organization.
- Has many PurchaseOrders, Invoices, Payments.

---

### 3.5 PurchaseOrder

**Purpose:** Represents a purchase order issued by the organization to a supplier.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `supplier_id` | UUID | Yes | FK → Supplier |
| `external_reference` | str | Yes | PO number from source system |
| `order_date` | date | Yes | Original document date |
| `currency` | Currency | Yes | ISO 4217 |
| `total_amount` | Money | Yes | Decimal, non-negative |
| `status` | str | Yes | e.g. `draft`, `issued`, `fulfilled`, `cancelled` |
| `created_at` | datetime | Yes | UTC |

**Invariants:**
- `total_amount` must be >= 0.
- `currency` should match the organization's base currency in the initial implementation. Cross-currency POs are deferred.
- `order_date` is the business document date, not the import timestamp.

**Relationships:**
- Belongs to one Organization and one Supplier.
- May be referenced by many Invoices.

---

### 3.6 Invoice

**Purpose:** Represents an invoice received from a supplier.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `supplier_id` | UUID | Yes | FK → Supplier |
| `purchase_order_id` | UUID \| None | No | FK → PurchaseOrder |
| `external_reference` | str | Yes | Invoice number from supplier |
| `invoice_date` | date | Yes | Original document date |
| `due_date` | date \| None | No | Payment due date |
| `currency` | Currency | Yes | ISO 4217 |
| `subtotal` | Money | Yes | Decimal, before tax |
| `tax_amount` | Money | Yes | Decimal, >= 0 |
| `total_amount` | Money | Yes | Decimal, = subtotal + tax_amount |
| `created_at` | datetime | Yes | UTC |

**Invariants:**
- `total_amount = subtotal + tax_amount` (within rounding tolerance of the currency's minor unit).
- `subtotal` and `tax_amount` must be >= 0.
- Invoice numbers (`external_reference`) are **not** globally unique. Duplicate detection must consider the composite key: `(organization_id, supplier_id, external_reference, invoice_date, total_amount)`.
- An invoice may exist without a linked purchase order.

**Relationships:**
- Belongs to one Organization and one Supplier.
- Optionally references one PurchaseOrder.
- May be linked to many Payments via Match records.

---

### 3.7 Payment

**Purpose:** Represents a payment made by the organization.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `supplier_id` | UUID \| None | No | FK → Supplier (may be unknown at import time) |
| `external_reference` | str \| None | No | Payment reference / transaction ID |
| `payment_date` | date | Yes | Original document date |
| `currency` | Currency | Yes | ISO 4217 |
| `amount` | Money | Yes | Decimal, > 0 |
| `payment_method` | str \| None | No | e.g. `bank_transfer`, `cheque`, `cash` |
| `created_at` | datetime | Yes | UTC |

**Invariants:**
- `amount` must be > 0.
- A payment may relate to one or more invoices. An invoice may be settled through multiple payments. **Do not enforce a 1:1 relationship.**
- `supplier_id` may be null if the payment source does not identify the supplier.

**Relationships:**
- Belongs to one Organization.
- Optionally belongs to one Supplier.
- May be linked to many Invoices via Match records.

---

### 3.8 Match

**Purpose:** Represents a proposed or established relationship between two financial records.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `match_type` | MatchType | Yes | See types below |
| `source_record_type` | RecordType | Yes | e.g. `invoice`, `payment`, `purchase_order` |
| `source_record_id` | UUID | Yes | ID of the source record |
| `target_record_type` | RecordType | Yes | e.g. `invoice`, `payment`, `purchase_order` |
| `target_record_id` | UUID | Yes | ID of the target record |
| `matched_amount` | Money | Yes | Decimal, the amount this match covers |
| `matching_method` | str | Yes | e.g. `exact_reference`, `fuzzy_amount`, `manual` |
| `confidence` | float | Yes | 0.0–1.0 |
| `status` | MatchStatus | Yes | See statuses below |
| `created_at` | datetime | Yes | UTC |

**Match Types:** `invoice_to_payment`, `invoice_to_purchase_order`, `payment_to_invoice`

**Statuses:** `proposed`, `confirmed`, `rejected`

**Invariants:**
- `confidence` must be in [0.0, 1.0].
- `matched_amount` must be > 0.
- `source_record_id` must not equal `target_record_id`.
- Polymorphic references (`source_record_type` + `source_record_id`) are used instead of multiple nullable FK columns. This preserves flexibility at the cost of database-level FK enforcement. Application-layer validation must ensure referential integrity.

**Design Note:** A fully normalized alternative would use separate junction tables per match type (e.g. `invoice_payment_match`, `invoice_po_match`). The polymorphic approach was chosen for initial flexibility and will be revisited in a future ADR if referential integrity issues arise.

**Relationships:**
- Belongs to one Organization.
- References two domain records polymorphically.

---

### 3.9 Finding

**Purpose:** Represents a potential financial discrepancy detected by the reconciliation engine.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `finding_type` | FindingType | Yes | See types below |
| `severity` | Severity | Yes | `low`, `medium`, `high`, `critical` |
| `status` | FindingStatus | Yes | See statuses below |
| `title` | str | Yes | Short human-readable summary |
| `description` | str | Yes | Detailed explanation |
| `amount_at_risk` | Money | Yes | Decimal, the potential financial exposure |
| `currency` | Currency | Yes | ISO 4217 |
| `confidence` | float | Yes | 0.0–1.0 |
| `rule_id` | str | Yes | Identifier of the detection rule |
| `rule_version` | str | Yes | Version of the rule that produced this finding |
| `created_at` | datetime | Yes | UTC |
| `updated_at` | datetime | Yes | UTC |

**Finding Types:**
- `duplicate_invoice`
- `duplicate_payment`
- `invoice_payment_mismatch`
- `purchase_order_price_mismatch`
- `unmatched_payment`

**Statuses:** `detected` → `under_review` → `confirmed` | `dismissed` | `resolved`

**Invariants:**
- A finding is an **investigation candidate**, not proof of fraud or loss.
- `amount_at_risk` represents the potential exposure for *this specific finding*. It must not be naively summed across findings to compute portfolio-level exposure, because the same underlying transaction may appear in multiple findings.
- `confidence` must be in [0.0, 1.0].
- `rule_id` and `rule_version` together enable reproducibility: given the same data and the same rule version, the finding should be deterministically reproducible.

**Relationships:**
- Belongs to one Organization.
- Has many Evidence records.
- May have one active Investigation.

---

### 3.10 Evidence

**Purpose:** Represents structured supporting information behind a finding.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `finding_id` | UUID | Yes | FK → Finding |
| `evidence_type` | str | Yes | e.g. `record_reference`, `calculation`, `comparison` |
| `source_record_type` | RecordType | Yes | e.g. `invoice`, `payment` |
| `source_record_id` | UUID | Yes | ID of the supporting record |
| `description` | str | Yes | Human-readable explanation |
| `calculation_details` | dict \| None | No | Structured inputs and formula |
| `created_at` | datetime | Yes | UTC |

**Invariants:**
- Evidence must reference a real source record. The combination of `source_record_type` + `source_record_id` must resolve to an existing domain entity.
- `calculation_details` should preserve the raw inputs and formula, not just the result. This enables auditors to reconstruct the finding.
- A human-readable `description` alone is insufficient. Structured evidence is mandatory for calculation-type evidence.

**Relationships:**
- Belongs to one Organization and one Finding.
- References one source record polymorphically.

---

### 3.11 Investigation

**Purpose:** Represents the human review process for a finding.

| Attribute | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID | Yes | System-generated |
| `organization_id` | UUID | Yes | FK → Organization |
| `finding_id` | UUID | Yes | FK → Finding |
| `status` | InvestigationStatus | Yes | `open`, `in_progress`, `concluded` |
| `review_notes` | str \| None | No | Free-text notes from the investigator |
| `created_at` | datetime | Yes | UTC |
| `updated_at` | datetime | Yes | UTC |

**Invariants:**
- A finding may have at most one active (non-concluded) investigation at a time.
- Full workflow functionality is deferred. This entity establishes the vocabulary and relationship only.

**Relationships:**
- Belongs to one Organization and one Finding.

---

## 4. Value Objects

### 4.1 Money

An immutable value object combining an amount and a currency.

```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str  # ISO 4217

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money amount must be a Decimal")
        if self.amount < 0:
            raise ValueError("Money amount must be non-negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO 4217 code")
```

**Rules:**
- Never construct from `float`. Always from `str` or `Decimal`.
- Arithmetic between two `Money` values requires matching currencies.
- Comparison between different currencies must raise an error.

### 4.2 Currency
A string value constrained to valid ISO 4217 codes. For MG-S0.2, validation is limited to format (3 uppercase letters). A full registry check can be added later.

## 5. Enumerations

| Enum | Values |
| :--- | :--- |
| `ImportStatus` | `pending`, `processing`, `completed`, `partially_completed`, `failed` |
| `FindingType` | `duplicate_invoice`, `duplicate_payment`, `invoice_payment_mismatch`, `purchase_order_price_mismatch`, `unmatched_payment` |
| `FindingStatus` | `detected`, `under_review`, `confirmed`, `dismissed`, `resolved` |
| `Severity` | `low`, `medium`, `high`, `critical` |
| `MatchType` | `invoice_to_payment`, `invoice_to_purchase_order`, `payment_to_invoice` |
| `MatchStatus` | `proposed`, `confirmed`, `rejected` |
| `RecordType` | `invoice`, `payment`, `purchase_order`, `supplier` |
| `InvestigationStatus` | `open`, `in_progress`, `concluded` |

## 6. Cross-Cutting Business Rules
- **All monetary values use `Decimal`, never `float`.**
- **Every monetary value has an associated currency.** Silent cross-currency comparison is forbidden.
- **Timestamps are UTC and timezone-aware.** Document dates (`invoice_date`, `payment_date`, `order_date`) are plain `date` objects preserving the original business date.
- **Missing ≠ zero.** A null amount, null reference, or null supplier must not be silently replaced with a default.
- **Source provenance is preserved.** Every imported record retains its import batch, source file, and external reference.
- **Deterministic findings.** Given the same data and the same rule version, the reconciliation engine must produce identical findings.
- **Human review before confirmation.** A finding with status `detected` is a candidate, not a verdict.

## 7. Deferred Concepts
The following are acknowledged but not fully modeled in MG-S0.2:
- Multi-currency support and exchange rates
- Line-item level matching (current model is header-level)
- Approval workflows and audit trails
- User and role entities (authentication deferred)
- Notification and alerting preferences