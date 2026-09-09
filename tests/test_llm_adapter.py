import json

from proofcheck.agent.llm_adapter import InvestigationLLM
from proofcheck.llm.client import LLMClient


def test_investigation_llm_rejects_empty_claim(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()
    agent = InvestigationLLM(client)

    try:
        agent.investigate("", "project-001")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Claim must not be empty."


def test_investigation_llm_rejects_empty_project_id(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()
    agent = InvestigationLLM(client)

    try:
        agent.investigate("Is the invoice supported?", "")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Project ID must not be empty."


def test_investigation_llm_normalizes_tool_call(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    class FakeFunction:
        name = "search_evidence"
        arguments = json.dumps(
            {
                "query": "Find the approved flooring quantity.",
                "document_type": "APPROVED_CHANGE",
            }
        )

    class FakeToolCall:
        function = FakeFunction()

    class FakeMessage:
        content = None
        tool_calls = [FakeToolCall()]

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    client.client.chat.completions.create = fake_create

    agent = InvestigationLLM(client)

    result = agent.investigate(
        "Is the invoiced flooring quantity supported?",
        "project-001",
    )

    assert result.text is None
    assert len(result.tool_calls) == 1

    tool_call = result.tool_calls[0]

    assert tool_call.name == "search_evidence"
    assert tool_call.arguments == {
        "query": "Find the approved flooring quantity.",
        "document_type": "APPROVED_CHANGE",
    }

    assert calls[0]["model"] == client.model
    assert calls[0]["tools"]


def test_investigation_llm_handles_text_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    class FakeMessage:
        content = "I need to search the evidence first."
        tool_calls = None

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    client.client.chat.completions.create = lambda **kwargs: FakeResponse()

    agent = InvestigationLLM(client)

    result = agent.investigate(
        "Is the invoice supported?",
        "project-001",
    )

    assert result.text == "I need to search the evidence first."
    assert result.tool_calls == []
