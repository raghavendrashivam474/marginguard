# Engineering Handover & Post-Completion Report: MG-S1.1
**Sprint:** MG-S1.1 — Data Ingestion & Import Foundation  
**Baseline Commit:** `ba05873` (`v-MG-S0.2`)  
**Database Engine:** PostgreSQL 16 (Alpine) @ `127.0.0.1:15432`  
**Alembic Revision:** `5c0df3e49454` (`head`)  
**Verification Status:** 51/51 Tests Passing (`0.78s`) | Ruff Check & Format: `0 errors`

---

## 1. Executive Technical Summary

Sprint **MG-S1.1** transitions MarginGuard from the static architectural contracts established in `v-MG-S0.2` to a live, database-backed ingestion system. 

Without modifying the core domain entities (`app/domain/entities.py`), `Money` value objects, or financial precision rules, we stood up the PostgreSQL 16 persistence layer, authored the initial 11-table Alembic schema migration, implemented concrete SQLAlchemy 2.0 repository adapters, built a local filesystem storage engine with path-traversal protection and SHA-256 checksums, implemented CSV/XLSX header and row inspection, and exposed versioned FastAPI (`v1`) endpoints for Organization CRUD and Multipart File Ingestion.

---

## 2. What Was Implemented & How

### Workstream A: Local PostgreSQL 16 Environment
* **Implementation:** Configured `docker-compose.yml` running `postgres:16-alpine` (`marginguard-postgres`) with persistent volume backing (`postgres_data`) and a `pg_isready` healthcheck.
* **Configuration Alignment:** Synchronized `apps/api/.env` and `apps/api/.env.example` with SQLAlchemy's synchronous/psycopg2 driver string:
  `postgresql+psycopg2://marginguard:marginguard_dev_2025@127.0.0.1:15432/marginguard`.

### Workstream B: Alembic Initial Schema Migration (`5c0df3e49454`)
* **Implementation:** Configured `apps/api/migrations/env.py` to load `settings.database_url` dynamically and bind `Base.metadata` from `app/infrastructure/models.py`.
* **DDL Enforcement:** Generated and hardened `migrations/versions/20261115_1904-5c0df3e49454_initial_schema.py` covering all 11 domain tables:
  `organizations`, `users`, `data_sources`, `import_batches`, `suppliers`, `purchase_orders`, `invoices`, `payments`, `findings`, `evidence`, and `audit_logs`.
* **Data Type Guarantees Verified in `information_schema`:**
  * **Primary/Foreign Keys:** Native PostgreSQL `UUID` across all tables.
  * **Monetary Precision:** All 7 monetary columns (`invoices.subtotal_amount`, `tax_amount`, `total_amount`, `payments.amount`, `purchase_orders.total_amount`, `findings.financial_impact_amount`, `recovered_amount`) are strictly `NUMERIC(18, 4)`. No `FLOAT` or `REAL` types exist in the schema.
  * **Temporal Precision:** All 16 timestamp columns across the schema use `TIMESTAMPTZ` (`sa.DateTime(timezone=True)`).

### Workstream C: SQLAlchemy Repository Adapters
Implemented the abstract repository ports defined in `app/domain/repositories.py` using SQLAlchemy 2.0 `select()` constructs and explicit domain-to-ORM mapping:
* **`SqlAlchemyOrganizationRepository`** (`app/infrastructure/repositories/organization_repository.py`):
  * Handles `save`, `get_by_id`, `get_by_slug`, and `list_all`.
  * Enforces unique slug constraints and translates SQLAlchemy `IntegrityError` into domain `ConflictError`.
* **`SqlAlchemyDataSourceRepository`** (`app/infrastructure/repositories/data_source_repository.py`):
  * Implements `save`, `get_by_id`, and `list_by_organization`.
* **`SqlAlchemyImportBatchRepository`** (`app/infrastructure/repositories/import_batch_repository.py`):
  * Implements `save`, `get_by_id`, `list_by_organization`, and `update_status`.
  * Maps between the slotted `ImportBatch` domain entity and `ImportBatchModel` while persisting infrastructure-specific metadata (`file_hash`, `storage_path`, `file_type`) at the ORM layer.

### Workstream D: Organization & Import Batch APIs (`/api/v1`)
* **Dependency Injection (`app/api/dependencies.py`):** Wired request-scoped SQLAlchemy `Session` generators into repository, storage, and application service factories.
* **Application Services:**
  * `OrganizationService`: Slug normalization, duplicate slug detection (`409 Conflict`), and existence checks (`404 Not Found`).
  * `ImportBatchService`: Tenant-scoped batch listing and single-batch retrieval.
