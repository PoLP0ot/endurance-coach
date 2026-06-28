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


def _metric_cell(label: str, value: str) -> str:
    """One email-safe metric cell (warm-stone theme)."""
    return (
        '<td width="50%" style="padding:14px 16px;border:1px solid #CFC7B4;'
        'background:#F3EFE5;">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        f'letter-spacing:0.12em;text-transform:uppercase;color:#7C7765;">{label}</div>'
        f'<div style="font-size:30px;font-weight:600;color:#38382C;'
        f'padding-top:6px;">{value}</div></td>'
    )


def render_weekly_email(athlete: str, facts: dict, narrative: str) -> str:
    """Render the weekly email HTML from already-computed facts (warm-stone theme)."""
    fitness = facts["fitness"]
    totals = facts["totals"]
    km = (totals.get("total_distance_m") or 0.0) / 1000.0
    row1 = _metric_cell("Fitness · CTL", f"{fitness['ctl']:.0f}") + _metric_cell(
        "Fatigue · ATL", f"{fitness['atl']:.0f}"
    )
    row2 = _metric_cell("Form · TSB", f"{fitness['tsb']:.0f}") + _metric_cell(
        "Recovery", f"{facts['recovery']}/100"
    )
    cta = f"{settings.cors_origins.split(',')[0]}/dashboard"
    return f"""<!DOCTYPE html>
<html lang="en">
  <body style="margin:0;padding:0;background:#E9E4D8;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
      style="background:#E9E4D8;padding:24px 0;">
      <tr><td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
          style="max-width:600px;width:100%;background:#F3EFE5;border:1px solid #CFC7B4;
          border-radius:3px;">
          <tr><td style="padding:26px 30px;">
            <div style="font-family:'Inter Tight',Arial,sans-serif;font-weight:600;
              font-size:16px;color:#38382C;">
              Endurance&nbsp;Coach
              <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                background:#D9703A;margin-left:4px;"></span>
            </div>
            <h1 style="font-family:'Inter Tight',Arial,sans-serif;font-size:24px;
              color:#38382C;margin:18px 0 14px;">Your week, {athlete}</h1>
            <p style="font-family:Inter,Arial,sans-serif;font-size:16px;font-weight:600;
              color:#38382C;margin:0 0 4px;">{facts['form']['headline']}</p>
            <p style="font-family:Inter,Arial,sans-serif;font-size:15px;line-height:1.6;
              color:#54513F;margin:0 0 20px;">{facts['form']['detail']}</p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
              style="border-collapse:collapse;">
              <tr>{row1}</tr>
              <tr>{row2}</tr>
            </table>
            <p style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#7C7765;
              margin:16px 0 0;">{totals['activity_count']} activities · {km:.1f} km</p>
            <div style="border-top:1px solid #DCD5C4;margin:22px 0;"></div>
            <p style="font-family:Inter,Arial,sans-serif;white-space:pre-line;font-size:15px;
              line-height:1.7;color:#54513F;margin:0;">{narrative}</p>
            <a href="{cta}"
              style="display:inline-block;margin-top:22px;background:#D9703A;color:#FBF7EE;
              font-family:'Inter Tight',Arial,sans-serif;font-weight:600;font-size:14px;
              text-decoration:none;padding:12px 22px;border-radius:3px;">View dashboard</a>
          </td></tr>
        </table>
        <p style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#9A9583;
          padding:16px 0;">Endurance Coach · <a href="#" style="color:#9A9583;">Unsubscribe</a></p>
      </td></tr>
    </table>
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
        "goal": data["goal_structured"],
        "fitness": data["fitness"],
        "form": data["form"],
        "recovery": data["recovery"],
        "health": data["health"],
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
