"""
GoviSense FastAPI Backend Server
Provides REST endpoints for AI 1 (Harvest Forecast), AI 2 (Price Forecast),
AI 3 (Supply Pressure Index), and AI 4 (Gap-Filling Optimization).
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd

from govisense.config import settings
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a1_allocation import HarvestVolumeForecaster
from govisense.models.a2_price_forecast import PriceForecaster
from govisense.models.a3_supply_pressure import SupplyPressureEngine, SPIResult
from govisense.models.a4_gap_deadline import GapFillingOptimizer

app = FastAPI(
    title="GoviSense API",
    description="Agricultural Supply Pressure & Price Forecasting System for Sri Lanka",
    version="1.0.0"
)

# Enable CORS for React frontend (localhost:8443)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory cache for models and data
cached_df: Optional[pd.DataFrame] = None
spi_engine = SupplyPressureEngine()
optimizer = GapFillingOptimizer()
a1_models: Dict[str, HarvestVolumeForecaster] = {}
a2_models: Dict[str, PriceForecaster] = {}


@app.on_event("startup")
def load_and_train():
    global cached_df, a1_models, a2_models
    raw = load_monthly_dataset()
    cached_df = engineer_features(raw)
    
    for crop in ["big_onion", "chilli"]:
        # AI 1
        a1 = HarvestVolumeForecaster(crop=crop)
        a1.train(cached_df)
        a1_models[crop] = a1
        
        # AI 2
        cutoff = cached_df["date"].max() - pd.DateOffset(months=6)
        train_s = cached_df[cached_df["date"] <= cutoff]
        val_s = cached_df[cached_df["date"] > cutoff]
        a2 = PriceForecaster(crop=crop)
        a2.train_and_select(train_s, val_s)
        a2_models[crop] = a2


@app.get("/")
def root():
    return {
        "app": "GoviSense",
        "pilot_district": "Anuradhapura",
        "crops": ["big_onion", "chilli"],
        "status": "online"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "models_loaded": len(a1_models) == 2}


@app.get("/api/forecasts/latest")
def get_latest_forecasts():
    """Returns real-time outputs from AI 1, AI 2, AI 3, and AI 4."""
    results = {}
    spi_list = []

    for crop in ["big_onion", "chilli"]:
        latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1]
        
        # AI 1
        a1_res = a1_models[crop].predict_row(latest_row)
        
        # AI 3
        spi_res = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=a1_res.point_forecast,
            month=int(latest_row["month"]),
            target_date=str(latest_row["year_month"]),
            import_volume_mt=float(latest_row.get("import_volume_mt", 0.0))
        )
        spi_list.append(spi_res)

        # AI 2
        a2_res = a2_models[crop].forecast_step(latest_row, horizon=1)

        results[crop] = {
            "crop": crop,
            "crop_name": settings.crops[crop].name_en,
            "crop_name_si": settings.crops[crop].name_si,
            "target_period": str(latest_row["year_month"]),
            "ai1_harvest_forecast": {
                "point_forecast_mt": a1_res.point_forecast,
                "lower_bound_10_mt": a1_res.lower_bound_10,
                "upper_bound_90_mt": a1_res.upper_bound_90,
                "baseline_mt": a1_res.baseline_pred
            },
            "ai3_supply_pressure_index": {
                "spi_score": spi_res.spi_score,
                "spi_label": spi_res.spi_label,
                "projected_demand_mt": spi_res.projected_demand_mt,
                "gap_mt": spi_res.gap_mt,
                "action_summary": spi_res.action_summary
            },
            "ai2_price_forecast": {
                "wholesale_price_rs_kg": a2_res.best_forecast,
                "lower_bound_rs_kg": a2_res.lower_bound,
                "upper_bound_rs_kg": a2_res.upper_bound,
                "direction": a2_res.direction,
                "confidence": a2_res.direction_confidence
            }
        }

    # AI 4
    opt_output = optimizer.optimize_recommendations(spi_list, target_season="Upcoming Season")

    return {
        "pilot_district": settings.pilot_district,
        "crops": results,
        "ai4_optimization": {
            "solver_status": opt_output["solver_status"],
            "target_season": opt_output["target_season"],
            "recommendations": [
                {
                    "crop": a.crop,
                    "action_type": a.action_type,
                    "quantity": a.quantity,
                    "unit": a.unit,
                    "timeline": a.target_timeline,
                    "rationale": a.rationale,
                    "fair_farmgate_floor_rs_kg": a.fair_farmgate_floor_rs_kg
                }
                for a in opt_output["actions"]
            ]
        }
    }


class SimulationRequest(BaseModel):
    crop: str
    custom_planted_extent_ha: Optional[float] = None
    custom_import_volume_mt: Optional[float] = None


@app.post("/api/simulate")
def simulate_scenario(req: SimulationRequest):
    """Allows authorities to simulate custom acreage or import scenarios."""
    crop = req.crop
    if crop not in settings.crops:
        return {"error": f"Invalid crop: {crop}"}

    latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1].copy()
    if req.custom_planted_extent_ha is not None:
        latest_row["planted_extent_lag3"] = req.custom_planted_extent_ha

    a1_res = a1_models[crop].predict_row(latest_row)
    import_vol = req.custom_import_volume_mt if req.custom_import_volume_mt is not None else float(latest_row.get("import_volume_mt", 0.0))

    spi_res = spi_engine.compute_spi(
        crop=crop,
        forecast_supply_mt=a1_res.point_forecast,
        month=int(latest_row["month"]),
        import_volume_mt=import_vol
    )

    return {
        "crop": crop,
        "simulated_supply_mt": a1_res.point_forecast,
        "simulated_spi": spi_res.spi_score,
        "simulated_label": spi_res.spi_label,
        "action_summary": spi_res.action_summary
    }
