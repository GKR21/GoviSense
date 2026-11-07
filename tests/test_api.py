"""
Tests for GoviSense FastAPI API Route Handlers (main.py)
Team DARKBITE · ModelX 2.0 Phase 1
"""

import pytest
from govisense.api.main import (
    load_and_train,
    root,
    health,
    get_latest_forecasts,
    farmer_top3,
    submit_planting_report,
    retrigger_pipeline,
    PlantingReportPayload,
    ReTriggerPayload,
)


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and cached data are loaded."""
    load_and_train()


def test_root_endpoint():
    res = root()
    assert res["app"] == "GoviSense"
    assert res["pilot_district"] == "Anuradhapura"
    assert res["status"] == "online"


def test_health_endpoint():
    res = health()
    assert res["status"] == "ok"
    assert res["models_loaded"] is True


def test_latest_forecasts_endpoint():
    res = get_latest_forecasts()
    assert "pilot_district" in res
    assert "crops" in res
    assert "big_onion" in res["crops"]
    assert "chilli" in res["crops"]
    assert "ai4_optimization" in res
    assert len(res["ai4_optimization"]["recommendations"]) > 0
    # Check Item 1: SPI scenarios and ratio
    bo = res["crops"]["big_onion"]
    assert "spi_ratio" in bo["ai3_supply_pressure_index"]
    assert "scenarios" in bo["ai3_supply_pressure_index"]
    assert "low" in bo["ai3_supply_pressure_index"]["scenarios"]
    assert "high" in bo["ai3_supply_pressure_index"]["scenarios"]
    # Check Item 2: Transparent accounting supply breakdown
    assert "accounting_supply_mt" in bo["ai1_harvest_forecast"]
    assert "accounting_breakdown" in bo["ai1_harvest_forecast"]
    # Check Item 3: A4 Decision Deadline and Policy Option
    first_action = res["ai4_optimization"]["recommendations"][0]
    assert "decision_deadline" in first_action
    assert "policy_option" in first_action
    assert first_action["policy_option"] in ["IMPORT_NOW", "IMPORT_LATER", "DELAY", "STORE"]


def test_simulation_with_area_and_yield_sliders():
    from govisense.api.main import simulate_scenario, SimulationRequest
    req = SimulationRequest(
        crop="big_onion",
        custom_planted_extent_ha=3500.0,
        custom_yield_mt_ha=16.5,
        custom_import_volume_mt=300.0,
    )
    sim = simulate_scenario(req)
    assert sim["crop"] == "big_onion"
    assert sim["area_ha"] == 3500.0
    assert sim["yield_mt_ha"] == 16.5
    assert sim["simulated_supply_mt"] > 0
    assert "simulated_spi_ratio" in sim
    assert "scenarios" in sim


def test_decision_history_with_model_and_data_versions():
    from govisense.api.main import log_officer_action, get_decision_history, DecisionLogPayload
    payload = DecisionLogPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id="OFFICER-007",
        action_type="HOLD_STORAGE",
        quantity=3000.0,
        unit="MT",
        rationale="Buffer hold to defend floor price",
        model_version="LightGBM-v2.1+HiGHS-LP",
        data_version="CBSL-HARTI-DOA-2024.12",
        assumptions={"loss_pct": 0.15, "lead_time_weeks": 7, "fair_floor": 120.0},
    )
    log_res = log_officer_action(payload)
    assert log_res["status"] == "RECORDED"

    records = get_decision_history(crop_id="big_onion", limit=5)
    assert len(records) > 0
    latest = records[0]
    assert latest["model_version"] == "LightGBM-v2.1+HiGHS-LP"
    assert latest["data_version"] == "CBSL-HARTI-DOA-2024.12"
    assert "loss_pct" in latest["assumptions"]


def test_farmer_top3_endpoint():
    res = farmer_top3(
        farmer_id="LK-NC-001",
        season="Maha",
        land_ha=2.5,
        current_month=10,
        is_rainfed=False,
        annual_rainfall_mm=1100.0,
        avg_temp_c=28.0,
        soil_ph=6.5,
        zone="dry",
    )
    assert res["farmer_id"] == "LK-NC-001"
    assert len(res["top3"]) > 0
    assert res["top3"][0]["fit_score"] > 0


def test_planting_report_and_retrigger_endpoints():
    payload = PlantingReportPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        planned_area_ha=2.0,
        actual_area_ha=2.5,
        consent_given=True,
        pseudonymous_id="LK-TEST-001",
    )
    rep_res = submit_planting_report(payload)
    assert rep_res["status"] == "ACCEPTED"

    ret_payload = ReTriggerPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        target_month=4,
    )
    ret_res = retrigger_pipeline(ret_payload)
    assert "new_a_rec_ha" in ret_res
