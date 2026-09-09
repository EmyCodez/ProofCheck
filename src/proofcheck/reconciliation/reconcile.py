from proofcheck.models.schemas import Finding, FindingType, Severity
from proofcheck.tools.compare_evidence import compare_numeric_evidence
from proofcheck.tools.validate_calculation import validate_calculation


def reconcile_quantity(
    expected_quantity: float,
    observed_quantity: float,
    unit: str,
    evidence_ids: list[str],
) -> Finding | None:
    """Create a deterministic quantity-conflict finding when values differ."""
    result = compare_numeric_evidence(
        expected_value=expected_quantity,
        observed_value=observed_quantity,
        unit=unit,
    )

    if result.matches:
        return None

    return Finding(
        finding_id="finding-quantity-conflict",
        type=FindingType.QUANTITY_CONFLICT,
        severity=Severity.HIGH,
        description=(
            f"Observed quantity differs from expected quantity by "
            f"{result.difference:g} {unit}."
        ),
        expected_value=result.expected_value,
        observed_value=result.observed_value,
        difference=result.difference,
        unit=unit,
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
