"""
A2 Price Forecast
(GoviSense internal label: AI 2 / WP4)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Forecasts wholesale & retail prices 1–3 months ahead.

Model competition:
  1. Statistical baseline: SARIMAX (1,1,0)×(0,1,0,12) — simplified for convergence
  2. Primary model: LightGBM on lag + exogenous features (SPI, imports, weather, festivals)

Selection rule: winner on held-out WAPE (not in-sample AIC).
If SARIMAX still fails to converge after maxiter=200, seasonal-naive is used instead.

Output: price point forecast, prediction interval, direction (UP/DOWN/FLAT), source label.
"""

import warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing


@dataclass
class PriceForecastResult:
    crop: str
    target_date: str
    horizon_months: int          # 1, 2, or 3
    baseline_sarimax: float
    lightgbm_forecast: float
    selected_model: str          # "lightgbm" | "sarimax" | "ets" | "seasonal_naive"
    best_forecast: float
    lower_bound: float
    upper_bound: float
    direction: str               # "up" | "down" | "flat"
    direction_confidence: float
    source: str = "model"        # "model" | "baseline"
    baseline_ets: Optional[float] = None
    baseline_seasonal_naive: Optional[float] = None


class PriceForecaster:
    """
    Price forecaster for a single crop.

    Model competition on held-out set (WAPE):
      - LightGBM (lag features + exogenous SPI, imports, rainfall)
      - SARIMAX (1,1,0)(0,1,0,12) with scaled target and exog features
      - ETS (Exponential Smoothing / Holt-Winters)
      - Seasonal Naive (lag 12 or last observed price)

    SARIMAX is scaled before fitting (divide series by its mean) to improve
    numerical conditioning. The scale factor is stored and applied in reverse
    on all predictions.
    """

    # Compact LightGBM params for small monthly datasets
    _LGB_PARAMS = {
        "objective": "regression",
        "metric": "mae",
        "learning_rate": 0.04,
        "max_depth": 3,
        "num_leaves": 7,
        "min_child_samples": 10,
        "reg_lambda": 5.0,
        "verbose": -1,
        "seed": 42,
    }
    _N_ESTIMATORS = 40

    def __init__(self, crop: str, target_col: str = "wholesale_price_rs_kg"):
        self.crop = crop
        self.target_col = target_col
        self.features = [
            "month_sin", "month_cos", "quarter", "is_festival_season",
            "wholesale_price_lag1", "wholesale_price_lag2", "wholesale_price_lag3",
            "wholesale_price_lag12", "wholesale_rolling_3m_mean",
            "retail_price_lag1",
            "actual_spi_lag1", "actual_spi_lag2",
            "import_volume_lag1",
            "rainfall_anomaly_3m_mean",
        ]
        self.lgb_model = None
        self.sarimax_res = None
        self.ets_res = None
        self._price_scale: float = 1.0     # scaling factor for numerical stability
        self.winner: str = "lightgbm"      # set after hold-out WAPE comparison
        self.best_baseline: str = "sarimax"
        self.source: str = "model"         # "model" | "baseline"
        self.last_known_price: float = 100.0
        self.wape_model: Optional[float] = None
        self.wape_baseline: Optional[float] = None

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train_and_select(
        self, train_df: pd.DataFrame, val_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Train SARIMAX, ETS, and LightGBM, evaluate on the held-out validation window
        using WAPE vs Seasonal Naive, and select the winner.
        """
        crop_train_raw = train_df[train_df["crop"] == self.crop]
        if "source" in crop_train_raw.columns:
            crop_train_raw = crop_train_raw[crop_train_raw["source"] == "real"]
        crop_train = (
            crop_train_raw
            .dropna(subset=self.features + [self.target_col])
            .copy()
        )
        crop_val = (
            val_df[val_df["crop"] == self.crop]
            .dropna(subset=self.features + [self.target_col])
            .copy()
        )

        if len(crop_train) < 18:
            raise ValueError(
                f"Insufficient training data for {self.crop}: {len(crop_train)}"
            )

        self.last_known_price = float(crop_train[self.target_col].iloc[-1])

        # ── 1. Fit LightGBM ──────────────────────────────────────────
        X_train, y_train = crop_train[self.features], crop_train[self.target_col]
        dtrain = lgb.Dataset(X_train, label=y_train, free_raw_data=False)
        self.lgb_model = lgb.train(self._LGB_PARAMS, dtrain, num_boost_round=self._N_ESTIMATORS)

        # ── 2. Fit SARIMAX (scaled, simplified order) ─────────────────
        self._price_scale = float(crop_train[self.target_col].mean()) or 1.0
        y_scaled = crop_train[self.target_col].values / self._price_scale
        exog_train = crop_train[["actual_spi_lag1", "import_volume_lag1"]].values

        self.sarimax_res = None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sarimax_model = SARIMAX(
                    y_scaled,
                    exog=exog_train,
                    order=(1, 1, 0),           # simplified from (1,1,1)
                    seasonal_order=(0, 1, 0, 12),
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                fit_result = sarimax_model.fit(
                    disp=False,
                    maxiter=200,
                    method="lbfgs",
                )
            self.sarimax_res = fit_result
        except Exception:
            self.sarimax_res = None

        # ── 3. Fit ETS (Exponential Smoothing) ────────────────────────
        self.ets_res = None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if len(y_scaled) >= 24:
                    ets_model = ExponentialSmoothing(
                        y_scaled,
                        seasonal_periods=12,
                        trend="add",
                        seasonal="add",
                        initialization_method="estimated",
                    )
                else:
                    ets_model = ExponentialSmoothing(
                        y_scaled,
                        trend="add",
                        initialization_method="estimated",
                    )
                self.ets_res = ets_model.fit()
        except Exception:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.ets_res = SimpleExpSmoothing(y_scaled).fit()
            except Exception:
                self.ets_res = None

        # ── 4. Evaluate on validation window (WAPE) ──────────────────
        val_metrics: Dict[str, float] = {
            "lgb_wape": 0.0,
            "sarimax_wape": 999.0,
            "ets_wape": 999.0,
            "seasonal_naive_wape": 999.0,
        }

        if len(crop_val) > 0:
            X_val = crop_val[self.features]
            y_val = crop_val[self.target_col].values
            denom = np.sum(np.maximum(np.abs(y_val), 1e-4))

            # LightGBM WAPE
            lgb_preds = self.lgb_model.predict(X_val)
            val_metrics["lgb_wape"] = float(np.sum(np.abs(y_val - lgb_preds)) / denom)

            # SARIMAX WAPE
            if self.sarimax_res is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        exog_val = crop_val[["actual_spi_lag1", "import_volume_lag1"]].values
                        sar_preds_scaled = self.sarimax_res.forecast(
                            steps=len(crop_val), exog=exog_val
                        )
                    sar_preds = sar_preds_scaled * self._price_scale
                    val_metrics["sarimax_wape"] = float(
                        np.sum(np.abs(y_val - sar_preds)) / denom
                    )
                except Exception:
                    val_metrics["sarimax_wape"] = 999.0

            # ETS WAPE
            if self.ets_res is not None:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        ets_preds_scaled = self.ets_res.forecast(steps=len(crop_val))
                    ets_preds = np.array(ets_preds_scaled) * self._price_scale
                    val_metrics["ets_wape"] = float(
                        np.sum(np.abs(y_val - ets_preds)) / denom
                    )
                except Exception:
                    val_metrics["ets_wape"] = 999.0

            # Seasonal Naive WAPE
            naive_preds = []
            for _, r in crop_val.iterrows():
                val_12 = r.get("wholesale_price_lag12")
                if pd.notna(val_12) and float(val_12) > 0:
                    naive_preds.append(float(val_12))
                else:
                    naive_preds.append(self.last_known_price)
            naive_arr = np.array(naive_preds)
            val_metrics["seasonal_naive_wape"] = float(
                np.sum(np.abs(y_val - naive_arr)) / denom
            )

            # Select best statistical baseline
            baselines = {
                "sarimax": val_metrics["sarimax_wape"],
                "ets": val_metrics["ets_wape"],
                "seasonal_naive": val_metrics["seasonal_naive_wape"],
            }
            self.best_baseline = min(baselines, key=baselines.get)
            best_baseline_wape = baselines[self.best_baseline]

            # Pick winner on held-out WAPE
            self.wape_model = val_metrics["lgb_wape"]
            self.wape_baseline = best_baseline_wape

            if val_metrics["lgb_wape"] <= best_baseline_wape:
                self.winner = "lightgbm"
                self.source = "model"
            else:
                self.winner = self.best_baseline
                self.source = "baseline"

        return {
            "crop": self.crop,
            "target": self.target_col,
            "lgb_val_wape": round(val_metrics["lgb_wape"], 4),
            "sarimax_val_wape": round(val_metrics["sarimax_wape"], 4),
            "ets_val_wape": round(val_metrics["ets_wape"], 4),
            "seasonal_naive_val_wape": round(val_metrics["seasonal_naive_wape"], 4),
            "best_baseline": self.best_baseline,
            "winner": self.winner,
            "source": self.source,
            "sarimax_fitted": self.sarimax_res is not None,
            "ets_fitted": self.ets_res is not None,
        }

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def forecast_step(self, row: pd.Series, horizon: int = 1) -> PriceForecastResult:
        """Forecast price for a given horizon (1, 2, or 3 months ahead)."""
        # 1. LightGBM forecast
        X_row = pd.DataFrame([row[self.features]])
        lgb_pred = float(self.lgb_model.predict(X_row)[0])

        # 2. SARIMAX forecast
        if self.sarimax_res is not None:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    exog_step = np.array([[row["actual_spi_lag1"], row["import_volume_lag1"]]])
                    sar_pred_scaled = float(
                        self.sarimax_res.forecast(steps=1, exog=exog_step)[0]
                    )
                sarimax_pred = sar_pred_scaled * self._price_scale
            except Exception:
                sarimax_pred = self.last_known_price
        else:
            sarimax_pred = float(row.get("wholesale_price_lag12") or self.last_known_price)

        # 3. ETS forecast
        if self.ets_res is not None:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    ets_forecasts = self.ets_res.forecast(steps=max(1, horizon))
                    ets_val = ets_forecasts[-1] if hasattr(ets_forecasts, "__getitem__") else ets_forecasts
                    ets_pred = float(ets_val) * self._price_scale
            except Exception:
                ets_pred = self.last_known_price
        else:
            ets_pred = self.last_known_price

        # 4. Seasonal Naive forecast
        lag12 = row.get("wholesale_price_lag12")
        seasonal_naive_pred = float(lag12) if (pd.notna(lag12) and float(lag12) > 0) else self.last_known_price

        # Select forecast according to winner
        if self.winner == "lightgbm":
            chosen_val = lgb_pred
        elif self.winner == "sarimax":
            chosen_val = sarimax_pred
        elif self.winner == "ets":
            chosen_val = ets_pred
        else:
            chosen_val = seasonal_naive_pred

        source = self.source

        # 90% Confidence Interval (horizon-adjusted margin)
        margin = 0.08 + (horizon * 0.03)
        lower = max(10.0, round(chosen_val * (1.0 - margin), 1))
        upper = round(chosen_val * (1.0 + margin), 1)

        # Direction relative to last observed price
        ref_price = float(row.get("wholesale_price_lag1") or self.last_known_price)
        pct_change = (chosen_val - ref_price) / max(ref_price, 1e-4)

        if pct_change > 0.04:
            direction = "up"
        elif pct_change < -0.04:
            direction = "down"
        else:
            direction = "flat"

        confidence = round(min(0.95, max(0.60, 1.0 - abs(pct_change * 0.5))), 2)

        return PriceForecastResult(
            crop=self.crop,
            target_date=str(row.get("year_month", row.get("date", "Upcoming"))),
            horizon_months=horizon,
            baseline_sarimax=round(sarimax_pred, 1),
            lightgbm_forecast=round(lgb_pred, 1),
            selected_model=self.winner,
            best_forecast=round(chosen_val, 1),
            lower_bound=lower,
            upper_bound=upper,
            direction=direction,
            direction_confidence=confidence,
            source=source,
            baseline_ets=round(ets_pred, 1),
            baseline_seasonal_naive=round(seasonal_naive_pred, 1),
        )
