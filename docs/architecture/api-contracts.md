# API Contracts

**Project:** MarginGuard
**Sprint:** MG-S0.2
**Status:** Accepted
**Last Updated:** 2025-11-14
**ADR Reference:** ADR-004

---

## 1. Overview

This document defines the API conventions and endpoint catalogue for MarginGuard. The authoritative machine-readable contracts are:

- **Backend (validation + serialization):** `apps/api/app/api/schemas/` (Pydantic v2 models)
- **Cross-module (language-agnostic):** `contracts/schemas/*.schema.json` (JSON Schema draft-07)
- **Frontend (TypeScript types):** `apps/web/src/types/`

This document is the human-readable reference. In case of conflict, the Pydantic models are authoritative for backend behavior, and the JSON Schema files are authoritative for cross-module integration.

---

## 2. Base URL and Versioning

- **Base URL:** `http://localhost:8000` (development)
- **Version prefix:** `/api/v1/`
- **Versioning strategy:** URL-path versioning. When breaking changes are required, a new version (`/api/v2/`) is introduced while v1 remains operational.

---

## 3. Endpoint Catalogue

### 3.1 Implemented Endpoints (MG-S0.2)

| Method | Path | Purpose | Status |
|---|---|---|---|
| GET | `/health` | Root health check | ✅ Implemented |
| GET | `/api/v1/health` | Versioned health check | ✅ Implemented |
| GET | `/docs` | Swagger UI | ✅ Implemented |
| GET | `/redoc` | ReDoc UI | ✅ Implemented |

### 3.2 Proposed Endpoints (Deferred to MG-S1.1+)

| Method | Path | Purpose | Status |
|---|---|---|---|
| GET | `/api/v1/organizations` | List organizations | 📋 Contract defined |
| POST | `/api/v1/organizations` | Create organization | 📋 Contract defined |
| POST | `/api/v1/imports` | Initiate an import | 📋 Contract defined |
| GET | `/api/v1/imports/{id}` | Retrieve import status | 📋 Contract defined |
| GET | `/api/v1/suppliers` | List suppliers | 📋 Contract defined |
| GET | `/api/v1/invoices` | List invoices | 📋 Contract defined |
| GET | `/api/v1/payments` | List payments | 📋 Contract defined |
| GET | `/api/v1/purchase-orders` | List purchase orders | 📋 Contract defined |
| GET | `/api/v1/findings` | List findings | 📋 Contract defined |
| GET | `/api/v1/findings/{id}` | Retrieve finding with evidence | 📋 Contract defined |

---

## 4. Request Conventions

### 4.1 Content Type

All request bodies use `application/json`.

### 4.2 Naming

- JSON field names use `snake_case` (matching Python/Pydantic conventions).
- IDs are UUID v4 strings.
- Dates are ISO 8601 date strings (`"2025-11-14"`).
- Timestamps are ISO 8601 datetime strings in UTC (`"2025-11-14T12:00:00Z"`).
- Monetary values are decimal strings (`"42000.00"`) to preserve precision.

### 4.3 Example: Create Organization

**Request:**
```http
POST /api/v1/organizations
Content-Type: application/json

{
  "name": "Example Distribution",
  "legal_name": "Example Distribution Pvt Ltd",
  "currency": "INR"
}

```

**Response (`201`):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Example Distribution",
  "legal_name": "Example Distribution Pvt Ltd",
  "currency": "INR",
  "created_at": "2025-11-14T12:00:00Z",
  "updated_at": "2025-11-14T12:00:00Z"
}

```

---

## 5. Response Conventions

### 5.1 Success Responses

* `200 OK` — Successful read or update.
* `201 Created` — Successful resource creation.
* `204 No Content` — Successful deletion.

### 5.2 List Responses (Paginated)

All list endpoints return a paginated envelope:

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20
}

```

**Query Parameters:**

| Parameter | Type | Default | Max | Description |
| --- | --- | --- | --- | --- |
| `page` | `int` | `1` | — | Page number (1-indexed) |
| `page_size` | `int` | `20` | `100` | Items per page |

---

## 6. Error Response Format

All errors follow a standardized envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The supplied data is invalid.",
    "details": [
      {
        "field": "currency",
        "issue": "String should match pattern '^[A-Z]{3}$'"
      }
    ],
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}

```

### Error Codes

| Code | HTTP Status | Description |
| --- | --- | --- |
| `VALIDATION_ERROR` | `422` | Request body or query params failed validation |
| `NOT_FOUND` | `404` | Requested resource does not exist |
| `DUPLICATE_RESOURCE` | `409` | Unique constraint violation |
| `BUSINESS_RULE_VIOLATION` | `422` | Domain invariant violated |
| `HTTP_ERROR` | varies | Standard HTTP error (405, etc.) |
| `INTERNAL_ERROR` | `500` | Unexpected server error (no stack trace exposed) |

---

## 7. Serialization Rules

| Type | JSON Representation | Example |
| --- | --- | --- |
| UUID | `string` | `"550e8400-e29b-41d4-a716-446655440000"` |
| Decimal (money) | `string` | `"42000.00"` |
| Date | ISO 8601 date | `"2025-11-14"` |
| Datetime | ISO 8601 UTC | `"2025-11-14T12:00:00Z"` |
| Enum | `string` value | `"detected"`, `"INR"` |
| JSON object | native JSON | `{"formula": "..."}` |

---

## 8. Contract Alignment Strategy

To keep frontend types, backend schemas, and JSON Schema files aligned:

1. **Domain model** (`docs/architecture/domain-model.md`) is the conceptual source of truth.
2. **Pydantic schemas** (`apps/api/app/api/schemas/`) implement the domain model for the backend.
3. **JSON Schema** (`contracts/schemas/`) provides the language-agnostic contract.
4. **TypeScript types** (`apps/web/src/types/`) mirror the JSON Schema for the frontend.

**When adding a new entity or field:**

1. Update the domain model documentation.
2. Add/update the Pydantic schema.
3. Add/update the JSON Schema.
4. Add/update the TypeScript type.
5. Add/update the relevant tests.

> **Future Improvement:** Evaluate OpenAPI code generation (e.g., `openapi-typescript`) to automate steps 3–4 from the FastAPI-generated OpenAPI spec.

```