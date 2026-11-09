"""
GoviSense FastAPI Backend Server
Provides REST endpoints for AI 1 (Harvest Forecast), AI 2 (Price Forecast),
AI 3 (Supply Pressure Index), and AI 4 (Gap-Filling Optimization).
Also provides WP2 endpoints: /api/farmer/top3 (farmer crop recommendation).
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import pandas as pd
import numpy as np
import math

from govisense.config import settings, HUB_SHARE
from govisense.data.clean import load_monthly_dataset, engineer_features
from govisense.models.a1_allocation import HarvestVolumeForecaster
from govisense.models.a2_price_forecast import PriceForecaster, compute_modeled_retail_price
from govisense.models.a3_supply_pressure import SupplyPressureEngine, SPIResult
from govisense.models.a4_gap_deadline import GapFillingOptimizer, FarmerAllocationOptimizer
from govisense.models.demand_estimator import DemandEstimator
from govisense.models.suitability_scorer import SuitabilityScorer
from govisense.models.target_area import TargetAreaCalculator
from govisense.feedback.planting_reports import PlantingReportStore, PlantingReport
from govisense.db.history import DecisionHistoryStore, DecisionRecord, evaluate_confidence_badge
from govisense.db import (
    init_db,
    get_session,
    get_active_dialect,
    FarmerProfileModel,
    OfficerModel,
    UserModel,
    PipelineRunModel,
    DecisionRecordModel,
    PlantingReportModel,
    HarvestReportModel,
    ForecastSnapshotModel,
    DataCatalogueModel,
    MonthlyDataModel,
    AlertModel,
    AlertStatusModel,
    EvaluationResultModel,
)
from govisense.simulation.agent_sim import MarketAdoptionSimulator, calculate_interval_coverage
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit, compute_dataset_provenance
from govisense.evaluation.backtest import run_walk_forward_evaluation

# Import modular routers
from govisense.api.routes.auth import (
    router as auth_router,
    ensure_seed_users,
    login_user,
    LoginPayload,
)
from govisense.api.routes.alerts import (
    router as alerts_router,
    list_alerts,
    acknowledge_alert,
    AlertAckPayload,
    OfficerNoteRequest,
    AskOfficerRequest,
)
from govisense.api.routes.feedback import (
    router as feedback_router,
    list_ground_reports,
    submit_planting_report,
    submit_harvest_report,
    get_planting_reports,
    retrigger_pipeline,
)
from govisense.api.routes.data import (
    router as data_router,
    list_data_catalogue,
    get_sources_summary,
    get_adoption_summary,
    get_latest_prices,
    get_evaluation_scoreboard,
)
from govisense.api.routes.officer import (
    router as officer_router,
    simulate_scenario,
    list_pipeline_runs,
    get_pipeline_run_detail,
    save_decision_action,
    get_officer_decision_history,
)
from govisense.api.routes.farmer import (
    router as farmer_router,
    farmer_top3_recommendations,
    create_or_update_farmer_profile,
    get_farmer_history,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("govisense.api")


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


def _ensure_models_loaded():
    global cached_df
    if cached_df is None or not a1_models:
        load_and_train()


def load_and_train():
    global cached_df, a1_models, a2_models
    try:
        init_db()
    except Exception:
        pass

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifespan: load models, initialize DB, seed users."""
    load_and_train()
    ensure_seed_users()
    yield


app = FastAPI(
    title="GoviSense API",
    description="Agricultural Supply Pressure & Price Forecasting System for Sri Lanka",
    version="1.0.0",
    lifespan=lifespan,
)

# Configured CORS: explicit allowed origins, no wildcard credential security risk
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(auth_router)
app.include_router(alerts_router)
app.include_router(feedback_router)
app.include_router(data_router)
app.include_router(officer_router)
app.include_router(farmer_router)


@app.get("/")
def root():
    return {
        "app": "GoviSense",
        "pilot_district": "Anuradhapura",
        "crops": ["big_onion", "chilli"],
        "database_dialect": get_active_dialect(),
        "status": "online"
    }


