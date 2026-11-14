"""MarginGuard application layer — repository ports.

These are abstract interfaces (Ports) that define how the Application layer
accesses persistent data. The Infrastructure layer provides concrete
implementations (Adapters) that satisfy these interfaces.

This inversion of dependency ensures the Application and Domain layers
never import SQLAlchemy, PostgreSQL, or any persistence framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import (
    DataSource,
    Evidence,
    Finding,
    ImportBatch,
    Investigation,
    Invoice,
    Match,
    Organization,
    Payment,
    PurchaseOrder,
    Supplier,
)


class OrganizationRepository(ABC):
    """Port for Organization persistence."""

    @abstractmethod
    async def get_by_id(self, organization_id: UUID) -> Organization | None: ...

    @abstractmethod
    async def list_all(self, *, page: int = 1, page_size: int = 20) -> list[Organization]: ...

    @abstractmethod
    async def save(self, organization: Organization) -> Organization: ...


class DataSourceRepository(ABC):
    """Port for DataSource persistence."""

    @abstractmethod
    async def get_by_id(self, data_source_id: UUID) -> DataSource | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[DataSource]: ...

    @abstractmethod
    async def save(self, data_source: DataSource) -> DataSource: ...


class ImportBatchRepository(ABC):
    """Port for ImportBatch persistence."""

    @abstractmethod
    async def get_by_id(self, batch_id: UUID) -> ImportBatch | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[ImportBatch]: ...

    @abstractmethod
    async def save(self, batch: ImportBatch) -> ImportBatch: ...

    @abstractmethod
    async def update_status(self, batch_id: UUID, status: str) -> None: ...


class SupplierRepository(ABC):
    """Port for Supplier persistence."""

    @abstractmethod
    async def get_by_id(self, supplier_id: UUID) -> Supplier | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Supplier]: ...

    @abstractmethod
    async def save(self, supplier: Supplier) -> Supplier: ...


class PurchaseOrderRepository(ABC):
    """Port for PurchaseOrder persistence."""

    @abstractmethod
    async def get_by_id(self, po_id: UUID) -> PurchaseOrder | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[PurchaseOrder]: ...

    @abstractmethod
    async def save(self, purchase_order: PurchaseOrder) -> PurchaseOrder: ...


class InvoiceRepository(ABC):
    """Port for Invoice persistence."""

    @abstractmethod
    async def get_by_id(self, invoice_id: UUID) -> Invoice | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Invoice]: ...

    @abstractmethod
    async def save(self, invoice: Invoice) -> Invoice: ...


class PaymentRepository(ABC):
    """Port for Payment persistence."""

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Payment]: ...

    @abstractmethod
    async def save(self, payment: Payment) -> Payment: ...


class MatchRepository(ABC):
    """Port for Match persistence."""

    @abstractmethod
    async def get_by_id(self, match_id: UUID) -> Match | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Match]: ...

    @abstractmethod
    async def save(self, match: Match) -> Match: ...


class FindingRepository(ABC):
    """Port for Finding persistence."""

    @abstractmethod
    async def get_by_id(self, finding_id: UUID) -> Finding | None: ...

    @abstractmethod
    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Finding]: ...

    @abstractmethod
    async def save(self, finding: Finding) -> Finding: ...

    @abstractmethod
    async def update_status(self, finding_id: UUID, status: str) -> None: ...


class EvidenceRepository(ABC):
    """Port for Evidence persistence."""

    @abstractmethod
    async def list_by_finding(self, finding_id: UUID) -> list[Evidence]: ...

    @abstractmethod
    async def save(self, evidence: Evidence) -> Evidence: ...


class InvestigationRepository(ABC):
    """Port for Investigation persistence."""

    @abstractmethod
    async def get_by_finding(self, finding_id: UUID) -> Investigation | None: ...

    @abstractmethod
    async def save(self, investigation: Investigation) -> Investigation: ...
