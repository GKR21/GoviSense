"""
GoviSense Rolling-Origin (Walk-Forward) Backtest Engine
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Rules:
- Never shuffle time series data. Always train on the past and test on the future.
- Report MAE and MAPE for harvest volume and price forecasts.
- Report SPI directional hit rate (Glut / Balanced / Shortage).
- Compare models against seasonal-naive and last-value baselines.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from govisense.data.clean import load_monthly_dataset, engineer_features, get_walk_forward_splits
from govisense.models.a1_allocation import HarvestVolumeForecaster
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a3_supply_pressure import SupplyPressureEngine


def run_walk_forward_evaluation(crops: List[str] = ["big_onion", "chilli"]) -> Dict[str, Any]:
    """
    Executes walk-forward evaluation across available historical time steps.
    """
    raw_df = load_monthly_dataset()
    df = engineer_features(raw_df)
    
    overall_report = {}
    
    for crop in crops:
        a1_forecaster = HarvestVolumeForecaster(crop=crop)
        price_forecaster = PriceForecaster(crop=crop, target_col="wholesale_price_rs_kg")
        spi_engine = SupplyPressureEngine()
        
        a1_errors_model = []
        a1_errors_base = []
        a2_errors_model = []
        a2_errors_base = []
        spi_hits = []
        
        # Walk-forward 6-month steps after 36 months initial training
        for split_idx, train_cutoff, val_cutoff, train_df, val_df in get_walk_forward_splits(df, min_train_months=36, step_months=6):
            crop_train = train_df[train_df["crop"] == crop].dropna(subset=a1_forecaster.features + ["harvest_volume_mt"])
            crop_val = val_df[val_df["crop"] == crop].dropna(subset=a1_forecaster.features + ["harvest_volume_mt"])
            
            if len(crop_train) < 18 or len(crop_val) == 0:
                continue

            # Train AI 1
            a1_forecaster.train(crop_train)
            
            # Train AI 2
            price_forecaster.train_and_select(crop_train, crop_val)
            
            # Evaluate on validation window
            for _, row in crop_val.iterrows():
                # AI 1
                res1 = a1_forecaster.predict_row(row)
                actual_vol = row["harvest_volume_mt"]
                a1_errors_model.append(abs(actual_vol - res1.point_forecast))
                a1_errors_base.append(abs(actual_vol - res1.baseline_pred))
                
                # AI 3
                res3 = spi_engine.compute_spi(
                    crop=crop,
                    forecast_supply_mt=res1.point_forecast,
                    month=row["month"],
                    target_date=str(row["year_month"]),
                    import_volume_mt=row.get("import_volume_mt", 0.0)
                )
                actual_label = row.get("spi_class", "Balanced")
                spi_hits.append(1 if res3.spi_label == actual_label else 0)
                
                # AI 2
                res2 = price_forecaster.forecast_step(row, horizon=1)
                actual_price = row["wholesale_price_rs_kg"]
                a2_errors_model.append(abs(actual_price - res2.best_forecast))
                a2_errors_base.append(abs(actual_price - res2.baseline_sarimax))

        # Compile metrics for this crop
        a1_mae_m = float(np.mean(a1_errors_model)) if a1_errors_model else 0.0
        a1_mae_b = float(np.mean(a1_errors_base)) if a1_errors_base else 0.0
        a2_mae_m = float(np.mean(a2_errors_model)) if a2_errors_model else 0.0
        a2_mae_b = float(np.mean(a2_errors_base)) if a2_errors_base else 0.0
        spi_hit_rate = float(np.mean(spi_hits) * 100) if spi_hits else 0.0

        overall_report[crop] = {
            "ai1_harvest_volume": {
                "lgbm_mae_mt": round(a1_mae_m, 2),
                "seasonal_naive_mae_mt": round(a1_mae_b, 2),
                "improvement_vs_baseline_pct": round(((a1_mae_b - a1_mae_m) / max(a1_mae_b, 1e-4)) * 100, 2)
            },
            "ai2_price_forecast": {
                "selected_model_mae_rs": round(a2_mae_m, 2),
                "sarimax_baseline_mae_rs": round(a2_mae_b, 2),
                "improvement_vs_baseline_pct": round(((a2_mae_b - a2_mae_m) / max(a2_mae_b, 1e-4)) * 100, 2)
            },
            "ai3_spi_classification": {
                "hit_rate_pct": round(spi_hit_rate, 1),
                "total_eval_points": len(spi_hits)
            }
        }

    return overall_report


if __name__ == "__main__":
    report = run_walk_forward_evaluation()
    print("\n--- GoviSense Walk-Forward Validation Results ---")
    for crop, metrics in report.items():
        print(f"\n[Crop: {crop.upper()}]")
        print(f"  AI 1 Harvest Volume: LightGBM MAE = {metrics['ai1_harvest_volume']['lgbm_mae_mt']} MT vs Baseline = {metrics['ai1_harvest_volume']['seasonal_naive_mae_mt']} MT (Beats baseline by {metrics['ai1_harvest_volume']['improvement_vs_baseline_pct']}%)")
        print(f"  AI 2 Price Forecast: Model MAE = Rs {metrics['ai2_price_forecast']['selected_model_mae_rs']}/kg vs SARIMAX = Rs {metrics['ai2_price_forecast']['sarimax_baseline_mae_rs']}/kg (Beats baseline by {metrics['ai2_price_forecast']['improvement_vs_baseline_pct']}%)")
        print(f"  AI 3 SPI Hit Rate: {metrics['ai3_spi_classification']['hit_rate_pct']}% across {metrics['ai3_spi_classification']['total_eval_points']} out-of-sample periods.")
