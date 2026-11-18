"""Integration tests for file upload, ingestion, inspection, and retrieval endpoints."""

import io

import openpyxl
import pytest


@pytest.mark.asyncio
async def test_csv_and_xlsx_file_upload_and_retrieval(client):
    """Test end-to-end file ingestion for CSV and XLSX files, isolation, and metadata retrieval."""
    # 1. Create test organization
    org_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Ingestion Corp", "legal_name": "Ingestion Inc", "currency": "EUR"},
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    # 2. Upload valid CSV file
    csv_content = b"po_number,amount,currency\nPO-001,1000.50,EUR\nPO-002,2500.00,EUR\n"
    csv_files = {"file": ("invoices.csv", csv_content, "text/csv")}
    csv_upload_res = await client.post(
        f"/api/v1/organizations/{org_id}/imports",
        files=csv_files,
    )
    assert csv_upload_res.status_code == 201, csv_upload_res.text
    csv_batch = csv_upload_res.json()
    assert csv_batch["organization_id"] == org_id
    assert csv_batch["filename"] == "invoices.csv"
    assert csv_batch["total_rows"] == 2
    assert csv_batch["status"] == "completed"
    assert len(csv_batch["file_hash"]) == 64  # SHA-256 hash
    csv_batch_id = csv_batch["id"]

    # 3. Upload valid XLSX file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["supplier_id", "invoice_no", "total"])
    ws.append(["SUPP-1", "INV-101", 500])
    ws.append(["SUPP-2", "INV-102", 750])
    ws.append(["SUPP-3", "INV-103", 1200])

    xlsx_io = io.BytesIO()
    wb.save(xlsx_io)
    xlsx_bytes = xlsx_io.getvalue()

    xlsx_files = {
        "file": (
            "suppliers.xlsx",
            xlsx_bytes,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    xlsx_upload_res = await client.post(
        f"/api/v1/organizations/{org_id}/imports",
        files=xlsx_files,
    )
    assert xlsx_upload_res.status_code == 201, xlsx_upload_res.text
    xlsx_batch = xlsx_upload_res.json()
    assert xlsx_batch["organization_id"] == org_id
    assert xlsx_batch["filename"] == "suppliers.xlsx"
    assert xlsx_batch["total_rows"] == 3
    assert xlsx_batch["status"] == "completed"

    # 4. List import batches for organization
    list_imports_res = await client.get(f"/api/v1/organizations/{org_id}/imports")
    assert list_imports_res.status_code == 200
    batches_data = list_imports_res.json()
    assert batches_data["total"] >= 2
    batch_ids = [b["id"] for b in batches_data["items"]]
    assert csv_batch_id in batch_ids

    # 5. Fetch single import batch
    get_import_res = await client.get(f"/api/v1/imports/{csv_batch_id}")
    assert get_import_res.status_code == 200
    assert get_import_res.json()["id"] == csv_batch_id

    # 6. Global listing endpoint /api/v1/imports returns 501 Not Implemented
    global_imports_res = await client.get("/api/v1/imports")
    assert global_imports_res.status_code == 501


@pytest.mark.asyncio
async def test_cross_tenant_isolation_on_imports(client):
    """Verify Organization A cannot access or upload to Organization B's imports."""
    # Create Org A and Org B
    res_a = await client.post("/api/v1/organizations", json={"name": "Tenant A", "currency": "USD"})
    org_a_id = res_a.json()["id"]

    res_b = await client.post("/api/v1/organizations", json={"name": "Tenant B", "currency": "USD"})
    org_b_id = res_b.json()["id"]

    # Upload file for Org A
    files = {"file": ("data.csv", b"col1,col2\nval1,val2\n", "text/csv")}
    upload_res = await client.post(f"/api/v1/organizations/{org_a_id}/imports", files=files)
    batch_a_id = upload_res.json()["id"]

    # Org B lists imports -> Org A's batch must NOT be returned
    org_b_list = await client.get(f"/api/v1/organizations/{org_b_id}/imports")
    b_batch_ids = [b["id"] for b in org_b_list.json()["items"]]
    assert batch_a_id not in b_batch_ids


@pytest.mark.asyncio
async def test_unsupported_file_extension_rejected(client):
    """Uploading invalid file format (e.g. .pdf or .txt) returns 400 Bad Request."""
    org_res = await client.post(
        "/api/v1/organizations", json={"name": "Validation Org", "currency": "USD"}
    )
    org_id = org_res.json()["id"]

    bad_files = {"file": ("document.pdf", b"%PDF-1.4 header text", "application/pdf")}
    res = await client.post(f"/api/v1/organizations/{org_id}/imports", files=bad_files)
    assert res.status_code == 400
    res_json = res.json()
    error_msg = res_json.get("error", {}).get("message", "") or res_json.get("detail", "")
    assert "Unsupported file extension" in error_msg
