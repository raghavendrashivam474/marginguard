"""SQLAlchemy repository adapter for DataSource domain entity."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports import DataSourceRepository
from app.domain.entities import DataSource
from app.infrastructure.models import DataSourceModel


class SqlAlchemyDataSourceRepository(DataSourceRepository):
    """SQLAlchemy implementation of DataSourceRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, data_source: DataSource) -> DataSource:
        """Persist or update a DataSource entity."""
        model = self._session.get(DataSourceModel, data_source.id)
        if model is None:
            model = DataSourceModel(
                id=data_source.id,
                organization_id=data_source.organization_id,
                source_type=data_source.source_type,
                source_name=data_source.source_name,
                created_at=data_source.created_at,
            )
            self._session.add(model)
        else:
            model.source_type = data_source.source_type
            model.source_name = data_source.source_name

        self._session.commit()
        self._session.refresh(model)

        return DataSource(
            id=model.id,
            organization_id=model.organization_id,
            source_type=model.source_type,
            source_name=model.source_name,
            created_at=model.created_at,
        )

    def find_or_create(
        self,
        organization_id: uuid.UUID,
        source_type: str,
        source_name: str,
    ) -> DataSource:
        """Find an existing DataSource by org and name, or create a new one."""
        stmt = select(DataSourceModel).where(
            DataSourceModel.organization_id == organization_id,
            DataSourceModel.source_name == source_name,
            DataSourceModel.source_type == source_type,
        )
        result = self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            now = datetime.now(timezone.utc)
            data_source_id = uuid.uuid4()
            model = DataSourceModel(
                id=data_source_id,
                organization_id=organization_id,
                source_type=source_type,
                source_name=source_name,
                created_at=now,
            )
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)

        return DataSource(
            id=model.id,
            organization_id=model.organization_id,
            source_type=model.source_type,
            source_name=model.source_name,
            created_at=model.created_at,
        )

    def get_by_id(self, source_id: uuid.UUID) -> DataSource | None:
        """Retrieve a DataSource by primary key."""
        model = self._session.get(DataSourceModel, source_id)
        if model is None:
            return None

        return DataSource(
            id=model.id,
            organization_id=model.organization_id,
            source_type=model.source_type,
            source_name=model.source_name,
            created_at=model.created_at,
        )

    def list_by_organization(self, organization_id: uuid.UUID) -> list[DataSource]:
        """List all data sources belonging to an organization."""
        stmt = select(DataSourceModel).where(DataSourceModel.organization_id == organization_id)
        models = self._session.scalars(stmt).all()
        return [
            DataSource(
                id=m.id,
                organization_id=m.organization_id,
                source_type=m.source_type,
                source_name=m.source_name,
                created_at=m.created_at,
            )
            for m in models
        ]
