"""MarginGuard API — custom exceptions and FastAPI exception handlers.

Provides a standardized error envelope for all API error responses.
See ADR-004 and contracts/schemas/common.schema.json.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class MarginGuardError(Exception):
    """Base exception for all MarginGuard business errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class NotFoundError(MarginGuardError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{resource_id}' not found.",
            status_code=404,
        )


class DuplicateResourceError(MarginGuardError):
    """Raised when a unique constraint would be violated."""

    def __init__(self, resource: str, detail: str) -> None:
        super().__init__(
            code="DUPLICATE_RESOURCE",
            message=f"Duplicate {resource}: {detail}",
            status_code=409,
        )


class BusinessRuleError(MarginGuardError):
    """Raised when a business invariant is violated."""

    def __init__(self, message: str, details: list[dict] | None = None) -> None:
        super().__init__(
            code="BUSINESS_RULE_VIOLATION",
            message=message,
            status_code=422,
            details=details,
        )


def _build_error_response(
    code: str,
    message: str,
    status_code: int,
    details: list[dict] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Construct a standardized JSON error response."""
    body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": request_id or str(uuid.uuid4()),
        }
    }
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(MarginGuardError)
    async def marginguard_error_handler(
        request: Request, exc: MarginGuardError
    ) -> JSONResponse:
        return _build_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"]),
                "issue": err["msg"],
            }
            for err in exc.errors()
        ]
        return _build_error_response(
            code="VALIDATION_ERROR",
            message="The supplied data is invalid.",
            status_code=422,
            details=details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _build_error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Never expose internal stack traces in production
        return _build_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            status_code=500,
        )
