"""Weekly coaching email (US6).

Deterministic facts come from the dashboard; the LLM narrates the week. The
EmailProvider isolates Resend (imported lazily so the module loads keyless).
"""
from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.dashboard import build_dashboard

WEEKLY_INSTRUCTION = (
    "Write a short, encouraging weekly summary for the athlete based on the "
    "facts: how training went, where their form is, and one focus for next "
    "week. Two short paragraphs, warm but specific."
)


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def render_weekly_email(athlete: str, facts: dict, narrative: str) -> str:
    """Render the weekly email HTML from already-computed facts."""
    fitness = facts["fitness"]
    totals = facts["totals"]
    km = (totals.get("total_distance_m") or 0.0) / 1000.0
    return f"""<!DOCTYPE html>
<html lang="en">
  <body style="font-family: Inter, Arial, sans-serif; color: #1c1c1c;">
    <h1 style="font-size: 20px;">Your week, {athlete}</h1>
    <p style="font-size: 16px; font-weight: 600;">{facts['form']['headline']}</p>
    <p style="color: #555;">{facts['form']['detail']}</p>
    <table cellpadding="8" style="border-collapse: collapse; margin: 16px 0;">
      <tr>
        <td><strong>Fitness (CTL)</strong></td><td>{fitness['ctl']:.0f}</td>
        <td><strong>Fatigue (ATL)</strong></td><td>{fitness['atl']:.0f}</td>
      </tr>
      <tr>
        <td><strong>Form (TSB)</strong></td><td>{fitness['tsb']:.0f}</td>
        <td><strong>Recovery</strong></td><td>{facts['recovery']}/100</td>
      </tr>
    </table>
    <p>{totals['activity_count']} activities · {km:.1f} km</p>
    <hr style="border: none; border-top: 1px solid #ddd;" />
    <p style="white-space: pre-line; font-size: 15px; line-height: 1.6;">{narrative}</p>
    <p style="color: #888; font-size: 12px;">Endurance Coach</p>
  </body>
</html>"""


def build_weekly_email(
    db: Session,
    user: User,
    llm: _Narrator,
    today: date,
) -> dict:
    """Assemble the weekly email (subject + html) for a user."""
    from app.services.llm import Task

    data = build_dashboard(db, user.id, today=today)
    facts = {
        "fitness": data["fitness"],
        "form": data["form"],
        "recovery": data["recovery"],
        "totals": data["totals"],
    }
    narrative = llm.narrate(Task.ANALYSIS, facts, WEEKLY_INSTRUCTION)
    athlete = user.display_name or (user.email.split("@")[0] if user.email else "athlete")
    subject = f"Your training week — {data['form']['headline']}"
    return {
        "subject": subject,
        "html": render_weekly_email(athlete, facts, narrative),
        "facts": facts,
    }


class EmailProvider:
    """Thin wrapper over Resend. The SDK is imported lazily."""

    def __init__(self, api_key: str | None = None, sender: str | None = None) -> None:
        self._api_key = api_key or settings.resend_api_key
        self._sender = sender or settings.email_from

    def send(self, to: str, subject: str, html: str) -> str:
        """Send an email and return the provider message id."""
        import resend

        resend.api_key = self._api_key
        result = resend.Emails.send(
            {"from": self._sender, "to": [to], "subject": subject, "html": html}
        )
        return result["id"]
