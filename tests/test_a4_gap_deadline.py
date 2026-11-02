"""
Unit Tests for AI 4 Gap-Filling Recommendation Optimizer
"""

import pytest
from govisense.models.a4_gap_deadline import GapFillingOptimizer
from govisense.models.a3_supply_pressure import SPIResult


def test_optimizer_shortage_action():
    optimizer = GapFillingOptimizer()
    spi_results = [
        SPIResult(
            crop="big_onion",
            target_date="2025-05",
            forecast_supply_mt=500.0,
            projected_demand_mt=5000.0,
            gap_mt=-4500.0,
            spi_score=-0.55,
            spi_label="Shortage",
            action_summary="Deficit detected"
        ),
        SPIResult(
            crop="chilli",
            target_date="2025-05",
            forecast_supply_mt=3500.0,
            projected_demand_mt=2200.0,
            gap_mt=1300.0,
            spi_score=0.45,
            spi_label="Glut",
            action_summary="Oversupply detected"
        )
    ]
    
    res = optimizer.optimize_recommendations(spi_results)
    assert res["solver_status"] in ["OPTIMAL", "FALLBACK"]
    assert len(res["actions"]) >= 2
    
    action_types = [a.action_type for a in res["actions"]]
    assert "PLANT_EXPANSION" in action_types
    assert "HOLD_STORAGE_BUFFER" in action_types