* **Endpoints Wired (`app/api/v1/`):**
  * `POST /api/v1/organizations` (`201 Created`)
  * `GET /api/v1/organizations` (`200 OK`)
  * `GET /api/v1/organizations/{org_id}` (`200 OK` / `404 Not Found`)
  * `GET /api/v1/organizations/{org_id}/imports` (`200 OK`)
  * `GET /api/v1/imports/{batch_id}` (`200 OK` / `404 Not Found`)

### Workstream E: File Upload, Storage Abstraction & Inspection Pipeline
* **`LocalFileStorageService` (`app/infrastructure/storage/local_storage.py`):**
  * Streams uploaded bytes to disk while computing a `SHA-256` digest in 64KB chunks.
  * Ignores client-supplied filenames for storage paths; generates server-side `<uuid4>.<ext>` keys organized under `<base_dir>/<organization_id>/<uuid4>.<ext>`.
  * Enforces path traversal protection via `Path.resolve().relative_to(base_dir.resolve())`.
* **`FileInspector` (`app/application/services/file_inspector.py`):**
  * Validates `.csv` (UTF-8 decoding, header extraction via `csv.reader`, data row counting) and `.xlsx` (via `openpyxl` in `read_only=True, data_only=True` mode).
  * Rejects empty files, header-only files (0 data rows), binary corruption, and unsupported extensions (`.txt`, `.json`, `.exe`, etc.) with `ValidationError` (`422 Unprocessable Entity`).
  * **Crucial Invariant:** Raw cell values are never coerced to `0` or `float` during inspection.
* **`IngestionService` & Upload Route (`POST /api/v1/organizations/{org_id}/imports/upload`):**
  * Accepts `multipart/form-data`.
  * Verifies organization existence.
  * Automatically resolves or provisions a default `file_upload` `DataSource` record for the tenant so foreign key constraints on `import_batches.data_source_id` are satisfied without requiring manual data-source setup prior to CSV upload.
  * Persists the `ImportBatch` with `total_rows` set to the inspected data row count and transitions status cleanly.

### Workstream F: Integration Testing & Static Analysis
* **Test Suite (`apps/api/tests/`):** 51 tests running against the live PostgreSQL 16 instance (`test_health.py`, `test_exceptions.py`, `test_organizations.py`, `test_imports.py`).
* **Static Analysis:** Configured `ruff.toml` and `pyproject.toml` (`line-length = 100`, target `py313`) with zero lint or formatting violations across `app/` and `tests/`.

---

## 3. Technical Problems Faced & How We Mitigated Them

During implementation, we hit several concrete environment, ORM, and domain-boundary issues. Below is the breakdown of each failure and how we resolved it:

### Problem 1: Host Port Collisions on `5432` and `5433`
* **Symptom:** `docker compose up -d` failed to bind host port `5432` (occupied by a local PostgreSQL service) and subsequently failed on `5433` (`bind: An attempt was made to access a socket in a way forbidden by its access permissions` due to Windows Hyper-V reserved port exclusion ranges).
* **Mitigation:** Bound the container explicitly to loopback port `15432` (`127.0.0.1:15432:5432`), updated `.env` / `.env.example`, and documented this decision formally in **ADR-008** (`docs/architecture/architecture-decisions/ADR-008-local-database-port-mapping.md`).

### Problem 2: UTF-8 BOM Corrupting `alembic.ini`
* **Symptom:** Running `python -m alembic` raised `configparser.MissingSectionHeaderError: File contains no section headers. file: '...\alembic.ini', line: 1 '\ufeff[alembic]\n'`.
* **Root Cause:** PowerShell's default UTF-8 encoding writes a 3-byte Byte Order Mark (`EF BB BF`), which Python's `configparser` does not strip when reading `.ini` files in standard `utf-8` mode.
* **Mitigation:** Rewrote all configuration and source files using `System.Text.UTF8Encoding($false)` (UTF-8 without BOM) and verified byte headers before running migrations.

### Problem 3: Autogenerated Migration Emitted Naive `DateTime()` Columns
* **Symptom:** Alembic's initial `--autogenerate` pass produced `sa.DateTime()` (which maps to PostgreSQL `TIMESTAMP WITHOUT TIME ZONE`) instead of `TIMESTAMPTZ`.
* **Root Cause:** Several timestamp columns in `app/infrastructure/models.py` were declared with `DateTime` without `timezone=True`.
* **Mitigation:** Audited and updated every timestamp column in `app/infrastructure/models.py` and `migrations/versions/20261115_1904-5c0df3e49454_initial_schema.py` to `sa.DateTime(timezone=True)`. Verified via `information_schema.columns` that all 16 temporal columns in PostgreSQL are `timestamp with time zone`.

