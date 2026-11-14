/**
 * MarginGuard API — shared API types.
 *
 * These types mirror the backend error envelope and pagination contracts
 * defined in ADR-004 and contracts/schemas/common.schema.json.
 *
 * Monetary values are typed as `string` to preserve Decimal precision
 * across JSON transport (ADR-002). Parse with a Decimal library or
 * convert to number only for display purposes.
 */

// ---------------------------------------------------------------------------
// Error envelope
// ---------------------------------------------------------------------------

export interface ApiErrorDetail {
  field: string | null
  issue: string
}

export interface ApiErrorBody {
  code: string
  message: string
  details: ApiErrorDetail[]
  request_id: string | null
}

export interface ApiErrorResponse {
  error: ApiErrorBody
}

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

export interface PaginationParams {
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// ---------------------------------------------------------------------------
// Common field types
// ---------------------------------------------------------------------------

/** ISO 4217 currency code (e.g. "INR", "USD") */
export type Currency = string

/**
 * Monetary amount serialized as a string to preserve precision.
 * Example: "42000.00"
 */
export type MoneyString = string

/** ISO 8601 date string (business document date) */
export type DateString = string

/** ISO 8601 datetime string, always UTC */
export type DateTimeString = string

/** UUID v4 string */
export type UUID = string
