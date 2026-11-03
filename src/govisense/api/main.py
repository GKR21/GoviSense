"""
GoviSense FastAPI Backend Server
Provides REST endpoints for AI 1 (Harvest Forecast), AI 2 (Price Forecast),
AI 3 (Supply Pressure Index), and AI 4 (Gap-Filling Optimization).
Also provides WP2 endpoints: /api/farmer/top3 (farmer crop recommendation).
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
from govisense.models.a4_gap_deadline import GapFillingOptimizer, FarmerAllocationOptimizer
from govisense.models.demand_estimator import DemandEstimator
from govisense.models.suitability_scorer import SuitabilityScorer
from govisense.models.target_area import TargetAreaCalculator

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
farmer_optimizer = FarmerAllocationOptimizer()
demand_estimator = DemandEstimator()
suitability_scorer = SuitabilityScorer()
target_area_calc = TargetAreaCalculator()
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


# ---------------------------------------------------------------------------
# Item 6 – Farmer Top-3 Comparison Endpoint
# ---------------------------------------------------------------------------

@app.get("/api/farmer/top3")
def farmer_top3(
    farmer_id: str = Query(..., description="Pseudonymous farmer identifier"),
    season: str = Query("Maha", description="Season: 'Maha' or 'Yala'"),
    land_ha: float = Query(3.0, description="Farmer's available land in hectares"),
    current_month: int = Query(10, description="Current calendar month (1-12)"),
    is_rainfed: bool = Query(False, description="Whether the farm area is rainfed (no irrigation)"),
    annual_rainfall_mm: float = Query(1100.0, description="Mean annual rainfall at site (mm)"),
    avg_temp_c: float = Query(28.0, description="Mean growing-season temperature (°C)"),
    soil_ph: Optional[float] = Query(None, description="Site soil pH (omit if unknown)"),
    zone: str = Query("dry", description="Agro-climatic zone: 'dry', 'intermediate', or 'wet'"),
):
    """
    Returns the top-3 recommended crops for a given farmer plus contextual
    metadata for each crop: fit_score, profit_range (P10–P90 price),
    risk_level, water_need, planting_window, harvest_period,
    spi_band_at_harvest, and confidence_badge.

    The endpoint uses:
    - SuitabilityScorer (WP2) for fit scores and hard filtering
    - DemandEstimator (WP1) for demand context
    - SPI engine for supply pressure at harvest
    - A2 price forecaster for profit range (if model is loaded)
    - TargetAreaCalculator for area recommendations
    """
    area_conditions = {
        "current_month": current_month,
        "is_rainfed": is_rainfed,
        "annual_rainfall_mm": annual_rainfall_mm,
        "avg_temp_c": avg_temp_c,
        "soil_ph": soil_ph,
        "zone": zone,
    }

    # Get suitability ranking for all crops
    ranking = suitability_scorer.rank_crops(area_conditions)

    if not ranking:
        return {
            "farmer_id": farmer_id,
            "season": season,
            "message": "No suitable crops found for the given area conditions.",
            "top3": [],
        }

    top3_results = []
    for scored_crop in ranking[:3]:
        crop_id = scored_crop.crop_id
        fit_score = scored_crop.score_0_100
        confidence_badge = scored_crop.confidence

        # Load crop requirements for this crop
        try:
            from govisense.data.crop_requirements import get_crop_requirements
            all_reqs = get_crop_requirements()
            req = all_reqs.get(crop_id)
        except Exception:
            req = None

        # Demand context
        demand_month = current_month
        try:
            dem_result = demand_estimator.estimate(crop_id, demand_month, scenario="mid")
            demand_info = {
                "monthly_demand_mt": dem_result.demand_mt,
                "seasonal_factor": dem_result.seasonal_factor,
            }
        except Exception:
            demand_info = {}

        # SPI at harvest (approx harvest = planting + duration)
        harvest_month = ((current_month + (req.duration_months if req else 3) - 1) % 12) + 1
        try:
            spi_harvest = spi_engine.compute_spi(
                crop=crop_id if crop_id in ("big_onion", "chilli") else "big_onion",
                forecast_supply_mt=1000.0,  # placeholder; real supply from AI 1
                month=harvest_month,
                target_date=f"Month {harvest_month}",
            )
            spi_band = spi_harvest.spi_label
        except Exception:
            spi_band = "Unknown"

        # Price range from A2 model (if available, else use config floor + margin)
        cfg = settings.crops.get(crop_id) or settings.crops.get(
            "chilli" if "chilli" in crop_id else "big_onion"
        )
        if cfg and a2_models.get(
            "chilli" if "chilli" in crop_id else
            "big_onion" if "onion" in crop_id else crop_id
        ):
            model_key = "chilli" if "chilli" in crop_id else "big_onion"
            a2 = a2_models[model_key]
            floor = cfg.min_fair_farmgate_price
            p10 = round(floor * 0.85, 0)
            p90 = round(a2.last_known_price * 1.30, 0)
            profit_range = {"p10_rs_kg": p10, "p90_rs_kg": p90}
        elif cfg:
            floor = cfg.min_fair_farmgate_price
            profit_range = {
                "p10_rs_kg": round(floor * 0.85, 0),
                "p90_rs_kg": round(floor * 1.60, 0),
            }
        else:
            profit_range = {"p10_rs_kg": None, "p90_rs_kg": None}

        # Risk level based on SPI + fit score
        if fit_score >= 75 and spi_band != "Shortage":
            risk_level = "Low"
        elif fit_score >= 55:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Target area for this farmer's land allocation
        if req:
            try:
                ta = target_area_calc.compute(
                    crop=crop_id,
                    season=season,
                    demand_mt=demand_info.get("monthly_demand_mt", 5000) * 4,
                    yield_mid=req.yield_mid_mt_ha,
                    loss_pct=req.loss_pct,
                    buffer=0.05,
                    a_reported=0.0,
                    suitable_land_ha=land_ha,
                )
                rec_ha = min(ta.a_rec_ha, land_ha)
            except Exception:
                rec_ha = round(land_ha * 0.5, 1)
        else:
            rec_ha = round(land_ha * 0.5, 1)

        top3_results.append({
            "rank": len(top3_results) + 1,
            "crop_id": crop_id,
            "crop_name": scored_crop.crop_name,
            "fit_score": fit_score,
            "confidence_badge": confidence_badge,
            "profit_range_rs_kg": profit_range,
            "risk_level": risk_level,
            "water_need_mm_season": req.water_mm_season if req else None,
            "planting_window": (
                f"Month {req.plant_start_month}–{req.plant_end_month}" if req else "N/A"
            ),
            "harvest_period": f"Month {harvest_month} (approx)",
            "duration_months": req.duration_months if req else None,
            "spi_band_at_harvest": spi_band,
            "recommended_ha": rec_ha,
            "demand_context": demand_info,
            "suitability_reasons": scored_crop.reasons,
        })

    return {
        "farmer_id": farmer_id,
        "season": season,
        "area_conditions": area_conditions,
        "top3": top3_results,
    }
