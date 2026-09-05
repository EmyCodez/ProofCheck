import json
from pathlib import Path

from proofcheck.models import ReviewStatus

FIXTURES = Path(__file__).parent / "fixtures" / "golden"


def test_all_12_golden_fixtures_exist():
    fixtures = sorted(FIXTURES.glob("GC-*.json"))
    assert len(fixtures) == 12


def test_golden_fixtures_have_valid_expected_status():
    for path in FIXTURES.glob("GC-*.json"):
        case = json.loads(path.read_text())
        ReviewStatus(case["expected_status"])
        assert "expected_findings" in case
