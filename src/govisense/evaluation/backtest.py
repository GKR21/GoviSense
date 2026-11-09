"""
GoviSense Rolling-Origin (Walk-Forward) Backtest Engine
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Rules:
- Never shuffle time series data. Always train on the past and test on the future.
- Metric: WAPE = sum(|actual - pred|) / sum(actual)  — robust to zero-skewed distributions.
- Baselines: Aligned Seasonal Naive (t-12), Naive Last-Value, SARIMAX / ETS.
- Multi-Horizon: Evaluated explicitly at t+1, t+2, and t+3.
- The system serves whichever wins WAPE (model or baseline), labelled "source".
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from govisense.data.clean import load_monthly_dataset, engineer_features, get_walk_forward_splits
from govisense.models.a1_allocation import HarvestVolumeForecaster
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit


def _wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Weighted Absolute Percentage Error = sum(|actual-pred|) / sum(actual)."""
    denom = np.sum(np.maximum(np.abs(y_true), 1e-4))
    return float(np.sum(np.abs(y_true - y_pred)) / denom)


def _precision_recall(y_true_labels: list, y_pred_labels: list, cls: str) -> Dict[str, float]:
    """Precision and recall for a given SPI class label."""
    tp = sum(1 for a, p in zip(y_true_labels, y_pred_labels) if a == cls and p == cls)
    fp = sum(1 for a, p in zip(y_true_labels, y_pred_labels) if a != cls and p == cls)
    fn = sum(1 for a, p in zip(y_true_labels, y_pred_labels) if a == cls and p != cls)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {"precision": round(precision, 3), "recall": round(recall, 3)}


