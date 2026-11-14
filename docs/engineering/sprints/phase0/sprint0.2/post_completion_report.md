---

# Post-Sprint Report: MG-S0.2 — Architecture & Engineering Contracts

**To:** Senior Engineering  
**From:** MarginGuard Core Team  
**Date:** 2026-06-14  
**Sprint:** MG-S0.2 (Phase 0 — Foundation)  
**Branch:** `feature/mg-s0.2-architecture-contracts`  
**Baseline:** `main` @ `e87b9f2` (tag `v-MG-S0.1`)  
**Head:** `0f9b205` → tag `v-MG-S0.2`  
**Total Commits:** 18  

---

## 1. Executive Summary

MG-S0.2 established the architectural and engineering foundation for MarginGuard. The sprint delivered a complete domain model (11 entities, 1 value object, 8 enumerations), SQLAlchemy ORM mappings with Alembic scaffolding, 10 JSON Schema API contracts, a typed frontend integration layer, 7 Architecture Decision Records, and a 50-test verification suite — all passing on CI. No feature logic was implemented; every artifact is a contract, port, or structural scaffold designed to be consumed by MG-S1.1 (Data Ingestion).

Three runtime defects were discovered and resolved during verification, and a CI/CD hardening pass was performed after identifying four pipeline risks that would have caused first-day CI failures.

---

## 2. What Was Implemented

### 2.1 Domain Model (`apps/api/app/domain/`)

**Entities (11):** Organization, DataSource, ImportBatch, Supplier, PurchaseOrder, Invoice, Payment, Match, Finding, Evidence, Investigation.

Each entity is a frozen Pydantic `BaseModel` with business invariants enforced at construction time. Examples:

- `Invoice` validates that `subtotal + tax_amount == total_amount` (within a Decimal tolerance of 0.01) and rejects negative subtotals.
- `Payment` rejects zero and negative amounts.
- `Match` rejects same-source-and-target references and enforces confidence ∈ [0.0, 1.0].
- `ImportBatch` enforces `total_rows >= 0` and `processed_rows <= total_rows`.

**Value Object:** `Money` — immutable, `Decimal`-backed, ISO 4217 currency code validated (3 uppercase ASCII). Supports `+`, `-`, `<`, `>`, `==` with cross-currency guards. Explicitly rejects `float` construction to prevent IEEE 754 precision loss on financial amounts.

**Enumerations (8):** `DataSourceType`, `ImportStatus`, `DocumentType`, `PaymentStatus`, `MatchStatus`, `MatchMethod`, `FindingSeverity`, `FindingStatus`.

**Architecture:** Hexagonal (ports-and-adapters). The domain layer has zero imports from infrastructure, framework, or ORM code. All cross-layer communication goes through abstract repository ports.

### 2.2 Application Ports (`apps/api/app/application/ports.py`)

11 abstract repository interfaces (one per entity), each defining `get_by_id`, `list`, `create`, `update`, and `delete` signatures. These are the dependency inversion boundaries that MG-S1.1 adapters will implement against PostgreSQL.

### 2.3 Infrastructure — Database (`apps/api/app/infrastructure/`)

**ORM Models (`models.py`):** 11 SQLAlchemy 2.x mapped classes using the declarative `MappedAsDataclass` pattern. Key design choices:

- **Primary keys:** `UUID` (server-generated via `uuid4()`), per ADR-003.
- **Money columns:** `NUMERIC(18, 4)` — not `FLOAT`, not `REAL`. Four decimal places to accommodate tax rate calculations and multi-currency rounding.
- **Timestamps:** `TIMESTAMPTZ` everywhere. No naive datetimes.
- **Constraints:** `CHECK` constraints mirror domain invariants at the database level (e.g., `CHECK (total_amount >= 0)`, `CHECK (confidence BETWEEN 0 AND 1)`).
- **Indexes:** Composite indexes on high-cardinality lookup paths (e.g., `(organization_id, status)` on `import_batches`, `(supplier_id, document_date)` on `invoices`).

**Session Management (`database.py`):** Async-capable `sessionmaker` with `create_async_engine` stub (sync for now, async-ready). Connection URL sourced from `Settings.database_url`.

**Alembic:** Fully configured (`alembic.ini`, `migrations/env.py`, `script.py.mako`). The `env.py` imports all ORM models from `app.infrastructure.models` so `autogenerate` will detect them. Initial migration generation is deferred to MG-S1.1 when a live PostgreSQL instance is available.

### 2.4 API Layer (`apps/api/app/api/`)

**Pydantic Schemas:** Request/response models for Organization, Financial documents (PO, Invoice, Payment), and Findings. All use Pydantic v2 syntax (`model_validator`, `field_validator`).

