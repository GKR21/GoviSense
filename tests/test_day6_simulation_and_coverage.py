"""
Tests for Day 6 Item 9: 80% Interval Coverage & Market Adoption Simulation
"""

import pytest
import numpy as np
from govisense.simulation.agent_sim import (
    calculate_interval_coverage,
    MarketAdoptionSimulator,
    AdoptionScenarioResult,
)


def test_interval_80_coverage():
    # 10 actual points
    actuals = np.array([100, 105, 110, 115, 120, 125, 130, 135, 140, 200])
    # 8 points fall inside [95, 145], point 9 (140) inside, point 10 (200) outside
    lowers = np.full(10, 95.0)
    uppers = np.full(10, 145.0)

    res = calculate_interval_coverage(actuals, lowers, uppers)
    assert res["target_coverage_pct"] == 80.0
    assert res["total_eval_points"] == 10
    # 9 of 10 points are inside -> 90.0%
    assert res["coverage_pct"] == pytest.approx(90.0)
    assert res["well_calibrated"] is True


def test_market_adoption_simulation():
    sim = MarketAdoptionSimulator()
    res = sim.simulate(
        crop="big_onion",
        season_demand_mt=26667.0,
        uncoordinated_supply_mt=46000.0,
        yield_mid=15.5,
        fair_floor_rs_kg=120.0,
        base_unregulated_price_rs_kg=75.0,
    )

    assert res["crop"] == "big_onion"
    assert len(res["scenarios"]) == 3

    s0 = res["scenarios"][0]   # 0% adoption
    s30 = res["scenarios"][1]  # 30% adoption
    s60 = res["scenarios"][2]  # 60% adoption

    assert s0["adoption_rate_pct"] == 0
    assert s30["adoption_rate_pct"] == 30
    assert s60["adoption_rate_pct"] == 60

    # 1. Supply decreases towards target as adoption increases
    assert s0["total_supply_mt"] > s30["total_supply_mt"] > s60["total_supply_mt"]

    # 2. SPI moves from extreme glut towards balanced band
    assert s0["spi_score"] > s30["spi_score"] > s60["spi_score"]
    assert s60["spi_score"] < 0.20

    # 3. Farmgate price increases and price crash risk decreases
    assert s60["farmgate_price_rs_kg"] > s0["farmgate_price_rs_kg"]
    assert s60["price_crash_risk_pct"] < s0["price_crash_risk_pct"]
    assert s60["price_crash_risk_pct"] <= 50.0
