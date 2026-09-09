import pytest

from proofcheck.llm.client import LLMClient


def test_llm_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
        LLMClient()


def test_llm_client_uses_configured_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("PROOFCHECK_MODEL", "test-model")

    client = LLMClient()

    assert client.model == "test-model"


def test_generate_calls_chat_completions_api(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("PROOFCHECK_MODEL", "test-model")

    client = LLMClient()

    class FakeMessage:
        content = "Test response"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    client.client.chat.completions.create = fake_create

    result = client.generate("Test prompt")

    assert result == "Test response"
    assert calls == [
        {
            "model": "test-model",
            "messages": [
                {
                    "role": "user",
                    "content": "Test prompt",
                }
            ],
        }
    ]


def test_generate_rejects_empty_prompt(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    client = LLMClient()

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        client.generate("   ")

def test_generate_retries_after_transient_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("PROOFCHECK_MODEL", "test-model")

    client = LLMClient(max_retries=2)

    class FakeMessage:
        content = "Recovered response"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    calls = {"count": 0}

    def fake_create(**kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("Temporary API failure")
        return FakeResponse()

    client.client.chat.completions.create = fake_create

    result = client.generate("Test prompt")

    assert result == "Recovered response"
    assert calls["count"] == 3


def test_generate_raises_controlled_error_after_retries(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("PROOFCHECK_MODEL", "test-model")

    client = LLMClient(max_retries=2)

    calls = {"count": 0}

    def fake_create(**kwargs):
        calls["count"] += 1
        raise RuntimeError("API unavailable")

    client.client.chat.completions.create = fake_create

    with pytest.raises(
        RuntimeError,
        match="LLM API request failed after 3 attempts",
    ):
        client.generate("Test prompt")

    assert calls["count"] == 3
