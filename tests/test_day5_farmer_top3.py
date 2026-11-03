"""
Tests for Day 5 Item 6: Farmer Top-3 Comparison Screen & Endpoint
"""

import pytest
from govisense.api.main import farmer_top3


def test_farmer_top3_endpoint_returns_required_fields():
    data = farmer_top3(
        farmer_id="ANU-FARMER-001",
        season="Maha",
        land_ha=3.0,
        current_month=10,
        is_rainfed=False,
        annual_rainfall_mm=1100.0,
        avg_temp_c=28.0,
        soil_ph=6.8,
        zone="dry",
    )

    assert data["farmer_id"] == "ANU-FARMER-001"
    assert "top3" in data
    top3 = data["top3"]
    assert len(top3) > 0
    assert len(top3) <= 3

    # Check that all 8 required fields from Day 5 specification are present:
    # 1. fit score
    # 2. profit range (P10–P90)
    # 3. risk
    # 4. water need
    # 5. planting window
    # 6. harvest period
    # 7. SPI band at harvest
    # 8. confidence badge
    for crop in top3:
        assert "fit_score" in crop
        assert 0.0 <= crop["fit_score"] <= 100.0

        assert "profit_range_rs_kg" in crop
        assert "p10_rs_kg" in crop["profit_range_rs_kg"]
        assert "p90_rs_kg" in crop["profit_range_rs_kg"]

        assert "risk_level" in crop
        assert crop["risk_level"] in ["Low", "Medium", "High"]

        assert "water_need_mm_season" in crop
        assert crop["water_need_mm_season"] is not None

        assert "planting_window" in crop
        assert len(crop["planting_window"]) > 0

        assert "harvest_period" in crop
        assert len(crop["harvest_period"]) > 0

        assert "spi_band_at_harvest" in crop
        assert crop["spi_band_at_harvest"] in ["Glut", "Balanced", "Shortage", "Unknown"]

        assert "confidence_badge" in crop
        assert crop["confidence_badge"] in ["high", "medium", "low"]


def test_farmer_top3_handles_rainfed_filtering():
    # Rainfed area filters out crops requiring irrigation (e.g. big_onion, tomato)
    data = farmer_top3(
        farmer_id="ANU-FARMER-RAINFED",
        season="Maha",
        land_ha=2.0,
        current_month=10,
        is_rainfed=True,
        annual_rainfall_mm=1100.0,
        avg_temp_c=28.0,
        soil_ph=6.5,
        zone="dry",
    )
    top_crop_ids = [c["crop_id"] for c in data["top3"]]
    assert "tomato" not in top_crop_ids
    assert "big_onion" not in top_crop_ids

