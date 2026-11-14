# MG-S0.2 Repository Inspection Report

**Sprint:** MG-S0.2 — Architecture & Engineering Contracts
**Baseline Tag:** `v-MG-S0.1`
**Baseline Commit:** `e87b9f2`
**Baseline Branch:** `main`
**Inspection Date:** 2025-11-14
**Working Branch:** `feature/mg-s0.2-architecture-contracts`

---

## 1. Purpose

This report captures the actual state of the repository at the start of MG-S0.2, so that subsequent architectural work extends what exists rather than silently replacing it. Per the sprint brief, the actual repository — not an earlier proposal — is the source of truth.

---

## 2. Git Baseline

| Item | Value |
|---|---|
| Branch | `main` |
| Commit | `e87b9f2` |
| Tag | `v-MG-S0.1` |
| Working tree | clean |
| Remote | `origin/main` tracks `e87b9f2` |

No uncommitted changes existed prior to branch creation.

---

## 3. Verified Existing Structure

### 3.1 Top-level

```text
.github/ apps/ contracts/ data/
docs/ packages/ scripts/ tests/
.editorconfig .gitignore LICENSE README.md
```
### 3.2 Backend (`apps/api/`)

- `pyproject.toml` — declares: FastAPI, Uvicorn, Pydantic v2, pydantic-settings, **SQLAlchemy 2.0**, **Alembic 1.13**. Dev extras: pytest, httpx, ruff.
- `.env.example` — defines `APP_NAME`, `APP_ENV`, `APP_VERSION`, `DATABASE_URL`, `LOG_LEVEL`.
- `app/main.py` — FastAPI app, includes `/health` root endpoint, mounts `app.api.v1.router`.
- `app/core/config.py` — Pydantic Settings-based `settings` singleton.
- `app/api/v1/router.py` — v1 APIRouter.
- `app/{domain,application,infrastructure}/` — present but contain only `__init__.py` (empty layers ready to be populated).
- `migrations/` — exists but holds only `.gitkeep` (Alembic **declared as dependency but not initialized**).
- `tests/` — exists but holds only `.gitkeep` (**no existing tests**).

### 3.3 Frontend (`apps/web/`)

