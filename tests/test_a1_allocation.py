"""
Unit tests for AI 1 Harvest Volume Forecaster (a1_allocation.py)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)
"""

import pytest
import numpy as np
import pandas as pd

from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a1_allocation import (
    HarvestVolumeForecaster,
    safe_forecast,
    ForecastResult,
)


def test_safe_forecast_guardrails():
    """Verifies that invalid or negative predictions trigger baseline fallback."""
    # Valid model output
    val, src = safe_forecast(model_pred=2500.0, baseline=2100.0)
    assert val == 2500.0
    assert src == "model"

    # NaN fallback
    val_nan, src_nan = safe_forecast(model_pred=np.nan, baseline=2100.0)
    assert val_nan == 2100.0
    assert "baseline" in src_nan

    # Non-positive fallback
    val_neg, src_neg = safe_forecast(model_pred=-50.0, baseline=1800.0)
    assert val_neg == 1800.0
    assert "baseline" in src_neg


def test_harvest_volume_forecaster_training_and_prediction():
    """Verifies training of LightGBM forecaster and prediction interval generation."""
    raw_df = load_monthly_dataset()
    df = engineer_features(raw_df)

    forecaster = HarvestVolumeForecaster(crop="big_onion")
    forecaster.train(df)

    assert forecaster.is_trained is True
    assert "point" in forecaster.models
    assert "lower" in forecaster.models
    assert "upper" in forecaster.models

    latest_row = df[df["crop"] == "big_onion"].iloc[-1]
    res = forecaster.predict_row(latest_row)

    assert isinstance(res, ForecastResult)
    assert res.point_forecast > 0
    assert res.lower_bound_10 <= res.point_forecast <= res.upper_bound_90
    assert res.baseline_pred > 0

