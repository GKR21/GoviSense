"""
Test F1: Leakage Elimination
Verifies that rolling and lag features in clean.py use only data available
at the forecast origin (strictly prior to target month).
Mutating the target month's actual rainfall, temperature, price, or harvest volume
must NOT change any input feature or the model prediction for that month.
"""

import pytest
import numpy as np
import pandas as pd
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a1_allocation import HarvestVolumeForecaster


def test_leakage_weather_and_actuals():
    raw_df = load_monthly_dataset()
    onion_raw = raw_df[raw_df["crop"] == "big_onion"].sort_values("date").copy()
    
    # Target month: 2024-08 (last index or specific row)
    target_idx = onion_raw[onion_raw["year_month"] == "2024-08"].index[0]
    
    # 1. Base engineered features
    df_base = engineer_features(onion_raw)
    target_row_base = df_base[df_base["year_month"] == "2024-08"].iloc[0]
    
    # 2. Mutated raw dataframe: drastically change target month's weather, price, and harvest
    onion_mutated = onion_raw.copy()
    onion_mutated.loc[target_idx, "rainfall_anomaly_mm"] = 999.0
    onion_mutated.loc[target_idx, "temp_anomaly_celsius"] = -50.0
    onion_mutated.loc[target_idx, "wholesale_price_rs_kg"] = 9999.0
    onion_mutated.loc[target_idx, "harvest_volume_mt"] = 88888.0
    
    df_mutated = engineer_features(onion_mutated)
    target_row_mutated = df_mutated[df_mutated["year_month"] == "2024-08"].iloc[0]
    
    # Check that rolling weather features at target month are IDENTICAL
    assert target_row_base["rainfall_anomaly_3m_mean"] == target_row_mutated["rainfall_anomaly_3m_mean"], (
        f"Leakage detected! Base: {target_row_base['rainfall_anomaly_3m_mean']}, "
        f"Mutated: {target_row_mutated['rainfall_anomaly_3m_mean']}"
    )
    assert target_row_base["temp_anomaly_3m_mean"] == target_row_mutated["temp_anomaly_3m_mean"], (
        f"Leakage detected! Base: {target_row_base['temp_anomaly_3m_mean']}, "
        f"Mutated: {target_row_mutated['temp_anomaly_3m_mean']}"
    )
    
    # Train forecaster on data prior to 2024-08
    train_slice = df_base[df_base["date"] < "2024-08-01"].copy()
    
    # Price model
    a2 = PriceForecaster(crop="big_onion")
    a2.train_and_select(train_slice, train_slice.tail(6))
    pred_base = a2.forecast_step(target_row_base, horizon=1)
    pred_mutated = a2.forecast_step(target_row_mutated, horizon=1)
    
    assert pred_base.best_forecast == pred_mutated.best_forecast, (
        f"Price forecast leaked target value! Base: {pred_base.best_forecast}, "
        f"Mutated: {pred_mutated.best_forecast}"
    )
    
    # A1 harvest model
    a1 = HarvestVolumeForecaster(crop="big_onion")
    a1.train(train_slice)
    a1_base = a1.predict_row(target_row_base)
    a1_mutated = a1.predict_row(target_row_mutated)
    
    assert a1_base.point_forecast == a1_mutated.point_forecast, (
        f"A1 harvest forecast leaked target value! Base: {a1_base.point_forecast}, "
        f"Mutated: {a1_mutated.point_forecast}"
    )

