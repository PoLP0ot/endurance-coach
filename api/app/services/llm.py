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
    """Thin wrapper over AI SDKs with a model router."""

    def __init__(self, api_key: str | None = None) -> None:
        self._openai_key = api_key or settings.openai_api_key

    def model_for(self, task: Task) -> str:
        if task is Task.PLAN:
            return settings.llm_model_plan
        return settings.llm_model_chat

    def narrate(self, task: Task, facts: dict, instruction: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self._openai_key)
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
        return response.choices[0].message.content or ""
