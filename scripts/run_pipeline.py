"""
GoviSense End-to-End Pipeline Runner
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Executes:
1. Feature Engineering & Historical Data Integrity Check
2. AI 3 Supply Pressure Index Thesis Validation
3. Rolling-Origin Walk-Forward Model Evaluation
4. Forward Horizon Prediction (AI 1, AI 2, AI 3)
5. AI 4 Gap-Filling Decision Optimization
"""

import sys
import json
import pickle
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from govisense.config import settings, MODELS_STORE_DIR, PROCESSED_DATA_DIR
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a1_allocation import HarvestVolumeForecaster
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.models.a4_gap_deadline import GapFillingOptimizer
from govisense.evaluation.backtest import run_walk_forward_evaluation


def main():
    print("=" * 70)
    print("🌾 GOVISENSE AI PIPELINE – PILOT ANURADHAPURA (BIG ONION & CHILLI)")
    print("   Team DARKBITE · ModelX 2.0 Phase 1")
    print("=" * 70)

    # 1. Load and Engineer Features
    print("\n[Step 1/5] Loading monthly grid & engineering causal lag features...")
    raw_df = load_monthly_dataset()
    df = engineer_features(raw_df)
    print(f"Loaded {len(df)} records spanning {df['date'].min().strftime('%Y-%m')} to {df['date'].max().strftime('%Y-%m')}.")
    
    # 2. AI 3 Thesis Validation
    print("\n[Step 2/5] Validating AI 3 Supply Pressure Index (SPI) economic correlation...")
    spi_engine = SupplyPressureEngine()
    thesis_results = spi_engine.validate_historical_alignment(df)
    for crop, t in thesis_results.items():
        print(f"  • {crop.upper()}:")
        print(f"    - SPI vs Next Month Price Change Correlation: {t['spi_vs_next_month_price_change_corr']} (Expected < -0.20)")
        print(f"    - Directional Hit Rate: {t['overall_direction_hit_rate_pct']}%")
        print(f"    - Core Thesis Confirmed: {'✅ PASS' if t['thesis_confirmed'] else '⚠️ TUNE'}")

    # 3. Walk-Forward Rolling Origin Evaluation
    print("\n[Step 3/5] Running Rolling-Origin Walk-Forward Validation (Train past -> Test future)...")
    eval_report = run_walk_forward_evaluation(["big_onion", "chilli"])
    for crop, metrics in eval_report.items():
        print(f"\n  📊 Performance Summary for {crop.upper()}:")
        a1 = metrics["ai1_harvest_volume"]
        print(f"    AI 1 Harvest Volume: LightGBM MAE={a1['lgbm_mae_mt']} MT vs Seasonal-Naive={a1['seasonal_naive_mae_mt']} MT (Beat baseline by {a1['improvement_vs_baseline_pct']}%)")
        a2 = metrics["ai2_price_forecast"]
        print(f"    AI 2 Price Forecast: Selected MAE=Rs {a2['selected_model_mae_rs']}/kg vs SARIMAX={a2['sarimax_baseline_mae_rs']}/kg (Beat baseline by {a2['improvement_vs_baseline_pct']}%)")
        a3 = metrics["ai3_spi_classification"]
        print(f"    AI 3 SPI Hit Rate: {a3['hit_rate_pct']}% out-of-sample accuracy")

    # 4. Train on Full Data & Generate Next-Period Forecasts
    print("\n[Step 4/5] Training production models and generating forward forecasts...")
    upcoming_spi_results = []
    trained_artifacts = {}

    for crop in ["big_onion", "chilli"]:
        a1 = HarvestVolumeForecaster(crop=crop)
        a1.train(df)
        
        # Train AI 2
        cutoff_date = df["date"].max() - pd.DateOffset(months=6)
        train_split = df[df["date"] <= cutoff_date]
        val_split = df[df["date"] > cutoff_date]
        
        a2 = PriceForecaster(crop=crop, target_col="wholesale_price_rs_kg")
        a2.train_and_select(train_split, val_split)

        # Generate forecast for the latest available month
        latest_row = df[df["crop"] == crop].sort_values("date").iloc[-1]
        
        # AI 1 Forecast
        vol_res = a1.predict_row(latest_row)
        
        # AI 3 SPI Calculation
        spi_res = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=vol_res.point_forecast,
            month=int(latest_row["month"]),
            target_date="Next Month",
            import_volume_mt=latest_row.get("import_volume_mt", 0.0)
        )
        upcoming_spi_results.append(spi_res)

        # AI 2 Price Forecast
        price_res = a2.forecast_step(latest_row, horizon=1)

        print(f"\n  🎯 [{crop.upper()}] Forward Forecast:")
        print(f"     • Supply (AI 1): {vol_res.point_forecast} MT [80% CI: {vol_res.lower_bound_10} – {vol_res.upper_bound_90} MT]")
        print(f"     • Demand: {spi_res.projected_demand_mt} MT | Gap: {spi_res.gap_mt} MT")
        print(f"     • SPI Score (AI 3): {spi_res.spi_score} -> Label: [{spi_res.spi_label.upper()}]")
        print(f"     • Price (AI 2): Rs {price_res.best_forecast}/kg [CI: Rs {price_res.lower_bound} – Rs {price_res.upper_bound}] | Direction: {price_res.direction.upper()}")

        # Save artifacts
        crop_store = MODELS_STORE_DIR / crop
        crop_store.mkdir(parents=True, exist_ok=True)
        with open(crop_store / "a1_harvest_forecaster.pkl", "wb") as f_a1:
            pickle.dump(a1, f_a1)
        with open(crop_store / "a2_price_forecaster.pkl", "wb") as f_a2:
            pickle.dump(a2, f_a2)

    # 5. AI 4 Gap-Filling Recommendation Optimizer
    print("\n[Step 5/5] Running AI 4 Gap-Filling Linear Optimization...")
    optimizer = GapFillingOptimizer()
    opt_output = optimizer.optimize_recommendations(upcoming_spi_results, target_season="Upcoming Season")

    print(f"  Solver Status: {opt_output['solver_status']}")
    print("  📋 Policy & Farmer Recommendations:")
    for act in opt_output["actions"]:
        print(f"     • Crop: {act.crop}")
        print(f"       Action: {act.action_type} ({act.quantity} {act.unit})")
        print(f"       Timeline: {act.target_timeline}")
        print(f"       Policy Rationale: {act.rationale}")
        print(f"       Farmer Fair Floor: Rs {act.fair_farmgate_floor_rs_kg}/kg\n")

    # Save summary report
    summary_path = ROOT_DIR / "docs" / "pipeline_run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump({
            "thesis_validation": thesis_results,
            "walk_forward_evaluation": eval_report,
            "status": "SUCCESS"
        }, f, indent=2)

    print(f"Pipeline executed successfully. Evaluation report saved to: {summary_path}")
    print("=" * 70)


if __name__ == "__main__":
    import pandas as pd
    main()
