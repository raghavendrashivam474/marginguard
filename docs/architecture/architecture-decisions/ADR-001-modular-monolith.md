# ADR-001: Modular Monolith and Layered Architecture

## Status
Accepted

## Context
MarginGuard needs an architecture that supports clear separation of concerns, testability, and future extensibility without the operational complexity of distributed systems. The team is small, the domain is complex, and the product is in early development.

## Decision
MarginGuard will use a **modular monolith** with a **layered architecture**:

- **Domain** — entities, value objects, business rules (zero external dependencies)
- **Application** — use cases, repository ports, orchestration
- **Infrastructure** — SQLAlchemy models, repository implementations, external adapters
- **Interfaces** — FastAPI routes, Pydantic schemas, dependency injection

Dependency direction: Interfaces → Application → Domain ← Infrastructure.

## Alternatives Considered
1. **Microservices** — Rejected. Adds network latency, deployment complexity, and distributed-transactions overhead for a team and scale that don't warrant it.
2. **Flat MVC** — Rejected. Would entangle business logic with HTTP concerns, making financial calculations hard to test in isolation.
3. **Hexagonal / Ports-and-Adapters (strict)** — Considered. The chosen layered approach is a simplified variant. Full hexagonal can be adopted later if the number of external adapters grows.

## Consequences
- Business logic is testable without HTTP or database dependencies.
- New modules (e.g. reconciliation engine) plug into the Application layer without touching routes.
- Single deployment unit simplifies CI/CD and local development.
- Risk: layers can erode over time if developers bypass them. Mitigation: linting rules and code review.

## Implementation Impact
- `apps/api/app/domain/` — populated with entities and value objects
- `apps/api/app/application/` — populated with repository ports
- `apps/api/app/infrastructure/` — populated with SQLAlchemy implementations
- `apps/api/app/api/` — thin routes only

## Migration / Rollback
No migration needed. The layer directories already exist from MG-S0.1. This ADR formalizes how they will be used.
