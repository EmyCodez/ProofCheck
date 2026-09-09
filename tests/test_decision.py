import pytest

from proofcheck.models.schemas import Finding, FindingType, ReviewStatus, Severity
from proofcheck.reconciliation.decision import determine_review_status


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


def test_complete_evidence_with_no_findings_is_supported():
    status = determine_review_status(
        evidence_complete=True,
        findings=[],
    )

    assert status == ReviewStatus.SUPPORTED


def test_missing_evidence_requires_review():
    status = determine_review_status(
        evidence_complete=False,
        findings=[],
    )

    assert status == ReviewStatus.REVIEW_REQUIRED


def test_material_finding_requires_review():
    status = determine_review_status(
        evidence_complete=True,
        findings=[make_finding()],
    )

    assert status == ReviewStatus.REVIEW_REQUIRED


def test_technical_failure_blocks_result():
    status = determine_review_status(
        evidence_complete=True,
        findings=[],
        technical_failure=True,
    )

    assert status == ReviewStatus.BLOCKED


def test_technical_failure_takes_precedence_over_missing_evidence():
    status = determine_review_status(
        evidence_complete=False,
        findings=[],
        technical_failure=True,
    )

    assert status == ReviewStatus.BLOCKED


def test_technical_failure_takes_precedence_over_business_finding():
    status = determine_review_status(
        evidence_complete=True,
        findings=[make_finding()],
        technical_failure=True,
    )

    assert status == ReviewStatus.BLOCKED
