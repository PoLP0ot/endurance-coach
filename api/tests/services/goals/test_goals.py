"""Goal definition tests — deterministic progress, projection, sessions."""
from __future__ import annotations

from datetime import date, timedelta

from app.services.goals import get_goal_definition
from app.services.goals.base import (
    AHEAD,
    NO_TARGET,
    OFF_TRACK,
    ON_TRACK,
    GoalContext,
)

TODAY = date(2026, 6, 24)


def _ctx(**overrides) -> GoalContext:
    base = dict(
        today=TODAY,
        goal_params={},
        fitness={"ctl": 50.0, "atl": 55.0, "tsb": -5.0},
        recovery=70,
        health={"steps": 9000, "sleep_score": 80, "stress_avg": 30, "body_battery": 60},
        recent_activities=[],
        weight_series=[],
    )
    base.update(overrides)
    return GoalContext(**base)


def _runs(paces_and_dists: list[tuple[int, float]]) -> list[dict]:
    """Build run activities from (pace_s_per_km, distance_m) pairs."""
    out = []
    for i, (pace, dist) in enumerate(paces_and_dists):
        out.append(
            {
                "date": (TODAY - timedelta(days=i)).isoformat(),
                "activity_type": "running",
                "distance_m": dist,
                "duration_s": int(pace * dist / 1000),
                "avg_hr": 150,
                "tss": 60.0,
            }
        )
    return out


def test_registry_falls_back_to_health_for_unknown():
    assert get_goal_definition(None).kind == "health"
    assert get_goal_definition("nonsense").kind == "health"
    for kind in ("marathon", "weight_loss", "hyrox", "triathlon", "health"):
        assert get_goal_definition(kind).kind == kind


def test_marathon_projects_and_is_deterministic():
    defn = get_goal_definition("marathon")
    ctx = _ctx(
        goal_params={"target_time_s": 3 * 3600 + 30 * 60, "race_distance_m": 42195.0},
        recent_activities=_runs([(270, 15000.0), (300, 10000.0)]),
    )
    p1 = defn.progress(ctx)
    p2 = defn.progress(ctx)
    assert p1 == p2  # deterministic
    assert p1["projection"] is not None
    assert p1["on_track_band"] in {AHEAD, ON_TRACK, "at_risk", OFF_TRACK}


def test_marathon_faster_runs_project_faster():
    defn = get_goal_definition("marathon")
    fast = defn.progress(_ctx(recent_activities=_runs([(240, 15000.0)])))
    slow = defn.progress(_ctx(recent_activities=_runs([(330, 15000.0)])))
    # Compare the underlying projection by re-deriving seconds via Riegel ordering:
    assert fast["projection"] < slow["projection"]  # 'H:MM:SS' strings compare lexically here


def test_marathon_no_runs_has_no_target_band():
    defn = get_goal_definition("marathon")
    p = defn.progress(_ctx(recent_activities=[]))
    assert p["projection"] is None
    assert p["on_track_band"] == NO_TARGET


def test_weight_loss_eta_sooner_with_steeper_loss():
    defn = get_goal_definition("weight_loss")

    def series(rate_kg_per_day: float) -> list[dict]:
        return [
            {"day": (TODAY - timedelta(days=14 - i)).isoformat(), "kg": 80.0 - rate_kg_per_day * i}
            for i in range(15)
        ]

    steep = defn.progress(
        _ctx(goal_params={"target_weight_kg": 75.0}, weight_series=series(0.1))
    )
    gentle = defn.progress(
        _ctx(goal_params={"target_weight_kg": 75.0}, weight_series=series(0.05))
    )
    assert steep["eta"] is not None and gentle["eta"] is not None
    assert steep["eta"] < gentle["eta"]  # sooner ISO date
    assert steep["rate_kg_per_week"] < 0  # losing


def test_weight_loss_reached_target_is_ahead():
    defn = get_goal_definition("weight_loss")
    series = [
        {"day": (TODAY - timedelta(days=2 - i)).isoformat(), "kg": 74.0}
        for i in range(3)
    ]
    p = defn.progress(_ctx(goal_params={"target_weight_kg": 75.0}, weight_series=series))
    assert p["on_track_band"] == AHEAD


def test_health_consistency_band():
    defn = get_goal_definition("health")
    acts = [
        {"date": (TODAY - timedelta(days=i)).isoformat(), "activity_type": "running", "tss": 40.0}
        for i in range(5)
    ]
    p = defn.progress(_ctx(goal_params={"weekly_activity_target": 4}, recent_activities=acts))
    assert p["current"] == 5
    assert p["on_track_band"] in {ON_TRACK, AHEAD}


def test_triathlon_flags_neglected_sport():
    defn = get_goal_definition("triathlon")
    acts = [
        {"date": TODAY.isoformat(), "activity_type": "running", "tss": 50.0},
        {"date": TODAY.isoformat(), "activity_type": "cycling", "tss": 60.0},
    ]
    p = defn.progress(_ctx(recent_activities=acts))
    assert p["by_sport"]["swim"] == 0.0
    assert "swim" in p["headline"]


def test_daily_session_template_distributes_week_tss():
    defn = get_goal_definition("marathon")
    week = {"phase": "build", "target_tss": 350.0}
    sessions = [defn.daily_session_template(week, d) for d in range(7)]
    active = [s for s in sessions if s is not None]
    assert active  # some sessions prescribed
    assert all(s["prescription"] for s in active)
    # Even split sums back near the weekly target.
    assert abs(sum(s["target_tss"] for s in active) - 350.0) < 1.0
