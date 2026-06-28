"""Plan adherence — match imported activities to prescribed sessions.

Pure functions: given a plan week's ``sessions`` and the athlete's activities,
classify each session completed / partial / missed / upcoming and surface extra
sessions. Deterministic; no DB, no LLM. Feeds the daily loop and adaptation.
"""
from __future__ import annotations

from datetime import date, timedelta

# A session counts as completed when actual load reaches this fraction of target.
_COMPLETE_FRACTION = 0.6

COMPLETED = "completed"
PARTIAL = "partial"
MISSED = "missed"
UPCOMING = "upcoming"


def _activity_day(activity: dict) -> date:
    return date.fromisoformat(activity["date"][:10])


def match_week(week: dict, activities: list[dict], today: date) -> dict:
    """Classify each session in ``week`` against ``activities``.

    Matching is by calendar day within the plan week. Each activity is consumed
    by at most one session; activities on a plan day with no remaining session
    are reported as ``extras``.
    """
    start = date.fromisoformat(week["start_date"])
    week_days = {start + timedelta(days=i) for i in range(7)}
    used = [False] * len(activities)

    results: list[dict] = []
    for session in week.get("sessions", []):
        day = start + timedelta(days=session["day_index"])
        target = session.get("target_tss") or 0.0
        match_idx = next(
            (
                i
                for i, a in enumerate(activities)
                if not used[i] and _activity_day(a) == day
            ),
            None,
        )
        if match_idx is not None:
            used[match_idx] = True
            actual = activities[match_idx].get("tss") or 0.0
            status = (
                COMPLETED if target == 0 or actual >= _COMPLETE_FRACTION * target else PARTIAL
            )
            load_delta = round(actual - target, 1)
        elif day <= today:
            status, load_delta = MISSED, round(-target, 1)
        else:
            status, load_delta = UPCOMING, 0.0
        results.append(
            {
                "day_index": session["day_index"],
                "kind": session["kind"],
                "status": status,
                "load_delta": load_delta,
            }
        )

    extras = [
        {"date": a["date"], "tss": a.get("tss")}
        for i, a in enumerate(activities)
        if not used[i] and _activity_day(a) in week_days
    ]
    return {"sessions": results, "extras": extras}


def week_adherence(match: dict) -> dict:
    """Summarise a matched week: adherence %, counts, missed sessions."""
    sessions = match["sessions"]
    done = [s for s in sessions if s["status"] in (COMPLETED, PARTIAL)]
    due = [s for s in sessions if s["status"] in (COMPLETED, PARTIAL, MISSED)]
    missed = [s for s in sessions if s["status"] == MISSED]
    pct = round(len(done) / len(due) * 100) if due else None
    return {
        "adherence_pct": pct,
        "completed": len([s for s in sessions if s["status"] == COMPLETED]),
        "partial": len([s for s in sessions if s["status"] == PARTIAL]),
        "missed": len(missed),
        "extras": len(match["extras"]),
        "missed_sessions": missed,
    }