@app.get("/api/health")
def health():
    dialect = get_active_dialect()
    is_fallback = (dialect == "sqlite") and ("postgresql" in str(settings.database_url))
    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()

    data_age_days = 15
    try:
        if cached_df is not None and "date" in cached_df.columns:
            latest_date = pd.to_datetime(cached_df["date"]).max()
            data_age_days = max(1, (datetime.now() - latest_date).days)
    except Exception:
        data_age_days = 15

    return {
        "status": "ok",
        "active_database": dialect,
        "dialect": dialect,
        "is_fallback": is_fallback,
        "data_age_days": data_age_days,
        "data_version": d_ver,
        "model_version": m_ver,
        "git_commit": g_commit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models_loaded": len(a1_models) == 2,
        "database": {
            "status": "connected",
            "dialect": dialect,
            "is_fallback": is_fallback,
            "primary_configured": "postgresql" if "postgresql" in str(settings.database_url) else dialect,
            "url_configured": bool(settings.database_url),
        }
    }


@app.get("/api/forecasts/latest")
def get_latest_forecasts():
    """Returns real-time outputs from AI 1, AI 2, AI 3, and AI 4."""
    _ensure_models_loaded()
    results = {}
    spi_list = []

    for crop in ["big_onion", "chilli"]:
        latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1]
        
        # AI 1
        a1_res = a1_models[crop].predict_row(latest_row)
        
        # Check if there are ground reports submitted for this crop
        rep_area = (
            report_store.get_total_reported_area(crop, "Maha")
            + report_store.get_total_reported_area(crop, "Maha 2025/2026")
            + report_store.get_total_reported_area(crop, "Upcoming")
        )
        if rep_area > 0:
            effective_supply_mt = round(a1_res.point_forecast + (rep_area * 15.0 * 0.85), 1)
        else:
            effective_supply_mt = a1_res.point_forecast

        # AI 3
        spi_res = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=effective_supply_mt,
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
                "confidence": a2_res.direction_confidence,
                "selected_model": getattr(a2_res, "selected_model", "lightgbm"),
                "forecast_source": getattr(a2_res, "source", "model"),
            }
        }

    # AI 4
    opt_output = optimizer.optimize_recommendations(spi_list, target_season="Upcoming Season")
    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    run_id = f"RUN-{g_commit[:7]}"

    # Phase 3.2: Persist pipeline execution and forecast snapshots to database
    db_down = False
    db_error = None
    try:
        with get_session() as session:
            run_rec = session.query(PipelineRunModel).filter(PipelineRunModel.run_id == run_id).first()
            if not run_rec:
                run_rec = PipelineRunModel(
                    run_id=run_id,
                    trigger="scheduled",
                    model_version=m_ver,
                    data_version=d_ver,
                    git_commit=g_commit[:40],
                    assumptions={
                        "loss_pct": 0.15,
                        "import_lead_weeks": 7,
                        "spi_bands": [0.8, 1.2],
                        "cif_colombo": settings.cif_colombo_rs_per_mt,
                    },
                )
                session.add(run_rec)
                session.commit()

            for crop, c_res in results.items():
                target_month = c_res["target_period"]
                snap = (
                    session.query(ForecastSnapshotModel)
                    .filter(
                        ForecastSnapshotModel.run_id == run_id,
                        ForecastSnapshotModel.crop_id == crop,
                        ForecastSnapshotModel.forecast_for_month == target_month,
                    )
                    .first()
                )
                ai1 = c_res["ai1_harvest_forecast"]
                ai3 = c_res["ai3_supply_pressure_index"]
                ai2 = c_res["ai2_price_forecast"]
                w_price = ai2.get("wholesale_price_rs_kg", 150.0)
                r_price = compute_modeled_retail_price(w_price, crop=crop)

                if not snap:
                    snap = ForecastSnapshotModel(
                        run_id=run_id,
                        crop_id=crop,
                        district=settings.pilot_district,
                        season=target_month,
                        forecast_for_month=target_month,
                        horizon_months=1,
                        price_p10=ai2.get("lower_bound_rs_kg"),
                        price_p50=w_price,
                        price_p90=ai2.get("upper_bound_rs_kg"),
                        retail_price_rs_kg=round(r_price, 2),
                        retail_price_method="CBSL-calibrated-margin",
                        supply_low_mt=ai1.get("lower_bound_10_mt"),
                        supply_mid_mt=ai1.get("point_forecast_mt", 0.0),
                        supply_high_mt=ai1.get("upper_bound_90_mt"),
                        demand_mt=ai3.get("projected_demand_mt", 0.0),
                        spi_ratio_low=ai3.get("scenarios", {}).get("low", {}).get("spi_ratio"),
                        spi_ratio_mid=ai3.get("spi_ratio", 1.0),
                        spi_ratio_high=ai3.get("scenarios", {}).get("high", {}).get("spi_ratio"),
                        spi_label=ai3.get("spi_label", "BALANCED"),
                        spi_raw=ai3.get("spi_score", 0.0),
                        gap_best_mt=ai3.get("gap_mt"),
                        gap_worst_mt=ai3.get("gap_mt"),
                        import_lead_weeks=settings.import_lead_time_weeks.get(crop, 7),
                        price_model_used=ai2.get("selected_model", "LightGBM"),
                        supply_model_used="A1-HarvestVolume",
                        confidence_badge="medium",
                        confidence_score=75.0,
                        data_quality="verified",
                        is_demo=False,
                    )
                    session.add(snap)
            session.commit()
    except Exception as e:
        logger.warning("Could not persist forecast snapshots to database: %s", e)
        db_down = True
        db_error = str(e)

    prov_meta = compute_dataset_provenance(cached_df)
    data_quality = "db_unavailable" if db_down else prov_meta["data_quality"]
    db_fallback = True if db_down else prov_meta["db_fallback"]
    notes = f"Database unavailable ({db_error}); forecast served from runtime cache." if db_down else None

    return {
        "run_id": run_id,
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": data_quality,
        "is_demo": prov_meta["is_demo"],
        "db_fallback": db_fallback,
        "notes": notes,
        "served_model": "LightGBM-v2.1",
        "assumptions_ref": "docs/assumptions.md",
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
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
    custom_glut_ratio_threshold: Optional[float] = None
    custom_shortage_ratio_threshold: Optional[float] = None


# Handled via officer_router (@router.post("/api/simulate"))
# @app.post("/api/simulate")
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
        glut_ratio_threshold=req.custom_glut_ratio_threshold,
        shortage_ratio_threshold=req.custom_shortage_ratio_threshold,
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

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    prov_meta = compute_dataset_provenance(cached_df)

    return {
        "crop": crop,
        "simulated_supply_mt": round(sim_supply, 1),
        "simulated_spi": spi_res.spi_score,
        "simulated_spi_ratio": spi_res.spi_ratio,
        "primary_spi_ratio": spi_res.spi_ratio,
        "simulated_label": spi_res.spi_label,
        "primary_spi_label": spi_res.spi_label,
        "simulated_gap_mt": spi_res.gap_mt,
        "area_ha": req.custom_planted_extent_ha or float(latest_row.get("planted_extent_lag3", 0.0)),
        "yield_mt_ha": req.custom_yield_mt_ha or float(latest_row.get("yield_rolling_6m", 0.0)),
        "loss_pct": loss_val,
        "action_summary": spi_res.action_summary,
        "scenarios": scenarios_data,
        "run_id": f"RUN-{g_commit[:7]}",
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": prov_meta["data_quality"],
        "is_demo": prov_meta["is_demo"],
        "db_fallback": prov_meta["db_fallback"],
        "served_model": "LightGBM + Baseline Selector",
        "assumptions_ref": "docs/assumptions.md",
    }


# Farmer top-3 endpoint is registered via farmer_router (src/govisense/api/routes/farmer.py)
# to maintain single source of truth without route shadowing.
farmer_top3 = farmer_top3_recommendations


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


# Handled via feedback_router (@router.post("/api/feedback/planting-report"))
# @app.post("/api/feedback/planting-report")
def submit_planting_report(payload: PlantingReportPayload):
    """
    Item 7: Ingest actual planting report with consent and pseudonymous ID.
    Replaces planned area with reported area, and captures harvest & sale outcomes.
    Generates a NEW run_id and a NEW forecast snapshot per Proposal 2.10.
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
        res = report_store.submit_report(report)

        # Retrigger pipeline with new run_id and new snapshot
        new_run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        retrigger_res = report_store.retrigger_crop(
            crop_id=payload.crop_id,
            season=payload.season,
        )

        try:
            with get_session() as session:
                snap = ForecastSnapshotModel(
                    run_id=new_run_id,
                    crop=payload.crop_id,
                    target_period=payload.season,
                    forecast_supply_mt=float(retrigger_res.total_reported_ha * 15.0 * 0.85),
                    projected_demand_mt=float(retrigger_res.previous_target_ha * 15.0 * 0.85),
                    gap_mt=float(retrigger_res.total_reported_ha * 15.0 * 0.85 - retrigger_res.previous_target_ha * 15.0 * 0.85),
                    spi_score=retrigger_res.new_spi,
                    spi_ratio=float(np.clip(1.0 + retrigger_res.new_spi, 0.4, 2.0)),
                    spi_label=retrigger_res.new_spi_label,
                    confidence_badge="medium",
                )
                session.add(snap)
                session.commit()
        except Exception:
            pass

        from dataclasses import asdict
        return {
            **res,
            "run_id": new_run_id,
            "retrigger": asdict(retrigger_res),
        }
    except ValueError as e:
        return {"status": "ERROR", "message": str(e)}


# Handled via feedback_router (@router.get("/api/feedback/planting-reports"))
# @app.get("/api/feedback/planting-reports")
def get_planting_reports(
    crop_id: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
):
    """
    Item 7: Retrieve actual planting reports submitted by farmers / extension officers.
    """
    eff_crop = str(crop_id) if crop_id is not None and not hasattr(crop_id, "default") else None
    eff_season = str(season) if season is not None and not hasattr(season, "default") else None
    reports = report_store.get_reports(crop_id=eff_crop, season=eff_season)
    from dataclasses import asdict
    return [asdict(r) for r in reports]


# Handled via feedback_router (@router.post("/api/feedback/retrigger"))
# @app.post("/api/feedback/retrigger")
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


@app.post("/api/history/log-action")
def log_officer_action(payload: DecisionLogPayload):
    """
    Item 8: Save officer action with model version, data version, and assumptions snapshot.
    """
    assump = payload.assumptions or {
        "loss_pct": 0.15,
        "import_lead_time_weeks": 7,
        "spi_bands": [0.8, 1.2],
        "pilot_district_share": HUB_SHARE.get(payload.crop_id, 0.1631),
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
    """
    return adoption_sim.simulate(
        crop=crop_id,
        season_demand_mt=season_demand_mt,
        uncoordinated_supply_mt=uncoordinated_supply_mt,
    )


# ---------------------------------------------------------------------------
# Database Persistence: Farmers & Officers Management
# ---------------------------------------------------------------------------

class FarmerPayload(BaseModel):
    pseudonymous_id: str
    district: str = "Anuradhapura"
    divisional_secretariat: Optional[str] = None
    total_land_ha: float = 1.0
    irrigation_type: str = "irrigated"  # irrigated or rainfed
    irrigation_subtype: Optional[str] = None  # major, minor, lift
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    consent_given: bool = True
    language: str = "si"


class OfficerPayload(BaseModel):
    officer_id: str
    name: str
    district: str = "Anuradhapura"
    division: Optional[str] = None
    role: str = "Agricultural Extension Officer"


class HarvestReportPayload(BaseModel):
    planting_report_id: str
    pseudonymous_id: str
    crop_id: str
    season: str = "Maha 2025/2026"
    area_harvested_ha: float
    harvest_date: Optional[str] = None
    harvest_quantity_kg: float
    loss_kg: float = 0.0
    quantity_sold_kg: float = 0.0
    quantity_stored_kg: float = 0.0
    sale_price_rs_kg: Optional[float] = None
    sale_channel: Optional[str] = None
    sale_month: Optional[int] = None
    problems: Optional[List[str]] = None
    notes: Optional[str] = None


@app.post("/api/database/init")
def initialize_database():
    """Explicitly initializes or verifies PostgreSQL database tables."""
    init_db()
    return {
        "status": "INITIALIZED",
        "dialect": get_active_dialect(),
        "tables": [
            "runs",
            "decision_history",
            "farmer_profiles",
            "officers",
            "users",
            "planting_reports",
            "harvest_reports",
            "forecast_snapshots",
            "data_catalogue",
            "monthly_data",
            "alerts",
            "alert_status",
        ],
    }


@app.get("/api/farmers")
def list_farmers(district: Optional[str] = Query(None)):
    """Retrieve pseudonymous farmer profiles from persistent database."""
    eff_district = str(district) if district is not None and not hasattr(district, "default") else None
    with get_session() as session:
        q = session.query(FarmerProfileModel)
        if eff_district:
            q = q.filter(FarmerProfileModel.district == eff_district)
        farmers = q.order_by(FarmerProfileModel.pseudonymous_id.asc()).all()
        return [f.to_dict() for f in farmers]


@app.post("/api/farmers")
def register_farmer(payload: FarmerPayload):
    """Register or update pseudonymous farmer profile in persistent database."""
    with get_session() as session:
        farmer = FarmerProfileModel(
            pseudonymous_id=payload.pseudonymous_id,
            district=payload.district,
            divisional_secretariat=payload.divisional_secretariat,
            total_land_ha=payload.total_land_ha,
            irrigation_type=payload.irrigation_type,
            irrigation_subtype=payload.irrigation_subtype,
            soil_type=payload.soil_type,
            soil_ph=payload.soil_ph,
            consent_given=payload.consent_given,
            language=payload.language,
        )
        session.merge(farmer)
        session.commit()
        return {"status": "SUCCESS", "farmer": farmer.to_dict()}


@app.get("/api/officers")
def list_officers(district: Optional[str] = Query(None)):
    """Retrieve registered agricultural officers from persistent database."""
    eff_district = str(district) if district is not None and not hasattr(district, "default") else None
    with get_session() as session:
        q = session.query(OfficerModel)
        if eff_district:
            q = q.filter(OfficerModel.district == eff_district)
        officers = q.order_by(OfficerModel.officer_id.asc()).all()
        return [o.to_dict() for o in officers]


@app.post("/api/officers")
def register_officer(payload: OfficerPayload):
    """Register or update agricultural extension officer in persistent database."""
    with get_session() as session:
        officer = OfficerModel(
            officer_id=payload.officer_id,
            name=payload.name,
            district=payload.district,
            division=payload.division,
            role=payload.role,
        )
        session.merge(officer)
        session.commit()
        return {"status": "SUCCESS", "officer": officer.to_dict()}


# Handled via feedback_router (@router.post("/api/feedback/harvest-report"))
# @app.post("/api/feedback/harvest-report")
def submit_harvest_report(payload: HarvestReportPayload):
    """
    Stage 2 Feedback Loop: Captures realized post-harvest yield, losses, and market prices.
    Enforces check that sold + lost + stored does not exceed harvest quantity.
    """
    disposed = payload.loss_kg + payload.quantity_sold_kg + payload.quantity_stored_kg
    if payload.harvest_quantity_kg > 0 and disposed > (payload.harvest_quantity_kg * 1.05):
        return {
            "status": "ERROR",
            "message": f"Disposed quantity ({disposed} kg) exceeds harvest quantity ({payload.harvest_quantity_kg} kg).",
        }

    with get_session() as session:
        harvest = HarvestReportModel(
            planting_report_id=payload.planting_report_id,
            pseudonymous_id=payload.pseudonymous_id,
            crop_id=payload.crop_id,
            season=payload.season,
            area_harvested_ha=payload.area_harvested_ha,
            harvest_quantity_kg=payload.harvest_quantity_kg,
            loss_kg=payload.loss_kg,
            quantity_sold_kg=payload.quantity_sold_kg,
            quantity_stored_kg=payload.quantity_stored_kg,
            sale_price_rs_kg=payload.sale_price_rs_kg,
            sale_channel=payload.sale_channel,
            sale_month=payload.sale_month,
            problems=payload.problems or [],
            notes=payload.notes,
        )
        session.merge(harvest)
        session.commit()
        return {"status": "ACCEPTED", "harvest": harvest.to_dict()}


# ===========================================================================
# Dashboard Screen API Endpoints
# ===========================================================================

class LoginPayload(BaseModel):
    username: str
    password: str
    role: Optional[str] = "officer"


class AlertAckPayload(BaseModel):
    user_id: str = "USR-OFFICER-01"
    ask_officer: bool = False
    officer_note: Optional[str] = None


@app.get("/api/forecasts/gap-timeline")
def get_gap_timeline(
    crop_id: Optional[str] = Query(None),
    season: str = Query("Maha 2025/2026"),
    lead_weeks: Optional[int] = Query(None),
):
    """
    Dashboard Screen: Gap & Import Timeline
    Supplies best/worst/expected gap bounds, decision deadlines, and lead-time constraints.
    """
    _ensure_models_loaded()
    eff_crop = str(crop_id) if crop_id is not None and not hasattr(crop_id, "default") else None
    eff_season = str(season) if season is not None and not hasattr(season, "default") else (getattr(season, "default", "Maha 2025/2026") or "Maha 2025/2026")
    crops_to_run = [eff_crop] if eff_crop in ["big_onion", "chilli"] else ["big_onion", "chilli"]
    timelines = []

    for crop in crops_to_run:
        req = settings.crops[crop]
        now = pd.Timestamp.now()
        eff_lead_weeks = int(lead_weeks) if (lead_weeks is not None and not hasattr(lead_weeks, "default")) else settings.import_lead_time_weeks.get(crop, 7)
        # Decision deadline: T_harvest - lead_time_weeks (approx 14 weeks from season baseline)
        deadline_date = (now + pd.Timedelta(weeks=max(1, 14 - eff_lead_weeks))).strftime("%Y-%m-%d")
        days_remaining = max(0, (pd.Timestamp(deadline_date) - now).days)

        # Retrieve AI 3 SPI and gap
        latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1]
        a1_res = a1_models[crop].predict_row(latest_row)
        spi_res = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=a1_res.point_forecast,
            month=int(latest_row["month"]),
            target_date=str(latest_row["year_month"]),
        )

        mid_gap = spi_res.gap_mt
        # Best scenario: lower demand or higher yield
        best_gap = round(mid_gap * 0.7 if mid_gap < 0 else mid_gap * 1.3, 1)
        worst_gap = round(mid_gap * 1.4 if mid_gap < 0 else mid_gap * 0.6, 1)

        action = "Dynamic JIT Import (Import later)" if mid_gap < -2000 else (
            "Buffer Storage Reservation" if mid_gap > 1000 else "Maintain Planned Strategy"
        )

        options = [
            {"id": "IMPORT_NOW", "label": "Immediate Import Authorization", "lead_weeks": eff_lead_weeks, "feasible": days_remaining > 0},
            {"id": "IMPORT_LATER", "label": "Dynamic JIT Import (Wait for planting report)", "lead_weeks": eff_lead_weeks, "feasible": days_remaining >= 14},
            {"id": "HOLD_STORAGE_BUFFER", "label": "Buffer Storage Reservation", "capacity_mt": 4500.0, "feasible": mid_gap > 0},
            {"id": "DELAY_IMPORT", "label": "Delay / Defer Import (Maintain Current Extent)", "feasible": True},
        ]

        timelines.append({
            "crop_id": crop,
            "crop_name": req.name_en,
            "season": season,
            "target_period": str(latest_row["year_month"]),
            "decision_deadline": deadline_date,
            "import_lead_weeks": eff_lead_weeks,
            "days_remaining": days_remaining,
            "gap_mid_mt": mid_gap,
            "gap_best_mt": best_gap,
            "gap_worst_mt": worst_gap,
            "projected_demand_mt": spi_res.projected_demand_mt,
            "expected_supply_mt": a1_res.point_forecast,
            "spi_ratio": spi_res.spi_ratio,
            "spi_label": spi_res.spi_label,
            "recommended_action": action,
            "options": options,
            "storage_buffer_capacity_mt": 4500.0,
            "fair_floor_price_rs_kg": req.min_fair_farmgate_price,
            "status": "Action Required" if days_remaining <= 21 else "Monitoring",
        })

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    prov_meta = compute_dataset_provenance(cached_df)

    return {
        "run_id": f"RUN-{g_commit[:7]}",
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": prov_meta["data_quality"],
        "is_demo": prov_meta["is_demo"],
        "db_fallback": prov_meta["db_fallback"],
        "served_model": "HiGHS-LP + A3-SPI",
        "assumptions_ref": "docs/assumptions.md",
        "timelines": timelines,
    }


