# ADR-007: Source Provenance and Evidence Traceability

## Status
Accepted

## Context
MarginGuard findings must be traceable to their underlying source records. An auditor or investigator must be able to answer: "Which records produced this finding, and what calculation was performed?" Without provenance, findings are unverifiable and the platform loses credibility.

## Decision
1. **Source provenance on imported records:** Every imported financial record will carry:
   - `import_batch_id` (FK → ImportBatch)
   - `source_row_number` (row index in the original file)
   - `original_data` (JSONB snapshot of the raw imported row)
   These columns will be added in MG-S1.1 when ingestion is implemented. The schema is designed to accommodate them.

2. **Evidence as first-class entity:** Findings link to Evidence records that preserve:
   - The source record reference (`source_record_type` + `source_record_id`)
   - A human-readable `description`
   - Structured `calculation_details` (JSONB) containing inputs and formula

3. **Rule versioning:** Each Finding records `rule_id` and `rule_version`, enabling deterministic reproduction of findings given the same data and rule version.

4. **No destructive updates to source records:** Once imported, original financial records are not modified. Corrections are handled through new records or adjustment entries.

## Alternatives Considered
1. **Evidence as a text field on Finding** — Rejected. A single string cannot preserve structured calculation inputs or link to multiple source records.
2. **Storing only the result, not the inputs** — Rejected. Auditors need to verify the calculation, not just trust the output.
3. **Event sourcing for full audit trail** — Considered. Deferred. Adds significant complexity. The current approach (immutable records + evidence snapshots) provides sufficient traceability for the initial product.

## Consequences
- Every finding is auditable and reproducible.
- Storage cost is higher due to `original_data` and `calculation_details` JSONB fields. Acceptable for the expected data volumes.
- The Evidence entity adds a join to finding queries, but this is a read-time cost that can be optimized with eager loading.

## Implementation Impact
- `app/domain/entities.py` — Evidence entity
- `contracts/schemas/evidence.schema.json` — evidence contract
- Future (MG-S1.1): provenance columns on invoice, payment, purchase_order, supplier tables
- Future: Evidence repository and creation logic in the reconciliation engine

## Migration / Rollback
- Evidence table is part of the initial migration (ADR-005).
- Provenance columns will be added via a future additive migration in MG-S1.1.
