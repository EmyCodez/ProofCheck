from proofcheck.models.schemas import Finding, FindingType, Severity
from proofcheck.tools.compare_evidence import compare_numeric_evidence
from proofcheck.tools.validate_calculation import validate_calculation


def reconcile_quantity(
    expected_quantity: float,
    observed_quantity: float,
    expected_unit: str,
    observed_unit: str,
    evidence_ids: list[str],
) -> Finding | None:
    """Create a deterministic quantity finding when values differ or units mismatch."""

    if expected_unit != observed_unit:
        return Finding(
            finding_id="finding-unit-mismatch",
            type=FindingType.UNIT_MISMATCH,
            severity=Severity.HIGH,
            description=(
                f"Expected unit {expected_unit} differs from "
                f"observed unit {observed_unit}."
            ),
            expected_value=expected_quantity,
            observed_value=observed_quantity,
            unit=expected_unit,
            evidence_ids=evidence_ids,
        )

    result = compare_numeric_evidence(
        expected_value=expected_quantity,
        observed_value=observed_quantity,
        unit=expected_unit,
    )

    if result.matches:
        return None

    return Finding(
        finding_id="finding-quantity-conflict",
        type=FindingType.QUANTITY_CONFLICT,
        severity=Severity.HIGH,
        description=(
            f"Observed quantity differs from expected quantity by "
            f"{result.difference:g} {expected_unit}."
        ),
        expected_value=result.expected_value,
        observed_value=result.observed_value,
        difference=result.difference,
        unit=expected_unit,
        evidence_ids=evidence_ids,
    )


def reconcile_calculation(
    quantity: float,
    unit_price: float,
    observed_total: float,
    evidence_ids: list[str],
) -> Finding | None:
    """Create a deterministic calculation finding when arithmetic is wrong."""
    result = validate_calculation(
        quantity=quantity,
        unit_price=unit_price,
        observed_total=observed_total,
    )

    if result.valid:
        return None

    return Finding(
        finding_id="finding-calculation-error",
        type=FindingType.CALCULATION_ERROR,
        severity=Severity.HIGH,
        description=(
            f"Observed total differs from calculated total by "
            f"{result.difference:g}."
        ),
        expected_value=result.expected_total,
        observed_value=result.observed_total,
        difference=result.difference,
        evidence_ids=evidence_ids,
    )


def reconcile_approved_measured_invoiced(
    approved_quantity: float,
    measured_quantity: float,
    invoiced_quantity: float,
    unit: str,
    evidence_ids: list[str],
) -> list[Finding]:
    """Reconcile approved, measured, and invoiced quantities deterministically."""

    findings = []

    measured_vs_approved = compare_numeric_evidence(
        expected_value=approved_quantity,
        observed_value=measured_quantity,
        unit=unit,
    )

    invoiced_vs_measured = compare_numeric_evidence(
        expected_value=measured_quantity,
        observed_value=invoiced_quantity,
        unit=unit,
    )

    # Measurement may legitimately be below the approved quantity.
    # The invoice should agree with the verified measurement.
    if not invoiced_vs_measured.matches:
        findings.append(
            Finding(
                finding_id="finding-invoice-measurement-conflict",
                type=FindingType.QUANTITY_CONFLICT,
                severity=Severity.HIGH,
                description=(
                    f"Invoiced quantity differs from measured quantity by "
                    f"{invoiced_vs_measured.difference:g} {unit}."
                ),
                expected_value=invoiced_vs_measured.expected_value,
                observed_value=invoiced_vs_measured.observed_value,
                difference=invoiced_vs_measured.difference,
                unit=unit,
                evidence_ids=evidence_ids,
            )
        )

    return findings