# ADR-009: Streaming CSV Ingestion and Strict Template Auto-Detection

## Status
Accepted

## Context
In Sprint MG-S1.2, MarginGuard extended file uploads into row-level financial ingestion. Prior to this sprint, uploaded files were stored and inspected, but individual rows were not parsed or mapped to domain entities. The ingestion system required a strategy to stream file rows efficiently, handle malformed CSV rows without crashing, detect document categories automatically, and validate monetary fields with strict precision.

## Decision
1. **Streaming CSV Parsing (`CsvRowReader`):**
   - Implement a streaming, memory-efficient row reader utilizing Python's `csv.reader` over line iterators (`read_bytes`).
   - Automatically strip UTF-8 BOM headers (`utf-8-sig`) and fallback to `latin-1` encoding on decoding errors.
   - Track physical 1-based line numbers (`source_row_number`) matching the exact position in the raw source file.
   - Preserve complete unparsed key-value snapshots (`original_data`) per ADR-007.

2. **Template Auto-Detection (`detect_document_category`):**
   - Automatically infer document categories (`supplier`, `purchase_order`, `invoice`, `payment`) based on header keywords.
   - If header clues are ambiguous, support explicit forced category selection from application callers.

3. **Strict Financial Decimal & Currency Parsing:**
   - Parse monetary values using Python `Decimal` strictly, stripping thousand separators (`,`) and currency symbols (`$`) without converting to Python `float`.
   - Validate currency codes against ISO-4217 standard uppercase codes.
   - Default optional dates to current UTC date (`datetime.utcnow().date()`) when unspecified.
   - Generate deterministic UUIDs (`uuid5`) for string vendor or invoice references to preserve entity relationships when explicit UUIDs are omitted.

4. **Partial Success & Failure Summary:**
   - Process valid rows and save canonical financial domain entities into PostgreSQL.
   - Record validation errors per row in `ImportBatch.error_summary` as structured JSON, marking the batch status as `PARTIALLY_COMPLETED` or `FAILED` accordingly.

## Alternatives Considered
1. **Pandas / Heavy Dataframe ETL Pipeline** — Rejected. Introduced excessive dependency weight, memory overhead, and automatic conversion of numbers to floating-point representation (`float64`).
2. **Strict File Rejection on First Error (All-or-Nothing)** — Rejected. In financial data processing, partial success reporting allows users to inspect valid records and fix only invalid rows.

## Consequences
- Financial precision is strictly preserved across all ingestion boundaries.
- Memory consumption remains low even when streaming large CSV files.
- All valid imported records carry complete provenance (`import_batch_id`, `source_row_number`, `original_data`).

## Implementation Impact
- `app/application/services/csv_reader.py` — `CsvRowReader` streaming adapter.
- `app/application/services/row_mappers.py` — Row mappers, auto-detection, and Decimal validation.
- `app/application/services/ingestion_service.py` — Ingestion orchestration and status updates.
- `docs/engineering/sprints/phase1/sprint1.2/csv-templates.md` — Complete CSV specification.
