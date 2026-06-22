"""GarminProvider — isolates the unofficial python-garminconnect library.

Everything Garmin-specific lives behind this interface so we can swap to the
official Garmin API later without touching callers.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


class GarminError(Exception):
    """Base class for typed Garmin failures surfaced to callers."""


class GarminAuthError(GarminError):
    """Invalid Garmin credentials."""


class GarminMFARequired(GarminError):
    """The Garmin account requires multi-factor authentication."""


class GarminAccountLocked(GarminError):
    """The Garmin account is temporarily locked (too many attempts)."""


@dataclass(frozen=True)
class GarminActivity:
    """Normalized activity summary, library-agnostic."""

    garmin_activity_id: str
    activity_type: str
    name: str | None
    start_time: str  # ISO-8601
    duration_s: int | None
    distance_m: float | None
    avg_hr: int | None
    max_hr: int | None
    elevation_gain_m: float | None
    avg_power_w: float | None


@dataclass(frozen=True)
class GarminDailyHealth:
    """Normalized daily health snapshot, library-agnostic."""

    day: str  # ISO date
    resting_hr: int | None
    hrv: float | None
    sleep_score: int | None
    steps: int | None
    body_battery: int | None
    stress_avg: int | None
    weight_kg: float | None


class GarminProvider(Protocol):
    """Contract every Garmin backend must satisfy."""

    def login(self, username: str, password: str) -> str:
        """Authenticate; return an opaque session token blob (to be encrypted).

        Raises GarminAuthError / GarminMFARequired / GarminAccountLocked.
        """
        ...

    def list_activities(self, token: str, since: date) -> list[GarminActivity]:
        """Return activities on/after `since`."""
        ...

    def list_daily_health(
        self, token: str, since: date
    ) -> list[GarminDailyHealth]:
        """Return daily health snapshots on/after `since`."""
        ...

    def get_activity_streams(self, token: str, garmin_activity_id: str) -> dict:
        """Return detailed time-series streams for one activity."""
        ...


class GarminConnectProvider:
    """Default implementation backed by python-garminconnect.

    The heavy import is deferred so the module loads without the dependency
    present (e.g. during unit tests that don't touch Garmin).
    """

    def login(self, username: str, password: str) -> str:
        from garminconnect import (
            Garmin,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        )

        client = Garmin(username, password)
        try:
            client.login()
        except GarminConnectTooManyRequestsError as exc:
            raise GarminAccountLocked(str(exc)) from exc
        except GarminConnectAuthenticationError as exc:
            if "mfa" in str(exc).lower() or "multi-factor" in str(exc).lower():
                raise GarminMFARequired(str(exc)) from exc
            raise GarminAuthError(str(exc)) from exc
        return client.garth.dumps()

    def list_activities(self, token: str, since: date) -> list[GarminActivity]:
        client = self._client_from_token(token)
        today = date.today()
        raw = client.get_activities_by_date(since.isoformat(), today.isoformat())
        return [self._normalize(a) for a in raw]

    def list_daily_health(
        self, token: str, since: date
    ) -> list[GarminDailyHealth]:
        client = self._client_from_token(token)
        today = date.today()
        raw = client.get_daily_stats(since.isoformat(), today.isoformat())
        return [self._normalize_health(h) for h in raw]

    def get_activity_streams(self, token: str, garmin_activity_id: str) -> dict:
        client = self._client_from_token(token)
        return client.get_activity_details(garmin_activity_id)

    @staticmethod
    def _client_from_token(token: str):
        from garminconnect import Garmin

        client = Garmin()
        client.garth.loads(token)
        return client

    @staticmethod
    def _normalize(a: dict) -> GarminActivity:
        return GarminActivity(
            garmin_activity_id=str(a.get("activityId")),
            activity_type=(a.get("activityType") or {}).get("typeKey", "unknown"),
            name=a.get("activityName"),
            start_time=a.get("startTimeGMT", ""),
            duration_s=int(a["duration"]) if a.get("duration") is not None else None,
            distance_m=a.get("distance"),
            avg_hr=a.get("averageHR"),
            max_hr=a.get("maxHR"),
            elevation_gain_m=a.get("elevationGain"),
            avg_power_w=a.get("avgPower"),
        )

    @staticmethod
    def _normalize_health(h: dict) -> GarminDailyHealth:
        return GarminDailyHealth(
            day=h.get("calendarDate", ""),
            resting_hr=h.get("restingHeartRate"),
            hrv=h.get("hrvWeeklyAverage"),
            sleep_score=h.get("sleepScore"),
            steps=h.get("totalSteps"),
            body_battery=h.get("bodyBatteryMostRecentValue"),
            stress_avg=h.get("averageStressLevel"),
            weight_kg=(h["weight"] / 1000.0) if h.get("weight") is not None else None,
        )
