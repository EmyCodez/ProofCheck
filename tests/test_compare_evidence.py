import pytest

from proofcheck.tools.compare_evidence import compare_numeric_evidence


def test_matching_values() -> None:
    result = compare_numeric_evidence(
        expected_value=1300,
        observed_value=1300,
        unit="m²",
    )

    assert result.matches is True
    assert result.difference == 0
    assert result.unit == "m²"


def test_detects_difference() -> None:
    result = compare_numeric_evidence(
        expected_value=1280,
        observed_value=1500,
        unit="m²",
    )

    assert result.matches is False
    assert result.difference == 220


def test_tolerance_allows_small_difference() -> None:
    result = compare_numeric_evidence(
        expected_value=100,
        observed_value=100.01,
        tolerance=0.01,
    )

    assert result.matches is True


def test_negative_tolerance_is_rejected() -> None:
    with pytest.raises(ValueError):
        compare_numeric_evidence(
            expected_value=100,
            observed_value=100,
            tolerance=-1,
        )
