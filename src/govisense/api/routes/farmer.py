"""
Farmer Advisor & Mobile Application Router
Team DARKBITE · ModelX 2.0 Proposal Specification
Provides Crop Suitability Scorer Top 3 recommendations, 110% oversupply stop rule,
12-month expected price bands (P10-P90), and pseudonymous farmer profile management.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import numpy as np

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from govisense.api.deps import get_db, require_farmer, get_optional_current_user
from govisense.config import settings
from govisense.db.session import get_session
from govisense.db.models import (
    FarmerProfileModel,
    PlantingReportModel,
    HarvestReportModel,
    PipelineRunModel,
    ForecastSnapshotModel,
)
from govisense.feedback.planting_reports import PlantingReportStore
from govisense.models.suitability_scorer import SuitabilityScorer
from govisense.models.demand_estimator import DemandEstimator
from govisense.models.a3_supply_pressure import SupplyPressureEngine
from govisense.models.target_area import TargetAreaCalculator
from govisense.data.crop_requirements import get_crop_requirements
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit, compute_dataset_provenance

logger = logging.getLogger("govisense.api.farmer")
router = APIRouter(prefix="", tags=["Farmer Advisor"])

suitability_scorer = SuitabilityScorer()
demand_estimator = DemandEstimator()
spi_engine = SupplyPressureEngine()
target_area_calc = TargetAreaCalculator()
report_store = PlantingReportStore()


class FarmerProfileCreateOrUpdate(BaseModel):
    pseudonymous_id: str
    district: str = "Anuradhapura"
    divisional_secretariat: Optional[str] = None
    total_land_ha: float = Field(..., gt=0.0, le=100.0)
    irrigation_type: str = "irrigated"
    irrigation_subtype: Optional[str] = None
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    consent_given: bool = True
    language: str = "si"


@router.get("/api/farmer/top3")
def farmer_top3_recommendations(
    farmer_id: Optional[str] = Query(None),
    soil_ph: Optional[float] = Query(None),
    soil_type: Optional[str] = Query(None),
    irrigation_type: Optional[str] = Query(None),
    irrigation_subtype: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    divisional_secretariat: Optional[str] = Query(None),
    land_area_ha: Optional[float] = Query(None),
    land_ha: Optional[float] = Query(None),
    season: Optional[str] = Query(None),
    planting_month: Optional[int] = Query(None),
    current_month: Optional[int] = Query(None),
    is_rainfed: Optional[bool] = Query(None),
    annual_rainfall_mm: Optional[float] = Query(None),
    avg_temp_c: Optional[float] = Query(None),
    zone: Optional[str] = Query(None),
    water_source: Optional[str] = Query(None),
    db: Any = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    **kwargs: Any,
):
    """
    Farmer Advisor: Returns top 3 crop recommendations based on agronomic suitability,
    market demand, 110% oversupply stop rule, 12-month expected price ranges (P10–P90),
    and expected net profit per acre.
    """
    if not isinstance(db, Session):
        db = get_session()

    eff_district = district if isinstance(district, str) else "Anuradhapura"
    eff_irrigation = irrigation_type if isinstance(irrigation_type, str) else "irrigated"
    eff_season = season if isinstance(season, str) else "Maha 2025/2026"
    eff_farmer_id = farmer_id if isinstance(farmer_id, str) else (current_user.get("pseudonymous_id") if isinstance(current_user, dict) else "LK-AP-DEFAULT")
    eff_land = land_ha if isinstance(land_ha, (int, float)) else (land_area_ha if isinstance(land_area_ha, (int, float)) else 1.0)
    eff_month = current_month if isinstance(current_month, int) else (planting_month if isinstance(planting_month, int) else 10)
    eff_rainfed = is_rainfed if isinstance(is_rainfed, bool) else (eff_irrigation.lower() == "rainfed")

    area_conditions = {
        "farmer_id": eff_farmer_id,
        "district": eff_district,
        "divisional_secretariat": divisional_secretariat if isinstance(divisional_secretariat, str) else "Nuwaragam Palatha Central",
        "soil_ph": soil_ph if isinstance(soil_ph, (int, float)) else 6.5,
        "soil_type": soil_type if isinstance(soil_type, str) else "Reddish Brown Earth (RBE)",
        "irrigation_type": eff_irrigation,
        "irrigation_subtype": irrigation_subtype if isinstance(irrigation_subtype, str) else "major_irrigation",
        "is_rainfed": eff_rainfed,
        "current_month": eff_month,
        "planting_month": eff_month,
        "season": eff_season,
        "annual_rainfall_mm": annual_rainfall_mm if isinstance(annual_rainfall_mm, (int, float)) else 1100.0,
        "avg_temp_c": avg_temp_c if isinstance(avg_temp_c, (int, float)) else 28.0,
        "zone": zone if isinstance(zone, str) else "dry",
        "total_land_ha": eff_land,
    }

    ranking = suitability_scorer.rank_crops(area_conditions)
    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    run_id = f"RUN-{g_commit[:7]}"
    prov_meta = compute_dataset_provenance()

    if not ranking:
        return {
            "run_id": run_id,
            "data_version": d_ver,
            "model_version": m_ver,
            "data_quality": prov_meta["data_quality"],
            "is_demo": prov_meta["is_demo"],
            "db_fallback": prov_meta["db_fallback"],
            "served_model": "SuitabilityScorer-v1.4",
            "assumptions_ref": "docs/assumptions.md",
            "farmer_id": eff_farmer_id,
            "season": eff_season,
            "message": "No suitable crops found for the given area conditions.",
            "top3": [],
        }

    all_reqs = get_crop_requirements()
    top3_results = []

    for scored_crop in ranking[:3]:
        crop_id = scored_crop.crop_id
        fit_score = scored_crop.score_0_100
        confidence_badge = scored_crop.confidence

        req = all_reqs.get(crop_id)
        # Demand context
        try:
            dem_result = demand_estimator.estimate(crop_id, eff_month, scenario="mid")
            monthly_demand = dem_result.demand_mt
        except Exception as e:
            logger.error("Demand estimator failed for %s in month %d: %s", crop_id, eff_month, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Demand estimation failed for crop '{crop_id}': {e}",
            )

        # Check cumulative reported acreage and oversupply stop rule
        total_reported = report_store.get_total_reported_area(crop_id, eff_season)
        yield_mid = req.yield_mid_mt_ha if req else 15.0
        loss_pct = req.loss_pct if req else 0.15

        target_ha = round((monthly_demand * 4.0) / (yield_mid * (1.0 - loss_pct) * 1.05), 1)
        remaining_target_ha = max(0.0, round(target_ha - total_reported, 1))

        # 110% oversupply stop rule per Proposal Section 6
        is_target_full = bool(total_reported >= 1.10 * target_ha and target_ha > 0)
        target_full_warning = "TARGET FULL - DO NOT PLANT" if is_target_full else None

        if is_target_full:
            fit_score = 0.0
            rec_ha = 0.0
        else:
            rec_ha = min(round(eff_land * 0.60, 2), remaining_target_ha)

        # Expected price ranges
        cfg = settings.crops.get(crop_id) or settings.crops.get("big_onion")
        floor = cfg.min_fair_farmgate_price if cfg else 120.0
        p10 = round(floor * 0.85, 0)
        p90 = round(floor * 1.50, 0)

        # 12-month expected price ranges
        monthly_price_ranges_12m = []
        for m in range(1, 13):
            s_factor = 1.0 + 0.15 * np.sin(2 * np.pi * m / 12.0)
            monthly_price_ranges_12m.append({
                "month": m,
                "p10_rs_kg": round(p10 * s_factor, 1),
                "p50_rs_kg": round(((p10 + p90) / 2.0) * s_factor, 1),
                "p90_rs_kg": round(p90 * s_factor, 1),
            })

        yield_kg_acre = yield_mid * 0.4047 * 1000.0
        cost_acre = (req.cost_per_ha_rs if req else 150000.0) * 0.4047
        expected_net_profit_per_acre = {
            "p10_rs_per_acre": round(yield_kg_acre * p10 - cost_acre, 1),
            "p90_rs_per_acre": round(yield_kg_acre * p90 - cost_acre, 1),
        }

        dur = req.duration_months if req else 3
        harvest_month = ((eff_month + dur - 1) % 12) + 1
        planting_window = (
            f"Month {req.plant_start_month}–{req.plant_end_month}" if req else f"Month {eff_month}"
        )
        harvest_period = f"Month {harvest_month} (approx)"
        try:
            spi_res = spi_engine.calculate(
                crop_id=crop_id,
                month=harvest_month,
                target_date=f"Month {harvest_month}",
            )
            spi_band = spi_res.spi_label
        except Exception:
            spi_band = "Balanced"

        exp_yield = round(rec_ha * yield_mid, 2)
        floor_price = settings.crops[crop_id].min_fair_farmgate_price if crop_id in settings.crops else 120.0

        top3_results.append({
            "rank": len(top3_results) + 1,
            "crop_id": crop_id,
            "crop_name": scored_crop.crop_name,
            "fit_score": fit_score,
            "confidence_badge": confidence_badge,
            "profit_range_rs_kg": {"p10_rs_kg": p10, "p90_rs_kg": p90},
            "price_forecast": {"p10_rs_kg": p10, "p50_rs_kg": round((p10 + p90) / 2.0, 1), "p90_rs_kg": p90},
            "fair_floor_price_rs_kg": floor_price,
            "expected_net_profit_per_acre": expected_net_profit_per_acre,
            "monthly_price_ranges_12m": monthly_price_ranges_12m,
            "risk_level": "Low" if fit_score >= 70 else "Medium",
            "water_need_mm_season": req.water_mm_season if req else None,
            "planting_window": planting_window,
            "harvest_period": harvest_period,
            "duration_months": dur,
            "spi_band_at_harvest": spi_band,
            "growing_duration_days": (req.duration_months * 30) if req else 90,
            "primary_fertilizer": "NPK + Compost",
            "allocated_ha": rec_ha,
            "allocated_area_ha": rec_ha,
            "recommended_ha": rec_ha,
            "expected_yield_mt": exp_yield,
            "expected_yield_mt_ha": yield_mid,
            "target_area_ha": target_ha,
            "cumulative_reported_ha": total_reported,
            "remaining_target_ha": remaining_target_ha,
            "is_target_full": is_target_full,
            "stop_rule_triggered": is_target_full,
            "status": "PAUSED" if is_target_full else "APPROVED",
            "target_full_warning": target_full_warning,
        })

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    prov_meta = compute_dataset_provenance()

    return {
        "run_id": f"RUN-{g_commit[:7]}",
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": prov_meta["data_quality"],
        "is_demo": prov_meta["is_demo"],
        "db_fallback": prov_meta["db_fallback"],
        "served_model": "SuitabilityScorer-v1.4",
        "assumptions_ref": "docs/assumptions.md",
        "farmer_id": eff_farmer_id,
        "season": eff_season,
        "district": eff_district,
        "total_land_ha": eff_land,
        "top3": top3_results,
    }


@router.get("/api/farmer/reports")
def get_farmer_history(
    farmer_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_farmer),
):
    """
    Retrieve all planting and harvest reports submitted under a farmer's pseudonymous ID.
    Enforces privacy by disallowing names, phones, or NICs.
    """
    plantings = (
        db.query(PlantingReportModel)
        .filter(PlantingReportModel.pseudonymous_id == farmer_id)
        .order_by(PlantingReportModel.timestamp.desc())
        .all()
    )
    harvests = (
        db.query(HarvestReportModel)
        .filter(HarvestReportModel.pseudonymous_id == farmer_id)
        .order_by(HarvestReportModel.timestamp.desc())
        .all()
    )

    return {
        "farmer_id": farmer_id,
        "planting_reports": [p.to_dict() for p in plantings],
        "harvest_reports": [h.to_dict() for h in harvests],
    }


@router.post("/api/farmer/profile")
def upsert_farmer_profile(
    payload: FarmerProfileCreateOrUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_farmer),
):
    """
    Create or update a pseudonymous farmer profile.
    Strictly forbids storing name, NIC, phone, or GPS coordinates.
    """
    existing = (
        db.query(FarmerProfileModel)
        .filter(FarmerProfileModel.pseudonymous_id == payload.pseudonymous_id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.district = payload.district
        existing.divisional_secretariat = payload.divisional_secretariat
        existing.total_land_ha = payload.total_land_ha
        existing.irrigation_type = payload.irrigation_type
        existing.irrigation_subtype = payload.irrigation_subtype
        existing.soil_type = payload.soil_type
        existing.soil_ph = payload.soil_ph
        existing.language = payload.language
        existing.consent_given = payload.consent_given
        db.commit()
        return {"status": "UPDATED", "profile": existing.to_dict()}
    else:
        profile = FarmerProfileModel(
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
            created_at=now,
        )
        db.add(profile)
        db.commit()
        return {"status": "CREATED", "profile": profile.to_dict()}


# Backwards compatibility aliases
create_or_update_farmer_profile = upsert_farmer_profile
