"""Regression tests for health endpoints.

Verifies that MG-S0.1 functionality remains intact after MG-S0.2 changes.
These are the only runtime regression checks required by the sprint brief.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_health(client: TestClient) -> None:
    """GET /health must return 200 with expected structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "marginguard-api"
    assert "version" in data


def test_v1_health(client: TestClient) -> None:
    """GET /api/v1/health must return 200 (existing v1 router)."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_openapi_docs_accessible(client: TestClient) -> None:
    """GET /docs must return 200 (Swagger UI)."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible(client: TestClient) -> None:
    """GET /redoc must return 200 (ReDoc)."""
    response = client.get("/redoc")
    assert response.status_code == 200
