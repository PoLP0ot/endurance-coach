"""Activity AI analysis ("What This Run Means", US3).

AnalyticsEngine computes every number; the LLM only narrates the resulting
facts. Narratives are cached per activity so the model runs at most once.
"""
from __future__ import annotations

from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityMetric
from app.models.analysis import AIAnalysis
from app.services.analytics import activity_tss, intensity_distribution

PROMPT_VERSION = "v1"
ANALYSIS_INSTRUCTION = (
    "Explain what this single activity means for the athlete: the type of "
    "stimulus, how hard it was, and one concrete takeaway. Two short paragraphs."
)
# Default max HR when the activity carries none (used only to derive zones).
DEFAULT_MAX_HR = 190


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def _pace_per_km(duration_s: int | None, distance_m: float | None) -> str | None:
    """Average pace as 'M:SS' per km, or None when it can't be computed."""
    if not duration_s or not distance_m or distance_m <= 0:
        return None
    sec_per_km = duration_s / (distance_m / 1000.0)
    minutes = int(sec_per_km // 60)
    seconds = int(round(sec_per_km % 60))
    if seconds == 60:
        minutes, seconds = minutes + 1, 0
    return f"{minutes}:{seconds:02d}"


def build_activity_facts(activity: Activity, streams: dict | None) -> dict:
    """Build the deterministic fact sheet handed to the LLM.

    Includes summary metrics, derived pace and TSS, and an HR-zone distribution
    when a stream is available. Pure and JSON-serialisable.
    """
    tss = activity.tss if activity.tss is not None else round(
        activity_tss(activity.duration_s, activity.avg_hr), 1
    )
    facts: dict = {
        "activity_type": activity.activity_type,
        "name": activity.name,
        "distance_km": round((activity.distance_m or 0.0) / 1000.0, 2),
        "duration_s": activity.duration_s,
        "avg_pace_per_km": _pace_per_km(activity.duration_s, activity.distance_m),
        "avg_hr": activity.avg_hr,
        "max_hr": activity.max_hr,
        "elevation_gain_m": activity.elevation_gain_m,
        "tss": tss,
    }
    if streams and isinstance(streams.get("hr"), list) and streams["hr"]:
        ceiling = activity.max_hr or DEFAULT_MAX_HR
        bounds = [int(ceiling * f) for f in (0.6, 0.7, 0.8, 0.9)]
        facts["intensity_distribution"] = {
            z: round(frac, 3)
            for z, frac in intensity_distribution(streams["hr"], bounds).items()
        }
    return facts


def _stream_for(db: Session, activity_id: str) -> dict | None:
    row = db.execute(
        select(ActivityMetric).where(
            ActivityMetric.activity_id == activity_id,
            ActivityMetric.kind == "stream",
        )
    ).scalars().first()
    return row.data if row is not None else None


def get_or_create_analysis(
    db: Session,
    activity: Activity,
    llm: _Narrator,
    prompt_version: str = PROMPT_VERSION,
) -> AIAnalysis:
    """Return the cached analysis for an activity, generating it on first ask."""
    from app.services.llm import Task

    existing = db.execute(
        select(AIAnalysis).where(
            AIAnalysis.activity_id == activity.id,
            AIAnalysis.prompt_version == prompt_version,
        )
    ).scalars().first()
    if existing is not None:
        return existing

    facts = build_activity_facts(activity, _stream_for(db, activity.id))
    narrative = llm.narrate(Task.ANALYSIS, facts, ANALYSIS_INSTRUCTION)
    analysis = AIAnalysis(
        activity_id=activity.id,
        model=llm.model_for(Task.ANALYSIS),
        facts=facts,
        narrative=narrative,
        prompt_version=prompt_version,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
