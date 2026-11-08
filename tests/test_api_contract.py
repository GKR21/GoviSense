"""
API Contract Verification Test Suite (Phase 0.3)
Verifies:
- All required endpoints from Phase 0.3 exist and return valid contract dictionaries
- Model-bearing endpoints satisfy Rule 7 provenance:
  run_id, data_version, model_version, data_quality, is_demo, served_model, assumptions_ref
- Pydantic response models from govisense.api.schemas validate successfully
"""

import pytest
from govisense.api.main import (
    load_and_train,
    health,
    get_latest_forecasts,
    get_gap_alias,
    farmer_top3,
    get_latest_prices,
    get_evaluation_scoreboard,
    list_pipeline_runs,
    get_pipeline_run_by_id,
    list_alerts,
    acknowledge_alert,
    ask_officer_on_alert,
    get_adoption_summary,
    AlertAckPayload,
)
from govisense.api.schemas import (
    HealthResponse,
    LatestPricesResponse,
    EvaluationScoreboardResponse,
)


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and data cache are initialized."""
    load_and_train()


def test_health_contract():
    data = health()
    validated = HealthResponse(**data)
    assert validated.status == "ok"
    assert len(validated.data_version) == 8
    assert "+" in validated.model_version


def test_forecasts_latest_contract_and_rule7():
    data = get_latest_forecasts()
    assert "run_id" in data
    assert "data_version" in data and len(data["data_version"]) == 8
    assert "model_version" in data and "+" in data["model_version"]
    assert "data_quality" in data
    assert "is_demo" in data
    assert "served_model" in data
    assert "assumptions_ref" in data
    assert "crops" in data
    assert "ai4_optimization" in data


def test_gap_contract_and_alias():
    data = get_gap_alias()
    assert "timelines" in data
    assert "run_id" in data
    assert "data_version" in data
    assert len(data["timelines"]) >= 2


def test_farmer_top3_contract_and_rule7():
    data = farmer_top3(farmer_id="LK-AP-001", land_ha=2.5)
    assert data["farmer_id"] == "LK-AP-001"
    assert "run_id" in data
    assert "data_version" in data
    assert "top3" in data
    assert len(data["top3"]) > 0


def test_prices_latest_contract():
    data = get_latest_prices()
    validated = LatestPricesResponse(**data)
    assert len(validated.prices) >= 2


def test_evaluation_scoreboard_contract_and_rule7():
    data = get_evaluation_scoreboard()
    validated = EvaluationScoreboardResponse(**data)
    assert validated.data_quality == "real"
    assert len(validated.scoreboard) >= 4


def test_runs_and_run_detail_contract():
    runs = list_pipeline_runs(limit=10)
    assert len(runs) > 0
    run_id = runs[0]["run_id"]

    data = get_pipeline_run_by_id(run_id=run_id)
    assert data["run_id"] == run_id
    assert "data_version" in data
    assert "model_version" in data


def test_alerts_and_ack_contract():
    alerts = list_alerts(limit=5)
    assert len(alerts) > 0
    alert_id = alerts[0]["alert_id"]

    # Acknowledge alert
    ack_res = acknowledge_alert(alert_id, AlertAckPayload(user_id="OFFICER-001", ask_officer=False))
    assert ack_res["status"] == "ACKNOWLEDGED"

    # Ask officer inquiry
    inquiry_res = ask_officer_on_alert(alert_id, {"farmer_id": "LK-AP-001", "question": "Can I store in regional buffer?"})
    assert inquiry_res["status"] == "INQUIRY_SENT"


def test_adoption_summary_contract():
    data = get_adoption_summary(crop_id="big_onion", season="Maha 2025/2026")
    assert data["crop_id"] == "big_onion"
    assert "acreage" in data
    assert "predicted_vs_actual" in data
