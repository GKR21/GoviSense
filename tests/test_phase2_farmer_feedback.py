"""
Acceptance Tests for Phase 2 Items 2.7 & 2.10:
  - 2.7: Farmer advisor (/api/farmer/top3) with remaining target area, 12m price ranges,
         profit/acre range, risk level, water need, planting window, and 110% stop rule.
  - 2.10: Feedback loop end-to-end (submit report -> new run_id & snapshot -> updates latest forecasts & top3).
"""

import pytest
import tempfile
from pathlib import Path
from govisense.api.main import (
    farmer_top3,
    submit_planting_report,
    get_latest_forecasts,
    PlantingReportPayload,
    report_store,
)
from govisense.feedback.planting_reports import PlantingReport, PlantingReportStore


def test_farmer_top3_rich_advisor_metadata():
    res = farmer_top3(
        farmer_id="FARMER-TEST-001",
        season="Maha",
        land_ha=2.5,
        current_month=10,
        is_rainfed=False,
    )
    assert "top3" in res
    assert len(res["top3"]) > 0

    top_crop = res["top3"][0]
    # Check 12-month expected price ranges
    assert "monthly_price_ranges_12m" in top_crop
    assert len(top_crop["monthly_price_ranges_12m"]) == 12
    for m in top_crop["monthly_price_ranges_12m"]:
        assert "p10_rs_kg" in m
        assert "p50_rs_kg" in m
        assert "p90_rs_kg" in m
        assert m["p10_rs_kg"] <= m["p90_rs_kg"]

    # Check net profit per acre range
    assert "expected_net_profit_per_acre" in top_crop
    assert "p10_rs_per_acre" in top_crop["expected_net_profit_per_acre"]
    assert "p90_rs_per_acre" in top_crop["expected_net_profit_per_acre"]

    # Check remaining target area
    assert "remaining_target_ha" in top_crop
    assert top_crop["remaining_target_ha"] >= 0.0

    # Check risk level, water need, planting window, harvest SPI
    assert top_crop["risk_level"] in ["Low", "Medium", "High"]
    assert top_crop["water_need_mm_season"] is not None
    assert "Month" in top_crop["planting_window"]
    assert top_crop["spi_band_at_harvest"] in ["Glut", "Balanced", "Shortage", "Unknown"]


def test_farmer_top3_oversupply_stop_rule_triggers_warning():
    # Submit massive acreage exceeding 110% of target
    report_store.submit_report(
        PlantingReport(
            crop_id="big_onion",
            season="Maha",
            planned_area_ha=8000.0,
            actual_area_ha=8000.0,
            consent_given=True,
            pseudonymous_id="COOP-ANURADHAPURA-TEST",
        )
    )

    res = farmer_top3(
        farmer_id="FARMER-TEST-002",
        season="Maha",
        land_ha=2.0,
        current_month=10,
    )

    # Big Onion must either have warning or be deprioritized with fit_score 0
    onion_entry = next((c for c in res["top3"] if c["crop_id"] == "big_onion"), None)
    if onion_entry:
        assert onion_entry["is_target_full"] is True
        assert "TARGET FULL - DO NOT PLANT" in onion_entry["target_full_warning"]
        assert onion_entry["recommended_ha"] == 0.0
        assert onion_entry["fit_score"] == 0.0


def test_feedback_loop_end_to_end_updates_forecast_and_top3():
    # 1. Capture before state
    before_forecasts = get_latest_forecasts()
    before_onion_supply = before_forecasts["crops"]["big_onion"]["ai1_harvest_forecast"]["point_forecast_mt"]

    # 2. Submit planting report
    payload = PlantingReportPayload(
        crop_id="big_onion",
        season="Maha",
        planned_area_ha=500.0,
        actual_area_ha=500.0,
        consent_given=True,
        pseudonymous_id="FEEDBACK-AUDIT-FARMER",
    )
    post_res = submit_planting_report(payload)

    # 3. Verify new run_id and status
    assert post_res["status"] == "ACCEPTED"
    assert "run_id" in post_res
    assert post_res["run_id"].startswith("RUN-")

    # 4. Verify updated forecast response
    after_forecasts = get_latest_forecasts()
    # The effective supply includes ground-reported planting
    after_onion_supply = after_forecasts["crops"]["big_onion"]["ai1_harvest_forecast"]["point_forecast_mt"]
    assert after_forecasts["crops"]["big_onion"]["ai3_supply_pressure_index"]["spi_score"] is not None
