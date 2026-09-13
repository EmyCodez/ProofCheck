import json
import logging
from dataclasses import dataclass, field
from typing import Any

from proofcheck.agent.prompts import INVESTIGATOR_SYSTEM_PROMPT
from proofcheck.agent.tool_executor import ToolExecutor
from proofcheck.agent.tools import get_investigation_tool_definitions
from proofcheck.llm.client import LLMClient

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class InvestigationToolResult:
    """Structured result from one investigation tool call."""

    tool_name: str
    arguments: dict[str, Any]
    result: Any
    failed: bool = False


@dataclass(frozen=True)
class InvestigationResult:
    """Result of a bounded LLM investigation."""

    text: str | None
    tool_calls: int
    blocked: bool = False
    tool_results: list[InvestigationToolResult] = field(
        default_factory=list
    )


class InvestigationAgent:
    """Run a bounded evidence investigation using Gemini and approved tools."""

    MAX_TOOL_CALLS = 8

    def __init__(
        self,
        client: LLMClient,
        tool_executor: ToolExecutor,
    ) -> None:
        self.client = client
        self.tool_executor = tool_executor

    def investigate(
        self,
        claim: str,
        project_id: str,
    ) -> InvestigationResult:
        """Investigate a claim through bounded tool calling."""
        if not claim.strip():
            raise ValueError("Claim must not be empty.")

        if not project_id.strip():
            raise ValueError("Project ID must not be empty.")

        messages: list[dict[str, Any]] = [
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
        ]

        tool_calls = 0
        tool_results: list[InvestigationToolResult] = []

        for _ in range(self.MAX_TOOL_CALLS):
            try:
                response = self.client.client.chat.completions.create(
                    model=self.client.model,
                    messages=messages,
                    tools=get_investigation_tool_definitions(),
                )
            except Exception as exc:
                raise RuntimeError(
                    "Investigation LLM request failed."
                ) from exc

            message = response.choices[0].message

            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                assistant_message["tool_calls"] = []

                for tc in message.tool_calls:
                    tool_call_data = {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }

                    if getattr(tc, "extra_content", None):
                        tool_call_data["extra_content"] = tc.extra_content

                    assistant_message["tool_calls"].append(tool_call_data)

                messages.append(assistant_message)

            if not message.tool_calls:
                return InvestigationResult(
                    text=message.content,
                    tool_calls=tool_calls,
                    tool_results=tool_results,
                )

            for tool_call in message.tool_calls:
                if tool_calls >= self.MAX_TOOL_CALLS:
                    try:
                        final_text = self._request_final_synthesis(
                            messages
                        )
                    except Exception as exc:
                        raise RuntimeError(
                            "Final investigation synthesis failed."
                        ) from exc

                    return InvestigationResult(
                        text=final_text,
                        tool_calls=tool_calls,
                        tool_results=tool_results,
                        blocked=False,
                    )

                arguments: dict[str, Any] = {}

                try:
                    arguments = tool_call.function.arguments

                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)

                    logger.info(
                        "investigation_tool_call | tool=%s | arguments=%s",
                        tool_call.function.name,
                        arguments,
                    )

                    result = self.tool_executor.execute(
                        tool_call.function.name,
                        arguments,
                    )

                    tool_result = self._serialize_tool_result(result)

                    tool_results.append(
                        InvestigationToolResult(
                            tool_name=tool_call.function.name,
                            arguments=arguments,
                            result=result,
                        )
                    )

                except Exception as exc:
                    tool_result = {
                        "error": str(exc),
                        "tool_failed": True,
                    }

                    tool_results.append(
                        InvestigationToolResult(
                            tool_name=tool_call.function.name,
                            arguments=arguments,
                            result=tool_result,
                            failed=True,
                        )
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result),
                    }
                )

                tool_calls += 1

        try:
            final_text = self._request_final_synthesis(messages)
        except Exception as exc:
            raise RuntimeError(
                "Final investigation synthesis failed."
            ) from exc

        return InvestigationResult(
            text=final_text,
            tool_calls=tool_calls,
            tool_results=tool_results,
            blocked=False,
        )

    def _request_final_synthesis(
        self,
        messages: list[dict[str, Any]],
    ) -> str | None:
        """Ask the LLM to synthesize the investigation without more tools."""
        synthesis_messages = [
            *messages,
            {
                "role": "user",
                "content": (
                    "The investigation tool-call limit has been reached. "
                    "Do not request any more tools. Synthesize the evidence "
                    "already gathered and provide the final evidence-backed "
                    "investigation result."
                ),
            },
        ]

        response = self.client.client.chat.completions.create(
            model=self.client.model,
            messages=synthesis_messages,
        )

        return response.choices[0].message.content

    @staticmethod
    def _serialize_tool_result(result: Any) -> dict[str, Any]:
        """Convert supported tool results into JSON-safe data."""
        if hasattr(result, "__dataclass_fields__"):
            return {
                key: getattr(result, key)
                for key in result.__dataclass_fields__
            }

        if isinstance(result, list):
            return {
                "results": [
                    InvestigationAgent._serialize_tool_result(item)
                    for item in result
                ]
            }

        if isinstance(result, dict):
            return result

        return {"result": result}