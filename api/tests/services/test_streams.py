"""Stream normalizer tests — raw Garmin detail → compact client payload (2.4)."""
from __future__ import annotations

from app.services.streams import normalize_streams


def _raw(rows: list[list[float]]) -> dict:
    """Build a minimal Garmin activity-detail payload from metric rows."""
    descriptors = [
        {"metricsIndex": 0, "key": "sumElapsedDuration"},
        {"metricsIndex": 1, "key": "directHeartRate"},
        {"metricsIndex": 2, "key": "directSpeed"},
        {"metricsIndex": 3, "key": "directElevation"},
        {"metricsIndex": 4, "key": "sumDistance"},
        {"metricsIndex": 5, "key": "directLatitude"},
        {"metricsIndex": 6, "key": "directLongitude"},
    ]
    return {
        "metricDescriptors": descriptors,
        "activityDetailMetrics": [{"metrics": r} for r in rows],
    }


def test_normalize_returns_none_for_empty():
    assert normalize_streams(None) is None
    assert normalize_streams({}) is None
    assert normalize_streams({"metricDescriptors": [], "activityDetailMetrics": []}) is None


def test_normalize_extracts_samples_route_and_splits():
    rows = [
        # elapsed, hr, speed, elev, dist, lat, lng
        [t, 140 + t // 60, 3.0, 40.0 + t // 120, t * 3.0, 50.0 + t * 1e-5, 4.0 + t * 1e-5]
        for t in range(0, 800, 5)
    ]
    out = normalize_streams(_raw(rows))
    assert out is not None
    assert out["has_route"] is True
    assert len(out["route"]) > 1
    assert out["samples"][0]["hr"] == 140
    # speed 3 m/s → 1000/3 ≈ 333 s/km
    assert out["samples"][0]["pace_s_per_km"] == 333.3
    # 800s * 3 m/s = 2400 m → two full kilometre splits
    assert [s["km"] for s in out["splits"]] == [1, 2]


def test_normalize_handles_missing_gps():
    rows = [[t, 150, 0.0, 30.0, 0.0, None, None] for t in range(0, 200, 5)]
    out = normalize_streams(_raw(rows))
    assert out["has_route"] is False
    assert out["route"] == []
    # zero speed → no pace, but HR still present
    assert out["samples"][0]["pace_s_per_km"] is None
    assert out["samples"][0]["hr"] == 150
