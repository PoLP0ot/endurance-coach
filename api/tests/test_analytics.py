"""AnalyticsEngine unit tests — deterministic metrics, no AI involved."""
from __future__ import annotations

import pytest
from app.services.analytics import (
    fitness_series,
    hr_training_stress_score,
    intensity_distribution,
    recovery_score,
    training_stress_score,
)


def test_tss_at_threshold_for_one_hour_is_100():
    # One hour at FTP (NP == FTP, IF == 1.0) is 100 TSS by definition.
    assert training_stress_score(3600, 250, 250) == pytest.approx(100.0)


def test_tss_scales_with_intensity():
    easy = training_stress_score(3600, 200, 250)
    hard = training_stress_score(3600, 300, 250)
    assert hard > 100 > easy


def test_tss_rejects_nonpositive_ftp():
    with pytest.raises(ValueError):
        training_stress_score(3600, 250, 0)


def test_hr_tss_at_threshold_for_one_hour_is_100():
    assert hr_training_stress_score(3600, 160, 160) == pytest.approx(100.0)


def test_fitness_series_grows_and_balances():
    # 30 days of steady 100 TSS: CTL rises, ATL rises faster, TSB goes negative.
    states = fitness_series([100.0] * 30)
    assert len(states) == 30
    assert states[-1].ctl > states[0].ctl
    assert states[-1].atl > states[-1].ctl  # fatigue outpaces fitness under load
    assert states[-1].tsb < 0


def test_recovery_score_clamped():
    assert 0 <= recovery_score(tsb=-50) <= 100
    assert 0 <= recovery_score(tsb=50) <= 100
    assert recovery_score(tsb=20) > recovery_score(tsb=-20)


def test_intensity_distribution_sums_to_one():
    samples = [100, 120, 140, 160, 180]
    dist = intensity_distribution(samples, zone_bounds=[110, 130, 150, 170])
    assert dist
    assert sum(dist.values()) == pytest.approx(1.0)
