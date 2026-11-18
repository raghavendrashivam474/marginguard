"""Integration tests for health check endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_check_endpoints(client):
    """Verify root health check and v1 health check endpoints return HTTP 200."""
    res_root = await client.get("/health")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "healthy"

    res_v1 = await client.get("/api/v1/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["status"] == "healthy"
