"""
Test Fix F3: Elimination of Silent Fallbacks
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from unittest.mock import patch
from fastapi import HTTPException

from govisense.api.main import get_latest_forecasts, load_and_train
from govisense.api.routes.farmer import farmer_top3_recommendations


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and cached data are initialized."""
    load_and_train()


def test_demand_estimator_failure_raises_503():
    """
    Verify that if the demand estimator fails, the farmer endpoint raises
    HTTP 503 with explicit service unavailable details instead of falling
    back to 5000 MT / 20000 MT.
    """
    with patch("govisense.api.routes.farmer.demand_estimator.estimate", side_effect=RuntimeError("DOA demand feed unavailable")):
        with pytest.raises(HTTPException) as exc_info:
            farmer_top3_recommendations(
                farmer_id="FARMER-TEST-503",
                season="Maha",
                land_ha=2.0,
                current_month=10,
            )
        assert exc_info.value.status_code == 503
        assert "Demand estimation service unavailable" in exc_info.value.detail
        assert "DOA demand feed unavailable" in exc_info.value.detail


def test_db_unavailable_sets_explicit_flags_in_latest_forecasts():
    """
    Verify that if the database is unreachable during snapshot persistence in
    get_latest_forecasts, it does NOT silently swallow the error:
    db_fallback must be True, data_quality must be 'db_unavailable', and notes must explain it.
    """
    with patch("govisense.api.main.get_session", side_effect=ConnectionError("Postgres cluster unreachable")):
        res = get_latest_forecasts()
        assert res["db_fallback"] is True
        assert res["data_quality"] == "db_unavailable"
        assert res["notes"] is not None
        assert "Database unavailable" in res["notes"]
        assert "Postgres cluster unreachable" in res["notes"]


def test_no_mock_multipliers_on_model_missing():
    """
    Verify that when a crop does not have trained models (e.g. brinjal),
    price_forecast and profit_range are None with 'no_price_data',
    rather than applying 0.85/1.50 static multipliers or 0.15*sin() loops.
    """
    res = farmer_top3_recommendations(
        farmer_id="FARMER-UNMODELED",
        season="Maha",
        land_ha=2.0,
        current_month=10,
    )
    for crop_item in res.get("top3", []):
        if crop_item["crop_id"] not in ("big_onion", "chilli", "chilli_green"):
            assert crop_item.get("price_forecast") is None
            assert crop_item.get("profit_range_rs_kg") is None
            assert crop_item.get("price_data_quality") == "no_price_data"
            assert crop_item.get("monthly_price_ranges_12m") is None
