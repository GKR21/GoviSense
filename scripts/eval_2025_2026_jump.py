import pandas as pd
import numpy as np
from govisense.models.a2_price_forecast import PriceForecaster

def evaluate_jump_period():
    df_prices = pd.read_csv("data/processed/monthly_prices_cbsl.csv")
    df_prices["date"] = pd.to_datetime(df_prices["date"])
    
    print("=" * 80)
    print("2.5: 2025 TO 2026 PRICE JUMP EVALUATION (2025-01 TO 2026-10)")
    print("=" * 80)
    
    for crop in ["big_onion", "chilli"]:
        print(f"\n--- Crop: {crop.upper()} ---")
        col = "big_onion_imp_wholesale_pettah" if crop == "big_onion" else "green_chilli_wholesale_pettah"
        
        # Prepare series
        sub = df_prices[["year_month", "date", "year", "month", col]].dropna().copy()
        sub["wholesale_price_rs_kg"] = sub[col]
        sub["crop"] = crop
        
        # Lags
        sub["wholesale_price_lag1"] = sub["wholesale_price_rs_kg"].shift(1)
        sub["wholesale_price_lag2"] = sub["wholesale_price_rs_kg"].shift(2)
        sub["wholesale_price_lag3"] = sub["wholesale_price_rs_kg"].shift(3)
        sub["wholesale_price_lag12"] = sub["wholesale_price_rs_kg"].shift(12)
        sub["wholesale_rolling_3m_mean"] = sub["wholesale_price_rs_kg"].shift(1).rolling(3, min_periods=1).mean()
        sub["month_sin"] = np.sin(2 * np.pi * sub["month"] / 12.0)
        sub["month_cos"] = np.cos(2 * np.pi * sub["month"] / 12.0)
        sub["quarter"] = sub["date"].dt.quarter
        sub["is_festival_season"] = sub["month"].isin([4, 12]).astype(int)
        sub["rainfall_anomaly_3m_mean"] = 0.0
        sub["local_vs_import_gap"] = 0.0
        sub["retail_price_lag1"] = sub["wholesale_price_lag1"] * 1.2
        
        # Train on pre-2025, evaluate on 2025-2026
        train_data = sub[sub["year_month"] < "2025-01"].dropna(subset=["wholesale_price_lag12", "wholesale_price_rs_kg"]).copy()
        eval_data = sub[sub["year_month"] >= "2025-01"].copy()
        
        forecaster = PriceForecaster(crop=crop, use_real_features_only=True)
        forecaster.train_and_select(train_data, eval_data.iloc[:4])
        
        actuals = []
        preds_model = []
        preds_snaive = []
        preds_last = []
        
        for _, row in eval_data.iterrows():
            act = float(row["wholesale_price_rs_kg"])
            res = forecaster.forecast_step(row, horizon=1)
            pred_m = float(res.best_forecast)
            
            snaive = float(row["wholesale_price_lag12"]) if pd.notna(row["wholesale_price_lag12"]) else float(row["wholesale_price_lag1"])
            last = float(row["wholesale_price_lag1"]) if pd.notna(row["wholesale_price_lag1"]) else act
            
            actuals.append(act)
            preds_model.append(pred_m)
            preds_snaive.append(snaive)
            preds_last.append(last)
            
        y_t = np.array(actuals)
        y_m = np.array(preds_model)
        y_s = np.array(preds_snaive)
        y_l = np.array(preds_last)
        
        denom = np.sum(y_t)
        wape_m = np.sum(np.abs(y_t - y_m)) / denom
        wape_s = np.sum(np.abs(y_t - y_s)) / denom
        wape_l = np.sum(np.abs(y_t - y_l)) / denom
        
        mae_m = np.mean(np.abs(y_t - y_m))
        mae_s = np.mean(np.abs(y_t - y_s))
        mae_l = np.mean(np.abs(y_t - y_l))
        
        print(f"Evaluation Window: 2025-01 to 2026-10 (N={len(y_t)} months)")
        print(f"  Model WAPE:          {wape_m:7.4f} | MAE: {mae_m:6.2f} Rs/kg")
        print(f"  Seasonal Naive WAPE: {wape_s:7.4f} | MAE: {mae_s:6.2f} Rs/kg")
        print(f"  Last Value WAPE:     {wape_l:7.4f} | MAE: {mae_l:6.2f} Rs/kg")
        print(f"  Stronger baseline:   {'Seasonal Naive' if wape_s < wape_l else 'Last Value'}")
        print(f"  Latest actual price: {y_t[-1]:6.2f} Rs/kg ({eval_data.iloc[-1]['year_month']})")
        print(f"  Latest model forecast: {y_m[-1]:6.2f} Rs/kg | Abs Diff: {abs(y_m[-1] - y_t[-1]):5.2f} Rs/kg")

if __name__ == "__main__":
    evaluate_jump_period()
