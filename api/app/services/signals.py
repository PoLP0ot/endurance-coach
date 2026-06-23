"""Signals service (Explore screen) — questions answered from real facts.

Each signal is a coach-facing question grounded in deterministic dashboard
metrics. The interpretation is templated from the facts by default; for premium
users it is narrated by the LLM (which never computes the numbers — it only
explains the facts it is given).
"""
from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from app.services.dashboard import build_dashboard

SIGNAL_INSTRUCTION = (
    "Answer the athlete's question in 1-2 sentences as their coach, using only "
    "the provided facts. Be specific and encouraging. Do not restate the number "
    "list; explain what it means and what to do."
)


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def _fitness_text(form: dict) -> str:
    return f"{form['headline']} {form['detail']}"


def _form_text(tsb: float) -> str:
    if tsb > 5:
        return (
            "You're fresh — TSB is positive, so you're primed for a hard session "
            "or a race."
        )
    if tsb < -15:
        return (
            "Fatigue is deep right now. Protect recovery before adding more "
            "intensity."
        )
    return (
        "You're carrying productive fatigue — normal for a build block. Keep an "
        "eye on recovery."
    )


def _recovery_text(recovery: int) -> str:
    if recovery >= 70:
        return f"Recovery is strong at {recovery}/100 — green light for quality work today."
    if recovery >= 45:
        return (
            f"Recovery is moderate at {recovery}/100 — train, but hold back on "
            "top-end intensity."
        )
    return f"Recovery is low at {recovery}/100 — prioritise easy aerobic or rest today."


def build_signals(
    db: Session,
    user_id: str,
    today: date,
    llm: _Narrator | None = None,
) -> dict:
    """Build the signal cards from the user's real dashboard facts.

    When ``llm`` is provided the interpretation text is narrated by the model;
    otherwise a deterministic template is used. The metric series and questions
    are always deterministic.
    """
    data = build_dashboard(db, user_id, today=today)
    if data["totals"]["activity_count"] == 0:
        return {"signals": []}

    tsb = data["fitness"]["tsb"]
    recovery = data["recovery"]
    ctl_series = [p["ctl"] for p in data["load_series"]]
    tsb_series = [p["tsb"] for p in data["load_series"]]

    specs = [
        {
            "key": "fitness",
            "eyebrow": "Fitness · CTL trend",
            "question": "How is my fitness trending?",
            "points": ctl_series,
            "color": "text-primary",
            "fallback": _fitness_text(data["form"]),
        },
        {
            "key": "form",
            "eyebrow": "Form · TSB balance",
            "question": "Is my form race-ready?",
            "points": tsb_series,
            "color": "text-olive",
            "fallback": _form_text(tsb),
        },
        {
            "key": "recovery",
            "eyebrow": "Recovery · today",
            "question": "Am I recovered enough to push?",
            "points": None,
            "color": "text-accent",
            "fallback": _recovery_text(recovery),
        },
    ]

    facts = {
        "fitness": data["fitness"],
        "form": data["form"],
        "recovery": recovery,
        "totals": data["totals"],
    }

    signals = []
    for spec in specs:
        interpretation = spec["fallback"]
        if llm is not None:
            from app.services.llm import Task

            try:
                narrated = llm.narrate(
                    Task.CHAT,
                    facts,
                    f"{SIGNAL_INSTRUCTION}\n\nQuestion: {spec['question']}",
                )
                if narrated.strip():
                    interpretation = narrated.strip()
            except Exception:  # noqa: BLE001 - narration is best-effort
                pass
        signals.append(
            {
                "key": spec["key"],
                "eyebrow": spec["eyebrow"],
                "question": spec["question"],
                "points": spec["points"],
                "color": spec["color"],
                "interpretation": interpretation,
            }
        )
    return {"signals": signals}
