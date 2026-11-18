\"\"\"SQLAlchemy repository adapter for ImportBatch domain entity.\"\"\"

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.application.ports import ImportBatchRepository
from app.domain.entities import ImportBatch
from app.domain.enums import ImportStatus
from app.infrastructure.models import ImportBatchModel


class SqlAlchemyImportBatchRepository(ImportBatchRepository):
    \"\"\"SQLAlchemy implementation of ImportBatchRepository.\"\"\"

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        batch: ImportBatch,
        file_hash: str | None = None,
        storage_key: str | None = None,
        error_summary: dict[str, Any] | None = None,
    ) -> ImportBatch:
        \"\"\"Persist or update an ImportBatch domain entity.\"\"\"
        model = self._session.get(ImportBatchModel, batch.id)
        if model is None:
            model = ImportBatchModel(
                id=batch.id,
                organization_id=batch.organization_id,
                data_source_id=batch.data_source_id,
                file_name=batch.file_name,
                file_type=batch.file_type,
                status=str(batch.status),
                total_rows=batch.total_rows or 0,
                successful_rows=batch.successful_rows,
                failed_rows=batch.failed_rows,
                file_hash=file_hash or getattr(batch, "file_hash", None),
                storage_key=storage_key or getattr(batch, "storage_key", None),
                error_summary=error_summary or getattr(batch, "error_summary", None),
                created_at=batch.created_at,
                completed_at=batch.completed_at,
            )
            self._session.add(model)
        else:
            model.status = str(batch.status)
            model.total_rows = batch.total_rows if batch.total_rows is not None else model.total_rows
            model.successful_rows = batch.successful_rows
            model.failed_rows = batch.failed_rows
            if file_hash:
                model.file_hash = file_hash
            if storage_key:
                model.storage_key = storage_key
            if error_summary is not None:
                model.error_summary = error_summary
            model.completed_at = batch.completed_at

        self._session.commit()
        self._session.refresh(model)

        return self._to_domain(model)

    def get_by_id(self, batch_id: uuid.UUID) -> ImportBatch | None:
        \"\"\"Retrieve an ImportBatch by primary key.\"\"\"
        model = self._session.get(ImportBatchModel, batch_id)
        if model is None:
            return None
        return self._to_domain(model)

    def update_status(
        self,
        batch_id: uuid.UUID,
        status: ImportStatus,
        successful_rows: int | None = None,
        failed_rows: int | None = None,
        error_summary: dict[str, Any] | None = None,
    ) -> ImportBatch | None:
        \"\"\"Update the status and row metrics of an import batch.\"\"\"
        model = self._session.get(ImportBatchModel, batch_id)
        if model is None:
            return None

        model.status = str(status)
        if successful_rows is not None:
            model.successful_rows = successful_rows
        if failed_rows is not None:
            model.failed_rows = failed_rows
        if error_summary is not None:
            model.error_summary = error_summary

        if status in (
            ImportStatus.COMPLETED,
            ImportStatus.FAILED,
            ImportStatus.PARTIALLY_COMPLETED,
        ):
            model.completed_at = datetime.now(timezone.utc)

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def list_by_organization(
        self,
        organization_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ImportBatch], int]:
        \"\"\"List paginated import batches for a specific organization.\"\"\"
        count_stmt = (
            select(func.count())
            .select_from(ImportBatchModel)
            .where(ImportBatchModel.organization_id == organization_id)
        )
        total = self._session.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = (
            select(ImportBatchModel)
            .where(ImportBatchModel.organization_id == organization_id)
            .order_by(ImportBatchModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        items = [self._to_domain(m) for m in models]

        return items, total

    @staticmethod
    def _to_domain(model: ImportBatchModel) -> ImportBatch:
        \"\"\"Map ORM model to domain entity.\"\"\"
        batch = ImportBatch(
            id=model.id,
            organization_id=model.organization_id,
            data_source_id=model.data_source_id,
            file_name=model.file_name,
            file_type=model.file_type,
            status=ImportStatus(model.status)
            if model.status in ImportStatus.__members__.values()
            else ImportStatus.COMPLETED,
            created_at=model.created_at,
            total_rows=model.total_rows,
            successful_rows=model.successful_rows,
            failed_rows=model.failed_rows,
            completed_at=model.completed_at,
        )
        # Attach non-dataclass storage attributes dynamically
        if model.file_hash:
            object.__setattr__(batch, "file_hash", model.file_hash)
        if model.storage_key:
            object.__setattr__(batch, "storage_key", model.storage_key)
        if model.error_summary:
            object.__setattr__(batch, "error_summary", model.error_summary)
        return batch
