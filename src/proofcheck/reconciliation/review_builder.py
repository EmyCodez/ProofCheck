from datetime import datetime, timezone

from proofcheck.models.schemas import Claim, Finding, Review, ReviewStatus
from proofcheck.reconciliation.decision import determine_review_status


def calculate_confidence(
    *,
    evidence_complete: bool,
    source_agreement: float,
    deterministic_validation: float,
    retrieval_quality: float,
    version_consistency: float,
) -> float:
    """
    Calculate ProofCheck's explainable confidence heuristic.

    This is a heuristic score, not a calibrated probability.
    """
    values = (
        source_agreement,
        deterministic_validation,
        retrieval_quality,
        version_consistency,
    )

    if any(not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("Confidence inputs must be between 0.0 and 1.0.")

    completeness = 1.0 if evidence_complete else 0.0

    confidence = (
        completeness * 0.30
        + source_agreement * 0.25
        + deterministic_validation * 0.25
        + retrieval_quality * 0.10
        + version_consistency * 0.10
    )

    return round(confidence, 4)


def build_review(
    *,
    claim: Claim,
    evidence_complete: bool,
    findings: list[Finding],
    evidence_ids: list[str],
    missing_evidence: list[str],
    source_agreement: float,
    deterministic_validation: float,
    retrieval_quality: float,
    version_consistency: float,
    technical_failure: bool = False,
) -> Review:
    """Build the final structured ProofCheck review."""
    status = determine_review_status(
        evidence_complete=evidence_complete,
        findings=findings,
        technical_failure=technical_failure,
    )

    confidence = calculate_confidence(
        evidence_complete=evidence_complete,
        source_agreement=source_agreement,
        deterministic_validation=deterministic_validation,
        retrieval_quality=retrieval_quality,
        version_consistency=version_consistency,
    )

    if status == ReviewStatus.SUPPORTED:
        summary = "The available evidence is sufficiently consistent."
        recommendation = "No material discrepancy identified; human review remains responsible for the final decision."

    elif status == ReviewStatus.REVIEW_REQUIRED:
        summary = "The available evidence contains a material discrepancy or is incomplete."
        recommendation = "Human review is required before relying on the claim."

    else:
        summary = "The investigation could not reliably establish the result because of a technical failure."
        recommendation = "Resolve the technical failure and repeat the investigation."

    if findings:
        summary = f"{summary} {len(findings)} finding(s) identified."

    now = datetime.now(timezone.utc)

    return Review(
        review_id=f"review-{claim.claim_id}-{now.strftime('%Y%m%d%H%M%S%f')}",
        project_id=claim.project_id,
        claim_id=claim.claim_id,
        status=status,
        confidence=confidence,
        summary=summary,
        findings=findings,
        evidence_ids=evidence_ids,
        missing_evidence=missing_evidence,
        recommendation=recommendation,
        created_at=now,
        completed_at=now,
    )
