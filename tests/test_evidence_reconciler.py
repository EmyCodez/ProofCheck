from proofcheck.agent.investigator import (
    InvestigationResult,
    InvestigationToolResult,
)
from proofcheck.reconciliation.evidence_reconciler import EvidenceReconciler
from proofcheck.models.schemas import FindingType, Severity


def test_reconciler_creates_calculation_finding():
    investigation = InvestigationResult(
        text="The invoice total does not match the calculated total.",
        tool_calls=2,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice total"},
                result=[
                    {"chunk_id": "invoice-chunk-001", "document_id": "invoice-001"},
                ],
            ),
            InvestigationToolResult(
                tool_name="validate_calculation",
                arguments={
                    "quantity": 1500,
                    "unit_price": 80,
                    "observed_total": 125000,
                },
                result={
                    "valid": False,
                    "expected_total": 120000,
                    "observed_total": 125000,
                    "difference": 5000,
                },
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert len(result.findings) == 1
    assert result.findings[0].type == FindingType.CALCULATION_ERROR
    assert result.findings[0].evidence_ids == ["invoice-chunk-001"]


def test_reconciler_does_not_create_finding_for_valid_calculation():
    investigation = InvestigationResult(
        text="The calculation is valid.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="validate_calculation",
                arguments={
                    "quantity": 1500,
                    "unit_price": 80,
                    "observed_total": 120000,
                },
                result={
                    "valid": True,
                    "expected_total": 120000,
                    "observed_total": 120000,
                    "difference": 0,
                },
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.findings == []


def test_reconciler_collects_evidence_ids_from_search_results():
    investigation = InvestigationResult(
        text="Evidence was found.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity"},
                result=[
                    {
                        "chunk_id": "invoice-chunk-001",
                        "document_id": "invoice-001",
                    },
                    {
                        "chunk_id": "measurement-chunk-001",
                        "document_id": "measurement-001",
                    },
                ],
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.evidence_ids == [
        "invoice-chunk-001",
        "measurement-chunk-001",
    ]


def test_reconciler_preserves_required_evidence_check():
    investigation = InvestigationResult(
        text="Required evidence is incomplete.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="check_required_evidence",
                arguments={
                    "required_types": [
                        "CONTRACT",
                        "INVOICE",
                        "WORK_RECORD",
                    ],
                    "present_types": [
                        "CONTRACT",
                        "INVOICE",
                    ],
                },
                result={
                    "complete": False,
                    "required_types": [
                        "CONTRACT",
                        "INVOICE",
                        "WORK_RECORD",
                    ],
                    "present_types": [
                        "CONTRACT",
                        "INVOICE",
                    ],
                    "missing_types": ["WORK_RECORD"],
                },
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.evidence_complete is False
    assert result.missing_evidence == ["WORK_RECORD"]


def test_reconciler_preserves_technical_failure():
    investigation = InvestigationResult(
        text=None,
        tool_calls=1,
        blocked=True,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity"},
                result={
                    "error": "Retrieval service unavailable.",
                    "tool_failed": True,
                },
                failed=True,
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.technical_failure is True
    assert result.evidence_complete is False


def test_reconciler_builds_review_from_investigation():
    from proofcheck.models.schemas import Claim, ReviewStatus

    claim = Claim(
        claim_id="claim-001",
        project_id="project-001",
        description="Is the invoiced quantity supported?",
        source_document_id="invoice-001",
        claimed_quantity=1500,
        unit="m2",
        claimed_unit_price=80,
        claimed_total=125000,
    )

    investigation = InvestigationResult(
        text="The invoice calculation contains a discrepancy.",
        tool_calls=2,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity total"},
                result=[
                    {
                        "chunk_id": "invoice-chunk-001",
                        "document_id": "invoice-001",
                    },
                ],
            ),
            InvestigationToolResult(
                tool_name="validate_calculation",
                arguments={
                    "quantity": 1500,
                    "unit_price": 80,
                    "observed_total": 125000,
                },
                result={
                    "valid": False,
                    "expected_total": 120000,
                    "observed_total": 125000,
                    "difference": 5000,
                },
            ),
        ],
    )

    result = EvidenceReconciler().build_review(
        claim=claim,
        investigation=investigation,
        source_agreement=0.0,
        deterministic_validation=0.0,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert result.status == ReviewStatus.REVIEW_REQUIRED
    assert result.claim_id == "claim-001"
    assert result.project_id == "project-001"
    assert result.evidence_ids == ["invoice-chunk-001"]
    assert len(result.findings) == 1
    assert result.findings[0].type == FindingType.CALCULATION_ERROR


def test_reconciler_does_not_mark_empty_investigation_as_complete():
    investigation = InvestigationResult(
        text="No additional evidence was gathered.",
        tool_calls=0,
        tool_results=[],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.evidence_complete is False
    assert result.evidence_ids == []

def test_reconciler_does_not_assume_evidence_complete_from_search():
    investigation = InvestigationResult(
        text="Evidence was found.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity"},
                result=[
                    {
                        "chunk_id": "invoice-chunk-001",
                        "document_id": "invoice-001",
                    }
                ],
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.evidence_complete is False
    assert result.evidence_ids == ["invoice-chunk-001"]

def test_reconciler_creates_quantity_finding_from_comparison():
    investigation = InvestigationResult(
        text="Quantity differs.",
        tool_calls=2,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity"},
                result=[
                    {"chunk_id": "invoice-chunk-001"},
                    {"chunk_id": "measurement-chunk-001"},
                ],
            ),
            InvestigationToolResult(
                tool_name="compare_evidence",
                arguments={
                    "expected_value": 1280,
                    "observed_value": 1500,
                    "unit": "m2",
                },
                result={
                    "matches": False,
                    "expected_value": 1280,
                    "observed_value": 1500,
                    "difference": 220,
                    "unit": "m2",
                },
            ),
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert len(result.findings) == 1
    assert result.findings[0].type == FindingType.QUANTITY_CONFLICT
    assert result.findings[0].difference == 220
    assert result.findings[0].evidence_ids == [
        "invoice-chunk-001",
        "measurement-chunk-001",
    ]

def test_reconciler_collects_evidence_ids_from_dataclass_results():
    from proofcheck.tools.search_evidence import EvidenceSearchResult

    investigation = InvestigationResult(
        text="Evidence found.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="search_evidence",
                arguments={"query": "invoice quantity"},
                result=[
                    EvidenceSearchResult(
                        chunk_id="invoice-chunk-001",
                        document_id="invoice-001",
                        document_type="INVOICE",
                        text="Invoice quantity: 1500 m²",
                        page=1,
                        section="Invoice Line Item",
                        score=0.9,
                    ),
                    EvidenceSearchResult(
                        chunk_id="measurement-chunk-001",
                        document_id="measurement-001",
                        document_type="WORK_RECORD",
                        text="Measured quantity: 1280 m²",
                        page=1,
                        section="Measurement",
                        score=0.8,
                    ),
                ],
            ),
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert result.evidence_ids == [
        "invoice-chunk-001",
        "measurement-chunk-001",
    ]

def test_reconciler_creates_missing_evidence_finding():
    investigation = InvestigationResult(
        text="Approved change order evidence is missing.",
        tool_calls=1,
        tool_results=[
            InvestigationToolResult(
                tool_name="check_required_evidence",
                arguments={
                    "required_types": [
                        "CHANGE_REQUEST",
                        "APPROVED_CHANGE",
                    ],
                    "present_types": [
                        "CHANGE_REQUEST",
                    ],
                },
                result={
                    "complete": False,
                    "required_types": [
                        "CHANGE_REQUEST",
                        "APPROVED_CHANGE",
                    ],
                    "present_types": [
                        "CHANGE_REQUEST",
                    ],
                    "missing_types": [
                        "APPROVED_CHANGE",
                    ],
                },
            )
        ],
    )

    result = EvidenceReconciler().reconcile(investigation)

    assert len(result.findings) == 1
    assert result.findings[0].type == FindingType.MISSING_EVIDENCE
    assert result.findings[0].severity == Severity.HIGH
    assert "APPROVED_CHANGE" in result.findings[0].description
    assert result.findings[0].evidence_ids == []