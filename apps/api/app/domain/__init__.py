"""MarginGuard domain layer.

This package contains business entities, value objects, and domain rules.
It must not depend on FastAPI, SQLAlchemy, Pydantic, or any infrastructure framework.
"""

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
    "FindingStatus",
    "FindingType",
    "ImportStatus",
    "InvestigationStatus",
    "MatchStatus",
    "MatchType",
    "Money",
    "RecordType",
    "Severity",
]
