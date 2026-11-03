"""
GoviSense End-to-End Pipeline Runner
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Executes:
1. Feature Engineering & Historical Data Integrity Check
2. A3 SPI Thesis Validation (historical alignment)
3. Rolling-Origin Walk-Forward Model Evaluation (WAPE)
4. Forward Horizon Prediction — next calendar month (A3, A2, SPI)
5. A4 Gap-Filling Decision Optimization

Naming convention (aligned with work packages):
  A3 Supply Forecast  = harvest volume model (was AI 1)
  A2 Price Forecast   = price model (was AI 2)
  SPI inside A3       = supply pressure index (was AI 3)
  A4 + A1 Allocation  = gap optimizer + farmer allocation (was AI 4)
"""

import sys
import json
import pickle
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

# Suppress statsmodels ConvergenceWarning in pipeline output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*converge.*")

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from govisense.config import settings, MODELS_STORE_DIR, PROCESSED_DATA_DIR
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a1_allocation import HarvestVolumeForecaster, safe_forecast
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.models.a4_gap_deadline import GapFillingOptimizer
from govisense.evaluation.backtest import run_walk_forward_evaluation


def _build_next_month_row(df: pd.DataFrame, crop: str) -> pd.Series:
    """
    Construct a synthetic feature row for the NEXT calendar month after the
    last historical observation. Lags are filled from the most recent values
    so the model receives plausible input instead of NaN.
    """
    crop_df = df[df["crop"] == crop].sort_values("date").copy()
    last = crop_df.iloc[-1].copy()
    next_date = last["date"] + pd.DateOffset(months=1)
    month = next_date.month
    quarter = (month - 1) // 3 + 1

    row = last.copy()
    row["date"] = next_date
    row["year_month"] = next_date.strftime("%Y-%m")
    row["month"] = month
    row["quarter"] = quarter
    row["year"] = next_date.year

    # Calendar features
    row["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    row["month_cos"] = np.cos(2 * np.pi * month / 12.0)
    row["is_festival_season"] = int(month in [4, 12])

    # Shift lag features forward by one month
    # (harvest_volume_lag1 for next month = current month's actual value)
    row["harvest_volume_lag1"] = float(last.get("harvest_volume_mt", last.get("harvest_volume_lag1", 0.0)))
    # harvest_volume_lag12 stays the same (12 months ago = same month last year)
    # planted_extent shifts: lag2 ← lag3, lag3 ← last actual planted_extent
    row["planted_extent_lag2"] = float(last.get("planted_extent_lag3", last.get("planted_extent_ha", 0.0)))
    row["planted_extent_lag3"] = float(last.get("planted_extent_ha", last.get("planted_extent_lag3", 0.0)))

    # Rolling weather: carry forward last value (best available for near-term forecast)
    # harvest_volume_mt is unknown for next month — remove it so it isn't used as target leak
    row["harvest_volume_mt"] = np.nan

    return row


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

    # 2. A3 SPI Thesis Validation
    print("\n[Step 2/5] Validating SPI economic correlation (historical alignment)...")
    spi_engine = SupplyPressureEngine()
    thesis_results = spi_engine.validate_historical_alignment(df)
    for crop, t in thesis_results.items():
        badge = "✅ PASS" if t["thesis_confirmed"] else "⚠️  LOW CONFIDENCE"
        print(f"  • {crop.upper()}:")
        print(f"    - SPI vs Next Month Price Change Correlation: {t['spi_vs_next_month_price_change_corr']} (Expected < -0.20)")
        print(f"    - Directional Hit Rate: {t['overall_direction_hit_rate_pct']}%")
        print(f"    - Core Thesis: {badge}")

    # 3. Walk-Forward Rolling Origin Evaluation (WAPE)
    print("\n[Step 3/5] Running Rolling-Origin Walk-Forward Validation (WAPE metric)...")
    eval_report = run_walk_forward_evaluation(["big_onion", "chilli"])
    print()
    print(f"  {'Crop':<12} {'Metric':<25} {'Model WAPE':>12} {'Baseline WAPE':>14} {'Serving':>10}")
    print(f"  {'-'*75}")
    for crop, metrics in eval_report.items():
        a3 = metrics["a3_supply_forecast"]
        a2 = metrics["a2_price_forecast"]
        spi = metrics["spi_classification"]
        print(f"  {crop.upper():<12} {'A3 Supply Forecast':<25} {str(a3['wape_model']):>12} {str(a3['wape_baseline']):>14} {a3['source'].upper():>10}")
        print(f"  {'':<12} {'A2 Price Forecast':<25} {str(a2['wape_model']):>12} {str(a2['wape_baseline']):>14} {a2['source'].upper():>10}")
        print(f"  {'':<12} {'SPI hit / P_glut / R_short':<25} {spi['hit_rate_pct']}% / {spi['glut_precision']} / {spi['shortage_recall']}  badge={spi['confidence_badge'].upper()} ({spi.get('label', '')})")
        print()

    # 4. Train on Full Data & Generate Next-Period Forecasts
    print("\n[Step 4/5] Training production models and generating NEXT-MONTH forecasts...")
    upcoming_spi_results = []

    for crop in ["big_onion", "chilli"]:
        # Train A3 supply forecaster (AI 1)
        a1 = HarvestVolumeForecaster(crop=crop)
        a1.train(df)

        # Set use_model from walk-forward WAPE result
        a3_metrics = eval_report.get(crop, {}).get("a3_supply_forecast", {})
        wape_m = a3_metrics.get("wape_model")
        wape_b = a3_metrics.get("wape_baseline")
        if wape_m is not None and wape_b is not None:
            a1.use_model = wape_m < wape_b

        # Train A2 price forecaster
        cutoff_date = df["date"].max() - pd.DateOffset(months=6)
        train_split = df[df["date"] <= cutoff_date]
        val_split = df[df["date"] > cutoff_date]
        a2 = PriceForecaster(crop=crop, target_col="wholesale_price_rs_kg")
        a2.train_and_select(train_split, val_split)

        # Build NEXT-MONTH feature row (avoids forecasting current month = last known data)
        next_row = _build_next_month_row(df, crop)

        # A3 Supply Forecast for next month
        vol_res = a1.predict_row(next_row)

        # Guardrail: if output still invalid, fall back to seasonal profile
        month = int(next_row["month"])
        seasonal_profile = a1.seasonal_mean_by_month.get(month)
        safe_vol, supply_source = safe_forecast(vol_res.point_forecast, vol_res.baseline_pred, seasonal_profile)
        vol_res.point_forecast = safe_vol
        vol_res.forecast_source = supply_source

        # SPI calculation using safe supply
        spi_res = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=vol_res.point_forecast,
            month=month,
            target_date=next_row["year_month"],
            import_volume_mt=float(next_row.get("import_volume_mt", 0.0)),
        )
        upcoming_spi_results.append(spi_res)

        # A2 Price Forecast for next month
        price_res = a2.forecast_step(next_row, horizon=1)

        print(f"\n  🎯 [{crop.upper()}] Forward Forecast → {next_row['year_month']}")
        print(f"     • Supply (A3): {vol_res.point_forecast:,.1f} MT  [80% CI: {vol_res.lower_bound_10:,.1f} – {vol_res.upper_bound_90:,.1f} MT]  source={supply_source}")
        print(f"     • Demand:      {spi_res.projected_demand_mt:,.1f} MT  |  Gap: {spi_res.gap_mt:,.1f} MT")
        print(f"     • SPI (A3):    {spi_res.spi_score:+.3f}  →  Label: [{spi_res.spi_label.upper()}]")
        print(f"     • Price (A2):  Rs {price_res.best_forecast}/kg  [CI: Rs {price_res.lower_bound}–{price_res.upper_bound}]  direction={price_res.direction.upper()}  source={a2.winner}")

        # Save trained artifacts
        crop_store = MODELS_STORE_DIR / crop
        crop_store.mkdir(parents=True, exist_ok=True)
        with open(crop_store / "a1_harvest_forecaster.pkl", "wb") as f_a1:
            pickle.dump(a1, f_a1)
        with open(crop_store / "a2_price_forecaster.pkl", "wb") as f_a2:
            pickle.dump(a2, f_a2)

    # 5. A4 Gap-Filling Recommendation Optimizer
    print("\n[Step 5/5] Running A4 Gap-Filling Linear Optimization...")
    optimizer = GapFillingOptimizer()
    opt_output = optimizer.optimize_recommendations(upcoming_spi_results, target_season="Upcoming Season")

    print(f"  Solver Status: {opt_output['solver_status']}")
    print("  📋 Policy & Farmer Recommendations:")
    for act in opt_output["actions"]:
        print(f"     • Crop: {act.crop}")
        print(f"       Action: {act.action_type} ({act.quantity} {act.unit})")
        print(f"       Timeline: {act.target_timeline}")
        print(f"       Rationale: {act.rationale}")
        print(f"       Fair Floor: Rs {act.fair_farmgate_floor_rs_kg}/kg\n")

    # Save summary report
    summary_path = ROOT_DIR / "docs" / "pipeline_run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(
            {
                "thesis_validation": thesis_results,
                "walk_forward_evaluation": eval_report,
                "status": "SUCCESS",
            },
            f,
            indent=2,
        )

    print(f"\nPipeline executed successfully. Evaluation report saved to: {summary_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
