"""
AI 1 – Harvest Volume Forecast
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Models:
1. Baseline: Seasonal-Naive (y_t = y_{t-12})
2. Primary Model: LightGBM Regressor with lag & seasonal features + Quantile prediction intervals (10%, 50%, 90%)
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ForecastResult:
    crop: str
    target_date: str
    baseline_pred: float
    point_forecast: float
    lower_bound_10: float
    upper_bound_90: float
    actual_volume: float = None


class HarvestVolumeForecaster:
    def __init__(self, crop: str):
        self.crop = crop
        self.features = [
            "month_sin", "month_cos", "quarter",
            "planted_extent_lag3", "planted_extent_lag2",
            "yield_rolling_6m",
            "rainfall_anomaly_3m_mean", "temp_anomaly_3m_mean",
            "harvest_volume_lag1", "harvest_volume_lag12"
        ]
        self.models = {}  # "point", "lower", "upper"
        self.is_trained = False

    def train(self, train_df: pd.DataFrame):
        crop_train = train_df[train_df["crop"] == self.crop].dropna(subset=self.features + ["harvest_volume_mt"])
        
        X = crop_train[self.features]
        y = crop_train["harvest_volume_mt"]

        if len(X) < 12:
            raise ValueError(f"Insufficient training samples for crop {self.crop}: {len(X)}")

        dtrain = lgb.Dataset(X, label=y, free_raw_data=False)

        # 1. Median / Point Regressor (Huber or L2)
        params_point = {
            "objective": "regression",
            "metric": "mae",
            "learning_rate": 0.05,
            "max_depth": 4,
            "num_leaves": 15,
            "verbose": -1,
            "seed": 42
        }
        self.models["point"] = lgb.train(params_point, dtrain, num_boost_round=80)

        # 2. Quantile 10% (Lower bound)
        params_lower = {
            "objective": "quantile",
            "alpha": 0.10,
            "learning_rate": 0.05,
            "max_depth": 4,
            "num_leaves": 15,
            "verbose": -1,
            "seed": 42
        }
        self.models["lower"] = lgb.train(params_lower, dtrain, num_boost_round=80)

        # 3. Quantile 90% (Upper bound)
        params_upper = {
            "objective": "quantile",
            "alpha": 0.90,
            "learning_rate": 0.05,
            "max_depth": 4,
            "num_leaves": 15,
            "verbose": -1,
            "seed": 42
        }
        self.models["upper"] = lgb.train(params_upper, dtrain, num_boost_round=80)

        self.is_trained = True

    def predict_row(self, row: pd.Series) -> ForecastResult:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")

        X_row = pd.DataFrame([row[self.features]])
        
        # Seasonal Naive baseline (value from 12 months ago)
        baseline = float(row.get("harvest_volume_lag12", row.get("harvest_volume_lag1", 0.0)))
        if np.isnan(baseline) or baseline <= 0:
            baseline = float(row.get("harvest_volume_lag1", 1000.0))

        point_pred = float(self.models["point"].predict(X_row)[0])
        lower_pred = float(self.models["lower"].predict(X_row)[0])
        upper_pred = float(self.models["upper"].predict(X_row)[0])

        # Enforce physical constraints (volume >= 0, lower <= point <= upper)
        point_pred = max(0.0, point_pred)
        lower_pred = max(0.0, min(lower_pred, point_pred))
        upper_pred = max(point_pred, upper_pred)

        actual = float(row["harvest_volume_mt"]) if "harvest_volume_mt" in row and pd.notna(row["harvest_volume_mt"]) else None

        return ForecastResult(
            crop=self.crop,
            target_date=str(row.get("year_month", row.get("date", "Unknown"))),
            baseline_pred=round(baseline, 1),
            point_forecast=round(point_pred, 1),
            lower_bound_10=round(lower_pred, 1),
            upper_bound_90=round(upper_pred, 1),
            actual_volume=round(actual, 1) if actual is not None else None
        )

    def evaluate_test_set(self, test_df: pd.DataFrame) -> Dict[str, float]:
        crop_test = test_df[test_df["crop"] == self.crop].dropna(subset=self.features + ["harvest_volume_mt"])
        if len(crop_test) == 0:
            return {"mae_model": 0.0, "mae_baseline": 0.0, "mape_model": 0.0, "mape_baseline": 0.0}

        y_true = crop_test["harvest_volume_mt"].values
        y_pred = []
        y_base = []

        for _, row in crop_test.iterrows():
            res = self.predict_row(row)
            y_pred.append(res.point_forecast)
            y_base.append(res.baseline_pred)

        y_pred = np.array(y_pred)
        y_base = np.array(y_base)

        mae_model = float(np.mean(np.abs(y_true - y_pred)))
        mae_base = float(np.mean(np.abs(y_true - y_base)))
        mape_model = float(np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-4))) * 100)
        mape_base = float(np.mean(np.abs((y_true - y_base) / np.maximum(y_true, 1e-4))) * 100)

        return {
            "crop": self.crop,
            "test_samples": len(crop_test),
            "mae_model": round(mae_model, 2),
            "mae_baseline": round(mae_base, 2),
            "mape_model": round(mape_model, 2),
            "mape_baseline": round(mape_base, 2),
            "improvement_pct": round(((mae_base - mae_model) / max(mae_base, 1e-4)) * 100, 2)
        }
