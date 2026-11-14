# ADR-002: Financial Data Types and Monetary Precision

## Status
Accepted

## Context
MarginGuard performs financial calculations. Binary floating-point arithmetic (`float`) introduces rounding errors that are unacceptable for monetary values. For example, `0.1 + 0.2 != 0.3` in IEEE 754.

## Decision
1. **Python side:** All monetary values use `decimal.Decimal`. Never construct from `float` literals. Always from `str` or `Decimal("...")`.
2. **Database side:** All monetary columns use `NUMERIC(18,4)` — 18 total digits, 4 decimal places.
3. **Domain model:** The `Money` value object bundles `amount: Decimal` + `currency: str` and forbids cross-currency arithmetic.
4. **API serialization:** Monetary values serialize as strings (e.g. `"42000.00"`) to preserve precision across JSON transport.

## Alternatives Considered
1. **Integer cents** — Store amounts as integers (e.g. 4200000 for 42000.00). Rejected because it complicates multi-currency support (different currencies have different minor unit counts) and makes the API less readable.
2. **Python `float`** — Rejected. Unacceptable precision loss for financial data.
3. **`NUMERIC(18,2)`** — Considered. Rejected because some ISO 4217 currencies have 3 decimal places (e.g. BHD, KWD). 4 decimal places covers all current ISO currencies.

## Consequences
- All financial calculations are exact and deterministic.
- JSON payloads use string-encoded decimals, which frontend must parse carefully.
- Slightly more verbose than float, but correctness outweighs convenience.

## Implementation Impact
- `app/domain/value_objects.py` — `Money` dataclass
- All SQLAlchemy models — `Numeric(18, 4, asdecimal=True)`
- All Pydantic schemas — `Decimal` fields with string serialization
- Frontend types — monetary fields typed as `string`

## Migration / Rollback
No migration needed (no existing financial data). If the precision needs to change later, a database migration altering column types would be required.
