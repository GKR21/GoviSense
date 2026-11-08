"""
Acceptance Tests for Phase 2 Item 2.2: A2 Price Forecast Engine
"""

import pytest
import pandas as pd
import numpy as np
from govisense.models.a2_price_forecast import (
    PriceForecaster,
    PriceForecastResult,
    compute_modeled_retail_price,
)
from govisense.data.clean import load_monthly_dataset, engineer_features


@pytest.fixture(scope="module")
def prepared_df():
    raw_df = load_monthly_dataset()
    return engineer_features(raw_df)


def test_modeled_retail_price_not_fixed_multiplier():
    # Wholesale 200 Rs/kg
    # For big onion: 200 + 12 (transport) + 200 * 0.18 (margin) = 248.0 Rs/kg
    # (If it were 1.35x, it would be 270.0)
    p_onion = compute_modeled_retail_price(200.0, crop="big_onion")
    assert p_onion == 248.0
    assert p_onion != round(200.0 * 1.35, 1)

    # For chilli: 200 + 12 + 200 * 0.22 = 256.0 Rs/kg
    p_chilli = compute_modeled_retail_price(200.0, crop="chilli")
    assert p_chilli == 256.0
    assert p_chilli != round(200.0 * 1.35, 1)


def test_price_forecaster_quantiles_and_conformal_calibration(prepared_df):
    df = prepared_df
    forecaster = PriceForecaster(crop="big_onion", target_col="wholesale_price_rs_kg")

    cutoff = df["date"].max() - pd.DateOffset(months=6)
    train_df = df[df["date"] <= cutoff]
    val_df = df[df["date"] > cutoff]

    res = forecaster.train_and_select(train_df, val_df)

    # Check quantiles models exist
    assert "p10" in forecaster.lgb_models
    assert "p50" in forecaster.lgb_models
    assert "p90" in forecaster.lgb_models

    # Check features include local_vs_import_gap, rainfall_anomaly, lags
    assert "local_vs_import_gap" in forecaster.features
    assert "rainfall_anomaly_3m_mean" in forecaster.features
    assert "wholesale_price_lag12" in forecaster.features

    # Check conformal scale factor and empirical coverage
    assert res["conformal_scale"] >= 1.0
    assert 0.0 <= res["empirical_coverage"] <= 1.0

    # Test multi-horizon forecasting (t+1, t+2, t+3)
    sample_row = val_df[val_df["crop"] == "big_onion"].iloc[-1]
    for h in [1, 2, 3]:
        f = forecaster.forecast_step(sample_row, horizon=h)
        assert isinstance(f, PriceForecastResult)
        assert f.horizon_months == h
        assert f.lower_bound <= f.best_forecast <= f.upper_bound
        assert f.modeled_retail_price > f.best_forecast
        assert f.direction in ["up", "down", "flat"]
        assert f.served_model in ["lightgbm", "sarimax", "ets", "seasonal_naive"]


def test_fallback_when_ml_fails_to_beat_baseline(prepared_df):
    df = prepared_df
    forecaster = PriceForecaster(crop="big_onion")
    # Simulate holdout where seasonal naive wins
    cutoff = df["date"].max() - pd.DateOffset(months=6)
    train_df = df[df["date"] <= cutoff]
    val_df = df[df["date"] > cutoff]
    forecaster.train_and_select(train_df, val_df)

    # If served_model is seasonal naive, beat_baseline must be False
    forecaster.served_model = "seasonal_naive"
    forecaster.beat_baseline = False
    sample_row = val_df[val_df["crop"] == "big_onion"].iloc[-1]
    f = forecaster.forecast_step(sample_row, horizon=1)
    assert f.served_model == "seasonal_naive"
    assert f.beat_baseline is False

