# Financial Ingestion CSV Templates Specification

This document defines the supported CSV templates for ingestion into MarginGuard canonical financial domain entities.

---

## 1. Supplier CSV Template (`supplier`)

Used to register vendors/suppliers transacting with the organization.

### Supported Headers

| CSV Column | Required | Type | Example | Description / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `supplier_name` / `vendor_name` / `name` | Yes | String | Acme Corp | Unique legal or trading name of the supplier |
| `tax_identifier` / `tax_id` / `tax_number` | No | String | TX-98765 | Tax registration number (VAT/EIN) |
| `supplier_code` / `supplier_id` / `external_reference` | No | String | SUPP-1001 | Unique external reference code |
| `currency` / `default_currency` | No | ISO-4217 | USD | Default transaction currency (default: `USD`) |

### Example CSV Content

```csv
supplier_name,tax_id,supplier_code,currency
Acme Corp,TX-98765,SUPP-1001,USD
Beta Logistics,TX-54321,SUPP-1002,EUR

```

---

## 2. Purchase Order CSV Template (`purchase_order`)

Used to record purchase orders issued to suppliers.

### Supported Headers

| CSV Column | Required | Type | Example | Description / Notes |
| --- | --- | --- | --- | --- |
| `po_number` / `order_number` / `external_reference` | Yes | String | PO-2026-001 | External PO identifier |
| `supplier_id` / `vendor_id` | No | UUID / String | 00000000-0000-0000-0000-000000000001 | Associated vendor UUID or external reference |
| `order_date` / `issue_date` / `po_date` | No | ISO Date | 2026-03-01 | Issue date (format: `YYYY-MM-DD`, `MM/DD/YYYY`, `YYYY/MM/DD`). Defaults to current UTC date if omitted. |
| `total_amount` / `amount` | Yes | Monetary Decimal | 1500.50 | Total purchase order amount (parsed strictly as Decimal) |
| `currency` | No | ISO-4217 | EUR | Transaction currency code (default: `USD`) |

### Example CSV Content

```csv
po_number,supplier_id,order_date,total_amount,currency
PO-2026-001,00000000-0000-0000-0000-000000000001,2026-03-01,1500.50,EUR
PO-2026-002,00000000-0000-0000-0000-000000000002,2026-03-05,2750.00,USD

```

---

## 3. Invoice CSV Template (`invoice`)

Used to record invoices received from suppliers.

### Supported Headers

| CSV Column | Required | Type | Example | Description / Notes |
| --- | --- | --- | --- | --- |
| `invoice_number` / `invoice_no` / `external_reference` | Yes | String | INV-9901 | External invoice reference number |
| `supplier_id` / `vendor_id` | No | UUID / String | 00000000-0000-0000-0000-000000000001 | Associated vendor UUID or external reference |
| `issue_date` / `invoice_date` | No | ISO Date | 2026-03-10 | Invoice issue date. Defaults to current UTC date if omitted. |
| `due_date` | No | ISO Date | 2026-04-10 | Payment due date |
| `subtotal` / `subtotal_amount` | No | Monetary Decimal | 1000.00 | Net amount before tax (inferred as `total - tax` if omitted) |
| `tax_amount` / `tax` | No | Monetary Decimal | 100.00 | Tax amount |
| `total_amount` / `total` | Yes | Monetary Decimal | 1100.00 | Total invoice amount |
| `currency` | No | ISO-4217 | EUR | Transaction currency code (default: `USD`) |
| `status` | No | String | PENDING | Status (`PENDING`, `APPROVED`, `PAID`, `CANCELLED`) |

### Example CSV Content

```csv
invoice_number,supplier_id,issue_date,subtotal,tax_amount,total_amount,currency
INV-9901,00000000-0000-0000-0000-000000000001,2026-03-10,1000.00,100.00,1100.00,EUR
INV-9902,00000000-0000-0000-0000-000000000002,2026-03-12,500.00,50.00,550.00,USD

```

---

## 4. Payment CSV Template (`payment`)

Used to record outgoing payments made by the organization.

### Supported Headers

| CSV Column | Required | Type | Example | Description / Notes |
| --- | --- | --- | --- | --- |
| `payment_number` / `payment_reference` / `reference` | Yes | String | PAY-8801 | External payment reference |
| `invoice_id` | No | UUID / String | 00000000-0000-0000-0000-000000000002 | Settled invoice UUID or reference |
| `payment_date` / `date` | No | ISO Date | 2026-03-15 | Payment execution date. Defaults to current UTC date if omitted. |
| `amount` / `total_amount` | Yes | Monetary Decimal | 1100.00 | Payment amount |
| `currency` | No | ISO-4217 | EUR | Payment currency (default: `USD`) |
| `payment_method` | No | String | ACH | Method (`ACH`, `WIRE`, `CHECK`, `CREDIT_CARD`) |

### Example CSV Content

```csv
payment_reference,invoice_id,payment_date,amount,currency,payment_method
PAY-8801,00000000-0000-0000-0000-000000000002,2026-03-15,1100.00,EUR,ACH
PAY-8802,00000000-0000-0000-0000-000000000003,2026-03-16,550.00,USD,WIRE

```

```