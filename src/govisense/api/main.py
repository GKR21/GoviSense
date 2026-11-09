"""
GoviSense FastAPI Backend Server
Provides REST endpoints for AI 1 (Harvest Forecast), AI 2 (Price Forecast),
AI 3 (Supply Pressure Index), and AI 4 (Gap-Filling Optimization).
Also provides WP2 endpoints: /api/farmer/top3 (farmer crop recommendation).
"""

from fastapi import FastAPI, Query, Depends
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
from govisense.feedback.planting_reports import PlantingReportStore, PlantingReport
from govisense.db.history import DecisionHistoryStore, DecisionRecord, evaluate_confidence_badge
from govisense.simulation.agent_sim import MarketAdoptionSimulator, calculate_interval_coverage
from govisense.api.auth import router as auth_router, require_farmer, require_officer

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

# Authentication & RBAC Router
app.include_router(auth_router)

# Global in-memory cache for models and data
cached_df: Optional[pd.DataFrame] = None
spi_engine = SupplyPressureEngine()
optimizer = GapFillingOptimizer()
farmer_optimizer = FarmerAllocationOptimizer()
demand_estimator = DemandEstimator()
suitability_scorer = SuitabilityScorer()
target_area_calc = TargetAreaCalculator()
report_store = PlantingReportStore()
history_store = DecisionHistoryStore()
adoption_sim = MarketAdoptionSimulator()
a1_models: Dict[str, HarvestVolumeForecaster] = {}
a2_models: Dict[str, PriceForecaster] = {}


from govisense.db.session import init_db

@app.on_event("startup")
def load_and_train():
    global cached_df, a1_models, a2_models
    init_db()
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
                "baseline_mt": a1_res.baseline_pred,
                "accounting_supply_mt": a1_res.accounting_supply_mt,
                "accounting_breakdown": a1_res.accounting_breakdown,
            },
            "ai3_supply_pressure_index": {
                "spi_score": spi_res.spi_score,
                "spi_ratio": spi_res.spi_ratio,
                "spi_label": spi_res.spi_label,
                "projected_demand_mt": spi_res.projected_demand_mt,
                "gap_mt": spi_res.gap_mt,
                "action_summary": spi_res.action_summary,
                "scenarios": {
                    k: {
                        "scenario": v.scenario,
                        "supply_mt": v.supply_mt,
                        "demand_mt": v.demand_mt,
                        "gap_mt": v.gap_mt,
                        "spi_ratio": v.spi_ratio,
                        "spi_score": v.spi_score,
                        "spi_label": v.spi_label,
                    }
                    for k, v in spi_res.scenarios.items()
                },
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
                    "fair_farmgate_floor_rs_kg": a.fair_farmgate_floor_rs_kg,
                    "best_case_gap_mt": a.best_case_gap_mt,
                    "mid_case_gap_mt": a.mid_case_gap_mt,
                    "worst_case_gap_mt": a.worst_case_gap_mt,
                    "decision_deadline": a.decision_deadline,
                    "days_until_deadline": a.days_until_deadline,
                    "import_lead_time_weeks": a.import_lead_time_weeks,
                    "policy_option": a.policy_option,
                }
                for a in opt_output["actions"]
            ]
        }
    }


class SimulationRequest(BaseModel):
    crop: str
    custom_planted_extent_ha: Optional[float] = None
    custom_yield_mt_ha: Optional[float] = None
    custom_import_volume_mt: Optional[float] = None
    custom_loss_pct: Optional[float] = None


