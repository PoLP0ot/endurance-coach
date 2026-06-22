"""Activity AI analysis service tests (US3).

The LLM is stubbed — only the deterministic facts and caching are exercised.
"""
from __future__ import annotations

from datetime import UTC, datetime

from app.models.activity import Activity, ActivityMetric
from app.services.activity_analysis import build_activity_facts, get_or_create_analysis


class _StubLLM:
    def __init__(self) -> None:
        self.calls = 0

    def model_for(self, task) -> str:  # noqa: ANN001
        return "stub-model"

    def narrate(self, task, facts, instruction) -> str:  # noqa: ANN001
        self.calls += 1
        return "Your easy run built aerobic base."


def _run(user_id: str = "u1") -> Activity:
    return Activity(
        user_id=user_id,
        garmin_activity_id="g-1",
        activity_type="running",
        name="Morning Run",
        start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
        duration_s=1800,
        distance_m=5000.0,
        avg_hr=150,
        max_hr=175,
    )


def test_facts_include_pace_and_tss():
    facts = build_activity_facts(_run(), streams=None)
    assert facts["distance_km"] == 5.0
    # 1800s over 5km → 6:00 /km.
    assert facts["avg_pace_per_km"] == "6:00"
    assert facts["tss"] > 0
    assert facts["activity_type"] == "running"


def test_facts_include_zone_distribution_from_streams():
    facts = build_activity_facts(
        _run(), streams={"hr": [110, 130, 150, 170, 175]}
    )
    assert "intensity_distribution" in facts
    assert sum(facts["intensity_distribution"].values()) > 0.99


def test_get_or_create_caches_and_calls_llm_once(db_session, seed_user):
    from tests.conftest import TEST_USER_ID

    activity = _run(TEST_USER_ID)
    db_session.add(activity)
    db_session.commit()
    db_session.add(
        ActivityMetric(activity_id=activity.id, kind="stream", data={"hr": [150]})
    )
    db_session.commit()

    llm = _StubLLM()
    first = get_or_create_analysis(db_session, activity, llm)
    second = get_or_create_analysis(db_session, activity, llm)

    assert first.id == second.id
    assert first.narrative == "Your easy run built aerobic base."
    assert llm.calls == 1  # second call served from cache
    assert "tss" in first.facts
