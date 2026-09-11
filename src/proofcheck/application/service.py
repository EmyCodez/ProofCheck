from dataclasses import dataclass

from proofcheck.agent.investigator import InvestigationAgent, InvestigationResult


@dataclass(frozen=True)
class InvestigationRequest:
    """Input required to investigate one claim."""

    project_id: str
    claim: str


class ProofCheckService:
    """Application-level orchestration for ProofCheck investigations."""

    def __init__(self, investigator: InvestigationAgent) -> None:
        self.investigator = investigator

    def investigate(
        self,
        request: InvestigationRequest,
    ) -> InvestigationResult:
        """Run one bounded evidence investigation."""

        if not request.project_id.strip():
            raise ValueError("Project ID must not be empty.")

        if not request.claim.strip():
            raise ValueError("Claim must not be empty.")

        return self.investigator.investigate(
            claim=request.claim.strip(),
            project_id=request.project_id.strip(),
        )