@app.post("/api/simulate")
def simulate_scenario(req: SimulationRequest):
    """Allows authorities to simulate custom acreage, yield, loss, and import scenarios."""
    crop = req.crop
    if crop not in settings.crops:
        return {"error": f"Invalid crop: {crop}"}

    latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1].copy()

    # Apply what-if area slider
    if req.custom_planted_extent_ha is not None:
        latest_row["planted_extent_lag3"] = req.custom_planted_extent_ha
        latest_row["planted_extent_ha"] = req.custom_planted_extent_ha

    # Apply what-if yield slider
    if req.custom_yield_mt_ha is not None:
        latest_row["yield_rolling_6m"] = req.custom_yield_mt_ha
        latest_row["yield_mt_per_ha"] = req.custom_yield_mt_ha

    a1_res = a1_models[crop].predict_row(latest_row)
    import_vol = req.custom_import_volume_mt if req.custom_import_volume_mt is not None else float(latest_row.get("import_volume_mt", 0.0))
    loss_val = req.custom_loss_pct if req.custom_loss_pct is not None else 0.15

    # If both area and yield were explicitly customized in sandbox, adjust point forecast proportionally
    base_area = float(latest_row.get("planted_extent_lag3") or 1.0)
    base_yield = float(latest_row.get("yield_rolling_6m") or 1.0)
    if req.custom_planted_extent_ha is not None and req.custom_yield_mt_ha is not None:
        sim_supply = req.custom_planted_extent_ha * req.custom_yield_mt_ha * 0.85
    else:
        sim_supply = a1_res.point_forecast

    spi_res = spi_engine.compute_spi(
        crop=crop,
        forecast_supply_mt=sim_supply,
        month=int(latest_row["month"]),
        import_volume_mt=import_vol,
        loss_pct=loss_val,
    )

    scenarios_data = {
        k: {
            "scenario": v.scenario,
            "supply_mt": v.supply_mt,
            "demand_mt": v.demand_mt,
            "gap_mt": v.gap_mt,
            "spi_ratio": v.spi_ratio,
            "spi_score": v.spi_score,
            "spi_label": v.spi_label,
        }
        for k, v in spi_res.scenarios.items()
    }

    return {
        "crop": crop,
        "simulated_supply_mt": round(sim_supply, 1),
        "simulated_spi": spi_res.spi_score,
        "simulated_spi_ratio": spi_res.spi_ratio,
        "simulated_label": spi_res.spi_label,
        "simulated_gap_mt": spi_res.gap_mt,
        "area_ha": req.custom_planted_extent_ha or float(latest_row.get("planted_extent_lag3", 0.0)),
        "yield_mt_ha": req.custom_yield_mt_ha or float(latest_row.get("yield_rolling_6m", 0.0)),
        "loss_pct": loss_val,
        "action_summary": spi_res.action_summary,
        "scenarios": scenarios_data,
    }


# ---------------------------------------------------------------------------
# Item 6 – Farmer Top-3 Comparison Endpoint (Protected: Farmer Role Required)
# ---------------------------------------------------------------------------

@app.get("/api/farmer/top3", dependencies=[Depends(require_farmer)])
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


# ---------------------------------------------------------------------------
# Day 6 Endpoints: Feedback Loop, Confidence Rules, Decision Audit, Simulation
# ---------------------------------------------------------------------------

class PlantingReportPayload(BaseModel):
    crop_id: str
    season: str = "Maha 2025/2026"
    planned_area_ha: float
    actual_area_ha: float
    consent_given: bool
    pseudonymous_id: str
    harvest_outcome_mt: Optional[float] = None
    sale_price_rs_kg: Optional[float] = None
    sale_channel: Optional[str] = None
    notes: Optional[str] = None


class ReTriggerPayload(BaseModel):
    crop_id: str
    season: str = "Maha 2025/2026"
    target_month: int = 4
    suitable_land_ha: Optional[float] = None


class DecisionLogPayload(BaseModel):
    crop_id: str
    season: str = "Maha 2025/2026"
    officer_id: str
    action_type: str
    quantity: float
    unit: str
    rationale: str
    model_version: Optional[str] = "LightGBM-v2.1+HiGHS-LP"
    data_version: Optional[str] = "CBSL-HARTI-DOA-2024.12"
    assumptions: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


@app.post("/api/feedback/planting-report")
def submit_planting_report(payload: PlantingReportPayload):
    """
    Item 7: Ingest actual planting report with consent and pseudonymous ID.
    Replaces planned area with reported area, and captures harvest & sale outcomes.
    """
    try:
        report = PlantingReport(
            crop_id=payload.crop_id,
            season=payload.season,
            planned_area_ha=payload.planned_area_ha,
            actual_area_ha=payload.actual_area_ha,
            consent_given=payload.consent_given,
            pseudonymous_id=payload.pseudonymous_id,
            harvest_outcome_mt=payload.harvest_outcome_mt,
            sale_price_rs_kg=payload.sale_price_rs_kg,
            sale_channel=payload.sale_channel,
            notes=payload.notes,
        )
        return report_store.submit_report(report)
    except ValueError as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/feedback/retrigger")
