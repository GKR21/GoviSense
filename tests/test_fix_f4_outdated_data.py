"""
Test Fix F4: Outdated Data Quality & Age Tracking
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
import pandas as pd
from unittest.mock import patch
from govisense.api.main import get_latest_forecasts, get_price_outlook, load_and_train
import govisense.api.main as api_main


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and cached data are loaded."""
    load_and_train()


def test_forecasts_and_price_outlook_flag_outdated_data():
    """
    When latest row in cached_df is > 60 days old (e.g. historical data through 2024),
    endpoints must return data_quality: 'outdated' and include data_age_days.
    """
    fc = get_latest_forecasts()
    assert fc["data_quality"] == "outdated"
    assert "data_age_days" in fc
    assert fc["data_age_days"] is not None
    assert fc["data_age_days"] > 60
    assert "outdated" in fc.get("notes", "").lower()

    po = get_price_outlook(crop_id="big_onion")
    assert po["data_quality"] == "outdated"
    assert "data_age_days" in po
    assert po["data_age_days"] is not None
    assert po["data_age_days"] > 60


def test_fresh_data_yields_real_quality():
    """
    When cached_df contains recent observations (within 60 days),
    data_quality must not be forced to 'outdated'.
    """
    fresh_df = api_main.cached_df.copy()
    fresh_df["date"] = pd.Timestamp.now()

    with patch.object(api_main, "cached_df", fresh_df):
        fc = get_latest_forecasts()
        assert fc["data_quality"] != "outdated"
        assert fc["data_age_days"] is not None
        assert fc["data_age_days"] <= 60

        po = get_price_outlook(crop_id="big_onion")
        assert po["data_quality"] != "outdated"
        assert po["data_age_days"] is not None
        assert po["data_age_days"] <= 60