- React 19, TypeScript, Vite 8, Tailwind v4 (`@tailwindcss/vite`), shadcn/ui components present: `button`, `card`, `badge`.
- Path alias `@/*` → `./src/*` configured in both `tsconfig.json` and `vite.config.ts`.
- Scripts: `dev`, `build`, `preview`, `lint` (oxlint), `format` (prettier), `typecheck` (tsc), `check` (composite).
- `src/lib/utils.ts` exists (shadcn's `cn` helper).
- **No `src/services/` directory** — needs to be created.
- **No `src/types/` directory** — needs to be created.

### 3.4 Contracts

- `contracts/schemas/` — present with only `.gitkeep`. No JSON Schema files yet.

### 3.5 Documentation

- `docs/architecture/system-overview.md` — MG-S0.1 preliminary version, explicitly noting it "will be formalized in MG-S0.2".
- `docs/architecture/architecture-decisions/` — present with only `.gitkeep`. **No ADRs yet; new ADRs start at ADR-001.**
- `docs/engineering/development-setup.md`, `git-workflow.md`, `repository-inspection.md` — present.
- `docs/engineering/sprints/phase0/sprint0.1/` — established convention for sprint reports. MG-S0.2 will follow the same pattern at `.../sprint0.2/`.

### 3.6 CI

- `.github/workflows/ci.yml` — exists (2372 bytes), reported passing at baseline. Must remain green.

---

## 4. Gap Analysis — What MG-S0.2 Must Add

| Area | Current State | MG-S0.2 Action |
|---|---|---|
| Domain layer | Empty `__init__.py` | Add entities, value objects, `Money` type |
| Application layer | Empty `__init__.py` | Add repository interfaces (Ports) |
| Infrastructure layer | Empty `__init__.py` | Add SQLAlchemy session, ORM models, repo impls |
| Alembic | Dependency declared, no config | Initialize `alembic.ini`, `env.py`, create initial migration |
| API routes | Only `/api/v1/health` (implied) | Keep health; **do not add CRUD routes this sprint** (contracts only) |
| Pydantic schemas | None | Add request/response schemas, error envelope, pagination |
| Error handling | FastAPI defaults | Add standardized error envelope + exception handlers |
| Contracts (JSON Schema) | Empty dir | Add 10 schemas: common, organization, supplier, PO, invoice, payment, import-batch, match, finding, evidence |
| ADRs | None | Add ADR-001 through ADR-007 |
| Architecture docs | `system-overview.md` placeholder | Update overview; add `domain-model.md`, `data-model.md`, `api-contracts.md`, `engineering-contracts.md` |
| Backend tests | None | Add contract tests, financial-precision tests, DB/migration tests |
| Frontend `services/` | Missing | Add typed API client, error normalization |
| Frontend `types/` | Missing | Add shared domain types aligned with backend contracts |

---

## 5. Non-Goals (Explicitly Deferred)

Per the sprint brief Section 14, MG-S0.2 will NOT implement:

- CSV/Excel ingestion pipelines (MG-S1.1)
- Any reconciliation or duplicate-detection logic
- CRUD endpoints beyond `/health` (contract-only sprint)
- Authentication, authorization, multi-tenant enforcement middleware
- Frontend dashboard, upload UI, or investigation workflow
- Background workers, message queues, external integrations

Contracts for the above *may* be defined without being implemented.

---

## 6. Architectural Observations

1. **Alembic dependency without initialization** is an inconsistency inherited from MG-S0.1. MG-S0.2 will initialize it rather than remove the dependency.
2. **Layer directories exist but are empty** — architecturally this is ideal: the modular monolith shape was reserved in S0.1 and will be populated in S0.2 without any restructuring.
3. **No existing tests** means there is no regression test suite to protect; the only runtime regression check is that `/health` and `/api/v1/health` still respond and OpenAPI docs still render. MG-S0.2 will add the first real test suite.
4. **Frontend already uses `@/*` alias** — new `services/` and `types/` should use this convention.
5. **Database decision is PostgreSQL** per sprint brief, but `DATABASE_URL` in `.env.example` is blank. MG-S0.2 will:
   - Default to a local dev-friendly URL in `.env.example` (PostgreSQL)
   - Make SQLAlchemy engine construction lazy, so the app still boots for `/health` without a live DB
   - Use SQLite only for isolated unit tests (explicitly documented as test-only — not an architectural downgrade)

---

## 7. Recommended Implementation Plan

Follows the sprint brief Section 13 (MG-S0.2.1 → MG-S0.2.6):

1. Architecture & domain design docs (this report + system overview update + domain/data model docs)
2. ADRs 001–007
3. JSON Schema contracts (`contracts/schemas/*.schema.json`)
4. Backend domain layer (entities, `Money` value object, enums)
5. Backend application layer (repository Ports)
6. Backend infrastructure (SQLAlchemy models, session, Alembic init + initial migration)
7. Backend interfaces (Pydantic schemas, error envelope, pagination) — no new routes
8. Backend tests (contracts, money precision, DB round-trip, migration up/down)
9. Frontend `services/` + `types/` conventions
10. Verification: lint, typecheck, pytest, frontend build, CI
11. Completion report + commits + tag

---

## 8. Verified Preservation Targets

The following must continue to work unchanged at sprint end:

- `GET /health`
- `GET /api/v1/health`
- `/docs` and `/redoc`
- `npm run check` in `apps/web`
- Existing CI pipeline

---

## 9. Baseline Snapshot

```text
Branch : main
Commit : e87b9f2
Tag : v-MG-S0.1
Status : clean
```

Feature branch created: `feature/mg-s0.2-architecture-contracts`
