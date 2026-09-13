import os
import logging

import gradio as gr

from proofcheck.application.factory import create_proofcheck_service
from proofcheck.application.projects import PROJECTS
from proofcheck.application.service import InvestigationRequest
from proofcheck.logging_config import configure_logging
from proofcheck.reconciliation.evidence_reconciler import EvidenceReconciler


logger = logging.getLogger(__name__)
configure_logging()


DEFAULT_PROJECT = next(iter(PROJECTS))
DEFAULT_PROJECT_CONFIG = PROJECTS[DEFAULT_PROJECT]

CLAIM_EXAMPLES = [
    (
        "Supported — approved change order",
        "Does Approved Change Order CO-001 formally approve an additional 300 m² of F-01 at AED 80 per m²?",
    ),
    (
        "Invoice quantity — INV1042",
        "Is invoice INV1042 sufficiently supported by the available project evidence?",
    ),
    (
        "Invoice price — INV1042",
        "Is the unit price charged in invoice INV1042 supported by the available project evidence?",
    ),
    (
        "Approved vs measured vs invoiced",
        "Is the invoiced quantity consistent with the approved and measured quantities?",
    ),
    (
        "Change approval",
        "Is the invoiced change supported by formal project approval?",
    ),
]

service = create_proofcheck_service(
    project_id=DEFAULT_PROJECT_CONFIG.project_id,
    corpus_dir=DEFAULT_PROJECT_CONFIG.corpus_dir,
)

reconciler = EvidenceReconciler()


def on_project_change(project: str) -> str:
    """Load the default claim for the selected project."""

    if not project or project not in PROJECTS:
        return "Select an example claim or enter your own."

    return PROJECTS[project].default_claim


def on_claim_example_change(example: str) -> str:
    """Load the selected example claim into the editable claim box."""

    if not example:
        return ""

    for label, claim_text in CLAIM_EXAMPLES:
        if example == label:
            return claim_text

    return ""


def investigate_claim(project: str, claim: str) -> str:
    """Run a ProofCheck investigation from the UI."""

    if not project or project not in PROJECTS:
        raise gr.Error("Please select a project.")

    if not claim or not claim.strip():
        raise gr.Error("Please enter a claim to investigate.")

    project_config = PROJECTS[project]

    logger.info(
        "investigation_started | project_id=%s",
        project_config.project_id,
    )

    request = InvestigationRequest(
        project_id=project_config.project_id,
        claim=claim.strip(),
    )

    investigation = service.investigate(request)

    if investigation.blocked:
        logger.warning(
            "investigation_blocked | project_id=%s | tool_calls=%s",
            project_config.project_id,
            investigation.tool_calls,
        )
        return (
            "## ⚫ BLOCKED\n\n"
            "The investigation could not reliably establish the result "
            "because of a technical failure."
        )

    reconciliation = reconciler.reconcile(investigation)

    status_value = (
        "REVIEW_REQUIRED"
        if reconciliation.findings or not reconciliation.evidence_complete
        else "SUPPORTED"
    )

    logger.info(
        "investigation_completed | project_id=%s | status=%s | tool_calls=%s",
        project_config.project_id,
        status_value,
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
            choices=list(PROJECTS.keys()),
            value=None,
            label="Project",
            info="Select the project whose evidence you want to investigate.",
        )

        claim_example = gr.Dropdown(
            choices=[label for label, _ in CLAIM_EXAMPLES],
            value=None,
            label="Example claims",
            info="Choose an example or write your own claim below.",
        )

        claim = gr.Textbox(
            value="Select an example claim or enter your own.",
            label="Claim to investigate",
            lines=3,
            info="You can edit the example or enter your own evidence question.",
        )

        with gr.Row():
            investigate_button = gr.Button(
                "Investigate Claim",
                variant="primary",
            )
            clear_button = gr.ClearButton(
                components=[project, claim_example, claim],
                value="Clear",
            )

        result = gr.Markdown(
            value="Select a project and investigate a claim.",
        )

        project.change(
            fn=on_project_change,
            inputs=project,
            outputs=claim,
        )

        claim_example.change(
            fn=on_claim_example_change,
            inputs=claim_example,
            outputs=claim,
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
    build_app().launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
    )
