from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    CONTRACT = "CONTRACT"
    BOQ = "BOQ"
    CHANGE_REQUEST = "CHANGE_REQUEST"
    APPROVED_CHANGE = "APPROVED_CHANGE"
    WORK_RECORD = "WORK_RECORD"
    INVOICE = "INVOICE"
    CORRESPONDENCE = "CORRESPONDENCE"
    OTHER = "OTHER"


class EvidenceType(str, Enum):
    TEXT = "TEXT"
    TABLE = "TABLE"
    LINE_ITEM = "LINE_ITEM"
    QUANTITY = "QUANTITY"
    PRICE = "PRICE"
    DATE = "DATE"
    REFERENCE = "REFERENCE"
    STATUS = "STATUS"


class FindingType(str, Enum):
    QUANTITY_CONFLICT = "QUANTITY_CONFLICT"
    PRICE_CONFLICT = "PRICE_CONFLICT"
    TOTAL_CONFLICT = "TOTAL_CONFLICT"
    DATE_CONFLICT = "DATE_CONFLICT"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    DESCRIPTION_MISMATCH = "DESCRIPTION_MISMATCH"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    DUPLICATE = "DUPLICATE"
    CALCULATION_ERROR = "CALCULATION_ERROR"


class ReviewStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Document(BaseModel):
    document_id: str
    project_id: str
    filename: str
    document_type: DocumentType
    revision: str | None = None
    document_date: str | None = None
    source: str
    uploaded_at: datetime | None = None
    checksum: str | None = None
    parser_status: str = "PENDING"


class Evidence(BaseModel):
    evidence_id: str
    document_id: str
    project_id: str
    page: int | None = None
    section: str | None = None
    text: str
    field_name: str | None = None
    field_value: str | None = None
    numeric_value: float | None = None
    unit: str | None = None
    evidence_type: EvidenceType
    revision: str | None = None
    document_date: str | None = None
    retrieval_score: float | None = None

class RetrievalChunk(BaseModel):
    chunk_id: str
    document_id: str
    project_id: str
    document_type: DocumentType
    chunk_type: str
    text: str
    page: int | None = None
    section: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    claim_id: str
    project_id: str
    description: str
    source_document_id: str
    claimed_quantity: float | None = None
    unit: str | None = None
    claimed_unit_price: float | None = None
    claimed_total: float | None = None
    created_at: datetime | None = None


class Finding(BaseModel):
    finding_id: str
    type: FindingType
    severity: Severity
    description: str
    expected_value: Any | None = None
    observed_value: Any | None = None
    difference: float | None = None
    unit: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class Review(BaseModel):
    review_id: str
    project_id: str
    claim_id: str
    status: ReviewStatus
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    recommendation: str
    created_at: datetime | None = None
    completed_at: datetime | None = None


class InvestigationStep(BaseModel):
    step_number: int
    action: str
    tool: str
    status: str
    latency_ms: float | None = None


class InvestigationTrace(BaseModel):
    trace_id: str
    review_id: str
    steps: list[InvestigationStep] = Field(default_factory=list)
