"""Ingestion orchestration service for validating, storing, tracking, and processing uploaded files into canonical financial records."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.application.ports import DataSourceRepository, ImportBatchRepository
from app.application.services.csv_reader import CsvRowReader
from app.application.services.file_inspector import FileInspector
from app.application.services.row_mappers import (
    DocumentCategory,
    InvoiceRowMapper,
    PaymentRowMapper,
    PurchaseOrderRowMapper,
    SupplierRowMapper,
    detect_document_category,
)
from app.domain.entities import ImportBatch, Invoice, Payment, PurchaseOrder, Supplier
from app.domain.enums import ImportStatus
from app.infrastructure.repositories import (
    SqlAlchemyInvoiceRepository,
    SqlAlchemyPaymentRepository,
    SqlAlchemyPurchaseOrderRepository,
    SqlAlchemySupplierRepository,
)
from app.infrastructure.storage.base import StoragePort

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates file upload ingestion, storage, inspection, row-level parsing, and canonical persistence."""

    def __init__(
        self,
        import_batch_repo: ImportBatchRepository,
        data_source_repo: DataSourceRepository,
        storage_service: StoragePort,
        supplier_repo: SqlAlchemySupplierRepository | None = None,
        po_repo: SqlAlchemyPurchaseOrderRepository | None = None,
        invoice_repo: SqlAlchemyInvoiceRepository | None = None,
        payment_repo: SqlAlchemyPaymentRepository | None = None,
    ) -> None:
        self._batch_repo = import_batch_repo
        self._data_source_repo = data_source_repo
        self._storage = storage_service
        self._supplier_repo = supplier_repo
        self._po_repo = po_repo
        self._invoice_repo = invoice_repo
        self._payment_repo = payment_repo

        # Initialize default row mappers
        self._mappers = {
            DocumentCategory.SUPPLIER: SupplierRowMapper(),
            DocumentCategory.PURCHASE_ORDER: PurchaseOrderRowMapper(),
            DocumentCategory.INVOICE: InvoiceRowMapper(),
            DocumentCategory.PAYMENT: PaymentRowMapper(),
        }

    async def process_file_upload(
        self,
        organization_id: uuid.UUID,
        filename: str,
        content: bytes,
        source_type: str = "file_upload",
        forced_category: str | None = None,
    ) -> ImportBatch:
        """Inspect, persist file to storage, parse CSV rows into financial domain records, and track lifecycle."""
        inspection = FileInspector.inspect_file(content=content, filename=filename)
        if not inspection.is_valid:
            raise ValueError(
                inspection.error_message or f"File '{filename}' failed structural inspection."
            )

        data_source = self._data_source_repo.find_or_create(
            organization_id=organization_id,
            source_type=source_type,
            source_name=filename,
        )

        stored_file = await self._storage.save_file(
            organization_id_str=str(organization_id),
            filename=filename,
            content=content,
        )

        now = datetime.now(timezone.utc)
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "csv"
        batch_id = uuid.uuid4()

        import_batch = ImportBatch(
            id=batch_id,
            organization_id=organization_id,
            data_source_id=data_source.id,
            file_name=filename,
            file_type=ext,
            status=ImportStatus.PROCESSING,
            created_at=now,
            total_rows=inspection.total_rows,
            successful_rows=0,
            failed_rows=0,
            file_hash=stored_file.checksum_sha256,
            storage_key=stored_file.storage_key,
        )

        # Save initial PENDING/PROCESSING batch
        if hasattr(self._batch_repo, "save"):
            try:
                import_batch = self._batch_repo.save(
                    import_batch,
                    file_hash=stored_file.checksum_sha256,
                    storage_key=stored_file.storage_key,
                )
            except TypeError:
                import_batch = self._batch_repo.save(import_batch)

        # Row-by-Row Ingestion for CSV files
        successful_rows = 0
        failed_rows = 0
        error_details: list[dict[str, Any]] = []

        if ext == "csv" and content:
            parsed_rows = list(CsvRowReader.read_bytes(content))

            if parsed_rows:
                # Detect category from the headers of the first row
                headers = list(parsed_rows[0].data.keys())
                category = forced_category or detect_document_category(headers)
                mapper = self._mappers.get(category) if category else None

                for parsed_row in parsed_rows:
                    if mapper is None:
                        successful_rows += 1
                        continue

                    domain_entity, row_errors = mapper.map_row(
                        parsed_row=parsed_row,
                        import_batch_id=str(batch_id),
                        organization_id=organization_id,
                    )

                    if row_errors:
                        failed_rows += 1
                        for err in row_errors:
                            error_details.append(err.to_dict())
                    elif domain_entity is not None:
                        try:
                            self._persist_domain_entity(domain_entity)
                            successful_rows += 1
                        except Exception as exc:
                            logger.error(
                                "Failed to persist domain record at row %d: %s",
                                parsed_row.source_row_number,
                                exc,
                            )
                            failed_rows += 1
                            error_details.append(
                                {
                                    "source_row_number": parsed_row.source_row_number,
                                    "field_name": "database",
                                    "error_code": "PERSISTENCE_ERROR",
                                    "message": str(exc),
                                    "original_value": None,
                                }
                            )
                    else:
                        successful_rows += 1

        # Determine final status
        total = inspection.total_rows or (successful_rows + failed_rows)
        if failed_rows == 0:
            final_status = ImportStatus.COMPLETED
        elif successful_rows > 0:
            final_status = ImportStatus.PARTIALLY_COMPLETED
        else:
            final_status = ImportStatus.FAILED

        import_batch.status = final_status
        import_batch.total_rows = total
        import_batch.successful_rows = successful_rows
        import_batch.failed_rows = failed_rows
        import_batch.completed_at = datetime.now(timezone.utc)
        import_batch.error_summary = {"errors": error_details[:100]} if error_details else None

        if hasattr(self._batch_repo, "save"):
            try:
                import_batch = self._batch_repo.save(
                    import_batch,
                    file_hash=stored_file.checksum_sha256,
                    storage_key=stored_file.storage_key,
                    error_summary=import_batch.error_summary,
                )
            except TypeError:
                import_batch = self._batch_repo.save(import_batch)

        logger.info(
            "Completed ingestion for batch %s: status=%s, success=%d, failed=%d",
            batch_id,
            final_status,
            successful_rows,
            failed_rows,
        )
        return import_batch

    def _persist_domain_entity(self, entity: Any) -> None:
        """Helper to route domain entity to correct SQLAlchemy repository."""
        if isinstance(entity, Supplier) and self._supplier_repo:
            self._supplier_repo.save(entity)
        elif isinstance(entity, PurchaseOrder) and self._po_repo:
            self._po_repo.save(entity)
        elif isinstance(entity, Invoice) and self._invoice_repo:
            self._invoice_repo.save(entity)
        elif isinstance(entity, Payment) and self._payment_repo:
            self._payment_repo.save(entity)

    # Alias for method name
    ingest_file = process_file_upload
