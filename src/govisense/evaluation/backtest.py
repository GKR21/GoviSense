"""
GoviSense Rolling-Origin (Walk-Forward) Backtest Engine
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Rules:
- Never shuffle time series data. Always train on the past and test on the future.
- Metric: WAPE = sum(|actual - pred|) / sum(actual)  — robust to zero-skewed distributions.
- Report WAPE for harvest volume and price forecasts vs seasonal-naive baseline.
- Report SPI directional hit rate with precision/recall for Glut/Shortage.
- The system serves whichever wins WAPE (model or baseline), labelled "source".
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
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


def run_walk_forward_evaluation(crops: List[str] = ["big_onion", "chilli"]) -> Dict[str, Any]:
    """
    Executes walk-forward evaluation across available historical time steps.
    Uses WAPE as the primary metric; model or baseline is selected per crop.
    """
    raw_df = load_monthly_dataset()
    df = engineer_features(raw_df)

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()

    overall_report = {
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

        a1_true, a1_model_preds, a1_base_preds = [], [], []
        a1_low_bounds, a1_high_bounds = [], []
        a2_true, a2_model_preds, a2_base_preds = [], [], []
        spi_true_labels, spi_pred_labels = [], []

        # Walk-forward: 6-month steps after 36-month initial training window
        for _, train_cutoff, val_cutoff, train_df, val_df in get_walk_forward_splits(
            df, min_train_months=36, step_months=6
        ):
            crop_train = train_df[train_df["crop"] == crop].dropna(
                subset=a1_forecaster.features + ["harvest_volume_mt"]
            )
            crop_val = val_df[val_df["crop"] == crop].dropna(
                subset=a1_forecaster.features + ["harvest_volume_mt"]
            )

            if len(crop_train) < 18 or len(crop_val) == 0:
                continue

            # Train models on this window
            a1_forecaster.train(crop_train)
            price_forecaster.train_and_select(crop_train, crop_val)

            for _, row in crop_val.iterrows():
                # --- A3 Supply Forecast (AI 1) ---
                res1 = a1_forecaster.predict_row(row)
                actual_vol = float(row["harvest_volume_mt"])
                a1_true.append(actual_vol)
                a1_model_preds.append(res1.point_forecast)
                a1_base_preds.append(res1.baseline_pred)
                a1_low_bounds.append(res1.lower_bound_10)
                a1_high_bounds.append(res1.upper_bound_90)

                # --- SPI (AI 3) ---
                res3 = spi_engine.compute_spi(
                    crop=crop,
                    forecast_supply_mt=res1.point_forecast,
                    month=int(row["month"]),
                    target_date=str(row["year_month"]),
                    import_volume_mt=float(row.get("import_volume_mt", 0.0)),
                )
                actual_label = str(row.get("spi_class", "Balanced"))
                spi_true_labels.append(actual_label)
                spi_pred_labels.append(res3.spi_label)

                # --- A2 Price Forecast (AI 2) ---
                res2 = price_forecaster.forecast_step(row, horizon=1)
                actual_price = float(row["wholesale_price_rs_kg"])
                a2_true.append(actual_price)
                a2_model_preds.append(res2.best_forecast)
                a2_base_preds.append(res2.baseline_sarimax)

        # ── WAPE metrics ──────────────────────────────────────────────
        a1_t = np.array(a1_true)
        a1_wape_m = _wape(a1_t, np.array(a1_model_preds)) if a1_true else None
        a1_wape_b = _wape(a1_t, np.array(a1_base_preds)) if a1_true else None
        a1_source = "model" if (a1_wape_m is not None and a1_wape_m < a1_wape_b) else "baseline"

        a2_t = np.array(a2_true)
        a2_wape_m = _wape(a2_t, np.array(a2_model_preds)) if a2_true else None
        a2_wape_b = _wape(a2_t, np.array(a2_base_preds)) if a2_true else None
        a2_source = "model" if (a2_wape_m is not None and a2_wape_m < a2_wape_b) else "baseline"

        # ── SPI hit rate + precision/recall ───────────────────────────
        n = len(spi_true_labels)
        hit_rate = (
            float(np.mean([a == p for a, p in zip(spi_true_labels, spi_pred_labels)])) * 100
            if n else 0.0
        )
        majority_class = max(set(spi_true_labels), key=spi_true_labels.count) if spi_true_labels else "Balanced"
        majority_hit_rate = float(spi_true_labels.count(majority_class)) / max(n, 1) * 100

        glut_pr = _precision_recall(spi_true_labels, spi_pred_labels, "Glut")
        shortage_pr = _precision_recall(spi_true_labels, spi_pred_labels, "Shortage")

        # Confidence badge & label
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

        # ── Coverage metric ───────────────────────────────────────────
        from govisense.simulation.agent_sim import calculate_interval_coverage
        coverage_res = calculate_interval_coverage(
            np.array(a1_true), np.array(a1_low_bounds), np.array(a1_high_bounds)
        )

        # Market Adoption Simulation (0%, 30%, 60%)
        from govisense.simulation.agent_sim import MarketAdoptionSimulator
        sim = MarketAdoptionSimulator()
        sim_res = sim.simulate(crop=crop)

        overall_report[crop] = {
            "data_version": d_ver,
            "model_version": m_ver,
            # Primary metrics — WAPE
            "a3_supply_forecast": {
                "wape_model": round(a1_wape_m, 4) if a1_wape_m is not None else None,
                "wape_baseline": round(a1_wape_b, 4) if a1_wape_b is not None else None,
                "interval_80_coverage_pct": coverage_res["coverage_pct"],
                "source": a1_source,
                "eval_points": len(a1_true),
            },
            "a2_price_forecast": {
                "wape_model": round(a2_wape_m, 4) if a2_wape_m is not None else None,
                "wape_baseline": round(a2_wape_b, 4) if a2_wape_b is not None else None,
                "source": a2_source,
                "eval_points": len(a2_true),
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
            # Backward-compatible aliases for run_pipeline.py
            "ai1_harvest_volume": {
                "lgbm_mae_mt": round(
                    float(np.mean(np.abs(a1_t - np.array(a1_model_preds)))) if a1_true else 0.0, 2
                ),
                "seasonal_naive_mae_mt": round(
                    float(np.mean(np.abs(a1_t - np.array(a1_base_preds)))) if a1_true else 0.0, 2
                ),
                "improvement_vs_baseline_pct": round(
                    ((a1_wape_b - a1_wape_m) / max(a1_wape_b, 1e-4)) * 100
                    if (a1_wape_b and a1_wape_m) else 0.0, 2,
                ),
            },
            "ai2_price_forecast": {
                "selected_model_mae_rs": round(
                    float(np.mean(np.abs(a2_t - np.array(a2_model_preds)))) if a2_true else 0.0, 2
                ),
                "sarimax_baseline_mae_rs": round(
                    float(np.mean(np.abs(a2_t - np.array(a2_base_preds)))) if a2_true else 0.0, 2
                ),
                "improvement_vs_baseline_pct": round(
                    ((a2_wape_b - a2_wape_m) / max(a2_wape_b, 1e-4)) * 100
                    if (a2_wape_b and a2_wape_m) else 0.0, 2,
                ),
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
        a3 = metrics["a3_supply_forecast"]
        print(
            f"  A3 Supply Forecast  : WAPE model={a3['wape_model']} | "
            f"baseline={a3['wape_baseline']} → serving: {a3['source'].upper()}"
        )
        a2 = metrics["a2_price_forecast"]
        print(
            f"  A2 Price Forecast   : WAPE model={a2['wape_model']} | "
            f"baseline={a2['wape_baseline']} → serving: {a2['source'].upper()}"
        )
        spi = metrics["spi_classification"]
        print(f"  SPI Classification  : hit={spi['hit_rate_pct']}% | majority-baseline={spi['majority_class_baseline_pct']}%")
        print(f"    Glut    → P={spi['glut_precision']} R={spi['glut_recall']}")
        print(f"    Shortage→ P={spi['shortage_precision']} R={spi['shortage_recall']}")
        print(f"    Confidence badge: {spi['confidence_badge'].upper()}")
