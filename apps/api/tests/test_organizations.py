"""Integration tests for organization management endpoints."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_organization_crud_flow(client):
    """Test organization creation, retrieval, listing, and updates via REST API."""
    # 1. Create Organization
    create_payload = {
        "name": "Acme Industrial",
        "legal_name": "Acme Industrial Holdings LLC",
        "currency": "USD",
    }
    res = await client.post("/api/v1/organizations", json=create_payload)
    assert res.status_code == 201, res.text
    org_data = res.json()
    assert org_data["name"] == "Acme Industrial"
    assert org_data["currency"] == "USD"
    org_id = org_data["id"]

    # 2. Get Organization by ID
    get_res = await client.get(f"/api/v1/organizations/{org_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == org_id

    # 3. List Organizations
    list_res = await client.get("/api/v1/organizations")
    assert list_res.status_code == 200
    res_json = list_res.json()
    items = res_json["items"] if isinstance(res_json, dict) else res_json
    assert len(items) >= 1
    assert any(item["id"] == org_id for item in items)

    # 4. Get Non-existent Organization returns 404
    fake_id = str(uuid.uuid4())
    not_found_res = await client.get(f"/api/v1/organizations/{fake_id}")
    assert not_found_res.status_code == 404
