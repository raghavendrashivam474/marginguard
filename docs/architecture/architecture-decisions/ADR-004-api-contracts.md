# ADR-004: API Contract and Versioning Strategy

## Status
Accepted

## Context
The frontend and backend must communicate through stable, well-defined contracts. Ad-hoc API changes would break the frontend and make integration testing unreliable.

## Decision
1. **Versioning:** URL-path versioning — `/api/v1/...`. The existing `/api/v1/health` already follows this convention.
2. **Contract format:** Pydantic v2 models are the authoritative backend contracts. JSON Schema files in `contracts/schemas/` serve as the cross-module, language-agnostic reference.
3. **Naming:** `snake_case` for JSON fields (matching Python conventions). IDs are UUID strings. Dates are ISO 8601. Monetary values are decimal strings.
4. **Error envelope:** Standardized structure with `error.code`, `error.message`, `error.details`, `error.request_id`.
5. **Pagination:** Query params `page` (default 1) and `page_size` (default 20, max 100). Response includes `items`, `total`, `page`, `page_size`.
6. **No CRUD routes in MG-S0.2:** Only `/health` and `/api/v1/health` are implemented. Contracts are defined but endpoints are deferred to MG-S1.1+.

## Alternatives Considered
1. **Header-based versioning** (`Accept: application/vnd.marginguard.v1+json`) — Rejected. Less visible, harder to test in browser, and the existing convention already uses URL versioning.
2. **GraphQL** — Rejected. Overkill for the current query patterns and team size. REST is sufficient.
3. **OpenAPI as single source of truth** — Considered. Pydantic models are preferred because they serve double duty (validation + serialization) and generate OpenAPI automatically via FastAPI.

## Consequences
- Frontend can develop against stable contracts before backend endpoints exist.
- API changes require a version bump, preventing silent breaking changes.
- JSON Schema files enable future code generation if needed.

## Implementation Impact
- `app/api/v1/` — route modules (deferred)
- `app/interfaces/schemas/` — Pydantic request/response models
- `contracts/schemas/` — JSON Schema files
- `apps/web/src/services/` — typed API client
- `apps/web/src/types/` — shared TypeScript types

## Migration / Rollback
No migration needed. When v2 is eventually required, v1 endpoints remain operational alongside v2.
