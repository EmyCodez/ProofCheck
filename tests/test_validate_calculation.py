import pytest

from proofcheck.tools.validate_calculation import validate_calculation


def test_valid_calculation() -> None:
    result = validate_calculation(
        quantity=1500,
        unit_price=80,
        observed_total=120000,
    )

    assert result.valid is True
    assert result.expected_total == 120000
    assert result.difference == 0


def test_detects_calculation_error() -> None:
    result = validate_calculation(
        quantity=1500,
        unit_price=80,
        observed_total=125000,
    )

    assert result.valid is False
    assert result.expected_total == 120000
    assert result.difference == 5000


def test_allows_currency_rounding_tolerance() -> None:
    result = validate_calculation(
        quantity=3,
        unit_price=10,
        observed_total=30.01,
        tolerance=0.01,
    )

    assert result.valid is True


def test_negative_tolerance_is_rejected() -> None:
    with pytest.raises(ValueError):
        validate_calculation(
            quantity=100,
            unit_price=10,
            observed_total=1000,
            tolerance=-0.01,
        )
