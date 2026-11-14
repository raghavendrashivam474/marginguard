"""Tests for the standardized error envelope.

Verifies that API errors follow the structure defined in ADR-004.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_404_returns_error_envelope(client: TestClient) -> None:
    """Non-existent routes should return the standard error structure."""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]


def test_method_not_allowed_returns_error_envelope(client: TestClient) -> None:
    """Wrong HTTP method should return the standard error structure."""
    response = client.delete("/health")
    assert response.status_code == 405
    data = response.json()
    assert "error" in data
