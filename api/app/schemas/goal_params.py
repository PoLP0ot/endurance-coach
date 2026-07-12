"""Per-goal target parameter validation.

``User.goal_params`` is a free JSON column whose shape depends on the user's
``primary_goal``. These models validate the shape per kind so the goal engine
can trust the numbers it reads. All fields are optional (onboarding may save
partials), but types and ranges are enforced; unknown keys are rejected.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Marathon = 42.195 km; other distances allowed via race_distance_m.
_MARATHON_M = 42195.0


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MarathonParams(_Base):
    race_distance_m: float = Field(default=_MARATHON_M, gt=0, le=200_000)
    target_time_s: int | None = Field(default=None, gt=0, le=24 * 3600)
    race_date: date | None = None


class TriathlonParams(_Base):
    race_date: date | None = None
    target_time_s: int | None = Field(default=None, gt=0, le=24 * 3600)


class WeightLossParams(_Base):
    target_weight_kg: float | None = Field(default=None, gt=20, lt=400)
    target_date: date | None = None
    weekly_activity_target: int | None = Field(default=None, ge=1, le=7)


class HyroxParams(_Base):
    race_date: date | None = None
    equipment: str | None = Field(default=None, max_length=120)


class HealthParams(_Base):
    weekly_activity_target: int | None = Field(default=None, ge=1, le=7)


_MODELS: dict[str, type[_Base]] = {
    "marathon": MarathonParams,
    "triathlon": TriathlonParams,
    "weight_loss": WeightLossParams,
    "hyrox": HyroxParams,
    "health": HealthParams,
}


def validate_goal_params(goal_kind: str | None, params: dict) -> dict:
    """Validate ``params`` against ``goal_kind`` and return a JSON-safe dict.

    Dates are serialised to ISO strings (the column is JSON). Raises
    ``ValueError`` on an unknown goal or invalid params.
    """
    model = _MODELS.get(goal_kind or "")
    if model is None:
        raise ValueError(f"no goal params accepted for goal '{goal_kind}'")
    try:
        validated = model.model_validate(params)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    return validated.model_dump(mode="json", exclude_none=True)
