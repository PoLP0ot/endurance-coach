"""Goal definition registry — maps a goal kind to its strategy."""
from __future__ import annotations

from app.services.goals.base import GoalContext, GoalDefinition
from app.services.goals.health import HealthGoal
from app.services.goals.hyrox import HyroxGoal
from app.services.goals.marathon import MarathonGoal
from app.services.goals.triathlon import TriathlonGoal
from app.services.goals.weight_loss import WeightLossGoal

GOAL_REGISTRY: dict[str, GoalDefinition] = {
    g.kind: g
    for g in (
        MarathonGoal(),
        WeightLossGoal(),
        HyroxGoal(),
        TriathlonGoal(),
        HealthGoal(),
    )
}


def get_goal_definition(kind: str | None) -> GoalDefinition:
    """Return the definition for ``kind``; unknown/None falls back to health."""
    return GOAL_REGISTRY.get(kind or "", GOAL_REGISTRY["health"])


__all__ = ["GOAL_REGISTRY", "GoalContext", "GoalDefinition", "get_goal_definition"]
