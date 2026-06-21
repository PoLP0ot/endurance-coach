"""LLMProvider — Anthropic Claude, narration only.

The LLM NEVER computes numbers. It receives structured facts (from
AnalyticsEngine) and produces natural-language coaching. A model router picks
Sonnet for chat/analysis and Opus for plan generation.
"""
from __future__ import annotations

from enum import StrEnum

from app.core.config import settings

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
    """Thin wrapper over the Anthropic SDK with a model router."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.anthropic_api_key

    def model_for(self, task: Task) -> str:
        """Route tasks to the right model tier."""
        if task is Task.PLAN:
            return settings.llm_model_plan
        return settings.llm_model_chat

    def narrate(self, task: Task, facts: dict, instruction: str) -> str:
        """Produce a narrative from already-computed facts.

        `facts` is rendered verbatim so the model cannot drift on numbers.
        The Anthropic client is imported lazily so the module loads without a
        key configured (e.g. in unit tests).
        """
        from anthropic import Anthropic

        client = Anthropic(api_key=self._api_key)
        message = client.messages.create(
            model=self.model_for(task),
            max_tokens=1024,
            system=COACH_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"{instruction}\n\n"
                        f"FACTS (authoritative, do not recompute):\n{facts}"
                    ),
                }
            ],
        )
        return "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        )