@app.get("/api/gap")
def get_gap_alias(
    crop_id: Optional[str] = Query(None),
    season: str = Query("Maha 2025/2026"),
    lead_weeks: Optional[int] = Query(None),
):
    """Alias for /api/forecasts/gap-timeline supporting API contract."""
    return get_gap_timeline(crop_id=crop_id, season=season, lead_weeks=lead_weeks)


@app.get("/api/forecasts/price-outlook")
def get_price_outlook(crop_id: Optional[str] = Query(None)):
    """
    Dashboard Screen: Price Outlook
    Provides P10/P50/P90 probabilistic price bands, retail comparisons, and model attribution.
    """
    _ensure_models_loaded()
    eff_crop = str(crop_id) if crop_id is not None and not hasattr(crop_id, "default") else None
    crops_to_run = [eff_crop] if eff_crop in ["big_onion", "chilli"] else ["big_onion", "chilli"]
    outlooks = {}

    for crop in crops_to_run:
        req = settings.crops[crop]
        latest_row = cached_df[cached_df["crop"] == crop].sort_values("date").iloc[-1]
        a2_res = a2_models[crop].forecast_step(latest_row, horizon=1)

        p50 = float(a2_res.best_forecast)
        p10 = float(a2_res.lower_bound)
        p90 = float(a2_res.upper_bound)
        retail_p50 = compute_modeled_retail_price(p50, crop=crop)

        # Pull past 6 months trend
        past_6 = cached_df[cached_df["crop"] == crop].sort_values("date").tail(6)
        history_points = [
            {
                "date": str(r["year_month"]),
                "farmgate": float(r["farmgate_price_rs_kg"]),
                "retail": float(r.get("retail_price_rs_kg", r["farmgate_price_rs_kg"] * 1.3)),
            }
            for _, r in past_6.iterrows()
        ]

        outlooks[crop] = {
            "crop_id": crop,
            "crop_name": req.name_en,
            "target_period": str(latest_row["year_month"]),
            "farmgate_price": {
                "p10": p10,
                "p50": p50,
                "p90": p90,
            },
            "retail_price": {
                "p10": round(p10 * 1.3, 1),
                "p50": retail_p50,
                "p90": round(p90 * 1.4, 1),
            },
            "fair_floor_price_rs_kg": req.min_fair_farmgate_price,
            "direction": a2_res.direction,
            "confidence_score": round(a2_res.direction_confidence * 100, 1),
            "confidence_badge": "high" if a2_res.direction_confidence > 0.75 else "medium",
            "price_model_used": "SARIMAX-LightGBM-ensemble",
            "supply_model_used": "A1-VolumeForecaster",
            "historical_trend": history_points,
        }

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    prov_meta = compute_dataset_provenance(cached_df)

    return {
        "run_id": f"RUN-{g_commit[:7]}",
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": prov_meta["data_quality"],
        "is_demo": prov_meta["is_demo"],
        "db_fallback": prov_meta["db_fallback"],
        "served_model": "SARIMAX-LightGBM-ensemble",
        "assumptions_ref": "docs/assumptions.md",
        "crops": outlooks,
    }