**Error Envelope:** Standardized `ErrorBody` schema:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Invoice inv_123 not found",
    "details": []
  }
}
```

**Exception Handlers:** Registered on the FastAPI app for `HTTPException` (404, 405, etc.) and `RequestValidationError` (422). All errors return the envelope format with appropriate HTTP status codes.

**Pagination:** `PaginationParams` (page ≥ 1, page_size 1–200, default 20) and generic `PaginatedResponse[T]` with `items`, `total`, `page`, `page_size`, `pages`.

### 2.5 API Contracts (`contracts/schemas/`)

10 JSON Schema files defining the wire format for all resources: `common.json` (shared types, error envelope, pagination), `organization.json`, `supplier.json`, `purchase-order.json`, `invoice.json`, `payment.json`, `import-batch.json`, `match.json`, `finding.json`, `evidence.json`. These are the source of truth for frontend/backend contract alignment.

### 2.6 Frontend Integration (`apps/web/src/`)

**Typed API Client (`services/client.ts`):** Generic `fetch`-based wrapper with typed request/response generics, automatic error envelope parsing, and base URL configuration from environment variables.

**Domain Types (`types/domain.ts`):** TypeScript interfaces mirroring the backend Pydantic schemas — `Organization`, `Supplier`, `PurchaseOrder`, `Invoice`, `Payment`, `Match`, `Finding`, `Money`, plus all enumerations.

**API Types (`types/api.ts`):** `ApiResponse<T>`, `PaginatedResponse<T>`, `ErrorBody`, `PaginationParams` — matching the backend envelope exactly.

### 2.7 Architecture Decision Records

7 ADRs in `docs/architecture/architecture-decisions/`:

| ADR | Decision | Rationale |
|-----|----------|-----------|
| 001 | Hexagonal Architecture | Testability, framework independence, clear boundaries |
| 002 | PostgreSQL | JSONB for flexible document storage, mature NUMERIC type, full-text search |
| 003 | UUID Primary Keys | Distributed-safe, no enumeration attacks, merge-friendly |
| 004 | Decimal Money | IEEE 754 floats lose precision on financial amounts |
| 005 | Event Sourcing Deferred | Complexity not justified at current scale; revisit at Phase 2 |
| 006 | Monorepo | Single CI pipeline, atomic cross-stack changes, small team |
| 007 | URL-Path API Versioning (`/api/v1/`) | Industry standard, cache-friendly, explicit |

### 2.8 Test Suite (50 tests)

| Suite | Count | What It Validates |
|-------|-------|-------------------|
| `test_health.py` | 4 | `/health`, `/api/v1/health`, OpenAPI docs, ReDoc — regression from MG-S0.1 |
| `test_money.py` | 14 | Construction, `from_str`, float rejection, currency validation, arithmetic, comparison, precision at scale |
| `test_entities.py` | 14 | Business invariants for Organization, Invoice, Payment, ImportBatch, Match |
| `test_schemas.py` | 11 | Pydantic validation, pagination bounds, error envelope structure |
| `test_exceptions.py` | 2 | 404 and 405 return correct error envelope format |

All 50 pass in 0.34s on Python 3.13 / pytest 8.3.5.

### 2.9 CI/CD Hardening

Performed after identifying four pipeline risks (detailed in Section 4):

- `.gitattributes` — LF enforcement for all code files, CRLF for Windows scripts
- `.python-version` (3.13) and `.nvmrc` (22) — consumed by CI via `python-version-file` / `node-version-file`
- Dependency pins tightened to known-good ranges with upper bounds
- `pytest-asyncio` loop scope explicitly configured
- `continue-on-error: true` removed from CI test step

---

## 3. How It Was Implemented

**Process:** Incremental, one-commit-per-deliverable. Each logical artifact (domain model, ORM layer, schemas, tests, docs) was authored, verified locally, and committed independently. This produced 18 atomic commits on the feature branch, each passing the existing test suite.

**Dependency direction:** Strictly inward. `domain/` → `application/` → `infrastructure/` → `api/`. No reverse imports. The domain layer imports only from the Python standard library and Pydantic.

**Type consistency:** Backend Pydantic schemas, SQLAlchemy models, JSON Schema contracts, and TypeScript types were all derived from the same domain model definitions. Field names, types, and constraints are consistent across all four representations.

**Verification cadence:** After every 2–3 commits, the full test suite was re-run. Frontend verification (`oxlint`, `tsc --noEmit`, `prettier --check`, `vite build`) was run at the end.

---

## 4. Problems Encountered & Mitigations

### 4.1 pydantic-settings v2 Rejects Undeclared `.env` Keys

**Symptom:** On first test run, `app.main` import failed with:
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
APP_NAME
  Extra inputs are not permitted [type=extra_forbidden]
```

**Root Cause:** The existing `.env` file (from MG-S0.1) contains `APP_NAME=MarginGuard`, but the `Settings` class in `config.py` only declared `database_url`, `debug`, and `api_prefix`. pydantic-settings v2 defaults to `extra="forbid"`, unlike v1 which silently ignored unknown keys.

**Mitigation:** Replaced the inline `model_config = {...}` dict with an explicit `SettingsConfigDict` import and added `extra="ignore"`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ← fix
    )
