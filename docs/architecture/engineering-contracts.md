# Engineering Contracts

**Project:** MarginGuard  
**Sprint:** MG-S0.2  
**Status:** Accepted  
**Last Updated:** 2025-11-14  

---

## 1. Purpose

This document defines the cross-module engineering conventions that all MarginGuard developers must follow. These conventions ensure consistency across the backend, frontend, and shared contracts.

---

## 2. Layer Dependency Rules

```text
Interfaces (API)  ──▶  Application  ──▶  Domain
                                           ▲
Infrastructure  ───────────────────────────┘

```

| Layer | May Import | Must NOT Import |
| --- | --- | --- |
| **Domain** | Python stdlib only | FastAPI, SQLAlchemy, Pydantic, any framework |
| **Application** | Domain | FastAPI, SQLAlchemy, infrastructure modules |
| **Infrastructure** | Domain, Application (ports) | FastAPI routes |
| **Interfaces** | Application, Domain | Infrastructure directly (use DI) |

> **Enforcement:** Code review + Ruff import linting rules (future).

---

## 3. Financial Data Rules

### 3.1 Monetary Arithmetic

* Always use `decimal.Decimal` for monetary values in Python.
* Never use `float` for financial calculations.
* Never construct `Decimal` from `float` literals. Use `Decimal("42.00")` or `Money.from_str("42.00", "INR")`.

### 3.2 Currency

* Every monetary value must have an associated ISO 4217 currency code.
* Cross-currency arithmetic and comparison must raise an error.
* Currency conversion is deferred, but the architecture supports it.

### 3.3 Timestamps

* Store all timestamps in UTC.
* Use timezone-aware `datetime` objects (`datetime.now(timezone.utc)`).
* Document dates (`invoice_date`, `payment_date`) are plain `date` objects.
* Never confuse a document date with an import timestamp.

### 3.4 Null Handling

* A missing value is not equivalent to zero.
* Never silently replace `None` with `0`, `""`, or a default.
* Handle optional values explicitly in business logic.

---

## 4. API Conventions

* **Versioned REST:** `/api/v1/...`
* `snake_case` JSON field names.
* Monetary values serialized as strings.
* Standardized error envelope (see `api-contracts.md`).
* **Pagination:** `page` + `page_size` query params, `items` + `total` response.
* **Routes must be thin** — no business logic in endpoint handlers.

---

## 5. Database Conventions

* PostgreSQL for production and development.
* SQLite in-memory for unit tests only (documented exception).
* UUID v4 primary keys.
* `NUMERIC(18,4)` for monetary columns.
* `TIMESTAMPTZ` for timestamps.
* All tenant-scoped tables have `organization_id` `NOT NULL` FK.
* Migrations via Alembic, additive only.

---

## 6. Frontend Conventions

* React 19 + TypeScript strict mode.
* API calls go through `@/services/client.ts` — no raw `fetch()` in components.
* Shared types in `@/types/` — aligned with backend Pydantic schemas.
* Path alias `@/*` → `./src/*`.
* UI components from `shadcn/ui` — do not introduce competing libraries.
* Monetary values arrive as strings from the API. Parse carefully for display.

---

## 7. Testing Conventions

* **Backend:** Pytest + `httpx` `TestClient`.
* **Frontend:** TypeScript type-check (`tsc --noEmit`) + Oxlint + Prettier.
* Test files mirror source structure: `app/domain/entities.py` → `tests/test_entities.py`.
* No test should require a live PostgreSQL instance (use SQLite or mocks).
* Integration tests that need PostgreSQL are marked with `@pytest.mark.integration` (future).

---

## 8. Git Conventions

* **Feature branches:** `feature/mg-sX.Y-description`
* **Commit messages:** Conventional Commits (`feat:`, `docs:`, `test:`, `fix:`, `refactor:`)
* No force-push to `main`.
* No `.env` files, credentials, or real financial data in commits.
* CI must be green before merge.

---

## 9. Adding a New Module

When adding a new feature module (e.g., reconciliation engine in `MG-S2.x`):

1. **Domain:** Add entities, value objects, and business rules to `app/domain/`.
2. **Application:** Define repository ports and use cases in `app/application/`.
3. **Infrastructure:** Implement ORM models and repository adapters in `app/infrastructure/`.
4. **Interfaces:** Add Pydantic schemas and thin routes in `app/api/`.
5. **Contracts:** Update JSON Schema in `contracts/schemas/` and TypeScript types in `apps/web/src/types/`.
6. **Database:** Create an Alembic migration for any new tables.
7. **Tests:** Add domain, schema, and integration tests.
8. **Documentation:** Update domain model, data model, and API contracts docs.
9. **ADR:** Record any significant architectural decisions.

---

## 10. Contract Authoritative Sources

| Contract | Authoritative Source | Derived From |
| --- | --- | --- |
| Entity definitions | `docs/architecture/domain-model.md` | Business requirements |
| Database schema | `docs/architecture/data-model.md` | Domain model |
| Backend validation | `apps/api/app/api/schemas/` (Pydantic) | Domain model |
| Cross-module schema | `contracts/schemas/*.schema.json` | Domain model |
| Frontend types | `apps/web/src/types/` | JSON Schema / Pydantic |
| API behavior | FastAPI OpenAPI spec (`/docs`) | Pydantic schemas |

**When sources conflict, the order of precedence is:**

1. Domain model documentation (conceptual truth)
2. Pydantic schemas (runtime behavior)
3. JSON Schema (cross-module contract)
4. TypeScript types (frontend convenience)

```