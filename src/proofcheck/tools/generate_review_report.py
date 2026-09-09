from datetime import datetime, timezone

from proofcheck.models.schemas import Claim, Finding, Review, ReviewStatus


def generate_review_report(
    claim: Claim,
    status: ReviewStatus,
    confidence: float,
    summary: str,
    findings: list[Finding],
    evidence: list[str],
    missing_evidence: list[str],
    recommendation: str,
) -> Review:
    """
    Generate a structured evidence-backed review report.

    This function does not make the business decision.
    It packages the investigation result for human review.
    """

    if not 0.0 <= confidence <= 1.0:
        raise ValueError("Confidence must be between 0.0 and 1.0.")

    if not summary.strip():
        raise ValueError("Summary must not be empty.")

    if not recommendation.strip():
        raise ValueError("Recommendation must not be empty.")

    now = datetime.now(timezone.utc)

    return Review(
        review_id=f"review-{claim.claim_id}-{now.strftime('%Y%m%d%H%M%S%f')}",
        project_id=claim.project_id,
        claim_id=claim.claim_id,
        status=status,
        confidence=confidence,
        summary=summary,
        findings=findings,
        evidence_ids=evidence,
        missing_evidence=missing_evidence,
        recommendation=recommendation,
        created_at=now,
        completed_at=now,
    )