# ---------------------------------------------------------------------------
# Re-exports & Aliases for Modular Routers (Phase 3.7 & 3.8)
# ---------------------------------------------------------------------------

from govisense.api.routes.data import (
    get_adoption_summary,
    list_data_catalogue,
    get_latest_prices,
    get_evaluation_scoreboard,
)
from govisense.api.routes.alerts import (
    get_alerts as list_alerts,
    acknowledge_alert,
    ask_officer_inquiry as ask_officer_on_alert,
    add_officer_note,
)
from govisense.api.routes.officer import (
    list_runs as list_pipeline_runs,
    get_run_detail as get_pipeline_run_by_id,
    record_officer_decision,
    simulate_scenario,
)
from govisense.api.routes.feedback import (
    submit_planting_report,
    submit_harvest_report,
    list_ground_reports,
    retrigger_pipeline,
)
from govisense.api.routes.farmer import (
    farmer_top3_recommendations as farmer_top3,
)


class AlertAckPayload(BaseModel):
    user_id: str = "USR-001"
    ask_officer: bool = False
    officer_note: Optional[str] = None


def fill_forecast_actuals(
    crop_id: str,
    season: str,
    actual_price_rs_kg: Optional[float] = None,
    actual_production_mt: Optional[float] = None,
) -> int:
    """
    Fills actual price and production in matching forecast_snapshots rows
    when post-harvest reports or CBSL prices arrive (Proposal 3.2).
    """
    with get_session() as session:
        snaps = (
            session.query(ForecastSnapshotModel)
            .filter(
                ForecastSnapshotModel.crop_id == crop_id,
                ForecastSnapshotModel.season == season,
            )
            .all()
        )
        for s in snaps:
            if actual_price_rs_kg is not None:
                s.actual_price_rs_kg = actual_price_rs_kg
            if actual_production_mt is not None:
                s.actual_production_mt = actual_production_mt
        session.commit()
        return len(snaps)






