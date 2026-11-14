"""MarginGuard application layer.

This package contains use cases, application services, and repository ports.
It depends on the Domain layer only. Infrastructure implements the ports
defined here.
"""

from app.application.ports import (
    DataSourceRepository,
    EvidenceRepository,
    FindingRepository,
    ImportBatchRepository,
    InvestigationRepository,
    InvoiceRepository,
    MatchRepository,
    OrganizationRepository,
    PaymentRepository,
    PurchaseOrderRepository,
    SupplierRepository,
)

__all__ = [
    "DataSourceRepository",
    "EvidenceRepository",
    "FindingRepository",
    "ImportBatchRepository",
    "InvestigationRepository",
    "InvoiceRepository",
    "MatchRepository",
    "OrganizationRepository",
    "PaymentRepository",
    "PurchaseOrderRepository",
    "SupplierRepository",
]
