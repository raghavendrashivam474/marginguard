"""MarginGuard API — Finding and Evidence schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceResponse(BaseModel):
    id: UUID
    organization_id: UUID
    finding_id: UUID
    evidence_type: str
    source_record_type: str
    source_record_id: UUID
    description: str
    calculation_details: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    id: UUID
    organization_id: UUID
    finding_type: str
    severity: str
    status: str
    title: str
    description: str
    amount_at_risk: Decimal
    currency: str
    confidence: float
    rule_id: str
    rule_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FindingDetailResponse(FindingResponse):
    """Extended finding response with embedded evidence."""

    evidence: list[EvidenceResponse] = Field(default_factory=list)
