import uuid
from unittest.mock import MagicMock

import pytest

from app.application.services.ingestion_service import IngestionService
from app.domain.enums import ImportStatus
from app.infrastructure.storage.base import StoragePort, StoredFileResult


class InMemoryImportBatchRepo:
    def __init__(self):
        self.batches = {}

    def save(self, batch, file_hash=None, storage_key=None, error_summary=None):
        if file_hash:
            batch.file_hash = file_hash
        if storage_key:
            batch.storage_key = storage_key
        if error_summary:
            batch.error_summary = error_summary
        self.batches[batch.id] = batch
        return batch

    def get_by_id(self, batch_id):
        return self.batches.get(batch_id)


class InMemoryDataSourceRepo:
    def find_or_create(self, organization_id, source_type, source_name):
        ds = MagicMock()
        ds.id = uuid.uuid4()
        ds.organization_id = organization_id
        ds.source_type = source_type
        ds.source_name = source_name
        return ds


class MockStoragePort(StoragePort):
    async def save_file(
        self, organization_id_str: str, filename: str, content: bytes
    ) -> StoredFileResult:
        from pathlib import Path

        return StoredFileResult(
            storage_key=f"test/{organization_id_str}/{filename}",
            file_path=Path(f"/tmp/{filename}"),
            filename=filename,
            file_size=len(content),
            checksum_sha256="fakehash123",
        )

    async def get_file_path(self, storage_key: str):
        return None


class InMemorySupplierRepo:
    def __init__(self):
        self.suppliers = []

    def save(self, supplier):
        self.suppliers.append(supplier)
        return supplier


class InMemoryInvoiceRepo:
    def __init__(self):
        self.invoices = []

    def save(self, invoice):
        self.invoices.append(invoice)
        return invoice


@pytest.mark.asyncio
async def test_ingestion_service_supplier_csv():
    batch_repo = InMemoryImportBatchRepo()
    ds_repo = InMemoryDataSourceRepo()
    storage = MockStoragePort()
    supplier_repo = InMemorySupplierRepo()

    service = IngestionService(
        import_batch_repo=batch_repo,
        data_source_repo=ds_repo,
        storage_service=storage,
        supplier_repo=supplier_repo,
    )

    csv_content = (
        "vendor_name,tax_id,currency\nAcme Global,TX-999,USD\nBeta Corp,TX-888,EUR\n"
    ).encode("utf-8")

    org_id = uuid.uuid4()
    batch = await service.process_file_upload(
        organization_id=org_id,
        filename="suppliers.csv",
        content=csv_content,
    )

    assert batch.status == ImportStatus.COMPLETED
    assert batch.total_rows == 2
    assert batch.successful_rows == 2
    assert batch.failed_rows == 0
    assert len(supplier_repo.suppliers) == 2
    assert supplier_repo.suppliers[0].name == "Acme Global"
    assert supplier_repo.suppliers[0].source_row_number == 2
    assert supplier_repo.suppliers[1].source_row_number == 3


@pytest.mark.asyncio
async def test_ingestion_service_partial_success_csv():
    batch_repo = InMemoryImportBatchRepo()
    ds_repo = InMemoryDataSourceRepo()
    storage = MockStoragePort()
    invoice_repo = InMemoryInvoiceRepo()

    service = IngestionService(
        import_batch_repo=batch_repo,
        data_source_repo=ds_repo,
        storage_service=storage,
        invoice_repo=invoice_repo,
    )

    # Row 1 is valid, Row 2 has bad total_amount ("INVALID_MONEY")
    csv_content = (
        "invoice_number,issue_date,subtotal,tax_amount,total_amount,currency\n"
        "INV-001,2026-03-01,100.00,10.00,110.00,USD\n"
        "INV-002,2026-03-02,200.00,20.00,INVALID_MONEY,USD\n"
    ).encode("utf-8")

    org_id = uuid.uuid4()
    batch = await service.process_file_upload(
        organization_id=org_id,
        filename="invoices.csv",
        content=csv_content,
    )

    assert batch.status == ImportStatus.PARTIALLY_COMPLETED
    assert batch.total_rows == 2
    assert batch.successful_rows == 1
    assert batch.failed_rows == 1
    assert len(invoice_repo.invoices) == 1
    assert invoice_repo.invoices[0].external_reference == "INV-001"
    assert batch.error_summary is not None
    assert len(batch.error_summary["errors"]) == 1
    assert batch.error_summary["errors"][0]["source_row_number"] == 3