```

**Lesson:** When upgrading pydantic-settings from v1 to v2, audit all `.env` files for keys not declared on the Settings model. The default behavior changed from permissive to strict.

### 4.2 SQLAlchemy 2.x `Real` → `REAL` Import

**Symptom:** Import error on `models.py`:
```
ImportError: cannot import name 'Real' from 'sqlalchemy'
```

**Root Cause:** The SQLAlchemy 2.x type system uses uppercase names for SQL-standard types. `REAL` is the correct symbol; `Real` does not exist. The initial code generation used the lowercase form.

**Mitigation:** Direct replacement in `models.py`:
- Import: `from sqlalchemy import ..., Real, ...` → `from sqlalchemy import ..., REAL, ...`
- Column definitions: `mapped_column(Real, ...)` → `mapped_column(REAL, ...)` (3 occurrences across `purchase_orders` and `invoices` tables)

**Lesson:** SQLAlchemy's type naming is inconsistent across versions. Always verify type symbols against the installed version's `sqlalchemy.__all__` rather than assuming camelCase.

### 4.3 FastAPI / Starlette Version Mismatch — `on_startup` Removed

**Symptom:** `app.main` import failed with:
```
TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'
```

**Root Cause:** This was the most subtle defect. The `router.py` code itself contained no `on_startup` parameter. The error originated inside FastAPI's internal `APIRouter` constructor, which passes `on_startup` to Starlette's `Router.__init__()`. The installed FastAPI 0.115.6 was compatible with Starlette 0.37.x, but the environment had Starlette 1.7.0 installed (a major version jump). Starlette 1.x removed the `on_startup`/`on_shutdown` parameters in favor of the `lifespan` context manager protocol.

The version mismatch occurred because `pyproject.toml` declared `fastapi>=0.115.0` with no upper bound, and `pip install -e ".[dev]"` resolved the latest FastAPI (0.163.0 at the time) alongside Starlette 1.7.0 — but the initially installed FastAPI was 0.115.6, which was too old for the newer Starlette.

**Mitigation:** Upgraded FastAPI to 0.163.0 (`pip install --upgrade "fastapi>=0.115.0"`), which is compatible with Starlette 1.7.0. Then pinned the dependency in `pyproject.toml` to `fastapi>=0.163.0,<1.0.0` to prevent future silent jumps.

**Lesson:** Unbounded `>=` dependency declarations are a latent CI/CD risk. A fresh `pip install` on a CI runner will resolve the latest compatible version, which may introduce breaking changes from transitive dependencies. Always pin upper bounds on framework dependencies.

### 4.4 CI/CD Pipeline Risks (Discovered Post-Implementation)

During a pre-merge CI audit, four issues were identified that would have caused first-day CI failures:

| Risk | Impact | Fix |
|------|--------|-----|
| No `.gitattributes` | Mixed LF/CRLF on Linux CI runners → shell script failures, Python `\r` import errors | Created `.gitattributes` with `* text=auto eol=lf` |
| No `.python-version` / `.nvmrc` | CI uses hardcoded versions that drift from local dev | Created both files; updated CI to use `*-version-file` |
| Unbounded Python deps | Same root cause as 4.3 — CI would install latest and potentially break | Pinned all deps with `<next-major` upper bounds |
| `pytest-asyncio` loop scope unset | Deprecation warning that becomes an error in pytest-asyncio 1.0 | Added `asyncio_default_fixture_loop_scope = "function"` to `pyproject.toml` |

**Additional fix:** Removed `continue-on-error: true` from the CI test step. This flag was set during MG-S0.1 when no real tests existed. With 50 tests now passing, masking failures is counterproductive.

---

## 5. Acceptance Criteria Status

All 16 acceptance criteria met. See `docs/engineering/sprints/phase0/sprint0.2/mg-s0.2-completion-report.md` for the full matrix with evidence links.

---

## 6. Carry-Forward Items for MG-S1.1

| Item | Reason | Priority |
|------|--------|----------|
| Initial Alembic migration | Requires live PostgreSQL (or Docker Compose) | High |
| Repository adapter implementations | Ports are defined; concrete SQLAlchemy implementations needed | High |
| API route handlers | Schemas and exception handling ready; need use-case wiring | High |
| Docker Compose for local PostgreSQL | Prerequisite for migration generation and integration tests | High |
| Frontend API client integration | Client is typed but has no real endpoints to call | Medium |
| `httpx` → `httpx2` migration | Starlette deprecation warning; not breaking yet | Low |

---

## 7. Recommendations

1. **Start MG-S1.1 with Docker Compose.** The first task should be a `docker-compose.yml` with PostgreSQL 16 so that `alembic revision --autogenerate` can produce the initial migration. Everything else depends on a real schema.

2. **Implement repositories in dependency order.** Start with `OrganizationRepository` and `ImportBatchRepository` — these are the roots of the entity graph and unblock the data ingestion pipeline.

3. **Add integration tests alongside unit tests.** The current 50 tests are all in-memory. MG-S1.1 should introduce a `tests/integration/` directory with pytest fixtures that spin up a test database via `testcontainers` or a CI PostgreSQL service.

4. **Consider `uv` for Python dependency management.** The `pyproject.toml` pins mitigate the immediate risk, but a lockfile (`uv.lock`) would provide deterministic installs across all environments. This is a low-effort, high-value improvement.

---

**Branch `feature/mg-s0.2-architecture-contracts` is ready for review and merge to `main`.** Tag `v-MG-S0.2` will be applied at merge.