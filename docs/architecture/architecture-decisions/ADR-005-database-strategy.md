# ADR-005: Database and Migration Strategy

## Status
Accepted

## Context
MarginGuard needs a relational database for structured financial data with strong consistency guarantees. The `pyproject.toml` from MG-S0.1 already declares SQLAlchemy 2.0 and Alembic as dependencies, but neither is initialized.

## Decision
1. **Database:** PostgreSQL 15+. Chosen for JSONB support, robust constraints, CHECK constraints, partial indexes, and industry prevalence.
2. **ORM:** SQLAlchemy 2.0 (declarative, async-ready). Already in dependencies.
3. **Migrations:** Alembic. Already in dependencies. Will be initialized in MG-S0.2.
4. **Primary keys:** UUID v4 via `gen_random_uuid()` (PostgreSQL 13+).
5. **Migration policy:** Additive only. No destructive changes (DROP COLUMN, DROP TABLE) without explicit ADR approval and a rollback plan.
6. **Test database:** SQLite in-memory for unit tests (speed, no external dependency). This is a documented exception, not an architectural change. Integration tests use a dedicated PostgreSQL test database.

## Alternatives Considered
1. **SQLite for production** — Rejected. Lacks concurrent write support, JSONB, and advanced constraints needed for financial data.
2. **MySQL** — Considered. PostgreSQL preferred for JSONB, CHECK constraints, and partial indexes.
3. **No ORM (raw SQL)** — Rejected. SQLAlchemy provides migration management, type safety, and testability that raw SQL does not.
4. **Django ORM** — Rejected. FastAPI is already chosen; mixing frameworks adds unnecessary complexity.

## Consequences
- Strong data integrity via FK constraints, CHECK constraints, and partial unique indexes.
- Alembic provides reversible, auditable schema evolution.
- SQLite test exception means some PostgreSQL-specific features (e.g. JSONB operators) need conditional handling in tests.
- Developers need a local PostgreSQL instance for integration testing.

## Implementation Impact
- `apps/api/alembic.ini` — Alembic configuration
- `apps/api/alembic/` — migration environment
- `apps/api/app/infrastructure/database.py` — engine, session factory
- `apps/api/app/infrastructure/models/` — SQLAlchemy ORM models
- `apps/api/.env.example` — `DATABASE_URL` with PostgreSQL default

## Migration / Rollback
- Initial migration `001_initial_schema` creates all 11 tables.
- Rollback: `alembic downgrade -1` drops tables in reverse dependency order.
- Safe to run in development. Never test rollbacks against production data.