def retrigger_pipeline(payload: ReTriggerPayload):
    """
    Item 7: Re-trigger SPI and Target Area Calculator (A_rec) using actual
    cumulative reported planting area.
    """
    result = report_store.retrigger_crop(
        crop_id=payload.crop_id,
        season=payload.season,
        target_month=payload.target_month,
        suitable_land_ha=payload.suitable_land_ha,
    )
    from dataclasses import asdict
    return asdict(result)


@app.get("/api/confidence/badge")
def get_confidence_badge(
    crop_id: str = Query("big_onion"),
    data_age_days: int = Query(15),
    area_reported_share: float = Query(0.35),
    soil_ph_available: bool = Query(True),
):
    """
    Item 8: Multi-factor confidence badge evaluation using the 5 operational rules.
    """
    # Look up crop model metrics if trained
    a1 = a1_models.get(crop_id)
    w_model = getattr(a1, "wape_model", 0.15)
    w_base = getattr(a1, "wape_baseline", 0.20)
    spi_val = crop_id != "chilli"  # chilli fails historical thesis correlation

    eval_res = evaluate_confidence_badge(
        crop_id=crop_id,
        data_age_days=data_age_days,
        area_reported_share=area_reported_share,
        model_wape=w_model,
        baseline_wape=w_base,
        spi_validated=spi_val,
        soil_ph_available=soil_ph_available,
    )
    from dataclasses import asdict
    return asdict(eval_res)


@app.post("/api/history/log-action", dependencies=[Depends(require_officer)])
def log_officer_action(payload: DecisionLogPayload):
    """
    Item 8: Save officer action with model version, data version, and assumptions snapshot.
    """
    assump = payload.assumptions or {
        "loss_pct": 0.15,
        "import_lead_time_weeks": 7,
        "spi_bands": [0.8, 1.2],
        "pilot_district_share": 0.50 if payload.crop_id == "big_onion" else 0.40,
        "notes": payload.notes,
    }
    record = DecisionRecord(
        crop_id=payload.crop_id,
        season=payload.season,
        officer_id=payload.officer_id,
        action_type=payload.action_type,
        quantity=payload.quantity,
        unit=payload.unit,
        rationale=payload.rationale,
        model_version=payload.model_version or "LightGBM-v2.1+HiGHS-LP",
        data_version=payload.data_version or "CBSL-HARTI-DOA-2024.12",
        assumptions=assump,
    )
    return history_store.log_decision(record)


@app.get("/api/history/decisions")
def get_decision_history(
    crop_id: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """
    Item 8: Retrieve audit decision log records with model, data, and assumption snapshots.
    """
    eff_crop = str(crop_id) if crop_id is not None and not hasattr(crop_id, "default") else None
    eff_season = str(season) if season is not None and not hasattr(season, "default") else None
    eff_limit = int(limit) if isinstance(limit, int) else 50

    records = history_store.list_decisions(crop_id=eff_crop, season=eff_season, limit=eff_limit)
    from dataclasses import asdict
    return [asdict(r) for r in records]


@app.get("/api/simulation/adoption")
def get_adoption_simulation(
    crop_id: str = Query("big_onion"),
    season_demand_mt: float = Query(26667.0),
    uncoordinated_supply_mt: float = Query(46000.0),
):
    """
    Item 9: Multi-agent market simulation at 0%, 30%, and 60% farmer adoption tiers.
    Explicitly tags data_available: false to distinguish simulation scenarios from live ground adoption.
    """
    return adoption_sim.simulate(
        crop=crop_id,
        season_demand_mt=season_demand_mt,
        uncoordinated_supply_mt=uncoordinated_supply_mt,
    )


@app.get("/api/simulation/adoption-summary")
@app.get("/api/adoption/summary")
def get_adoption_summary(
    crop_id: str = Query("big_onion"),
    season: str = Query("Maha 2025/2026"),
    district: str = Query("Anuradhapura"),
):
    """
    Task 5 (P0): Replaces the hardcoded 64/24/12 adoption counts with an explicit data_available: false response.
    Returns transparent status indicating empirical farmer adoption telemetry is not yet connected.
    """
    return adoption_sim.get_adoption_summary(
        crop=crop_id,
        district=district,
        season=season,
    )

