"""SQLAlchemy implementation of OrganizationRepository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports import OrganizationRepository
from app.domain.entities import Organization
from app.infrastructure.models import OrganizationModel


class SqlAlchemyOrganizationRepository(OrganizationRepository):
    """Concrete Organization repository backed by PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _to_domain(model: OrganizationModel) -> Organization:
        """Convert ORM model to domain entity."""
        return Organization(
            id=model.id,
            name=model.name,
            currency=model.currency,
            created_at=model.created_at,
            updated_at=model.updated_at,
            legal_name=model.legal_name,
        )

    @staticmethod
    def _to_model(
        entity: Organization, existing: OrganizationModel | None = None
    ) -> OrganizationModel:
        """Convert domain entity to ORM model (create or update)."""
        if existing is not None:
            existing.name = entity.name
            existing.currency = entity.currency
            existing.legal_name = entity.legal_name
            existing.updated_at = entity.updated_at
            return existing
        return OrganizationModel(
            id=entity.id,
            name=entity.name,
            currency=entity.currency,
            legal_name=entity.legal_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    # -- port implementation ----------------------------------------------

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        model = self._session.get(OrganizationModel, organization_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def list_all(self, *, page: int = 1, page_size: int = 20) -> list[Organization]:
        offset = (page - 1) * page_size
        stmt = (
            select(OrganizationModel)
            .order_by(OrganizationModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    async def save(self, organization: Organization) -> Organization:
        existing = self._session.get(OrganizationModel, organization.id)
        model = self._to_model(organization, existing)
        if existing is None:
            self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)
