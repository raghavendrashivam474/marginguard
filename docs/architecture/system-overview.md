# System Overview

**Project:** MarginGuard
**Sprint:** MG-S0.2 — Architecture & Engineering Contracts
**Status:** Formalized
**Last Updated:** 2025-11-14

---

## 1. Product Purpose

MarginGuard is an independent financial leakage detection and investigation platform designed for SMEs, distributors, and wholesalers.

It analyses operational financial records — purchase orders, supplier invoices, payment records, and supplier information — to identify:

- Duplicate invoices
- Duplicate payments
- Invoice-payment mismatches
- Purchase-order and invoice price discrepancies
- Unmatched payments and orphaned invoices
- Other potential financial inconsistencies

The platform quantifies potential financial exposure and provides evidence-backed findings for human investigation. Every finding is traceable to its underlying source records.

---

## 2. Architectural Style

MarginGuard uses a **modular monolith with clear architectural boundaries**.

There are no microservices. The application is deployed as a single backend process and a single frontend application. Modularity is achieved through internal layer boundaries and explicit dependency rules, not through network separation.

### Layered Architecture

```text
┌─────────────────────────────────────────────────┐
│ Interfaces (API) │
│ FastAPI routes, request/response schemas, │
│ dependency injection, serialization │
├─────────────────────────────────────────────────┤
│ Application │
│ Use cases, orchestration, repository ports, │
│ application services │
├─────────────────────────────────────────────────┤
│ Domain │
│ Entities, value objects, business rules, │
│ financial invariants, domain validation │
├─────────────────────────────────────────────────┤
│ Infrastructure │
│ SQLAlchemy models, repository implementations, │
│ database sessions, external adapters │
└─────────────────────────────────────────────────┘
```


### Dependency Rule

- **Domain** depends on nothing external (no FastAPI, no SQLAlchemy, no framework imports).
- **Application** depends on Domain only.
- **Infrastructure** implements interfaces defined by Application and uses Domain types.
- **Interfaces** depends on Application and Domain. Infrastructure is injected at runtime.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite 8, Tailwind CSS v4, shadcn/ui |
| Backend API | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| Database | PostgreSQL (primary), SQLAlchemy 2.0 ORM |
| Migrations | Alembic |
| Validation | Pydantic v2 (backend), JSON Schema (cross-module contracts) |
| Financial Arithmetic | Python `decimal.Decimal` |
| Testing | Pytest + httpx (backend), TypeScript type-check + Oxlint (frontend) |
| CI | GitHub Actions |
| Linting | Ruff (backend), Oxlint + Prettier (frontend) |

---

## 4. High-Level Data Flow
```text
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Data Import │────▶│ Validation │────▶│ Persistence │
│ (CSV/Excel) │ │ & Normalize │ │ (PostgreSQL)│
└──────────────┘ └──────────────┘ └──────┬───────┘
│
▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Human Review │◀────│ Findings │◀────│ Reconciliation│
│ & Resolution │ │ & Evidence │ │ Engine │
└──────────────┘ └──────────────┘ └──────────────┘
```


1. Financial records are imported from external sources (CSV, Excel, ERP exports).
2. Records are validated, normalized, and persisted with full source provenance.
3. The reconciliation engine analyses records to detect discrepancies.
4. Findings are generated with structured evidence and calculation details.
5. Human investigators review, confirm, or dismiss findings.

---

## 5. Core Domain Entities

The system revolves around these financial entities (detailed in `domain-model.md`):

| Entity | Purpose |
|---|---|
| Organization | Tenant boundary; the business using MarginGuard |
| DataSource | Origin of imported records |
| ImportBatch | A single import operation with status tracking |
| Supplier | A vendor or supplier |
| PurchaseOrder | An order issued by the organization |
| Invoice | A bill received from a supplier |
| Payment | A payment made by the organization |
| Match | A proposed or established link between records |
| Finding | A potential financial discrepancy |
| Evidence | Structured proof supporting a finding |
| Investigation | Human review workflow for a finding |

---

## 6. Key Architectural Principles

1. **Deterministic calculations** — identical inputs always produce identical findings.
2. **Decimal arithmetic** — no binary floating-point for monetary values.
3. **Traceable evidence** — every finding links to its source records and calculation.
4. **Separation of concerns** — business logic lives in Domain/Application, not in routes or ORM models.
5. **API stability** — versioned REST contracts independent of frontend implementation.
6. **Modular monolith** — clear internal boundaries without microservice overhead.
7. **Explicit validation** — predictable error responses, no silent data coercion.
8. **Extensibility** — new modules plug in without breaking existing ones.
9. **Human-in-the-loop** — findings are investigation candidates, not automatic verdicts.
10. **Documented decisions** — every significant choice recorded in an ADR.

---

## 7. Tenant Isolation Strategy

Every tenant-scoped record carries an `organization_id` foreign key. The backend will eventually derive the authorized organization from authenticated server-side context. Browser-supplied organization IDs are never trusted for authorization.

Full authentication and production enforcement are deferred to a later sprint. The data model is designed to support it without schema changes.

---

## 8. Deployment Model

Single-process deployment:

- One FastAPI backend (Uvicorn)
- One static frontend (served by CDN or reverse proxy)
- One PostgreSQL database
- No message queues, no background workers, no Kubernetes (current scope)

---

## 9. Related Documentation

- [Domain Model](domain-model.md) — entity definitions, relationships, invariants
- [Data Model](data-model.md) — database schema, ER diagram, constraints
- [API Contracts](api-contracts.md) — endpoint catalogue, conventions, error format
- [Engineering Contracts](engineering-contracts.md) — cross-module integration rules
- [Architecture Decisions](architecture-decisions/) — ADRs with rationale and trade-offs
