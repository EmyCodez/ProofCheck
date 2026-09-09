from proofcheck.models.schemas import (
    Claim,
    Finding,
    FindingType,
    ReviewStatus,
    Severity,
)
from proofcheck.reconciliation.review_builder import (
    build_review,
    calculate_confidence,
)


def make_claim() -> Claim:
    return Claim(
        claim_id="claim-001",
        project_id="project-001",
        description="Is the invoiced quantity supported?",
        source_document_id="invoice-001",
        claimed_quantity=1500,
        unit="m2",
        claimed_unit_price=80,
        claimed_total=120000,
    )


def make_finding() -> Finding:
    return Finding(
        finding_id="finding-001",
        type=FindingType.QUANTITY_CONFLICT,
        severity=Severity.HIGH,
        description="Quantity differs.",
        expected_value=1300,
        observed_value=1500,
        difference=200,
        unit="m2",
        evidence_ids=["evidence-001", "evidence-002"],
    )


def test_confidence_uses_defined_weights():
    confidence = calculate_confidence(
        evidence_complete=True,
        source_agreement=1.0,
        deterministic_validation=1.0,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert confidence == 1.0


def test_incomplete_evidence_reduces_confidence():
    confidence = calculate_confidence(
        evidence_complete=False,
        source_agreement=1.0,
        deterministic_validation=1.0,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert confidence == 0.7


def test_supported_claim_builds_supported_review():
    review = build_review(
        claim=make_claim(),
        evidence_complete=True,
        findings=[],
        evidence_ids=["evidence-001"],
        missing_evidence=[],
        source_agreement=1.0,
        deterministic_validation=1.0,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert review.status == ReviewStatus.SUPPORTED
    assert review.confidence == 1.0
    assert review.findings == []
    assert review.missing_evidence == []


def test_conflicting_claim_builds_review_required():
    review = build_review(
        claim=make_claim(),
        evidence_complete=True,
        findings=[make_finding()],
        evidence_ids=["evidence-001", "evidence-002"],
        missing_evidence=[],
        source_agreement=0.5,
        deterministic_validation=0.5,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert review.status == ReviewStatus.REVIEW_REQUIRED
    assert len(review.findings) == 1
    assert review.confidence == 0.75


def test_missing_evidence_builds_review_required():
    review = build_review(
        claim=make_claim(),
        evidence_complete=False,
        findings=[],
        evidence_ids=["evidence-001"],
        missing_evidence=["APPROVED_CHANGE"],
        source_agreement=1.0,
        deterministic_validation=1.0,
        retrieval_quality=1.0,
        version_consistency=1.0,
    )

    assert review.status == ReviewStatus.REVIEW_REQUIRED
    assert review.missing_evidence == ["APPROVED_CHANGE"]


def test_technical_failure_builds_blocked_review():
    review = build_review(
        claim=make_claim(),
        evidence_complete=False,
        findings=[],
        evidence_ids=[],
        missing_evidence=[],
        source_agreement=0.0,
        deterministic_validation=0.0,
        retrieval_quality=0.0,
        version_consistency=0.0,
        technical_failure=True,
    )

    assert review.status == ReviewStatus.BLOCKED
    assert review.confidence == 0.0
    assert "technical failure" in review.summary.lower()


def test_confidence_rejects_out_of_range_inputs():
    try:
        calculate_confidence(
            evidence_complete=True,
            source_agreement=1.2,
            deterministic_validation=1.0,
            retrieval_quality=1.0,
            version_consistency=1.0,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "between 0.0 and 1.0" in str(exc)
