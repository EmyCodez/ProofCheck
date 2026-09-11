import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMClient:
    """Thin wrapper around the Gemini API using OpenAI-compatible client."""

    def __init__(
        self,
        model: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        if max_retries < 0:
            raise ValueError("max_retries must not be negative.")

        self.model = model or os.getenv(
            "PROOFCHECK_MODEL",
            "gemini-3.5-flash-lite",
        )
        self.max_retries = max_retries
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=timeout,
        )

    def generate(self, prompt: str) -> str:
        """Generate a text response with bounded retry handling."""
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                return response.choices[0].message.content or ""

            except Exception as exc:
                last_error = exc

                if attempt >= self.max_retries:
                    break

                time.sleep(0.5 * (2**attempt))

        raise RuntimeError(
            f"LLM API request failed after {self.max_retries + 1} attempts."
        ) from last_error
