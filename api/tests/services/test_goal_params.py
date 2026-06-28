"""Goal-params validation tests (Phase E)."""
from __future__ import annotations

import pytest
from app.schemas.goal_params import validate_goal_params


def test_marathon_params_default_distance():
    out = validate_goal_params("marathon", {"target_time_s": 12600})
    assert out["target_time_s"] == 12600
    assert out["race_distance_m"] == 42195.0


def test_weight_loss_params_roundtrip():
    out = validate_goal_params("weight_loss", {"target_weight_kg": 75.0})
    assert out == {"target_weight_kg": 75.0}


def test_dates_serialised_to_iso():
    out = validate_goal_params("marathon", {"race_date": "2026-09-14"})
    assert out["race_date"] == "2026-09-14"


def test_unknown_goal_rejected():
    with pytest.raises(ValueError, match="no goal params"):
        validate_goal_params("unsure", {"foo": 1})


def test_unknown_key_rejected():
    with pytest.raises(ValueError):
        validate_goal_params("health", {"target_weight_kg": 75.0})


def test_out_of_range_rejected():
    with pytest.raises(ValueError):
        validate_goal_params("health", {"weekly_activity_target": 9})
    with pytest.raises(ValueError):
        validate_goal_params("weight_loss", {"target_weight_kg": 5.0})
