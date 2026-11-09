"""
Test Fix F5: Missing Model Error Handling (HTTP 503 instead of KeyError)
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from unittest.mock import patch
from fastapi import HTTPException
from govisense.api.main import get_latest_forecasts, load_and_train
import govisense.api.main as api_main


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure baseline models are loaded."""
    load_and_train()


def test_missing_a1_model_raises_503():
    """
    Verify that if an A1 harvest forecaster is missing from a1_models,
    get_latest_forecasts raises an explicit HTTP 503 exception rather
    than crashing with an unhandled KeyError.
    """
    # Keep chilli but omit big_onion so _ensure_models_loaded doesn't trigger re-train
    with patch.dict(api_main.a1_models, {"chilli": api_main.a1_models["chilli"]}, clear=True):
        with pytest.raises(HTTPException) as exc_info:
            get_latest_forecasts()
        assert exc_info.value.status_code == 503
        assert "A1 harvest model for 'big_onion' is not loaded." in exc_info.value.detail


def test_missing_a2_model_raises_503():
    """
    Verify that if an A2 price forecaster is missing from a2_models,
    get_latest_forecasts raises an explicit HTTP 503 exception rather
    than crashing with an unhandled KeyError.
    """
    with patch.dict(api_main.a2_models, {"chilli": api_main.a2_models["chilli"]}, clear=True):
        with pytest.raises(HTTPException) as exc_info:
            get_latest_forecasts()
        assert exc_info.value.status_code == 503
        assert "A2 price model for 'big_onion' is not loaded." in exc_info.value.detail
