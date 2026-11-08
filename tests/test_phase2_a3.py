"""
Acceptance Tests for Phase 2 Item 2.1: A3 Supply Pressure Engine
"""

import pytest
from govisense.models.a3_supply_pressure import (
    SupplyPressureEngine,
    compute_harvest_month,
    compute_phenology_supply,
)
from govisense.config import settings


def test_harvest_month_duration_computation():
    # Big onion: duration ~ 3.5 months -> rounds to 4
    # Planting in May (month 5) -> Harvest in September (month 9)
    assert compute_harvest_month(planting_month=5, duration_months=3.5) == 9
    # November (month 11) + 4 months -> March (month 3)
    assert compute_harvest_month(planting_month=11, duration_months=3.5) == 3


def test_phenology_supply_and_unreported_area():
    res = compute_phenology_supply(
        planted_area_ha=1000.0,
        yield_mt_ha=15.0,
        loss_pct=0.15,
        unreported_area_ratio=0.15,
    )
    # Effective area: 1000 * 1.15 = 1150 ha
    assert res["effective_area_ha"] == 1150.0
    # Total supply: 1150 * 15.0 * 0.85 = 14662.5 MT
    assert res["total_effective_supply_mt"] == 14662.5
    # Phenology weights: 20%, 60%, 20%
    curve = res["phenology_curve"]
    assert curve["early_month_20pct"] == round(14662.5 * 0.20, 1)
    assert curve["peak_month_60pct"] == round(14662.5 * 0.60, 1)
    assert curve["late_month_20pct"] == round(14662.5 * 0.20, 1)


def test_scenarios_vary_yield_percentiles_not_demand():
    engine = SupplyPressureEngine()
    res = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=15000.0,
        month=8,
    )
    # Demand must be constant across all 3 scenarios per Proposal Rule
    d_mid = res.scenarios["mid"].demand_mt
    d_low = res.scenarios["low"].demand_mt
    d_high = res.scenarios["high"].demand_mt
    assert d_mid == d_low == d_high == res.projected_demand_mt

    # Supply must vary across 10th, 50th, 90th percentiles
    s_low = res.scenarios["low"].supply_mt
    s_mid = res.scenarios["mid"].supply_mt
    s_high = res.scenarios["high"].supply_mt
    assert s_low < s_mid < s_high


def test_spi_threshold_adjustability():
    engine = SupplyPressureEngine()
    # At ratio 1.15, with default 1.20 glut threshold it is Balanced
    res_default = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=15500.0,
        month=8,
        glut_ratio_threshold=1.25,
    )
    assert res_default.spi_label == "Balanced"

    # If officer tightens glut threshold to 1.10, it triggers Glut
    res_tight = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=15500.0,
        month=8,
        glut_ratio_threshold=1.10,
    )
    assert res_tight.spi_label == "Glut"
