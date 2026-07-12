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

# Appended to the system prompt when tools are available.
TOOL_ADDENDUM = (
    "You may call tools to fetch more facts. NEVER do arithmetic or estimate a "
    "number yourself — no calorie counts, deficits, rates, dates, paces or "
    "percentages of your own. If you need a value, call a tool and narrate what "
    "it returns; for weight-loss pacing or calories use get_weight_guidance. "
    "If no tool provides a number, say you don't compute numbers and share what "
    "the tools do provide. Prefer one or two tool calls, then answer."
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

    def _client(self):
        from openai import OpenAI

        if not self._openai_key:
            raise LLMError("not_configured", retryable=False, message="LLM key missing")
        return OpenAI(api_key=self._openai_key, timeout=LLM_TIMEOUT_S, max_retries=1)

    @staticmethod
    def _guard(fn):
        """Run an OpenAI call, classifying provider failures into ``LLMError``."""
        import openai

        try:
            return fn()
        except openai.APITimeoutError as exc:
            raise LLMError("timeout", retryable=True, message=str(exc)) from exc
        except openai.RateLimitError as exc:
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

    def narrate(self, task: Task, facts: dict, instruction: str) -> str:
        """Narrate the given facts. Raises ``LLMError`` on any provider failure."""
        client = self._client()
        response = self._guard(
            lambda: client.chat.completions.create(
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
        )
        return response.choices[0].message.content or ""

    def converse(
        self,
        task: Task,
        facts: dict,
        instruction: str,
        tools: list[dict],
        tool_runner,
        max_turns: int = 4,
    ) -> str:
        """Agentic chat: let the model call tools for any number it needs.

        The model is told never to do arithmetic — it must call a tool. Each tool
        returns deterministic, pre-computed facts; the model only narrates them.
        Stops at the first text answer or after ``max_turns`` tool rounds.
        """
        import json

        client = self._client()
        messages = [
            {"role": "system", "content": COACH_SYSTEM_PROMPT + " " + TOOL_ADDENDUM},
            {
                "role": "user",
                "content": f"{instruction}\n\nSTARTING FACTS:\n{facts}",
            },
        ]
        for _ in range(max_turns):
            response = self._guard(
                lambda: client.chat.completions.create(
                    model=self.model_for(task),
                    max_tokens=1024,
                    messages=messages,
                    tools=tools,
                )
            )
            msg = response.choices[0].message
            if not getattr(msg, "tool_calls", None):
                return msg.content or ""
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                result = tool_runner(tc.function.name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, default=str),
                    }
                )
        # Turns exhausted: force a final text answer without tools.
        final = self._guard(
            lambda: client.chat.completions.create(
                model=self.model_for(task), max_tokens=1024, messages=messages
            )
        )
        return final.choices[0].message.content or ""
