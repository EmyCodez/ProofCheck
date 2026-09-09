from proofcheck.agent.investigator import InvestigationAgent
from proofcheck.agent.tool_executor import ToolExecutor
from proofcheck.llm.client import LLMClient


def test_investigator_rejects_empty_claim(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    agent = InvestigationAgent(
        LLMClient(),
        ToolExecutor(None, "project-001"),
    )

    try:
        agent.investigate("", "project-001")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "Claim must not be empty."


def test_investigator_returns_final_text_without_tool_call(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    class FakeMessage:
        content = "The claim requires further evidence."
        tool_calls = None

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    client.client.chat.completions.create = lambda **kwargs: FakeResponse()

    agent = InvestigationAgent(
        client,
        ToolExecutor(None, "project-001"),
    )

    result = agent.investigate(
        "Is the invoice supported?",
        "project-001",
    )

    assert result.text == "The claim requires further evidence."
    assert result.tool_calls == 0
    assert result.blocked is False


def test_investigator_executes_tool_and_returns_final_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    class FakeFunction:
        name = "compare_evidence"
        arguments = (
            '{"expected_value": 1300, '
            '"observed_value": 1500, '
            '"unit": "m2"}'
        )

    class FakeToolCall:
        id = "call-001"
        function = FakeFunction()

    responses = []

    class FirstMessage:
        content = None
        tool_calls = [FakeToolCall()]

    class FirstChoice:
        message = FirstMessage()

    class FirstResponse:
        choices = [FirstChoice()]

    class FinalMessage:
        content = "The observed quantity exceeds the expected quantity."
        tool_calls = None

    class FinalChoice:
        message = FinalMessage()

    class FinalResponse:
        choices = [FinalChoice()]

    responses.extend(
        [
            FirstResponse(),
            FinalResponse(),
        ]
    )

    calls = {"count": 0}

    def fake_create(**kwargs):
        response = responses[calls["count"]]
        calls["count"] += 1

        if calls["count"] == 2:
            assert any(
                message.get("role") == "tool"
                for message in kwargs["messages"]
            )

        return response

    client.client.chat.completions.create = fake_create

    executor = ToolExecutor(None, "project-001")

    agent = InvestigationAgent(client, executor)

    result = agent.investigate(
        "Is 1500 m2 supported by 1300 m2?",
        "project-001",
    )

    assert result.text == (
        "The observed quantity exceeds the expected quantity."
    )
    assert result.tool_calls == 1
    assert result.blocked is False


def test_investigator_synthesizes_at_tool_call_limit(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    class FakeFunction:
        name = "compare_evidence"
        arguments = (
            '{"expected_value": 100, '
            '"observed_value": 101}'
        )

    class FakeToolCall:
        id = "call-loop"
        function = FakeFunction()

    class ToolMessage:
        content = None
        tool_calls = [FakeToolCall()]

    class ToolChoice:
        message = ToolMessage()

    class ToolResponse:
        choices = [ToolChoice()]

    class FinalMessage:
        content = "The investigation was completed using the evidence gathered."
        tool_calls = None

    class FinalChoice:
        message = FinalMessage()

    class FinalResponse:
        choices = [FinalChoice()]

    calls = {"count": 0}

    def fake_create(**kwargs):
        calls["count"] += 1

        # First 8 requests request another tool.
        if calls["count"] <= agent.MAX_TOOL_CALLS:
            return ToolResponse()

        # The next request must be the final synthesis without tools.
        assert "tools" not in kwargs
        return FinalResponse()

    client.client.chat.completions.create = fake_create

    executor = ToolExecutor(None, "project-001")
    agent = InvestigationAgent(client, executor)

    result = agent.investigate(
        "Keep investigating until the tool-call limit is reached.",
        "project-001",
    )

    assert result.blocked is False
    assert result.tool_calls == agent.MAX_TOOL_CALLS
    assert result.text == (
        "The investigation was completed using the evidence gathered."
    )
    assert calls["count"] == agent.MAX_TOOL_CALLS + 1
