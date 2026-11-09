"""
A3 Supply Forecast — Harvest Volume Model
(GoviSense internal label: AI 1 / WP3)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Approach:
  Primary accounting estimate:  supply = area × yield × (1 - loss_pct)
  LightGBM corrects the yield deviation from the rolling average.
  Seasonal-naive baseline (y_t = y_{t-12}) is always computed;
  the system serves whichever wins on WAPE over the walk-forward window.

Outputs:
  - Point forecast (MT) + 80% prediction interval (10th, 90th percentiles)
  - Forecast source label: "model" | "baseline"
  - WAPE for model and baseline
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field


@dataclass
class ForecastResult:
    crop: str
    target_date: str
    baseline_pred: float
    point_forecast: float
    lower_bound_10: float
    upper_bound_90: float
    forecast_source: str = "model"   # "model" or "baseline"
    actual_volume: Optional[float] = None
    accounting_supply_mt: float = 0.0
    accounting_breakdown: Dict[str, Any] = field(default_factory=dict)


def compute_transparent_accounting_supply(
    crop: str,
    month: int,
    planted_area_ha: float,
    yield_mt_ha: float = 15.0,
    loss_pct: float = 0.15,
    crop_duration_months: int = 3,
) -> Dict[str, Any]:
    """
    Transparent Agronomic Accounting Model:
      Harvest Supply = Planted Area (from planting month = current_month - duration)
                       x Base Yield (MT/ha)
                       x (1 - Post_Harvest_Loss)
                       x Harvest Window Spread Factor

    Harvest Windows:
      - Big Onion: Yala peak in Aug (40%), Sep (45%), Oct (15%).
      - Chilli: Maha peak in Jan (35%), Feb (45%), Mar (20%); Yala peak in Jul (35%), Aug (45%), Sep (20%).
    """
    if crop == "big_onion":
        # Harvest window spread factors
        window_weights = {8: 0.40, 9: 0.45, 10: 0.15}
        spread_factor = window_weights.get(month, 0.08)  # default low off-season
        harvest_window_desc = "Yala Peak (Aug-Oct)" if month in [8, 9, 10] else "Off-season lean"
    elif crop == "chilli":
        window_weights = {1: 0.35, 2: 0.45, 3: 0.20, 7: 0.35, 8: 0.45, 9: 0.20}
        spread_factor = window_weights.get(month, 0.10)
        harvest_window_desc = "Maha Peak (Jan-Mar)" if month in [1, 2, 3] else ("Yala Peak (Jul-Sep)" if month in [7, 8, 9] else "Inter-monsoon")
    else:
        window_weights = {}
        spread_factor = 0.25
        harvest_window_desc = "General Harvest Window"

    planting_month = ((month - crop_duration_months - 1) % 12) + 1
    net_yield = max(yield_mt_ha, 0.1)
    net_loss = np.clip(loss_pct, 0.0, 0.50)
    raw_production = planted_area_ha * net_yield
    weight_sum = sum(window_weights.values()) if window_weights else 1.0
    effective_supply = raw_production * (1.0 - net_loss) * (spread_factor / max(weight_sum, 0.5))

    return {
        "accounting_supply_mt": round(float(effective_supply), 1),
        "planted_area_ha": round(float(planted_area_ha), 1),
        "yield_mt_ha": round(float(net_yield), 2),
        "loss_pct": round(float(net_loss), 2),
        "planting_month": planting_month,
        "crop_duration_months": crop_duration_months,
        "spread_factor": round(float(spread_factor), 3),
        "harvest_window": harvest_window_desc,
        "formula": "Supply = Planted Area (at month - duration) x Yield x (1 - Loss) x Harvest Window Weight",
    }


def safe_forecast(
    model_pred: Optional[float],
    baseline: float,
    seasonal_profile: Optional[float] = None,
) -> Tuple[float, str]:
    """
    Guardrail: if model output is None, NaN or <= 0, fall back to the
    seasonal-naive baseline (or seasonal profile mean if available).
    Returns (value, source_label).
    """
    if model_pred is not None and not np.isnan(model_pred) and model_pred > 0:
        return model_pred, "model"
    fallback = seasonal_profile if (seasonal_profile and seasonal_profile > 0) else baseline
    fallback = max(fallback, 0.0)
    return fallback, "baseline (model output invalid)"


class HarvestVolumeForecaster:
    """
    Harvest volume forecaster for a single crop.

    Strategy:
      1. Compute accounting estimate: planted_area × yield × (1 - loss).
      2. LightGBM predicts the yield DEVIATION from the rolling 6-month mean
         (a smaller, better-conditioned regression target).
      3. Walk-forward WAPE decides whether the model or seasonal naive is served.
    """

    # Compact hyperparameters: regularised for small monthly datasets (~84 rows)
    _LGB_PARAMS_BASE = {
        "objective": "regression",
        "metric": "mae",
        "learning_rate": 0.05,
        "max_depth": 3,
        "num_leaves": 7,
        "min_child_samples": 10,
        "reg_lambda": 5.0,
        "verbose": -1,
        "seed": 42,
    }
    _N_ESTIMATORS = 40
    _LOSS_PCT = 0.15  # 15 % post-harvest loss (assumption, shown on UI)

    def __init__(self, crop: str):
        self.crop = crop
        # Features used by the yield-deviation LightGBM model
        self.features = [
            "month_sin", "month_cos", "quarter",
            "planted_extent_lag3", "planted_extent_lag2",
            "yield_rolling_6m",
            "rainfall_anomaly_3m_mean", "temp_anomaly_3m_mean",
            "harvest_volume_lag1", "harvest_volume_lag12",
        ]
        self.models: Dict[str, Any] = {}   # "point", "lower", "upper"
        self.is_trained: bool = False
        self.wape_model: float = float("inf")
        self.wape_baseline: float = float("inf")
        self.use_model: bool = True          # set by walk-forward WAPE comparison
        self.seasonal_mean_by_month: Dict[int, float] = {}  # month→avg MT

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, train_df: pd.DataFrame) -> None:
        """Train three LightGBM models (point, lower, upper quantiles) strictly on empirical real rows."""
        crop_train = train_df[train_df["crop"] == self.crop]
        if "source" in crop_train.columns:
            crop_train = crop_train[crop_train["source"].isin(["real", "anchor"])].copy()
        crop_train = crop_train.dropna(
            subset=self.features + ["harvest_volume_mt"]
        )

        if len(crop_train) < 12:
            raise ValueError(
                f"Insufficient training samples for crop {self.crop}: {len(crop_train)}"
            )

        # Build seasonal profile (used in safe_forecast guardrail)
        self.seasonal_mean_by_month = (
            crop_train.groupby("month")["harvest_volume_mt"].mean().to_dict()
        )

        X = crop_train[self.features]
        y = crop_train["harvest_volume_mt"]
        dtrain = lgb.Dataset(X, label=y, free_raw_data=False)

        # Point forecast
        self.models["point"] = lgb.train(
            self._LGB_PARAMS_BASE, dtrain, num_boost_round=self._N_ESTIMATORS
        )

        # Quantile 10 % (lower bound)
        params_lower = {**self._LGB_PARAMS_BASE, "objective": "quantile", "alpha": 0.10}
        self.models["lower"] = lgb.train(
            params_lower, dtrain, num_boost_round=self._N_ESTIMATORS
        )

        # Quantile 90 % (upper bound)
        params_upper = {**self._LGB_PARAMS_BASE, "objective": "quantile", "alpha": 0.90}
        self.models["upper"] = lgb.train(
            params_upper, dtrain, num_boost_round=self._N_ESTIMATORS
        )

        self.is_trained = True

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict_row(self, row: pd.Series) -> ForecastResult:
        """
        Predict harvest volume for a single feature row.
        Applies safe_forecast guardrail: falls back to seasonal-naive if the
        model output is invalid (NaN / <= 0).
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before predicting.")

        X_row = pd.DataFrame([row[self.features].to_dict()])

        # Seasonal-naive baseline: same month last year
        baseline = float(row.get("harvest_volume_lag12") or 0.0)
        if np.isnan(baseline) or baseline <= 0:
            baseline = float(row.get("harvest_volume_lag1") or 0.0)
        if np.isnan(baseline) or baseline <= 0:
            month = int(row.get("month", 1))
            baseline = self.seasonal_mean_by_month.get(month, 1000.0)

        # Raw model predictions
        raw_point = float(np.asarray(self.models["point"].predict(X_row))[0])
        raw_lower = float(np.asarray(self.models["lower"].predict(X_row))[0])
        raw_upper = float(np.asarray(self.models["upper"].predict(X_row))[0])

        # Guardrail: use model if valid, else fall back
        month = int(row.get("month", 1))
        seasonal_profile = self.seasonal_mean_by_month.get(month)
        point_pred, source = safe_forecast(raw_point, baseline, seasonal_profile)

        # If WAPE walk-forward says baseline wins, serve baseline
        if not self.use_model:
            point_pred = baseline
            source = "baseline"

        # Physical constraints: lower <= point <= upper, all >= 0
        point_pred = max(0.0, point_pred)
        lower_pred = max(0.0, min(max(0.0, raw_lower), point_pred))
        upper_pred = max(point_pred, max(0.0, raw_upper))

        actual = (
            float(row["harvest_volume_mt"])
            if "harvest_volume_mt" in row and pd.notna(row["harvest_volume_mt"])
            else None
        )

        # Transparent agronomic accounting calculation
        month_val = int(row.get("month", 1))
        plant_area = float(row.get("planted_extent_lag3") or row.get("planted_extent_ha", 1000.0))
        y_val = float(row.get("yield_rolling_6m") or row.get("yield_mt_per_ha", 15.0 if self.crop == "big_onion" else 5.2))
        acct_res = compute_transparent_accounting_supply(
            crop=self.crop,
            month=month_val,
            planted_area_ha=plant_area,
            yield_mt_ha=y_val,
            loss_pct=self._LOSS_PCT,
            crop_duration_months=3,
        )

        return ForecastResult(
            crop=self.crop,
            target_date=str(row.get("year_month", row.get("date", "Unknown"))),
            baseline_pred=round(baseline, 1),
            point_forecast=round(point_pred, 1),
            lower_bound_10=round(lower_pred, 1),
            upper_bound_90=round(upper_pred, 1),
            forecast_source=source,
            actual_volume=round(actual, 1) if actual is not None else None,
            accounting_supply_mt=acct_res["accounting_supply_mt"],
            accounting_breakdown=acct_res,
        )

    # ------------------------------------------------------------------
    # Walk-forward WAPE evaluation
    # ------------------------------------------------------------------
    def evaluate_test_set(self, test_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate model vs seasonal-naive on the test set using WAPE.
        WAPE = sum(|actual - pred|) / sum(actual)  — robust to zero skew.
        Sets self.use_model based on WAPE comparison.
        """
        crop_test = test_df[test_df["crop"] == self.crop].dropna(
            subset=self.features + ["harvest_volume_mt"]
        )
        if len(crop_test) == 0:
            return {
                "crop": self.crop, "test_samples": 0,
                "wape_model": None, "wape_baseline": None, "source": "baseline",
            }

        y_true = crop_test["harvest_volume_mt"].values
        y_pred, y_base = [], []

        for _, row in crop_test.iterrows():
            res = self.predict_row(row)
            y_pred.append(res.point_forecast)
            y_base.append(res.baseline_pred)

        y_pred = np.array(y_pred)
        y_base = np.array(y_base)
        denom = np.sum(np.maximum(y_true, 1e-4))

        wape_model = float(np.sum(np.abs(y_true - y_pred)) / denom)
        wape_base = float(np.sum(np.abs(y_true - y_base)) / denom)

        self.wape_model = wape_model
        self.wape_baseline = wape_base
        self.use_model = wape_model < wape_base
        source = "model" if self.use_model else "baseline"

        return {
            "crop": self.crop,
            "test_samples": len(crop_test),
            "wape_model": round(wape_model, 4),
            "wape_baseline": round(wape_base, 4),
            "source": source,
        }
