from datetime import datetime, timezone

import pytest

from proofcheck.models.schemas import Claim, Finding, FindingType, ReviewStatus, Severity
from proofcheck.tools.generate_review_report import generate_review_report


def make_claim() -> Claim:
    return Claim(
        claim_id="claim-001",
        project_id="al-noor-office-building",
        description="Invoice quantity for office floor tiles",
        source_document_id="06_invoice_INV1042",
        claimed_quantity=1500,
        unit="m²",
        claimed_unit_price=80,
        claimed_total=120000,
        created_at=datetime.now(timezone.utc),
    )


def make_finding() -> Finding:
    return Finding(
        finding_id="finding-001",
        type=FindingType.QUANTITY_CONFLICT,
        severity=Severity.HIGH,
        description="Invoice quantity exceeds measured quantity.",
        expected_value=1280,
        observed_value=1500,
        difference=220,
        unit="m²",
        evidence_ids=["evidence-001", "evidence-002"],
    )


def test_generates_structured_review():
    claim = make_claim()
    finding = make_finding()

    review = generate_review_report(
        claim=claim,
        status=ReviewStatus.REVIEW_REQUIRED,
        confidence=0.92,
        summary="Invoice quantity is not fully supported by the available evidence.",
        findings=[finding],
        evidence=["evidence-001", "evidence-002"],
        missing_evidence=[],
        recommendation="Human review is required.",
    )

    assert review.project_id == claim.project_id
    assert review.claim_id == claim.claim_id
    assert review.status == ReviewStatus.REVIEW_REQUIRED
    assert review.confidence == 0.92
    assert len(review.findings) == 1
    assert review.findings[0].type == FindingType.QUANTITY_CONFLICT
    assert review.evidence_ids == ["evidence-001", "evidence-002"]


def test_generates_supported_review():
    claim = make_claim()

    review = generate_review_report(
        claim=claim,
        status=ReviewStatus.SUPPORTED,
        confidence=0.98,
        summary="The claim is supported by the available evidence.",
        findings=[],
        evidence=["evidence-001"],
        missing_evidence=[],
        recommendation="No material discrepancy identified; human review remains responsible for the final decision.",
    )

    assert review.status == ReviewStatus.SUPPORTED
    assert review.findings == []
    assert review.missing_evidence == []


def test_rejects_invalid_confidence():
    claim = make_claim()

    with pytest.raises(ValueError):
        generate_review_report(
            claim=claim,
            status=ReviewStatus.SUPPORTED,
            confidence=1.5,
            summary="Valid summary.",
            findings=[],
            evidence=[],
            missing_evidence=[],
            recommendation="Human review.",
        )


def test_rejects_empty_summary():
    claim = make_claim()

    with pytest.raises(ValueError):
        generate_review_report(
            claim=claim,
            status=ReviewStatus.SUPPORTED,
            confidence=0.9,
            summary="   ",
            findings=[],
            evidence=[],
            missing_evidence=[],
            recommendation="Human review.",
        )


def test_rejects_empty_recommendation():
    claim = make_claim()

    with pytest.raises(ValueError):
        generate_review_report(
            claim=claim,
            status=ReviewStatus.SUPPORTED,
            confidence=0.9,
            summary="Valid summary.",
            findings=[],
            evidence=[],
            missing_evidence=[],
            recommendation="   ",
        )
