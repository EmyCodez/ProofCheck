from proofcheck.models.schemas import FindingType, Severity
from proofcheck.reconciliation.reconcile import (
    reconcile_calculation,
    reconcile_quantity,
)


def test_reconcile_quantity_returns_no_finding_when_values_match():
    result = reconcile_quantity(
        expected_quantity=1300,
        observed_quantity=1300,
        unit="m2",
        evidence_ids=["evidence-001"],
    )

    assert result is None


def test_reconcile_quantity_creates_conflict():
    result = reconcile_quantity(
        expected_quantity=1300,
        observed_quantity=1500,
        unit="m2",
        evidence_ids=["approved-change-001", "invoice-001"],
    )

    assert result is not None
    assert result.type == FindingType.QUANTITY_CONFLICT
    assert result.severity == Severity.HIGH
    assert result.expected_value == 1300
    assert result.observed_value == 1500
    assert result.difference == 200
    assert result.unit == "m2"
    assert result.evidence_ids == [
        "approved-change-001",
        "invoice-001",
    ]


def test_reconcile_calculation_returns_no_finding_when_valid():
    result = reconcile_calculation(
        quantity=1500,
        unit_price=80,
        observed_total=120000,
        evidence_ids=["invoice-001"],
    )

    assert result is None


def test_reconcile_calculation_creates_error():
    result = reconcile_calculation(
        quantity=1500,
        unit_price=80,
        observed_total=125000,
        evidence_ids=["invoice-001"],
    )

    assert result is not None
    assert result.type == FindingType.CALCULATION_ERROR
    assert result.severity == Severity.HIGH
    assert result.expected_value == 120000
    assert result.observed_value == 125000
    assert result.difference == 5000
    assert result.evidence_ids == ["invoice-001"]
