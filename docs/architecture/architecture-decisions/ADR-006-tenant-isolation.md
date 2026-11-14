# ADR-006: Organization-Level Data Isolation

## Status
Accepted

## Context
MarginGuard will serve multiple organizations (tenants). Each organization's financial data must be strictly isolated. A data leak between tenants would be a critical security and compliance failure.

## Decision
1. **Shared database, shared schema** with `organization_id` FK on every tenant-scoped table.
2. **Application-layer scoping:** All repository queries must filter by `organization_id`. The organization context will eventually be derived from authenticated server-side session, never from client-supplied parameters.
3. **Future enhancement:** PostgreSQL Row-Level Security (RLS) policies as a defense-in-depth layer. Not implemented in MG-S0.2.
4. **No cross-tenant queries:** The application layer must never execute a query that spans multiple organizations unless explicitly authorized for administrative purposes.

## Alternatives Considered
1. **Separate database per tenant** — Rejected. Operational complexity (provisioning, backups, migrations) is disproportionate for the current scale.
2. **Separate schema per tenant** — Rejected. Similar operational overhead with limited additional benefit over row-level isolation.
3. **RLS from day one** — Considered. Deferred because it requires a functioning authentication system, which is out of scope for MG-S0.2. The `organization_id` FK foundation enables RLS to be added later without schema changes.

## Consequences
- Data isolation is enforced at the application layer (current) and will be reinforced at the database layer (future).
- Every query must include `WHERE organization_id = :org_id`. Missing this filter is a security bug.
- The `Organization` entity is the root of the aggregate hierarchy.

## Implementation Impact
- All SQLAlchemy models — `organization_id` column with NOT NULL + FK
- All repository interfaces — `organization_id` parameter on every method
- Future: authentication middleware, RLS policies

## Migration / Rollback
No migration needed (design decision). The `organization_id` columns are part of the initial schema in ADR-005.
