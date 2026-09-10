import logging

import gradio as gr

from proofcheck.application.factory import create_proofcheck_service
from proofcheck.application.service import InvestigationRequest
from proofcheck.reconciliation.evidence_reconciler import EvidenceReconciler
from proofcheck.logging_config import configure_logging

DEFAULT_PROJECT_ID = "project-001"
DEFAULT_PROJECT = "Al Noor Office Building — Flooring Package"
logger = logging.getLogger(__name__)
configure_logging()

DEFAULT_CLAIM = (
    "Is invoice INV1042 sufficiently supported by the available "
    "project evidence?"
)


service = create_proofcheck_service(
    project_id=DEFAULT_PROJECT_ID,
)

reconciler = EvidenceReconciler()

def investigate_claim(project: str, claim: str) -> str:
    """Run a ProofCheck investigation from the UI."""

    if not project.strip():
        raise gr.Error("Please select a project.")

    if not claim.strip():
        raise gr.Error("Please enter a claim to investigate.")

    logger.info("investigation_started | project_id=%s", DEFAULT_PROJECT_ID)

    request = InvestigationRequest(
        project_id=DEFAULT_PROJECT_ID,
        claim=claim,
    )

    investigation = service.investigate(request)

    if investigation.blocked:
        logger.warning(
            "investigation_blocked | project_id=%s | tool_calls=%s",
            DEFAULT_PROJECT_ID,
            investigation.tool_calls,
        )
        return (
            "## ⚫ BLOCKED\n\n"
            "The investigation could not reliably establish the result "
            "because of a technical failure."
        )

    reconciliation = reconciler.reconcile(investigation)

    logger.info(
        "investigation_completed | project_id=%s | status=%s | tool_calls=%s",
        DEFAULT_PROJECT_ID,
        "REVIEW_REQUIRED" if reconciliation.findings or not reconciliation.evidence_complete else "SUPPORTED",
        investigation.tool_calls,
    )

    if reconciliation.findings:
        status = "🔴 REVIEW REQUIRED"
        summary = (
            "The available evidence contains a material discrepancy "
            "that requires human review."
        )
    elif not reconciliation.evidence_complete:
        status = "🔴 REVIEW REQUIRED"
        summary = (
            "The available evidence is incomplete and requires human review."
        )
    else:
        status = "🟢 SUPPORTED"
        summary = "The available evidence is sufficiently consistent."

    evidence_text = (
        "\n".join(
            f"- `{evidence_id}`"
            for evidence_id in reconciliation.evidence_ids
        )
        or "- None identified"
    )

    findings_text = (
        "\n".join(
            f"- **{finding.type.value}** — {finding.description}"
            for finding in reconciliation.findings
        )
        or "- No deterministic discrepancies identified."
    )

    missing_text = (
        "\n".join(
            f"- `{missing}`"
            for missing in reconciliation.missing_evidence
        )
        or "- None identified"
    )

    return (
        f"## {status}\n\n"
        f"**Summary:** {summary}\n\n"
        f"### Findings\n{findings_text}\n\n"
        f"### Evidence\n{evidence_text}\n\n"
        f"### Missing Evidence\n{missing_text}\n\n"
        "**Recommendation:** Human review remains responsible for the "
        "final decision."
    )


def build_app() -> gr.Blocks:
    """Build the ProofCheck user interface."""

    with gr.Blocks(title="ProofCheck") as app:
        gr.Markdown(
            """
# ProofCheck
### Evidence Reconciliation Agent

**Don't just summarize documents. Prove whether they agree.**
"""
        )

        project = gr.Dropdown(
            choices=[DEFAULT_PROJECT],
            value=DEFAULT_PROJECT,
            label="Project",
        )

        claim = gr.Textbox(
            value=DEFAULT_CLAIM,
            label="Claim",
            lines=3,
        )

        with gr.Row():
            investigate_button = gr.Button(
                "Investigate Claim",
                variant="primary",
            )
            clear_button = gr.ClearButton(
                components=[project, claim],
                value="Clear",
            )

        result = gr.Markdown(
            value="Click **Investigate Claim** to begin.",
        )

        investigate_button.click(
            fn=investigate_claim,
            inputs=[project, claim],
            outputs=result,
            show_progress="full",
        )

        clear_button.add(
            result,
        )

    return app


if __name__ == "__main__":
    build_app().launch()
