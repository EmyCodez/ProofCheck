from dataclasses import dataclass


@dataclass(frozen=True)
class ComparisonResult:
    """Deterministic comparison between two numeric evidence values."""

    matches: bool
    expected_value: float
    observed_value: float
    difference: float
    unit: str | None = None


def compare_numeric_evidence(
    expected_value: float,
    observed_value: float,
    unit: str | None = None,
    tolerance: float = 0.0,
) -> ComparisonResult:
    """
    Compare two numeric evidence values deterministically.

    Args:
        expected_value: The reference or expected value.
        observed_value: The value being checked.
        unit: Optional unit associated with both values.
        tolerance: Allowed absolute difference.

    Returns:
        A deterministic comparison result.

    Raises:
        ValueError: If tolerance is negative.
    """
    if tolerance < 0:
        raise ValueError("Tolerance must not be negative.")

    difference = observed_value - expected_value
    matches = abs(difference) <= tolerance + 1e-9

    return ComparisonResult(
        matches=matches,
        expected_value=expected_value,
        observed_value=observed_value,
        difference=difference,
        unit=unit,
    )
