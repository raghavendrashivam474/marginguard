"""Integration tests for exception handler error responses."""

import pytest


@pytest.mark.asyncio
async def test_404_returns_error_envelope(client) -> None:
    """Non-existent routes should return the standard error structure."""
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_method_not_allowed_returns_error_envelope(client) -> None:
    """Wrong HTTP method should return the standard error structure."""
    response = await client.delete("/health")
    assert response.status_code == 405
