"""LLMProvider — Anthropic Claude, narration only.

The LLM NEVER computes numbers. It receives structured facts (from
AnalyticsEngine) and produces natural-language coaching. A model router picks
Sonnet for chat/analysis and Opus for plan generation.
"""
from __future__ import annotations

from enum import StrEnum

from app.core.config import settings

# Hard ceiling on a single narration call so a hung model never blocks a request.
LLM_TIMEOUT_S = 30.0


class LLMError(Exception):
    """A narration call failed. ``reason`` classifies it; ``retryable`` says
    whether a later retry could succeed (timeout / rate-limit) vs. not (quota /
    auth / bad config)."""

    def __init__(self, reason: str, *, retryable: bool, message: str = "") -> None:
        super().__init__(message or reason)
        self.reason = reason
        self.retryable = retryable


COACH_SYSTEM_PROMPT = (
    "You are an elite endurance coach. You are given STRUCTURED METRICS that "
    "have already been computed deterministically. Never invent, recompute, or "
    "alter any number. Narrate what the facts mean for the athlete's goal and "
    "what to do next. Be specific, encouraging, and concise."
)


class Task(StrEnum):
    CHAT = "chat"
    ANALYSIS = "analysis"
    PLAN = "plan"


class LLMProvider:
    """Thin wrapper over AI SDKs with a model router."""

    def __init__(self, api_key: str | None = None) -> None:
        self._openai_key = api_key or settings.openai_api_key

    def model_for(self, task: Task) -> str:
        if task is Task.PLAN:
            return settings.llm_model_plan
        return settings.llm_model_chat

    def narrate(self, task: Task, facts: dict, instruction: str) -> str:
        """Narrate the given facts. Raises ``LLMError`` on any provider failure.

        Network/provider exceptions are classified so callers can return a clean,
        actionable status instead of a bare 500.
        """
        import openai
        from openai import OpenAI

        if not self._openai_key:
            raise LLMError("not_configured", retryable=False, message="LLM key missing")

        client = OpenAI(api_key=self._openai_key, timeout=LLM_TIMEOUT_S, max_retries=1)
        try:
            response = client.chat.completions.create(
                model=self.model_for(task),
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": COACH_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"{instruction}\n\n"
                            f"FACTS (authoritative, do not recompute):\n{facts}"
                        ),
                    },
                ],
            )
        except openai.APITimeoutError as exc:
            raise LLMError("timeout", retryable=True, message=str(exc)) from exc
        except openai.RateLimitError as exc:
            # Quota exhaustion is a non-retryable rate-limit; throttling is retryable.
            quota = "insufficient_quota" in str(exc).lower()
            raise LLMError(
                "quota" if quota else "rate_limit",
                retryable=not quota,
                message=str(exc),
            ) from exc
        except openai.AuthenticationError as exc:
            raise LLMError("auth", retryable=False, message=str(exc)) from exc
        except (openai.APIConnectionError, openai.APIError) as exc:
            raise LLMError("provider", retryable=True, message=str(exc)) from exc
        return response.choices[0].message.content or ""
