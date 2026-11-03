"""
Tests for Day 4 Fix 3: SARIMAX Convergence & Baseline Competition
"""

import pytest
import pandas as pd
import numpy as np
from govisense.models.a2_price_forecast import PriceForecaster, PriceForecastResult
from govisense.data.clean import load_monthly_dataset, engineer_features


@pytest.fixture(scope="module")
def processed_data():
    raw_df = load_monthly_dataset()
    return engineer_features(raw_df)


def test_price_forecaster_sarimax_convergence_and_scaling(processed_data):
    df = processed_data
    forecaster = PriceForecaster(crop="big_onion", target_col="wholesale_price_rs_kg")

    # Split train/val
    cutoff = df["date"].max() - pd.DateOffset(months=6)
    train_df = df[df["date"] <= cutoff]
    val_df = df[df["date"] > cutoff]

    res = forecaster.train_and_select(train_df, val_df)

    # 1. Price scaling applied (> 1.0)
    assert forecaster._price_scale > 1.0

    # 2. SARIMAX fitted without raising ConvergenceWarning error
    assert res["sarimax_fitted"] is True
    assert forecaster.sarimax_res is not None

    # 3. ETS fitted
    assert res["ets_fitted"] is True
    assert forecaster.ets_res is not None

    # 4. Baselines recorded in result
    assert "sarimax_val_wape" in res
    assert "ets_val_wape" in res
    assert "seasonal_naive_val_wape" in res
    assert res["winner"] in ["lightgbm", "sarimax", "ets", "seasonal_naive"]
    assert res["source"] in ["model", "baseline"]


def test_price_forecaster_forecast_step(processed_data):
    df = processed_data
    forecaster = PriceForecaster(crop="chilli", target_col="wholesale_price_rs_kg")

    cutoff = df["date"].max() - pd.DateOffset(months=6)
    train_df = df[df["date"] <= cutoff]
    val_df = df[df["date"] > cutoff]

    forecaster.train_and_select(train_df, val_df)

    sample_row = val_df[val_df["crop"] == "chilli"].iloc[-1]
    forecast = forecaster.forecast_step(sample_row, horizon=1)

    assert isinstance(forecast, PriceForecastResult)
    assert forecast.crop == "chilli"
    assert forecast.best_forecast > 0
    assert forecast.lower_bound <= forecast.best_forecast <= forecast.upper_bound
    assert forecast.direction in ["up", "down", "flat"]
    assert 0.0 <= forecast.direction_confidence <= 1.0
    assert forecast.source in ["model", "baseline"]
    assert forecast.baseline_sarimax > 0
    assert forecast.baseline_ets is not None
    assert forecast.baseline_seasonal_naive is not None

