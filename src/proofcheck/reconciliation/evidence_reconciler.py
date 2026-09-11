from dataclasses import dataclass, field

from proofcheck.agent.investigator import InvestigationResult
from proofcheck.reconciliation.reconcile import (
    reconcile_calculation,
    reconcile_quantity,
)
from proofcheck.reconciliation.review_builder import build_review as build_structured_review

@dataclass(frozen=True)
class ReconciliationResult:
    findings: list = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    evidence_complete: bool = True
    missing_evidence: list[str] = field(default_factory=list)
    technical_failure: bool = False


class EvidenceReconciler:
    """Convert structured investigation tool results into deterministic findings."""

    def reconcile(
        self,
        investigation: InvestigationResult,
    ) -> ReconciliationResult:
        findings = []
        evidence_ids = []
        evidence_complete = False
        missing_evidence = []
        technical_failure = investigation.blocked

        for tool_result in investigation.tool_results:
            if tool_result.failed:
                continue

            if tool_result.tool_name == "search_evidence":
                self._collect_evidence_ids(
                    tool_result.result,
                    evidence_ids,
                )

            elif tool_result.tool_name == "check_required_evidence":
                result = tool_result.result

                if isinstance(result, dict):
                    evidence_complete = result.get(
                        "complete",
                        evidence_complete,
                    )
                    missing_evidence.extend(
                        result.get("missing_types", [])
                    )

            elif tool_result.tool_name == "compare_evidence":
                finding = self._reconcile_quantity(
                    tool_result,
                    evidence_ids,
                )

                if finding is not None:
                    findings.append(finding)

            elif tool_result.tool_name == "validate_calculation":
                finding = self._reconcile_calculation(
                    tool_result,
                    evidence_ids,
                )

                if finding is not None:
                    findings.append(finding)

        return ReconciliationResult(
            findings=findings,
            evidence_ids=evidence_ids,
            evidence_complete=evidence_complete,
            missing_evidence=list(dict.fromkeys(missing_evidence)),
            technical_failure=technical_failure,
        )

    @staticmethod
    def _collect_evidence_ids(
        result,
        evidence_ids: list[str],
    ) -> None:
        if not isinstance(result, list):
            return

        for item in result:
            if isinstance(item, dict):
                chunk_id = item.get("chunk_id")
            else:
                chunk_id = getattr(item, "chunk_id", None)

            if chunk_id and chunk_id not in evidence_ids:
                evidence_ids.append(chunk_id)

    @staticmethod
    def _reconcile_quantity(
        tool_result,
        evidence_ids: list[str],
    ):
        result = tool_result.result

        if isinstance(result, dict):
            matches = result.get("matches")
            expected_value = result.get("expected_value")
            observed_value = result.get("observed_value")
            unit = result.get("unit")
        else:
            matches = getattr(result, "matches", None)
            expected_value = getattr(result, "expected_value", None)
            observed_value = getattr(result, "observed_value", None)
            unit = getattr(result, "unit", None)

        if matches is None or expected_value is None or observed_value is None:
            return None

        return reconcile_quantity(
            expected_quantity=expected_value,
            observed_quantity=observed_value,
            unit=unit,
            evidence_ids=evidence_ids,
        )

    @staticmethod
    def _reconcile_calculation(
        tool_result,
        evidence_ids: list[str],
    ):
        arguments = tool_result.arguments

        if not isinstance(arguments, dict):
            return None

        return reconcile_calculation(
            quantity=arguments["quantity"],
            unit_price=arguments["unit_price"],
            observed_total=arguments["observed_total"],
            evidence_ids=evidence_ids,
        )

    def build_review(
        self,
        *,
        claim,
        investigation: InvestigationResult,
        source_agreement: float,
        deterministic_validation: float,
        retrieval_quality: float,
        version_consistency: float,
    ):
        reconciliation = self.reconcile(investigation)

        return build_structured_review(
            claim=claim,
            evidence_complete=reconciliation.evidence_complete,
            findings=reconciliation.findings,
            evidence_ids=reconciliation.evidence_ids,
            missing_evidence=reconciliation.missing_evidence,
            source_agreement=source_agreement,
            deterministic_validation=deterministic_validation,
            retrieval_quality=retrieval_quality,
            version_consistency=version_consistency,
            technical_failure=reconciliation.technical_failure,
        )