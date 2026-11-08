"""
Unit Tests for AI 3 Supply Pressure Index Engine
"""

import pytest
from govisense.models.a3_supply_pressure import SupplyPressureEngine, SPIResult


def test_spi_calculation_glut():
    engine = SupplyPressureEngine()
    # High supply vs demand should trigger Glut
    res = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=15000.0,
        month=8,
        import_volume_mt=500.0
    )
    assert isinstance(res, SPIResult)
    assert res.spi_score > 0.15
    assert res.spi_label == "Glut"
    assert "Oversupply detected" in res.action_summary


def test_spi_calculation_shortage():
    engine = SupplyPressureEngine()
    # Very low supply should trigger Shortage
    res = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=200.0,
        month=3,
        import_volume_mt=100.0
    )
    assert res.spi_score < -0.15
    assert res.spi_label == "Shortage"
    assert "Deficit detected" in res.action_summary


def test_spi_calculation_balanced():
    engine = SupplyPressureEngine()
    demand = engine.project_monthly_demand("big_onion", 1)
    # Supply calibrated to roughly match demand
    approx_supply = demand / 0.85
    res = engine.compute_spi(
        crop="big_onion",
        forecast_supply_mt=approx_supply,
        month=1,
        import_volume_mt=0.0
    )
    assert res.spi_label == "Balanced"
