"""Dependency injection utilities for FastAPI routes."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.import_batch_service import ImportBatchService
from app.application.services.ingestion_service import IngestionService
from app.application.services.organization_service import OrganizationService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import (
    SqlAlchemyDataSourceRepository,
    SqlAlchemyImportBatchRepository,
    SqlAlchemyOrganizationRepository,
)
from app.infrastructure.storage.base import StoragePort
from app.infrastructure.storage.local_storage import LocalFileStorageService


def get_storage_service() -> StoragePort:
    """Dependency that provides the local storage service."""
    return LocalFileStorageService()


def get_organization_service(
    session: Session = Depends(get_db),
) -> OrganizationService:
    """Dependency for OrganizationService."""
    repo = SqlAlchemyOrganizationRepository(session)
    return OrganizationService(repo)


def get_import_batch_service(
    session: Session = Depends(get_db),
) -> ImportBatchService:
    """Dependency for ImportBatchService."""
    repo = SqlAlchemyImportBatchRepository(session)
    return ImportBatchService(repo)


def get_ingestion_service(
    session: Session = Depends(get_db),
    storage: StoragePort = Depends(get_storage_service),
) -> IngestionService:
    """Dependency for IngestionService."""
    batch_repo = SqlAlchemyImportBatchRepository(session)
    data_source_repo = SqlAlchemyDataSourceRepository(session)
    return IngestionService(
        import_batch_repo=batch_repo,
        data_source_repo=data_source_repo,
        storage_service=storage,
    )
