"""Weekly coaching email tests (US6) — LLM stubbed, no network."""
from __future__ import annotations

from datetime import UTC, date, datetime

from app.models.activity import Activity
from app.services.email import build_weekly_email, render_weekly_email


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "Great week — your fitness is trending up."


def test_render_includes_metrics_and_narrative():
    html = render_weekly_email(
        athlete="Sam",
        facts={
            "fitness": {"ctl": 42.0, "atl": 50.0, "tsb": -8.0},
            "recovery": 70,
            "form": {"headline": "You're balanced.", "detail": "Keep building."},
            "totals": {"activity_count": 5, "total_distance_m": 42000.0, "window_days": 42},
        },
        narrative="Solid block of training.",
    )
    assert "Sam" in html
    assert "42" in html  # CTL
    assert "Solid block of training." in html
    assert "<html" in html.lower()


def test_build_weekly_email_uses_dashboard_and_llm(db_session, seed_user):
    db_session.add(
        Activity(
            user_id=seed_user.id,
            garmin_activity_id="g-1",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
            duration_s=3600,
            avg_hr=150,
        )
    )
    db_session.commit()

    email = build_weekly_email(
        db_session, seed_user, _StubLLM(), today=date(2026, 6, 22)
    )
    assert "subject" in email and "html" in email
    assert "Great week" in email["html"]
    assert email["subject"]
