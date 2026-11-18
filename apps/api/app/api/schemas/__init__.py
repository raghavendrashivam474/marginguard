"""MarginGuard API schemas.

Pydantic v2 models for request validation and response serialization.
These are the authoritative backend contracts (see ADR-004).
"""

from app.api.schemas.common import (
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.api.schemas.financial import (
    InvoiceResponse,
    PaymentResponse,
    PurchaseOrderResponse,
    SupplierResponse,
)
from app.api.schemas.finding import (
    EvidenceResponse,
    FindingDetailResponse,
    FindingResponse,
)
from app.api.schemas.import_batch import (
    ImportBatchListResponse,
    ImportBatchResponse,
)
from app.api.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)

__all__ = [
    "ErrorBody",
    "ErrorDetail",
    "ErrorResponse",
    "EvidenceResponse",
    "FindingDetailResponse",
    "FindingResponse",
    "ImportBatchListResponse",
    "ImportBatchResponse",
    "InvoiceResponse",
    "OrganizationCreate",
    "OrganizationResponse",
    "PaginatedResponse",
    "PaginationParams",
    "PaymentResponse",
    "PurchaseOrderResponse",
    "SupplierResponse",
]
