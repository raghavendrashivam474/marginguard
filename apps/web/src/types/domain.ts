/**
 * MarginGuard API — domain entity types.
 *
 * These types mirror the backend Pydantic response schemas and the
 * canonical domain model (docs/architecture/domain-model.md).
 *
 * Keep in sync with:
 * - apps/api/app/api/schemas/
 * - contracts/schemas/*.schema.json
 */

import type { Currency, DateString, DateTimeString, MoneyString, UUID } from './api'

// ---------------------------------------------------------------------------
// Organization
// ---------------------------------------------------------------------------

export interface Organization {
  id: UUID
  name: string
  legal_name: string | null
  currency: Currency
  created_at: DateTimeString
  updated_at: DateTimeString
}

export interface OrganizationCreate {
  name: string
  legal_name?: string | null
  currency: Currency
}

// ---------------------------------------------------------------------------
// Supplier
// ---------------------------------------------------------------------------

export interface Supplier {
  id: UUID
  organization_id: UUID
  external_reference: string | null
  name: string
  tax_identifier: string | null
  created_at: DateTimeString
  updated_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Purchase Order
// ---------------------------------------------------------------------------

export interface PurchaseOrder {
  id: UUID
  organization_id: UUID
  supplier_id: UUID
  external_reference: string
  order_date: DateString
  currency: Currency
  total_amount: MoneyString
  status: string
  created_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Invoice
// ---------------------------------------------------------------------------

export interface Invoice {
  id: UUID
  organization_id: UUID
  supplier_id: UUID
  purchase_order_id: UUID | null
  external_reference: string
  invoice_date: DateString
  due_date: DateString | null
  currency: Currency
  subtotal: MoneyString
  tax_amount: MoneyString
  total_amount: MoneyString
  created_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Payment
// ---------------------------------------------------------------------------

export interface Payment {
  id: UUID
  organization_id: UUID
  supplier_id: UUID | null
  external_reference: string | null
  payment_date: DateString
  currency: Currency
  amount: MoneyString
  payment_method: string | null
  created_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Finding
// ---------------------------------------------------------------------------

export type FindingType =
  | 'duplicate_invoice'
  | 'duplicate_payment'
  | 'invoice_payment_mismatch'
  | 'purchase_order_price_mismatch'
  | 'unmatched_payment'

export type FindingStatus = 'detected' | 'under_review' | 'confirmed' | 'dismissed' | 'resolved'

export type Severity = 'low' | 'medium' | 'high' | 'critical'

export interface Finding {
  id: UUID
  organization_id: UUID
  finding_type: FindingType
  severity: Severity
  status: FindingStatus
  title: string
  description: string
  amount_at_risk: MoneyString
  currency: Currency
  confidence: number
  rule_id: string
  rule_version: string
  created_at: DateTimeString
  updated_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------

export interface CalculationDetails {
  formula: string
  inputs: Record<string, unknown>
  result: string
}

export interface Evidence {
  id: UUID
  organization_id: UUID
  finding_id: UUID
  evidence_type: string
  source_record_type: string
  source_record_id: UUID
  description: string
  calculation_details: CalculationDetails | null
  created_at: DateTimeString
}

// ---------------------------------------------------------------------------
// Import Batch
// ---------------------------------------------------------------------------

export type ImportStatus = 'pending' | 'processing' | 'completed' | 'partially_completed' | 'failed'

export interface ImportBatch {
  id: UUID
  organization_id: UUID
  data_source_id: UUID
  file_name: string
  file_type: string
  status: ImportStatus
  total_rows: number | null
  successful_rows: number
  failed_rows: number
  created_at: DateTimeString
  completed_at: DateTimeString | null
}
