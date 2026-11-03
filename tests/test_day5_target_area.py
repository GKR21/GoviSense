"""
Tests for Day 5 Item 4: Target Area Calculator
"""

import pytest
from govisense.models.target_area import TargetAreaCalculator, TargetAreaResult


def test_target_area_core_formula():
    calc = TargetAreaCalculator()
    # demand = 20,000 MT, buffer = 5% (1.05), yield_mid = 10 MT/ha, loss = 20% (0.80)
    # effective yield = 10 * 0.8 = 8 MT/ha
    # A_target = 20,000 * 1.05 / 8 = 2,625 ha
    res = calc.compute(
        crop="big_onion",
        season="Maha 2025/2026",
        demand_mt=20000.0,
        yield_mid=10.0,
        loss_pct=0.20,
        buffer=0.05,
        a_reported=0.0,
    )
    assert isinstance(res, TargetAreaResult)
    assert res.a_target_ha == pytest.approx(2625.0)
    assert res.a_rec_ha == pytest.approx(2625.0)


def test_target_area_with_cap_from_parcels():
    calc = TargetAreaCalculator()
    # Parcels with fit scores: threshold is 60.0
    parcels = [
        {"land_ha": 500.0, "fit_score": 75.0},  # included (>= 60)
        {"land_ha": 300.0, "fit_score": 85.0},  # included (>= 60)
        {"land_ha": 400.0, "fit_score": 45.0},  # excluded (< 60)
    ]
    # Cap should be 500 + 300 = 800 ha
    cap = calc.calculate_cap(parcels, fit_threshold=60.0)
    assert cap == pytest.approx(800.0)

    # A_target is 2,625 ha, but cap is 800 ha -> A_capped is 800 ha
    res = calc.compute(
        crop="big_onion",
        season="Maha 2025/2026",
        demand_mt=20000.0,
        yield_mid=10.0,
        loss_pct=0.20,
        buffer=0.05,
        a_reported=100.0,
        suitable_land_ha=parcels,
        fit_threshold=60.0,
    )
    assert res.a_cap_ha == pytest.approx(800.0)
    # A_rec = min(A_target, A_cap) - A_reported = 800 - 100 = 700 ha
    assert res.a_rec_ha == pytest.approx(700.0)


def test_oversupply_stop_rule():
    calc = TargetAreaCalculator()
    # A_target = 2625 ha
    # If A_reported > 110% of target (2625 * 1.10 = 2887.5 ha):
    # say A_reported = 2900 ha
    res = calc.compute(
        crop="big_onion",
        season="Maha 2025/2026",
        demand_mt=20000.0,
        yield_mid=10.0,
        loss_pct=0.20,
        buffer=0.05,
        a_reported=2900.0,
    )
    # Stop rule triggered: A_rec must be 0
    assert res.a_rec_ha == 0.0
    assert "Oversupply stop rule triggered" in res.rationale
    assert "110% of A_target" in res.rationale

