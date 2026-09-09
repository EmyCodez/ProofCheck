from typing import Any, Callable

from proofcheck.tools.check_required_evidence import (
    check_required_evidence,
)
from proofcheck.tools.compare_evidence import compare_numeric_evidence
from proofcheck.tools.search_evidence import search_evidence
from proofcheck.tools.validate_calculation import validate_calculation


class ToolExecutor:
    """Execute only the explicitly approved ProofCheck tools."""

    MAX_TOOL_CALLS = 8

    def __init__(self, retriever, project_id: str) -> None:
        if not project_id.strip():
            raise ValueError("Project ID must not be empty.")

        self.retriever = retriever
        self.project_id = project_id
        self.call_count = 0

        self._tools: dict[str, Callable[..., Any]] = {
            "search_evidence": self._search_evidence,
            "check_required_evidence": check_required_evidence,
            "compare_evidence": compare_numeric_evidence,
            "validate_calculation": validate_calculation,
        }

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Execute one approved tool within the investigation boundary."""
        if self.call_count >= self.MAX_TOOL_CALLS:
            raise RuntimeError(
                "Maximum investigation tool-call limit reached."
            )

        tool = self._tools.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' is not approved for execution."
            )

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object.")

        self.call_count += 1

        return tool(**arguments)

    def _search_evidence(
        self,
        query: str,
        document_type: str | None = None,
    ) -> Any:
        return search_evidence(
            retriever=self.retriever,
            query=query,
            project_id=self.project_id,
            document_type=document_type,
        )