### Problem 4: Slotted Domain Dataclasses (`@dataclass(slots=True)`) vs. Infrastructure Metadata
* **Symptom:** `AttributeError: 'ImportBatch' object has no attribute 'file_hash'` and `AttributeError: type object 'ImportBatch' has no attribute 'create'`.
* **Root Cause:** In `v-MG-S0.2`, domain entities in `app/domain/entities.py` were defined with `@dataclass(slots=True)`. Because `slots=True` prevents dynamic attribute assignment on instances, attaching infrastructure metadata like `batch.file_hash` or `batch.storage_path` directly onto the `ImportBatch` domain instance failed at runtime. Furthermore, our constraint prohibited modifying `app/domain/entities.py`.
* **Mitigation:** Kept `ImportBatch` strictly pure. Passed infrastructure-level attributes (`file_type`, `file_hash`, `storage_path`) as optional keyword arguments to `SqlAlchemyImportBatchRepository.save(batch, file_type=..., file_hash=..., storage_path=...)` so the ORM model (`ImportBatchModel`) persists them to PostgreSQL while the domain entity remains untouched.

### Problem 5: ORM Model vs. Migration Column Drift on `ImportBatchModel`
* **Symptom:** `psycopg2.errors.UndefinedColumn: column import_batches.source_id does not exist` during integration test execution.
* **Root Cause:** `ImportBatchModel` in `app/infrastructure/models.py` referenced legacy column names (`source_id`, `original_filename`), whereas the canonical database schema in `5c0df3e49454` created `data_source_id`, `file_name`, and `file_type`.
* **Mitigation:** Aligned `ImportBatchModel` in `app/infrastructure/models.py` and the mapper in `SqlAlchemyImportBatchRepository` to match the exact DDL columns (`data_source_id`, `file_name`, `file_type`, `file_hash`, `storage_path`).

### Problem 6: Abstract Repository Port Signatures Mismatch
* **Symptom:** `TypeError: Can't instantiate abstract class SqlAlchemyDataSourceRepository without an implementation for abstract methods 'list_by_organization', 'save'` and `SqlAlchemyImportBatchRepository` missing `update_status`.
* **Root Cause:** The abstract base classes in `app/domain/repositories.py` declared full lifecycle methods (`list_by_organization`, `update_status`) beyond basic `get_by_id` and `save`.
* **Mitigation:** Implemented all required abstract methods across `SqlAlchemyDataSourceRepository` and `SqlAlchemyImportBatchRepository` with full type annotations matching the domain ports.

### Problem 7: Async Fixture Lifecycle in `pytest-asyncio`
* **Symptom:** `PytestRemovedIn9Warning` / fixture setup error when injecting the `httpx.AsyncClient` fixture into async test functions.
* **Root Cause:** `pytest-asyncio` requires async generator fixtures (`async def client()`) to be decorated with `@pytest_asyncio.fixture` rather than standard `@pytest.fixture`.
* **Mitigation:** Installed `pytest-asyncio` and `greenlet`, updated `tests/conftest.py` to use `@pytest_asyncio.fixture`, and isolated test runs via database cleanup hooks.

---

## 4. Architectural Invariants & Security Checklist

| Invariant / Requirement | Implementation Detail | Status |
| :--- | :--- | :--- |
| **Baseline Preservation (`v-MG-S0.2`)** | `app/domain/entities.py` and `Money` value objects untouched. | Verified |
| **Financial Precision** | `NUMERIC(18, 4)` in Postgres; `Decimal` in Python. Zero `float` usage. | Verified |
| **No Silent Zero Coercion** | `FileInspector` inspects raw cells without converting `None`/`""` to `0`. | Verified |
| **Timezone Awareness** | All timestamps use `datetime.now(timezone.utc)` and `TIMESTAMPTZ`. | Verified |
| **Path Traversal Prevention** | Server-generated UUID filenames + `Path.resolve().relative_to()` check. | Verified |
| **Idempotency / Provenance Foundation** | `SHA-256` file hash calculated and stored on `import_batches.file_hash`. | Verified |

---

## 5. Readiness for Sprint MG-S1.2 (Row-Level Parsing & Canonical Mapping)

With **MG-S1.1** complete:
1. Uploaded files are safely stored on disk at `import_batches.storage_path` and verified via `import_batches.file_hash`.
2. Every `ImportBatch` is linked to a tenant `Organization` and a `DataSource`.
3. **Next Step (MG-S1.2):** Build the row-level parser worker/service that reads the stored file from `storage_path`, maps rows to canonical `Supplier`, `Invoice`, `Payment`, and `PurchaseOrder` entities (preserving `import_batch_id`, `source_row_number`, and `original_data` JSONB snapshots per **ADR-007**), and transitions the batch status from `PROCESSING` to `COMPLETED` or `FAILED`.