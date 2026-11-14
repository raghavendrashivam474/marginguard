# ADR-003: Canonical Financial Domain Model

## Status
Accepted

## Context
MarginGuard needs a shared vocabulary for financial entities. Without a canonical model, different developers may use inconsistent names, relationships, or business rules, leading to integration bugs and incorrect financial calculations.

## Decision
The domain model defined in `docs/architecture/domain-model.md` is the single source of truth for entity names, attributes, relationships, and invariants. Key decisions within the model:

1. **11 core entities:** Organization, DataSource, ImportBatch, Supplier, PurchaseOrder, Invoice, Payment, Match, Finding, Evidence, Investigation.
2. **Polymorphic references in Match and Evidence:** `source_record_type` + `source_record_id` instead of typed FK columns. This provides flexibility at the cost of DB-level FK enforcement.
3. **No 1:1 invoice-payment assumption:** The model supports many-to-many via Match records.
4. **Finding as investigation candidate:** Status workflow `detected → under_review → confirmed/dismissed/resolved` enforces human review.

## Alternatives Considered
1. **Typed FK columns in Match** (e.g. `invoice_id`, `payment_id`, `po_id` all nullable) — Rejected. Would require schema changes for every new match type and result in sparse tables.
2. **Separate junction tables per match type** — Acknowledged as more normalized. Deferred. If referential integrity issues arise with the polymorphic approach, this will be reconsidered.
3. **Embedding evidence in finding** — Rejected. Evidence is a separate entity because a single finding may have multiple supporting records.

## Consequences
- All developers, contracts, and schemas use the same terminology.
- Polymorphic references require application-layer validation (no DB FK safety net).
- The model supports the full finding lifecycle without schema changes.

## Implementation Impact
- `app/domain/entities.py` — all 11 entities
- `app/domain/value_objects.py` — Money, Currency
- `app/domain/enums.py` — all enumerations
- `contracts/schemas/*.schema.json` — aligned with domain model
- `docs/architecture/domain-model.md` — canonical reference

## Migration / Rollback
No migration needed (conceptual model). Schema changes would follow ADR-005's migration strategy.
