"""Normalize raw Garmin activity-detail streams into a light client payload.

The stored stream is Garmin's raw ``get_activity_details`` response (~1 MB of
column-indexed samples). The frontend only needs a downsampled series for the
HR/pace/elevation chart, a route polyline for the map, and per-kilometre splits.
This module turns the raw payload into that compact, deterministic shape.
"""
from __future__ import annotations

# Cap the number of points sent to the client for charts and the route.
SAMPLE_CAP = 300


def _index_map(descriptors: list[dict]) -> dict[str, int]:
    """Map each metric key to its column index in the sample rows."""
    return {d["key"]: d["metricsIndex"] for d in descriptors if "metricsIndex" in d}


def _value(metrics: list, idx: dict[str, int], key: str) -> float | None:
    """Read one metric from a sample row, or None when absent."""
    i = idx.get(key)
    if i is None or i >= len(metrics):
        return None
    v = metrics[i]
    return float(v) if isinstance(v, (int, float)) else None


def _pace_s_per_km(speed_m_s: float | None) -> float | None:
    """Convert m/s to seconds-per-kilometre, guarding against zero speed."""
    if speed_m_s is None or speed_m_s <= 0.2:
        return None
    return round(1000.0 / speed_m_s, 1)


def _splits(rows: list[dict], idx: dict[str, int]) -> list[dict]:
    """Per-kilometre splits derived from cumulative distance and elapsed time."""
    splits: list[dict] = []
    last_time = 0.0
    next_km = 1
    for r in rows:
        metrics = r.get("metrics") or []
        dist = _value(metrics, idx, "sumDistance")
        elapsed = _value(metrics, idx, "sumElapsedDuration")
        if dist is None or elapsed is None:
            continue
        while dist >= next_km * 1000.0:
            splits.append({"km": next_km, "duration_s": round(elapsed - last_time)})
            last_time = elapsed
            next_km += 1
    return splits


def normalize_streams(raw: dict | None) -> dict | None:
    """Return ``{samples, route, splits, has_route}`` or None when unusable.

    ``samples`` is a downsampled series (t, hr, pace_s_per_km, elevation_m,
    distance_m). ``route`` is a list of [lat, lng] pairs. ``splits`` are
    per-kilometre durations. All numbers come straight from the stored samples.
    """
    if not raw:
        return None
    descriptors = raw.get("metricDescriptors")
    rows = raw.get("activityDetailMetrics")
    if not descriptors or not rows:
        return None

    idx = _index_map(descriptors)
    step = max(1, len(rows) // SAMPLE_CAP)

    samples: list[dict] = []
    route: list[list[float]] = []
    for r in rows[::step]:
        metrics = r.get("metrics") or []
        elapsed = _value(metrics, idx, "sumElapsedDuration")
        samples.append(
            {
                "t": round(elapsed) if elapsed is not None else None,
                "hr": _value(metrics, idx, "directHeartRate"),
                "pace_s_per_km": _pace_s_per_km(_value(metrics, idx, "directSpeed")),
                "elevation_m": _value(metrics, idx, "directElevation"),
                "distance_m": _value(metrics, idx, "sumDistance"),
            }
        )
        lat = _value(metrics, idx, "directLatitude")
        lng = _value(metrics, idx, "directLongitude")
        if lat is not None and lng is not None:
            route.append([round(lat, 6), round(lng, 6)])

    return {
        "samples": samples,
        "route": route,
        "splits": _splits(rows, idx),
        "has_route": len(route) > 1,
    }
