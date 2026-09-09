from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationResult:
    """Deterministic result of an arithmetic validation."""

    valid: bool
    expected_total: float
    observed_total: float
    difference: float


def validate_calculation(
    quantity: float,
    unit_price: float,
    observed_total: float,
    tolerance: float = 0.01,
) -> CalculationResult:
    """
    Validate quantity × unit price against an observed total.

    Args:
        quantity: Quantity from the evidence.
        unit_price: Unit price from the evidence.
        observed_total: Claimed or observed total.
        tolerance: Allowed absolute difference for currency rounding.

    Returns:
        A deterministic calculation result.

    Raises:
        ValueError: If tolerance is negative.
    """
    if tolerance < 0:
        raise ValueError("Tolerance must not be negative.")

    expected_total = quantity * unit_price
    difference = observed_total - expected_total
    valid = abs(difference) <= tolerance + 1e-9

    return CalculationResult(
        valid=valid,
        expected_total=expected_total,
        observed_total=observed_total,
        difference=difference,
    )
