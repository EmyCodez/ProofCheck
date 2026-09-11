from dataclasses import dataclass

import pytest

from proofcheck.application.service import (
    InvestigationRequest,
    ProofCheckService,
)


@dataclass
class FakeInvestigationResult:
    text: str
    tool_calls: int


class FakeInvestigator:
    def __init__(self) -> None:
        self.calls = []

    def investigate(self, claim: str, project_id: str):
        self.calls.append((claim, project_id))
        return FakeInvestigationResult(
            text="Investigation completed.",
            tool_calls=2,
        )


def test_service_delegates_investigation():
    investigator = FakeInvestigator()
    service = ProofCheckService(investigator)

    request = InvestigationRequest(
        project_id="project-001",
        claim="Is the invoiced quantity supported?",
    )

    result = service.investigate(request)

    assert result.text == "Investigation completed."
    assert result.tool_calls == 2
    assert investigator.calls == [
        ("Is the invoiced quantity supported?", "project-001")
    ]


def test_service_rejects_empty_project_id():
    service = ProofCheckService(FakeInvestigator())

    with pytest.raises(ValueError, match="Project ID must not be empty"):
        service.investigate(
            InvestigationRequest(
                project_id=" ",
                claim="Is the invoiced quantity supported?",
            )
        )


def test_service_rejects_empty_claim():
    service = ProofCheckService(FakeInvestigator())

    with pytest.raises(ValueError, match="Claim must not be empty"):
        service.investigate(
            InvestigationRequest(
                project_id="project-001",
                claim=" ",
            )
        )


def test_service_strips_input_whitespace():
    investigator = FakeInvestigator()
    service = ProofCheckService(investigator)

    request = InvestigationRequest(
        project_id="  project-001  ",
        claim="  Is the invoiced quantity supported?  ",
    )

    service.investigate(request)

    assert investigator.calls == [
        ("Is the invoiced quantity supported?", "project-001")
    ]