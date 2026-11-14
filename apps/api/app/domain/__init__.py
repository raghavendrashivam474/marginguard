"""MarginGuard domain layer.

This package contains business entities, value objects, and domain rules.
It must not depend on FastAPI, SQLAlchemy, Pydantic, or any infrastructure framework.
"""

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
from app.domain.enums import (
    FindingStatus,
    FindingType,
    ImportStatus,
    InvestigationStatus,
    MatchStatus,
    MatchType,
    RecordType,
    Severity,
)
from app.domain.value_objects import Money

__all__ = [
    "DataSource",
    "Evidence",
    "Finding",
    "FindingStatus",
    "FindingType",
    "ImportBatch",
    "ImportStatus",
    "Investigation",
    "InvestigationStatus",
    "Invoice",
    "Match",
    "MatchStatus",
    "MatchType",
    "Money",
    "Organization",
    "Payment",
    "PurchaseOrder",
    "RecordType",
    "Severity",
    "Supplier",
]
