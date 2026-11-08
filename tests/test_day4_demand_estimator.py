"""
Tests for Day 4 Item 1: Demand Estimator Module (WP1)
"""

import pytest
from govisense.models.demand_estimator import DemandEstimator, SEASONAL_FACTORS, SCENARIO_SPREAD
from govisense.config import HUB_SHARE
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.data.crop_requirements import get_crop_requirements


def test_demand_estimator_big_onion_anchor():
    estimator = DemandEstimator()
    annual_hub = estimator.annual_hub_demand("big_onion")
    expected_hub = 320000.0 * HUB_SHARE["big_onion"]
    assert annual_hub == pytest.approx(expected_hub, rel=1e-3)

    jan_res = estimator.estimate("big_onion", month=1)
    expected_jan = (expected_hub / 12.0) * 1.0
    assert jan_res.demand_mt == pytest.approx(expected_jan, rel=1e-2)
    assert "Commodity Board" in jan_res.source_note


def test_demand_estimator_seasonal_spread():
    estimator = DemandEstimator()
    res = estimator.estimate("big_onion", month=5)
    # Low is -10%, High is +10%
    expected_low = res.demand_mt * (1.0 - SCENARIO_SPREAD)
    expected_high = res.demand_mt * (1.0 + SCENARIO_SPREAD)
    assert res.demand_low == pytest.approx(expected_low, rel=1e-2)
    assert res.demand_high == pytest.approx(expected_high, rel=1e-2)


def test_demand_estimator_seasonal_factors():
    estimator = DemandEstimator()
    res_apr = estimator.estimate("big_onion", month=4)  # April festival
    res_jan = estimator.estimate("big_onion", month=1)  # January baseline
    assert res_apr.seasonal_factor == 1.30
    assert res_apr.demand_mt > res_jan.demand_mt
    assert res_apr.demand_mt == pytest.approx(res_jan.demand_mt * 1.30, rel=1e-2)


def test_demand_estimator_ai3_integration():
    engine = SupplyPressureEngine()
    estimator = DemandEstimator()

    demand_from_engine = engine.project_monthly_demand("big_onion", month=4)
    demand_from_estimator = estimator.estimate("big_onion", month=4).demand_mt
    assert demand_from_engine == pytest.approx(demand_from_estimator, rel=1e-3)


def test_demand_estimator_all_catalog_crops():
    estimator = DemandEstimator()
    reqs = get_crop_requirements()
    for crop_id in reqs:
        res = estimator.estimate(crop_id, month=1)
        assert res.demand_mt > 0
        assert res.demand_low < res.demand_mt < res.demand_high

