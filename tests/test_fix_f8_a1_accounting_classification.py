"""
Test Fix F8: A1 Plan-Based Agronomic Accounting Classification & Config Weights
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from govisense.config import HARVEST_WINDOW_WEIGHTS, settings
from govisense.models.harvest_volume import (
    HarvestVolumeForecaster,
    compute_transparent_accounting_supply,
)
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.api.main import get_latest_forecasts, load_and_train
from govisense.api.routes.data import get_evaluation_scoreboard


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and cached data are loaded."""
    load_and_train()


def test_harvest_window_weights_in_config():
    """
    Verify harvest window weights are stored in config.py under HARVEST_WINDOW_WEIGHTS
    with proper values (0.40, 0.65, 0.88 for onion, 0.75 for chilli).
    """
    assert "big_onion" in HARVEST_WINDOW_WEIGHTS
    bo_weights = HARVEST_WINDOW_WEIGHTS["big_onion"]
    assert bo_weights[8] == 0.40
    assert bo_weights[9] == 0.65
    assert bo_weights[10] == 0.88

    assert "chilli" in HARVEST_WINDOW_WEIGHTS
    chilli_weights = HARVEST_WINDOW_WEIGHTS["chilli"]
    assert chilli_weights[1] == 0.75
    assert chilli_weights[7] == 0.75

    assert settings.harvest_window_weights == HARVEST_WINDOW_WEIGHTS


def test_transparent_accounting_supply_uses_config_weights():
    """
    Verify compute_transparent_accounting_supply retrieves weights from config
    and labels the output as 'agreement with CPP plan' and data_quality: 'partial'.
    """
    acct = compute_transparent_accounting_supply(
        crop="big_onion",
        month=8,
        planted_area_ha=1000.0,
        yield_mt_ha=15.0,
        loss_pct=0.15,
    )
    assert acct["model_classification"] == "agreement with CPP plan"
    assert acct["data_quality"] == "partial"
    assert acct["method"] == "plan-based agronomic accounting"
    assert acct["harvest_spread_factor"] == 0.40


def test_a1_forecast_result_classification():
    """
    Verify HarvestVolumeForecaster produces ForecastResult with
    model_classification 'agreement with CPP plan' and data_quality 'partial'.
    """
    raw = load_monthly_dataset()
    df = engineer_features(raw)
    bo_df = df[df["crop"] == "big_onion"].sort_values("date")

    forecaster = HarvestVolumeForecaster(crop="big_onion")
    forecaster.train(bo_df.iloc[:40])
    res = forecaster.predict_row(bo_df.iloc[-1])

    assert res.model_classification == "agreement with CPP plan"
    assert res.data_quality == "partial"
    assert res.method == "plan-based agronomic accounting"


def test_api_and_scoreboard_expose_a1_classification():
    """
    Verify both /api/forecasts/latest and /api/evaluation/scoreboard expose
    the explicit classification and data_quality: 'partial' for A1 harvest volume.
    """
    latest = get_latest_forecasts()
    assert "crops" in latest
    ai1_bo = latest["crops"]["big_onion"]["ai1_harvest_forecast"]
    assert ai1_bo["model_classification"] == "agreement with CPP plan"
    assert ai1_bo["data_quality"] == "partial"

    board = get_evaluation_scoreboard()
    assert "scoreboard" in board
    supply_rows = [
        r for r in board["scoreboard"]
        if "Supply" in r.get("module", "") or "Harvest" in r.get("module", "")
    ]
    assert len(supply_rows) > 0
    for r in supply_rows:
        assert r["model_classification"] == "agreement with CPP plan"
        assert r["data_quality"] == "partial"