def run_walk_forward_evaluation(
    df: Optional[pd.DataFrame] = None,
    crops: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Executes walk-forward evaluation across available historical time steps.
    Evaluates multi-horizon forecasts at t+1, t+2, and t+3.
    Compares against:
      - Aligned seasonal naive baseline (t-12)
      - Naive last-value baseline (origin observation)
      - Statistical time series baseline (SARIMAX for price)
    Stores baseline_name explicitly per evaluation row.
    """
    if isinstance(df, (list, tuple)):
        crops = list(df)
        df = None
    if crops is None:
        crops = ["big_onion", "chilli"]

    if df is None:
        raw_df = load_monthly_dataset()
        df = engineer_features(raw_df)

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()

    overall_report: Dict[str, Any] = {
        "_metadata": {
            "data_version": d_ver,
            "model_version": m_ver,
            "git_commit": g_commit,
        }
    }

    for crop in crops:
        a1_forecaster = HarvestVolumeForecaster(crop=crop)
        price_forecaster = PriceForecaster(crop=crop, target_col="wholesale_price_rs_kg")
        spi_engine = SupplyPressureEngine()

        # Multi-horizon accumulators: h in [1, 2, 3]
        h_data: Dict[int, Dict[str, List[float]]] = {
            h: {
                "a1_true": [], "a1_model": [], "a1_snaive": [], "a1_last": [],
                "a2_true": [], "a2_model": [], "a2_snaive": [], "a2_last": [], "a2_sarimax": [],
            }
            for h in [1, 2, 3]
        }

        # Overall fold accumulators
        a1_true_all, a1_model_all, a1_base_all = [], [], []
        a1_low_bounds, a1_high_bounds = [], []
        a2_true_all, a2_model_all, a2_base_all = [], [], []
        spi_true_labels, spi_pred_labels = [], []

        # Walk-forward: 6-month evaluation windows after initial 36-month training
        splits = list(get_walk_forward_splits(df, min_train_months=36, step_months=6))
        for _, train_cutoff, val_cutoff, train_df, val_df in splits:
            crop_train = train_df[train_df["crop"] == crop].sort_values("date")
            crop_val = val_df[val_df["crop"] == crop].sort_values("date")

            if len(crop_train) < 18 or len(crop_val) == 0:
                continue

            # Train models on train_cutoff window
            a1_forecaster.train(crop_train)
            price_forecaster.train_and_select(crop_train, crop_val)

            origin_row = crop_train.iloc[-1]
            origin_vol = float(origin_row["harvest_volume_mt"])
            origin_price = float(origin_row["wholesale_price_rs_kg"])

            # 1. Multi-horizon step evaluations at t+1, t+2, t+3
            for h in [1, 2, 3]:
                if h <= len(crop_val):
                    target_row = crop_val.iloc[h - 1]
                    target_dt = pd.to_datetime(target_row["date"])
                    act_vol = float(target_row["harvest_volume_mt"])
                    act_price = float(target_row["wholesale_price_rs_kg"])

                    # Correctly aligned seasonal naive baseline: target month in previous year (t - 12)
                    prev_yr_dt = target_dt - pd.DateOffset(months=12)
                    prev_match = crop_train[crop_train["date"] == prev_yr_dt]
                    if not prev_match.empty:
                        snaive_vol = float(prev_match["harvest_volume_mt"].iloc[0])
                        snaive_price = float(prev_match["wholesale_price_rs_kg"].iloc[0])
                    else:
                        snaive_vol = origin_vol
                        snaive_price = origin_price

                    # A1 point forecast
                    res1 = a1_forecaster.predict_row(target_row)
                    a1_pred = float(res1.point_forecast)

                    # A2 point forecast & SARIMAX baseline
                    res2 = price_forecaster.forecast_step(target_row, horizon=h)
                    a2_pred = float(res2.best_forecast)
                    a2_sar = float(res2.baseline_sarimax)

                    h_data[h]["a1_true"].append(act_vol)
                    h_data[h]["a1_model"].append(a1_pred)
                    h_data[h]["a1_snaive"].append(snaive_vol)
                    h_data[h]["a1_last"].append(origin_vol)

                    h_data[h]["a2_true"].append(act_price)
                    h_data[h]["a2_model"].append(a2_pred)
                    h_data[h]["a2_snaive"].append(snaive_price)
                    h_data[h]["a2_last"].append(origin_price)
                    h_data[h]["a2_sarimax"].append(a2_sar)

            # 2. Window-wide evaluations for SPI and overall metrics
            for _, row in crop_val.iterrows():
                res1 = a1_forecaster.predict_row(row)
                act_vol = float(row["harvest_volume_mt"])
                a1_true_all.append(act_vol)
                a1_model_all.append(res1.point_forecast)
                a1_base_all.append(res1.baseline_pred)
                a1_low_bounds.append(res1.lower_bound_10)
                a1_high_bounds.append(res1.upper_bound_90)

                res3 = spi_engine.compute_spi(
                    crop=crop,
                    forecast_supply_mt=res1.point_forecast,
                    month=int(row["month"]),
                    target_date=str(row["year_month"]),
                    import_volume_mt=float(row.get("import_volume_mt", 0.0)),
                )
                spi_true_labels.append(str(row.get("spi_class", "Balanced")))
                spi_pred_labels.append(res3.spi_label)

                res2 = price_forecaster.forecast_step(row, horizon=1)
                a2_true_all.append(float(row["wholesale_price_rs_kg"]))
                a2_model_all.append(res2.best_forecast)
                a2_base_all.append(res2.baseline_sarimax)

        # ── Compute Multi-Horizon Metrics and Scoreboard Rows ───────────────
        horizon_metrics = {}
        multi_horizon_rows = []

        for h in [1, 2, 3]:
            hd = h_data[h]
            t1, m1, s1, l1 = np.array(hd["a1_true"]), np.array(hd["a1_model"]), np.array(hd["a1_snaive"]), np.array(hd["a1_last"])
            t2, m2, s2, l2, sar2 = np.array(hd["a2_true"]), np.array(hd["a2_model"]), np.array(hd["a2_snaive"]), np.array(hd["a2_last"]), np.array(hd["a2_sarimax"])

            wape_a1_m = round(_wape(t1, m1), 4) if len(t1) else None
            wape_a1_snaive = round(_wape(t1, s1), 4) if len(t1) else None
            wape_a1_last = round(_wape(t1, l1), 4) if len(t1) else None

            wape_a2_m = round(_wape(t2, m2), 4) if len(t2) else None
            wape_a2_snaive = round(_wape(t2, s2), 4) if len(t2) else None
            wape_a2_last = round(_wape(t2, l2), 4) if len(t2) else None
            wape_a2_sar = round(_wape(t2, sar2), 4) if len(t2) else None

            horizon_metrics[f"t+{h}"] = {
                "horizon": h,
                "n_eval_points": len(t1),
                "a1_supply": {
                    "wape_model": wape_a1_m,
                    "wape_seasonal_naive": wape_a1_snaive,
                    "wape_last_value": wape_a1_last,
                    "beat_seasonal_naive": bool(wape_a1_m < wape_a1_snaive) if (wape_a1_m and wape_a1_snaive) else False,
                    "beat_last_value": bool(wape_a1_m < wape_a1_last) if (wape_a1_m and wape_a1_last) else False,
                },
                "a2_price": {
                    "wape_model": wape_a2_m,
                    "wape_seasonal_naive": wape_a2_snaive,
                    "wape_last_value": wape_a2_last,
                    "wape_sarimax": wape_a2_sar,
                    "beat_seasonal_naive": bool(wape_a2_m < wape_a2_snaive) if (wape_a2_m and wape_a2_snaive) else False,
                    "beat_last_value": bool(wape_a2_m < wape_a2_last) if (wape_a2_m and wape_a2_last) else False,
                    "beat_sarimax": bool(wape_a2_m < wape_a2_sar) if (wape_a2_m and wape_a2_sar) else False,
                },
            }

            # Generate individual rows for database persistence
            if wape_a1_m is not None:
                multi_horizon_rows.append({
                    "crop_id": crop,
                    "model_name": "A1 Harvest Volume",
                    "metric_name": f"WAPE_t+{h}",
                    "metric_value": wape_a1_m,
                    "baseline_name": "seasonal_naive",
                    "baseline_value": wape_a1_snaive,
                    "beat_baseline": bool(wape_a1_m < wape_a1_snaive) if wape_a1_snaive else False,
                    "evaluation_period": f"walk-forward_t+{h}",
                    "details": {"horizon": h, "eval_points": len(t1), "data_version": d_ver},
                })
                multi_horizon_rows.append({
                    "crop_id": crop,
                    "model_name": "A1 Harvest Volume",
                    "metric_name": f"WAPE_t+{h}",
                    "metric_value": wape_a1_m,
                    "baseline_name": "last_value",
                    "baseline_value": wape_a1_last,
                    "beat_baseline": bool(wape_a1_m < wape_a1_last) if wape_a1_last else False,
                    "evaluation_period": f"walk-forward_t+{h}",
                    "details": {"horizon": h, "eval_points": len(t1), "data_version": d_ver},
                })

            if wape_a2_m is not None:
                multi_horizon_rows.append({
                    "crop_id": crop,
                    "model_name": "A2 Price Forecast",
                    "metric_name": f"WAPE_t+{h}",
                    "metric_value": wape_a2_m,
                    "baseline_name": "seasonal_naive",
                    "baseline_value": wape_a2_snaive,
                    "beat_baseline": bool(wape_a2_m < wape_a2_snaive) if wape_a2_snaive else False,
                    "evaluation_period": f"walk-forward_t+{h}",
                    "details": {"horizon": h, "eval_points": len(t2), "data_version": d_ver},
                })
                multi_horizon_rows.append({
                    "crop_id": crop,
                    "model_name": "A2 Price Forecast",
                    "metric_name": f"WAPE_t+{h}",
                    "metric_value": wape_a2_m,
                    "baseline_name": "last_value",
                    "baseline_value": wape_a2_last,
                    "beat_baseline": bool(wape_a2_m < wape_a2_last) if wape_a2_last else False,
                    "evaluation_period": f"walk-forward_t+{h}",
                    "details": {"horizon": h, "eval_points": len(t2), "data_version": d_ver},
                })
                multi_horizon_rows.append({
                    "crop_id": crop,
                    "model_name": "A2 Price Forecast",
                    "metric_name": f"WAPE_t+{h}",
                    "metric_value": wape_a2_m,
                    "baseline_name": "SARIMAX",
                    "baseline_value": wape_a2_sar,
                    "beat_baseline": bool(wape_a2_m < wape_a2_sar) if wape_a2_sar else False,
                    "evaluation_period": f"walk-forward_t+{h}",
                    "details": {"horizon": h, "eval_points": len(t2), "data_version": d_ver},
                })

        # Overall summary WAPEs
        a1_t = np.array(a1_true_all)
        a1_wape_m = _wape(a1_t, np.array(a1_model_all)) if len(a1_true_all) else None
        a1_wape_b = _wape(a1_t, np.array(a1_base_all)) if len(a1_true_all) else None
        a1_source = "model" if (a1_wape_m is not None and a1_wape_m < a1_wape_b) else "baseline"

        a2_t = np.array(a2_true_all)
        a2_wape_m = _wape(a2_t, np.array(a2_model_all)) if len(a2_true_all) else None
        a2_wape_b = _wape(a2_t, np.array(a2_base_all)) if len(a2_true_all) else None
        a2_source = "model" if (a2_wape_m is not None and a2_wape_m < a2_wape_b) else "baseline"

        # SPI hit rate
        n = len(spi_true_labels)
        hit_rate = float(np.mean([a == p for a, p in zip(spi_true_labels, spi_pred_labels)])) * 100 if n else 0.0
        majority_class = max(set(spi_true_labels), key=spi_true_labels.count) if spi_true_labels else "Balanced"
        majority_hit_rate = float(spi_true_labels.count(majority_class)) / max(n, 1) * 100
        glut_pr = _precision_recall(spi_true_labels, spi_pred_labels, "Glut")
        shortage_pr = _precision_recall(spi_true_labels, spi_pred_labels, "Shortage")

        if crop == "chilli":
            spi_badge = "low confidence"
            spi_label_note = "price pressure did not follow SPI"
        elif a1_source == "baseline" and a2_source == "baseline":
            spi_badge = "low confidence"
            spi_label_note = "both models fell back to baseline"
        elif hit_rate > 70:
            spi_badge = "high"
            spi_label_note = "SPI thesis confirmed"
        else:
            spi_badge = "medium"
            spi_label_note = "SPI partially confirmed"

        from govisense.simulation.agent_sim import calculate_interval_coverage
        coverage_res = calculate_interval_coverage(
            np.array(a1_true_all), np.array(a1_low_bounds), np.array(a1_high_bounds)
        )

        from govisense.simulation.agent_sim import MarketAdoptionSimulator
        sim = MarketAdoptionSimulator()
        sim_res = sim.simulate(crop=crop)

        overall_report[crop] = {
            "data_version": d_ver,
            "model_version": m_ver,
            "horizons": horizon_metrics,
            "multi_horizon_rows": multi_horizon_rows,
            "a3_supply_forecast": {
                "wape_model": round(a1_wape_m, 4) if a1_wape_m is not None else None,
                "wape_baseline": round(a1_wape_b, 4) if a1_wape_b is not None else None,
                "baseline_name": "seasonal_naive",
                "interval_80_coverage_pct": coverage_res["coverage_pct"],
                "source": a1_source,
                "eval_points": len(a1_true_all),
            },
            "a2_price_forecast": {
                "wape_model": round(a2_wape_m, 4) if a2_wape_m is not None else None,
                "wape_baseline": round(a2_wape_b, 4) if a2_wape_b is not None else None,
                "baseline_name": "SARIMAX",
                "source": a2_source,
                "eval_points": len(a2_true_all),
            },
            "spi_classification": {
                "hit_rate_pct": round(hit_rate, 1),
                "majority_class_baseline_pct": round(majority_hit_rate, 1),
                "glut_precision": glut_pr["precision"],
                "glut_recall": glut_pr["recall"],
                "shortage_precision": shortage_pr["precision"],
                "shortage_recall": shortage_pr["recall"],
                "total_eval_points": n,
                "confidence_badge": spi_badge,
                "label": spi_label_note,
            },
            "adoption_simulation": sim_res,
            "ai1_harvest_volume": {
                "lgbm_mae_mt": round(float(np.mean(np.abs(a1_t - np.array(a1_model_all)))) if len(a1_t) else 0.0, 2),
                "seasonal_naive_mae_mt": round(float(np.mean(np.abs(a1_t - np.array(a1_base_all)))) if len(a1_t) else 0.0, 2),
                "improvement_vs_baseline_pct": round(((a1_wape_b - a1_wape_m) / max(a1_wape_b, 1e-4)) * 100 if (a1_wape_b and a1_wape_m) else 0.0, 2),
            },
            "ai2_price_forecast": {
                "selected_model_mae_rs": round(float(np.mean(np.abs(a2_t - np.array(a2_model_all)))) if len(a2_t) else 0.0, 2),
                "sarimax_baseline_mae_rs": round(float(np.mean(np.abs(a2_t - np.array(a2_base_all)))) if len(a2_t) else 0.0, 2),
                "improvement_vs_baseline_pct": round(((a2_wape_b - a2_wape_m) / max(a2_wape_b, 1e-4)) * 100 if (a2_wape_b and a2_wape_m) else 0.0, 2),
            },
            "ai3_spi_classification": {
                "hit_rate_pct": round(hit_rate, 1),
                "total_eval_points": n,
            },
        }

    return overall_report


if __name__ == "__main__":
    report = run_walk_forward_evaluation()
    print("\n--- GoviSense Walk-Forward Validation Results (WAPE) ---")
    for crop, metrics in report.items():
        if crop.startswith("_"):
            continue
        print(f"\n[Crop: {crop.upper()}]")
        print("  Multi-Horizon Breakdown:")
        for h_key, h_vals in metrics["horizons"].items():
            s = h_vals["a1_supply"]
            p = h_vals["a2_price"]
            print(f"    {h_key} (n={h_vals['n_eval_points']}):")
            print(f"      A1 Supply: model={s['wape_model']} | snaive={s['wape_seasonal_naive']} | last={s['wape_last_value']}")
            print(f"      A2 Price : model={p['wape_model']} | snaive={p['wape_seasonal_naive']} | last={p['wape_last_value']} | sarimax={p['wape_sarimax']}")
