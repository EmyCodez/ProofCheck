from proofcheck.tools.check_required_evidence import check_required_evidence


def test_all_required_evidence_is_present():
    result = check_required_evidence(
        required_types=["CONTRACT", "INVOICE", "WORK_RECORD"],
        present_types=["CONTRACT", "INVOICE", "WORK_RECORD"],
    )

    assert result.complete is True
    assert result.missing_types == []


def test_missing_evidence_is_detected():
    result = check_required_evidence(
        required_types=["CONTRACT", "INVOICE", "WORK_RECORD"],
        present_types=["CONTRACT", "INVOICE"],
    )

    assert result.complete is False
    assert result.missing_types == ["WORK_RECORD"]


def test_duplicate_types_are_removed():
    result = check_required_evidence(
        required_types=["CONTRACT", "INVOICE", "INVOICE"],
        present_types=["CONTRACT", "INVOICE", "INVOICE"],
    )

    assert result.complete is True
    assert result.required_types == ["CONTRACT", "INVOICE"]
    assert result.present_types == ["CONTRACT", "INVOICE"]


def test_empty_requirements_are_complete():
    result = check_required_evidence(
        required_types=[],
        present_types=[],
    )

    assert result.complete is True
    assert result.missing_types == []
