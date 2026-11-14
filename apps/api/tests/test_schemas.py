"""Tests for Pydantic API schemas.

Verifies that request/response schemas enforce validation rules
and serialize correctly (ADR-004).
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.api.schemas.common import ErrorBody, PaginatedResponse, PaginationParams
from app.api.schemas.organization import OrganizationCreate


class TestOrganizationCreate:
    def test_valid(self) -> None:
        org = OrganizationCreate(name="Test Corp", currency="INR")
        assert org.name == "Test Corp"
        assert org.currency == "INR"

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            OrganizationCreate(name="", currency="INR")

    def test_rejects_invalid_currency(self) -> None:
        with pytest.raises(ValidationError):
            OrganizationCreate(name="Test", currency="inr")

    def test_rejects_long_currency(self) -> None:
        with pytest.raises(ValidationError):
            OrganizationCreate(name="Test", currency="INRR")

    def test_optional_legal_name(self) -> None:
        org = OrganizationCreate(name="Test", currency="USD")
        assert org.legal_name is None


class TestPaginationParams:
    def test_defaults(self) -> None:
        p = PaginationParams()
        assert p.page == 1
        assert p.page_size == 20

    def test_custom(self) -> None:
        p = PaginationParams(page=3, page_size=50)
        assert p.page == 3
        assert p.page_size == 50

    def test_rejects_zero_page(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_rejects_oversized_page(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(page_size=200)


class TestErrorBody:
    def test_minimal(self) -> None:
        err = ErrorBody(code="NOT_FOUND", message="Resource not found")
        assert err.code == "NOT_FOUND"
        assert err.details == []

    def test_with_details(self) -> None:
        err = ErrorBody(
            code="VALIDATION_ERROR",
            message="Invalid data",
            details=[{"field": "currency", "issue": "Must be 3 letters"}],
        )
        assert len(err.details) == 1


class TestPaginatedResponse:
    def test_structure(self) -> None:
        resp = PaginatedResponse[str](
            items=["a", "b"], total=10, page=1, page_size=2
        )
        assert len(resp.items) == 2
        assert resp.total == 10
