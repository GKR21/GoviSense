import pandas as pd
import numpy as np
import pytest
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a2_price_forecast import PriceForecaster, get_cbsl_retail_margin_stats

def test_price_forecaster_p50_moves_with_latest_price():
    """
    Test: raise the latest price by 100 Rs/kg and require P50 to move upwards.
    """
    df = load_monthly_dataset()
    feat_df = engineer_features(df)
    crop_df = feat_df[feat_df["crop"] == "big_onion"].sort_values("date").reset_index(drop=True)
    
    train_df = crop_df.iloc[:-6].copy()
    val_df = crop_df.iloc[-6:].copy()
    
    forecaster = PriceForecaster(crop="big_onion", use_real_features_only=True)
    forecaster.train_and_select(train_df, val_df)
    
    # Baseline forecast with original latest row
    target_row = val_df.iloc[-1].copy()
    orig_res = forecaster.forecast_step(target_row, horizon=1)
    
    # Mutate row: raise latest observed price features by 100 Rs/kg
    mutated_row = target_row.copy()
    mutated_row["wholesale_price_lag1"] = float(target_row["wholesale_price_lag1"]) + 100.0
    mutated_row["wholesale_price_lag2"] = float(target_row["wholesale_price_lag2"]) + 100.0
    mutated_row["wholesale_rolling_3m_mean"] = float(target_row["wholesale_rolling_3m_mean"]) + 100.0
    mutated_row["retail_price_lag1"] = float(target_row.get("retail_price_lag1", 150.0)) + 120.0
    mutated_row["local_vs_import_gap"] = float(target_row.get("local_vs_import_gap", 0.0)) + 100.0
    mutated_res = forecaster.forecast_step(mutated_row, horizon=1)
    
    assert mutated_res.p50_forecast > orig_res.p50_forecast, (
        f"P50 did not increase when lag price raised by 100: "
        f"orig={orig_res.p50_forecast}, mutated={mutated_res.p50_forecast}"
    )


def test_serve_stronger_baseline_when_ml_fails():
    """
    Verify that if LightGBM WAPE exceeds the stronger baseline WAPE,
    served_model is set to that baseline and beat_baseline is False.
    """
    df = load_monthly_dataset()
    feat_df = engineer_features(df)
    crop_df = feat_df[feat_df["crop"] == "big_onion"].sort_values("date").reset_index(drop=True)
    
    train_df = crop_df.iloc[:-4].copy()
    val_df = crop_df.iloc[-4:].copy()
    
    forecaster = PriceForecaster(crop="big_onion", use_real_features_only=True)
    forecaster.train_and_select(train_df, val_df)
    
    # If beat_baseline is False, served_model must equal best_baseline
    if not forecaster.beat_baseline:
        assert forecaster.served_model == forecaster.best_baseline
        assert forecaster.source == "baseline"


def test_dynamic_retail_margin_stats():
    """
    Asserts retail margin stats are computed dynamically from monthly_prices_cbsl.csv
    with empirical band and sample size n.
    """
    stats_onion = get_cbsl_retail_margin_stats("big_onion")
    assert stats_onion["n"] == 12
    assert 1.10 <= stats_onion["median"] <= 1.35
    assert stats_onion["p10"] < stats_onion["p90"]
    assert stats_onion["method"] == "12m_cbsl_median_ratio"
    
    stats_chilli = get_cbsl_retail_margin_stats("chilli")
    assert stats_chilli["n"] == 12
    assert 1.05 <= stats_chilli["median"] <= 1.30
