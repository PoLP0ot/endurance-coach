"""GarminProvider — isolates the unofficial python-garminconnect library.

Everything Garmin-specific lives behind this interface so we can swap to the
official Garmin API later without touching callers.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol

# Daily health is fetched one day at a time, so cap the look-back to keep the
# number of Garmin calls (and rate-limit risk) bounded.
HEALTH_WINDOW_DAYS = 28


class GarminError(Exception):
    """Base class for typed Garmin failures surfaced to callers."""


class GarminAuthError(GarminError):
    """Invalid Garmin credentials."""


class GarminMFARequired(GarminError):
    """The Garmin account requires multi-factor authentication.

    Carries the garth ``client_state`` needed by ``resume_login`` — a live
    HTTP client, so it must stay in process memory (see services.garmin_mfa).
    """

    def __init__(self, message: str, client_state: dict | None = None) -> None:
        super().__init__(message)
        self.client_state = client_state


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

    def resume_login(self, client_state: dict, mfa_code: str) -> str:
        """Complete an MFA login challenge; return the session token blob.

        Raises GarminAuthError on a rejected code, GarminAccountLocked on
        rate-limiting.
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

    def push_workouts(self, token: str, workouts: list[dict]) -> int:
        """Upload structured workouts to Garmin Connect; return the count pushed."""
        ...


class GarminConnectProvider:
    """Default implementation backed by python-garminconnect.

    The heavy import is deferred so the module loads without the dependency
    present (e.g. during unit tests that don't touch Garmin).
    """

    def login(self, username: str, password: str) -> str:
        """Authenticate via garth directly so MFA returns a resumable state.

        garminconnect's ``Garmin.login`` can only prompt for the MFA code
        synchronously; ``garth.sso.login(return_on_mfa=True)`` instead hands
        back a client_state we can resume from a second HTTP request.
        """
        import garth.sso as sso
        from garth import Client as GarthClient

        client = GarthClient()
        try:
            result = sso.login(username, password, client=client, return_on_mfa=True)
        except Exception as exc:  # noqa: BLE001 — garth/requests raise their own types
            raise self._map_login_error(exc) from exc
        if isinstance(result, dict) and result.get("needs_mfa"):
            raise GarminMFARequired(
                "Garmin account requires a verification code.",
                client_state=result.get("client_state"),
            )
        client.oauth1_token, client.oauth2_token = result
        return client.dumps()

    def resume_login(self, client_state: dict, mfa_code: str) -> str:
        import garth.sso as sso

        try:
            oauth1, oauth2 = sso.resume_login(client_state, mfa_code)
        except Exception as exc:  # noqa: BLE001 — garth raises its own types
            msg = str(exc).lower()
            if "429" in msg or "too many" in msg or "rate" in msg:
                raise GarminAccountLocked(
                    "Garmin is rate-limiting attempts — wait a few minutes."
                ) from exc
            raise GarminAuthError(
                "Garmin rejected the verification code."
            ) from exc
        client = client_state["client"]
        client.oauth1_token = oauth1
        client.oauth2_token = oauth2
        return client.dumps()

    @staticmethod
    def _map_login_error(exc: Exception) -> GarminError:
        """Translate garth/requests login failures into typed Garmin errors."""
        msg = str(exc).lower()
        if "429" in msg or "too many" in msg or "rate" in msg:
            return GarminAccountLocked(
                "Garmin is rate-limiting login attempts — wait a few minutes "
                "and try again."
            )
        if "mfa" in msg or "multi-factor" in msg:
            return GarminMFARequired(str(exc))
        return GarminAuthError(
            "Garmin rejected the login (401). Check your credentials; if the "
            "account uses two-factor auth, or you've retried several times, "
            "Garmin may be temporarily blocking — wait and try once."
        )

    def list_activities(self, token: str, since: date) -> list[GarminActivity]:
        client = self._client_from_token(token)
        today = date.today()
        raw = client.get_activities_by_date(since.isoformat(), today.isoformat())
        return [self._normalize(a) for a in raw]

    def list_daily_health(
        self, token: str, since: date
    ) -> list[GarminDailyHealth]:
        """Fetch per-day health snapshots (garminconnect is per-day, not range)."""
        client = self._client_from_token(token)
        today = date.today()
        start = max(since, today - timedelta(days=HEALTH_WINDOW_DAYS))
        out: list[GarminDailyHealth] = []
        day = start
        while day <= today:
            iso = day.isoformat()
            stats = self._safe(lambda d=iso: client.get_stats(d)) or {}
            sleep = self._safe(lambda d=iso: client.get_sleep_data(d)) or {}
            hrv = self._safe(lambda d=iso: client.get_hrv_data(d)) or {}
            out.append(self._normalize_health(iso, stats, sleep, hrv))
            day += timedelta(days=1)
        return out

    @staticmethod
    def _safe(fn: Callable[[], object]) -> object | None:
        """Call a Garmin endpoint, swallowing per-day failures (best-effort)."""
        try:
            return fn()
        except Exception:  # noqa: BLE001 — one bad day shouldn't sink the import
            return None

    def get_activity_streams(self, token: str, garmin_activity_id: str) -> dict:
        client = self._client_from_token(token)
        return client.get_activity_details(garmin_activity_id)

    def push_workouts(self, token: str, workouts: list[dict]) -> int:
        """Create structured workouts in Garmin Connect via the workout-service.

        Each ``workout`` is a Garmin workout JSON (see ``build_garmin_workout``).
        Returns the number successfully created. A single failure does not abort
        the rest — pushing is best-effort, like the import pipeline.
        """
        client = self._client_from_token(token)
        pushed = 0
        for workout in workouts:
            try:
                client.garth.connectapi(
                    "/workout-service/workout",
                    method="POST",
                    json=workout,
                )
                pushed += 1
            except Exception:  # noqa: BLE001 — one bad upload shouldn't sink the batch
                continue
        return pushed

    @staticmethod
    def _client_from_token(token: str):
        from garminconnect import Garmin

        client = Garmin()
        client.garth.loads(token)
        # login() normally sets these from the profile; restore them when we load
        # from a stored token, else usersummary URLs resolve to .../daily/None.
        profile = getattr(client.garth, "profile", None) or {}
        client.display_name = profile.get("displayName")
        client.full_name = profile.get("fullName")
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
    def _normalize_health(
        iso: str, stats: dict, sleep: dict, hrv: dict
    ) -> GarminDailyHealth:
        """Pull health fields defensively from the per-day Garmin payloads."""
        sleep_dto = (sleep or {}).get("dailySleepDTO") or {}
        sleep_scores = sleep_dto.get("sleepScores") or {}
        sleep_overall = sleep_scores.get("overall") or {}
        hrv_summary = (hrv or {}).get("hrvSummary") or {}
        weight_g = stats.get("weight")

        def clean(v: object) -> object | None:
            """Garmin uses -1 as a 'no data' sentinel for several fields."""
            return None if isinstance(v, int | float) and v < 0 else v

        return GarminDailyHealth(
            day=iso,
            resting_hr=clean(stats.get("restingHeartRate")),
            hrv=hrv_summary.get("lastNightAvg") or hrv_summary.get("weeklyAvg"),
            sleep_score=sleep_overall.get("value"),
            steps=clean(stats.get("totalSteps")),
            body_battery=clean(
                stats.get("bodyBatteryMostRecentValue")
                or stats.get("bodyBatteryHighestValue")
            ),
            stress_avg=clean(stats.get("averageStressLevel")),
            weight_kg=(weight_g / 1000.0) if weight_g is not None else None,
        )
