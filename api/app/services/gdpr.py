"""GDPR data export + erasure (US11b).

Export gathers all of a user's data as a JSON bundle plus CSV for activities.
Delete purges every table keyed on the user and writes a durable audit record
(the audit log is intentionally FK-free so it outlives the account).
"""
from __future__ import annotations

import csv
import io

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityMetric
from app.models.analysis import AIAnalysis
from app.models.audit import GDPR_DELETE, GDPR_EXPORT, GdprAuditLog
from app.models.chat import ChatMessage
from app.models.garmin import GarminConnection
from app.models.health import DailyHealth
from app.models.import_job import ImportJob
from app.models.plan import TrainingPlan
from app.models.subscription import Subscription
from app.models.user import User

ACTIVITY_CSV_FIELDS = [
    "garmin_activity_id",
    "activity_type",
    "name",
    "start_time",
    "distance_m",
    "duration_s",
    "avg_hr",
    "tss",
]


def _activities_csv(activities: list[Activity]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=ACTIVITY_CSV_FIELDS)
    writer.writeheader()
    for a in activities:
        writer.writerow(
            {
                "garmin_activity_id": a.garmin_activity_id,
                "activity_type": a.activity_type,
                "name": a.name or "",
                "start_time": a.start_time.isoformat(),
                "distance_m": a.distance_m or "",
                "duration_s": a.duration_s or "",
                "avg_hr": a.avg_hr or "",
                "tss": a.tss or "",
            }
        )
    return buffer.getvalue()


def build_export(db: Session, user_id: str) -> dict:
    """Assemble a full data-portability bundle and record the export.

    Garmin credentials are never exported — only connection metadata.
    """
    user = db.get(User, user_id)
    activities = list(
        db.execute(select(Activity).where(Activity.user_id == user_id)).scalars()
    )
    health = list(
        db.execute(select(DailyHealth).where(DailyHealth.user_id == user_id)).scalars()
    )
    messages = list(
        db.execute(select(ChatMessage).where(ChatMessage.user_id == user_id)).scalars()
    )
    plans = list(
        db.execute(select(TrainingPlan).where(TrainingPlan.user_id == user_id)).scalars()
    )
    conn = db.execute(
        select(GarminConnection).where(GarminConnection.user_id == user_id)
    ).scalars().first()

    bundle = {
        "json": {
            "profile": {
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "primary_goal": user.primary_goal,
                "units": user.units,
                "subscription_status": user.subscription_status,
            }
            if user
            else None,
            "garmin_connection": (
                {
                    "garmin_username": conn.garmin_username,
                    "status": conn.status,
                    "last_sync_at": conn.last_sync_at.isoformat()
                    if conn and conn.last_sync_at
                    else None,
                }
                if conn
                else None
            ),
            "activities": [
                {
                    "garmin_activity_id": a.garmin_activity_id,
                    "activity_type": a.activity_type,
                    "name": a.name,
                    "start_time": a.start_time.isoformat(),
                    "distance_m": a.distance_m,
                    "duration_s": a.duration_s,
                    "avg_hr": a.avg_hr,
                    "tss": a.tss,
                }
                for a in activities
            ],
            "daily_health": [
                {
                    "day": h.day.isoformat(),
                    "resting_hr": h.resting_hr,
                    "hrv": h.hrv,
                    "sleep_score": h.sleep_score,
                    "steps": h.steps,
                    "weight_kg": h.weight_kg,
                }
                for h in health
            ],
            "chat_messages": [
                {"role": m.role, "content": m.content} for m in messages
            ],
            "training_plans": [
                {"goal": p.goal, "weeks": p.weeks, "structure": p.structure}
                for p in plans
            ],
        },
        "csv": {"activities": _activities_csv(activities)},
    }

    db.add(GdprAuditLog(user_id=user_id, action=GDPR_EXPORT))
    db.commit()
    return bundle


def delete_user_data(db: Session, user_id: str) -> None:
    """Purge every record keyed on the user, then write a durable audit entry.

    Activity-child rows (metrics, analyses) are removed first since they key on
    activity_id, then all user-keyed tables, then the user row.
    """
    activity_ids = list(
        db.execute(
            select(Activity.id).where(Activity.user_id == user_id)
        ).scalars()
    )
    if activity_ids:
        db.execute(
            delete(ActivityMetric).where(ActivityMetric.activity_id.in_(activity_ids))
        )
        db.execute(delete(AIAnalysis).where(AIAnalysis.activity_id.in_(activity_ids)))

    for model in (
        Activity,
        DailyHealth,
        ChatMessage,
        TrainingPlan,
        Subscription,
        GarminConnection,
        ImportJob,
    ):
        db.execute(delete(model).where(model.user_id == user_id))
    db.execute(delete(User).where(User.id == user_id))

    db.add(GdprAuditLog(user_id=user_id, action=GDPR_DELETE))
    db.commit()
