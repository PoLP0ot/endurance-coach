"""Adherence matcher tests — prescribed sessions vs actual activities (C2)."""
from __future__ import annotations

from datetime import date

from app.services.adherence import (
    COMPLETED,
    MISSED,
    PARTIAL,
    UPCOMING,
    match_week,
    week_adherence,
)

WEEK = {
    "start_date": "2026-07-06",  # Monday
    "target_tss": 300.0,
    "sessions": [
        {"day_index": 1, "kind": "easy", "prescription": "Easy 8 km", "target_tss": 100.0},
        {"day_index": 3, "kind": "tempo", "prescription": "Tempo", "target_tss": 100.0},
        {"day_index": 5, "kind": "long", "prescription": "Long run", "target_tss": 100.0},
    ],
}


def _act(day: str, tss: float) -> dict:
    return {"date": f"{day}T07:00:00", "activity_type": "running", "tss": tss}


def test_completed_partial_and_missed_classification():
    today = date(2026, 7, 12)  # end of the plan week
    activities = [
        _act("2026-07-07", 110.0),  # Tue easy → completed
        _act("2026-07-09", 40.0),  # Thu tempo → partial (< 60% of 100)
        # Sat long absent → missed
    ]
    match = match_week(WEEK, activities, today)
    by_day = {s["day_index"]: s["status"] for s in match["sessions"]}
    assert by_day[1] == COMPLETED
    assert by_day[3] == PARTIAL
    assert by_day[5] == MISSED

    summary = week_adherence(match)
    assert summary["completed"] == 1
    assert summary["partial"] == 1
    assert summary["missed"] == 1
    assert summary["adherence_pct"] == round(2 / 3 * 100)


def test_future_sessions_are_upcoming_not_missed():
    today = date(2026, 7, 6)  # Monday — nothing due yet except Mon (no session)
    match = match_week(WEEK, [], today)
    assert all(s["status"] == UPCOMING for s in match["sessions"])
    assert week_adherence(match)["adherence_pct"] is None


def test_unmatched_activity_is_an_extra():
    today = date(2026, 7, 12)
    activities = [_act("2026-07-08", 50.0)]  # Wed — no session that day
    match = match_week(WEEK, activities, today)
    assert len(match["extras"]) == 1
    assert week_adherence(match)["extras"] == 1
