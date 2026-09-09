from dataclasses import dataclass
from typing import Any

from proofcheck.agent.prompts import INVESTIGATOR_SYSTEM_PROMPT
from proofcheck.agent.tools import get_investigation_tool_definitions
from proofcheck.llm.client import LLMClient


@dataclass(frozen=True)
class ToolCallRequest:
    """A tool request returned by the LLM."""

    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AgentResponse:
    """Normalized response from the investigation LLM."""

    text: str | None
    tool_calls: list[ToolCallRequest]


class InvestigationLLM:
    """Adapter between ProofCheck and the LLM function-calling interface."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def investigate(
        self,
        claim: str,
        project_id: str,
    ) -> AgentResponse:
        """Ask the LLM to investigate a claim using approved tools."""
        if not claim.strip():
            raise ValueError("Claim must not be empty.")

        if not project_id.strip():
            raise ValueError("Project ID must not be empty.")

        response = self.client.client.chat.completions.create(
            model=self.client.model,
            messages=[
                {
                    "role": "system",
                    "content": INVESTIGATOR_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        f"Project ID: {project_id}\n"
                        f"Claim to investigate: {claim}"
                    ),
                },
            ],
            tools=get_investigation_tool_definitions(),
        )

        message = response.choices[0].message

        tool_calls: list[ToolCallRequest] = []

        for tool_call in message.tool_calls or []:
            arguments = tool_call.function.arguments

            if isinstance(arguments, str):
                import json

                arguments = json.loads(arguments)

            tool_calls.append(
                ToolCallRequest(
                    name=tool_call.function.name,
                    arguments=arguments,
                )
            )

        return AgentResponse(
            text=message.content,
            tool_calls=tool_calls,
        )
