# System Overview

**Project:** MarginGuard
**Sprint:** MG-S0.1
**Status:** Preliminary — will be formalized in MG-S0.2
**Last Updated:** 2025-07-11

---

## 1. Product Purpose

MarginGuard is an AI-assisted financial leakage detection and investigation platform designed for SMEs, distributors and wholesalers.

It analyses operational financial records — purchase orders, supplier invoices and payment records — to identify:

- Duplicate invoices
- Duplicate payments
- Invoice-payment mismatches
- Purchase-order and invoice price discrepancies
- Other potential financial inconsistencies

The platform quantifies potential financial exposure and provides evidence-backed findings for human investigation.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Users / SMEs                     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Frontend (web)                      │
│         React + TypeScript + Vite                    │
│         Tailwind CSS + shadcn/ui                     │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ Dashboard│ │ Uploads  │ │ Investigation Views  │  │
│  │ (future) │ │ (future) │ │ (future)             │  │
│  └──────────┘ └──────────┘ └──────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ REST / JSON
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Backend (api)                      │
│              Python + FastAPI                        │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ API Layer (api/v1/)                            │  │
│  │   Routes, request/response handling             │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Application Layer (application/)               │  │
│  │   Use cases, orchestration                      │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Domain Layer (domain/)                         │  │
│  │   Business concepts, rules, entities            │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Infrastructure Layer (infrastructure/)         │  │
│  │   Database, storage, external providers         │  │
│  ├────────────────────────────────────────────────┤  │
│  │ Core (core/)                                   │  │
│  │   Config, logging, shared technical concerns    │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   PostgreSQL                        │
│              (not yet configured)                    │
└─────────────────────────────────────────────────────┘
```

---

## 3. Application Boundaries

### 3.1 Frontend (`apps/web/`)

| Aspect | Detail |
|--------|--------|
| Framework | React 19 + TypeScript |
| Build tool | Vite 8 |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui |
| State | TBD (MG-S0.2+) |
| Routing | TBD (MG-S0.2+) |

**Current state (MG-S0.1):** Minimal foundation screen with product branding and environment status indicators. No financial functionality.

### 3.2 Backend (`apps/api/`)

| Aspect | Detail |
|--------|--------|
| Framework | FastAPI |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Config | pydantic-settings |

**Current state (MG-S0.1):** Health check endpoints only. No database schema, no business logic, no financial entities.

### 3.3 Shared Contracts (`contracts/`)

Will contain shared API schemas and data contracts used by both frontend and backend. Initially empty — financial entity schemas will be defined in MG-S0.2.

### 3.4 Packages (`packages/`)

Reserved for reusable internal packages shared between applications. Not yet populated.

---

## 4. Domain Concepts (Future)

The following domain concepts will be formalized in subsequent sprints:

| Concept | Description |
|---------|-------------|
| **Organization** | A business entity using MarginGuard |
| **Purchase Order** | A buyer's order to a supplier |
| **Supplier Invoice** | A bill from a supplier for goods/services |
| **Payment Record** | A record of payment made to a supplier |
| **Finding** | A detected potential financial discrepancy |
| **Evidence** | Supporting data backing a finding |
| **Investigation** | A human review workflow for a finding |

---

## 5. Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React + TypeScript + Vite | React 19, Vite 8 |
| Styling | Tailwind CSS | v4 |
| UI Components | shadcn/ui | Latest |
| Backend | Python + FastAPI | Python 3.13, FastAPI 0.162 |
| Validation | Pydantic | v2 |
| ORM | SQLAlchemy | v2 |
| Database | PostgreSQL | TBD |
| Migrations | Alembic | v1.20 |
| API | REST + OpenAPI | OpenAPI 3.x |
| Containerization | Docker | TBD |

---

## 6. Integration Direction

MarginGuard is being developed as an independent product. It may become part of the Aryntra ecosystem in the future.

**Current constraints:**
- No dependency on Aryntra-specific services or infrastructure.
- Architecture should support future integration without a complete rewrite.
- API contracts should be designed for standalone and embedded use.

---

## 7. What Is Not Yet Decided

The following architectural decisions are deferred to MG-S0.2 and beyond:

- Authentication and authorization strategy
- Multi-tenancy model
- Database schema design
- File upload and storage architecture
- AI/LLM integration approach
- Background job processing
- Event-driven vs. synchronous processing
- Caching strategy
- Deployment architecture

These will be documented as Architecture Decision Records (ADRs) in `docs/architecture/architecture-decisions/` as decisions are made.

---

## 8. Document Status

> ⚠️ **This is a preliminary overview.** It reflects the MG-S0.1 foundation state and will be significantly expanded in MG-S0.2 when architectural contracts and domain models are formalized.
```

---

✅ **All 3 documentation files done!**

| # | File | Status |
|---|------|--------|
| 1 | `docs/engineering/development-setup.md` | ✅ |
| 2 | `docs/engineering/git-workflow.md` | ✅ |
| 3 | `docs/architecture/system-overview.md` | ✅ |

---