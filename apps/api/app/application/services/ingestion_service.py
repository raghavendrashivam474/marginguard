"""Ingestion orchestration service for validating, storing, and tracking uploaded files."""

import logging
import uuid
from datetime import datetime, timezone

from app.application.ports import DataSourceRepository, ImportBatchRepository
from app.application.services.file_inspector import FileInspector
from app.domain.entities import ImportBatch
from app.domain.enums import ImportStatus
from app.infrastructure.storage.base import StoragePort

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates file upload ingestion, storage, inspection, and database tracking."""

    def __init__(
        self,
        import_batch_repo: ImportBatchRepository,
        data_source_repo: DataSourceRepository,
        storage_service: StoragePort,
    ) -> None:
        self._batch_repo = import_batch_repo
        self._data_source_repo = data_source_repo
        self._storage = storage_service

    async def process_file_upload(
        self,
        organization_id: uuid.UUID,
        filename: str,
        content: bytes,
        source_type: str = "file_upload",
    ) -> ImportBatch:
        """Inspect, persist file to storage, and save ImportBatch metadata."""
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

        import_batch = ImportBatch(
            id=uuid.uuid4(),
            organization_id=organization_id,
            data_source_id=data_source.id,
            file_name=filename,
            file_type=ext,
            status=ImportStatus.COMPLETED,
            created_at=now,
            total_rows=inspection.total_rows,
            successful_rows=0,
            failed_rows=0,
            completed_at=now,
        )

        # Pass storage metadata to repository save
        if hasattr(self._batch_repo, "save"):
            try:
                saved_batch = self._batch_repo.save(
                    import_batch,
                    file_hash=stored_file.checksum_sha256,
                    storage_key=stored_file.storage_key,
                )
            except TypeError:
                saved_batch = self._batch_repo.save(import_batch)
        else:
            saved_batch = import_batch

        logger.info(
            "Successfully processed upload for org %s: batch %s (storage_key=%s, rows=%d)",
            organization_id,
            saved_batch.id,
            stored_file.storage_key,
            inspection.total_rows,
        )
        return saved_batch

    # Alias for method name
    ingest_file = process_file_upload
