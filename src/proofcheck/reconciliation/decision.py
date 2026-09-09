from proofcheck.models.schemas import Finding, ReviewStatus


def determine_review_status(
    *,
    evidence_complete: bool,
    findings: list[Finding],
    technical_failure: bool = False,
) -> ReviewStatus:
    """
    Determine the review status from deterministic investigation state.

    Technical failures take precedence over business-evidence findings because
    the system cannot reliably establish the result when a required dependency
    has failed.
    """
    if technical_failure:
        return ReviewStatus.BLOCKED

    if not evidence_complete or findings:
        return ReviewStatus.REVIEW_REQUIRED

    return ReviewStatus.SUPPORTED
