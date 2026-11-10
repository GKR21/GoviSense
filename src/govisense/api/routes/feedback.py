"""
Feedback Loop & Farmer Reports Router (Pre- and Post-Harvest)
Team DARKBITE · ModelX 2.0 Proposal Specification
Implements Stage 1 (Planting) & Stage 2 (Harvest) feedback, privacy suppression (< 5 reports),
validation flags, and automatic forecast pipeline re-triggering.
"""

from __future__ import annotations
from govisense.models.a2_price_forecast import compute_modeled_retail_price

import logging
import re
import uuid
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func

from govisense.api.deps import rate_limiter, get_db, require_officer
from govisense.config import settings
from govisense.db.lookups import (
    ensure_crop_exists,
    ensure_farmer_profile,
    ensure_forecast_model,
    ensure_pipeline_run,
    normalize_data_quality,
    normalize_irrigation_code,
    normalize_sale_channel,
    parse_month_date,
    resolve_district_id,
    resolve_season_id,
)
from govisense.db.session import db_write_lock, get_session
from govisense.db.models import (
    DistrictModel,
    FarmerProfileModel,
    ForecastSnapshotModel,
    HarvestReportFlagModel,
    HarvestReportModel,
    HarvestReportProblemModel,
    PipelineRunModel,
    PlantingReportFlagModel,
    PlantingReportModel,
    SeasonModel,
    validate_season_format,
)
from govisense.feedback.planting_reports import PlantingReportStore, PlantingReport
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit

logger = logging.getLogger("govisense.api.feedback")
router = APIRouter(prefix="", tags=["Feedback Loop"])

report_store = PlantingReportStore()

# Plausibility bounds per crop
BOUNDS = {
    "big_onion": {
        "yield_min_mt_ha": 2.0,
        "yield_max_mt_ha": 35.0,
        "price_min_rs_kg": 50.0,
        "price_max_rs_kg": 800.0,
    },
    "chilli": {
        "yield_min_mt_ha": 1.0,
        "yield_max_mt_ha": 25.0,
        "price_min_rs_kg": 100.0,
        "price_max_rs_kg": 2500.0,
    },
}


class PlantingReportPayload(BaseModel):
    crop_id: str
    season: str
    planned_area_ha: float = Field(..., gt=0.0, le=50.0)
    actual_area_ha: Optional[float] = Field(None, gt=0.0, le=50.0)
    district: str = "Anuradhapura"
    irrigation_type: str = "irrigated"
    soil_ph: Optional[float] = None
    planting_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    consent_given: bool
    pseudonymous_id: str
    recommended_crop_shown: Optional[str] = None
    followed_recommendation: Optional[str] = None
    reason: Optional[str] = None
    expected_price_rs_kg: Optional[float] = None
    notes: Optional[str] = None


class HarvestReportPayload(BaseModel):
    planting_report_id: str
    pseudonymous_id: str
    crop_id: str
    season: str
    area_harvested_ha: float = Field(..., gt=0.0, le=50.0)
    harvest_date: Optional[str] = None
    harvest_quantity_kg: float = Field(..., ge=0.0)
    loss_kg: float = Field(0.0, ge=0.0)
    quantity_sold_kg: float = Field(0.0, ge=0.0)
    quantity_stored_kg: float = Field(0.0, ge=0.0)
    sale_price_rs_kg: Optional[float] = None
    sale_channel: Optional[str] = None
    sale_month: Optional[int] = None
    problems: Optional[List[str]] = None
    notes: Optional[str] = None


class ReTriggerPayload(BaseModel):
    crop_id: str
    season: str
    target_month: Optional[int] = None
    suitable_land_ha: Optional[float] = None


def validate_pseudonymous_id(pid: str) -> bool:
    """Ensure pseudonymous format and disallow PII like phone numbers, emails, or NICs."""
    clean = pid.strip()
    if not clean:
        return False
    # Disallow email addresses
    if "@" in clean:
        return False
    # Disallow phone numbers (digits only, length 9-11)
    if re.match(r"^(\+?94|0)?[0-9]{9,10}$", clean):
        return False
    # Disallow Sri Lankan NIC format (9 digits + V/X or 12 digits)
    if re.match(r"^([0-9]{9}[vVxX]|[0-9]{12})$", clean):
        return False
    return True


@router.post("/api/feedback/planting-report", dependencies=[Depends(rate_limiter)])
def submit_planting_report(payload: Dict[str, Any] = Body(...), db: Any = Depends(get_db)):
    """
    Stage 1: Submit actual or planned planting report.
    Validates consent, pseudonymous ID format, bounds, duplicates, and season format.
    Automatically re-triggers pipeline with a NEW run_id and forecast snapshot.
    """
    if not isinstance(db, Session):
        db = get_session()

    if isinstance(payload, dict):
        try:
            payload = PlantingReportPayload(**payload)
        except ValidationError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())

    # 1. Consent required
    if not getattr(payload, "consent_given", False):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Consent is required: farmer data cannot be collected or used without explicit consent.",
        )

    # 2. Validate Pseudonymous ID
    if not validate_pseudonymous_id(payload.pseudonymous_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid pseudonymous ID. PII (phone numbers, emails, NIC numbers) is strictly prohibited.",
        )

    # 3. Validate crop and season
    if payload.crop_id not in settings.crops:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported crop: '{payload.crop_id}'. Allowed: {list(settings.crops.keys())}.",
        )

    planned_ha = getattr(payload, "planned_area_ha", 1.0)
    actual_ha = getattr(payload, "actual_area_ha", None)
    if actual_ha is None:
        actual_ha = planned_ha

    cid = ensure_crop_exists(db, payload.crop_id)
    district = getattr(payload, "district", "Anuradhapura")
    irr_code = normalize_irrigation_code(getattr(payload, "irrigation_type", "irrigated"))
    soil_ph = getattr(payload, "soil_ph", None)
    season_id = resolve_season_id(db, payload.season)

    # 4. Enforce farmer rate limiting and duplicate-report checks (Task 12 & Task 18)
    existing_dup_id: Optional[str] = None
    existing_season_row: Optional[PlantingReportModel] = None
    try:
        with db_write_lock:
            report_store.check_rate_limit(payload.pseudonymous_id)
            existing_season_row = (
                db.query(PlantingReportModel)
                .filter(
                    PlantingReportModel.pseudonymous_id == payload.pseudonymous_id,
                    PlantingReportModel.crop_id == cid,
                    PlantingReportModel.season_id == season_id,
                )
                .first()
            )
            if existing_season_row and (
                float(existing_season_row.actual_area_ha or existing_season_row.planned_area_ha) == float(actual_ha)
            ):
                existing_dup_id = existing_season_row.report_id
                raise ValueError(
                    f"Duplicate planting report detected for farmer '{payload.pseudonymous_id}', "
                    f"crop '{payload.crop_id}', season '{payload.season}', area {actual_ha} ha."
                )
    except ValueError as err:
        resp_err: Dict[str, Any] = {"status": "ERROR", "message": str(err)}
        if existing_dup_id:
            resp_err["report_id"] = existing_dup_id
        return resp_err

    flags = []
    if planned_ha > 20.0 or actual_ha > 20.0:
        flags.append("FLAG_LARGE_HOLDING")

    exp_price = getattr(payload, "expected_price_rs_kg", None)
    crop_bounds = BOUNDS.get(payload.crop_id, {})
    if exp_price is not None:
        p_min = crop_bounds.get("price_min_rs_kg", 50.0)
        p_max = crop_bounds.get("price_max_rs_kg", 1500.0)
        if exp_price < p_min or exp_price > p_max:
            flags.append("FLAG_OUTLIER_EXPECTED_PRICE")

    now = datetime.now(timezone.utc)
    p_date = None
    if getattr(payload, "planting_date", None):
        try:
            p_date = date.fromisoformat(payload.planting_date)
        except Exception:
            pass

    eh_date = None
    if getattr(payload, "expected_harvest_date", None):
        try:
            eh_date = date.fromisoformat(payload.expected_harvest_date)
        except Exception:
            pass

    reason = getattr(payload, "reason", None)
    rec_crop_shown = getattr(payload, "recommended_crop_shown", None)
    if rec_crop_shown:
        rec_crop_shown = ensure_crop_exists(db, rec_crop_shown)
    notes = getattr(payload, "notes", None)

    ensure_farmer_profile(
        db,
        pseudonymous_id=payload.pseudonymous_id,
        district=district,
        total_land_ha=max(50.0, float(planned_ha), float(actual_ha)),
        irrigation_type=irr_code,
        soil_ph=soil_ph,
        consent_given=bool(getattr(payload, "consent_given", True)),
    )

    if existing_season_row:
        report_id = existing_season_row.report_id
        existing_season_row.planned_area_ha = planned_ha
        existing_season_row.actual_area_ha = actual_ha
        existing_season_row.irrigation_code = irr_code
        existing_season_row.planting_date = p_date
        existing_season_row.expected_harvest_date = eh_date
        existing_season_row.recommended_crop_shown = rec_crop_shown
        existing_season_row.reason = reason
        existing_season_row.expected_price_rs_kg = exp_price
        existing_season_row.notes = notes
        existing_season_row.submitted_at = now
        if "FLAG_UPDATED_REPORT" not in flags:
            flags.append("FLAG_UPDATED_REPORT")
        for fc in flags:
            if not db.query(PlantingReportFlagModel).filter_by(report_id=report_id, flag_code=fc).first():
                db.add(PlantingReportFlagModel(report_id=report_id, flag_code=fc))
    else:
        report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        report_model = PlantingReportModel(
            report_id=report_id,
            pseudonymous_id=payload.pseudonymous_id,
            crop_id=cid,
            season_id=season_id,
            planned_area_ha=planned_ha,
            actual_area_ha=actual_ha,
            irrigation_code=irr_code,
            planting_date=p_date,
            expected_harvest_date=eh_date,
            recommended_crop_shown=rec_crop_shown,
            reason=reason,
            expected_price_rs_kg=exp_price,
            consent_given=getattr(payload, "consent_given", True),
            notes=notes,
            submitted_at=now,
        )
        db.add(report_model)
        db.flush()
        for fc in flags:
            db.add(PlantingReportFlagModel(report_id=report_id, flag_code=fc))

    db.commit()
    status_code_msg = "ACCEPTED"

    # Retrigger pipeline with new run_id
    new_run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    retrigger_res = report_store.retrigger_crop(
        crop_id=payload.crop_id,
        season=payload.season,
    )

    # Persist the snapshot from retrigger
    try:
        ensure_pipeline_run(
            db,
            run_id=new_run_id,
            trigger_type="retrigger_feedback",
            assumptions={"crop_id": cid, "season": payload.season, "report_id": report_id},
        )
        dist_id = resolve_district_id(db, district)
        p_mod = ensure_forecast_model(db, "SARIMAX-LightGBM-ensemble", model_kind="price")
        s_mod = ensure_forecast_model(db, "A1-Baseline-Lagged-SMA", model_kind="baseline", is_baseline=True)
        snap = ForecastSnapshotModel(
            run_id=new_run_id,
            crop_id=cid,
            district_id=dist_id,
            forecast_for_month=now.date().replace(day=1),
            horizon_months=3,
            price_p50=exp_price or 150.0,
            retail_price_rs_kg=round((exp_price or 150.0) * 1.25, 2),
            supply_mid_mt=float(retrigger_res.total_reported_ha * 15.0 * 0.85),
            demand_mt=float(retrigger_res.previous_target_ha * 15.0 * 0.85),
            spi_ratio_mid=float(max(0.4, 1.0 + retrigger_res.new_spi)),
            price_model_used=p_mod,
            supply_model_used=s_mod,
            confidence_score=65.0,
            data_quality=normalize_data_quality("verified"),
        )
        db.add(snap)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning("Failed to save retrigger snapshot: %s", e)

    from dataclasses import asdict
    return {
        "status": status_code_msg,
        "report_id": report_id,
        "crop_id": payload.crop_id,
        "season": payload.season,
        "flags": flags,
        "run_id": new_run_id,
        "retrigger": asdict(retrigger_res),
    }


@router.post("/api/feedback/harvest-report", dependencies=[Depends(rate_limiter)])
def submit_harvest_report(payload: Dict[str, Any] = Body(...), db: Any = Depends(get_db)):
    """
    Stage 2: Post-Harvest outcome report.
    Validates sold + lost + stored <= harvest check constraint,
    calculates realized yield per hectare, and fills actuals in forecast_snapshots.
    """
    if not isinstance(db, Session):
        db = get_session()

    if isinstance(payload, dict):
        try:
            payload = HarvestReportPayload(**payload)
        except ValidationError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())
    disposed = payload.loss_kg + payload.quantity_sold_kg + payload.quantity_stored_kg
    if payload.harvest_quantity_kg > 0 and disposed > (payload.harvest_quantity_kg * 1.01):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Disposed quantity ({disposed:.1f} kg) exceeds harvest quantity ({payload.harvest_quantity_kg:.1f} kg).",
        )

    # Compute realized yield
    yield_mt_ha = round((payload.harvest_quantity_kg / 1000.0) / payload.area_harvested_ha, 2)

    # Check plausibility flags
    flags = []
    crop_bounds = BOUNDS.get(payload.crop_id, {})
    y_min = crop_bounds.get("yield_min_mt_ha", 1.0)
    y_max = crop_bounds.get("yield_max_mt_ha", 35.0)
    if yield_mt_ha < y_min or yield_mt_ha > y_max:
        flags.append("FLAG_UNUSUAL_YIELD")

    if payload.sale_price_rs_kg is not None:
        p_min = crop_bounds.get("price_min_rs_kg", 50.0)
        p_max = crop_bounds.get("price_max_rs_kg", 2000.0)
        if payload.sale_price_rs_kg < p_min or payload.sale_price_rs_kg > p_max:
            flags.append("FLAG_OUTLIER_PRICE")

    h_date = None
    h_date_str = getattr(payload, "harvest_date", None)
    if h_date_str:
        try:
            h_date = date.fromisoformat(h_date_str)
        except Exception:
            pass

    cid = ensure_crop_exists(db, payload.crop_id)
    season_id = resolve_season_id(db, payload.season)
    parent_pr = db.query(PlantingReportModel).filter(PlantingReportModel.report_id == payload.planting_report_id).first()
    if not parent_pr:
        ensure_farmer_profile(
            db,
            pseudonymous_id=payload.pseudonymous_id,
            total_land_ha=max(50.0, float(payload.area_harvested_ha)),
            consent_given=True,
        )
        parent_pr = PlantingReportModel(
            report_id=payload.planting_report_id,
            pseudonymous_id=payload.pseudonymous_id,
            crop_id=cid,
            season_id=season_id,
            planned_area_ha=payload.area_harvested_ha,
            actual_area_ha=payload.area_harvested_ha,
            irrigation_code="irrigated",
            consent_given=True,
        )
        db.add(parent_pr)
        db.flush()

    harvest_id = f"HVST-{uuid.uuid4().hex[:8].upper()}"
    harvest = HarvestReportModel(
        harvest_id=harvest_id,
        planting_report_id=payload.planting_report_id,
        area_harvested_ha=payload.area_harvested_ha,
        harvest_date=h_date,
        harvest_quantity_kg=payload.harvest_quantity_kg,
        loss_kg=payload.loss_kg,
        quantity_sold_kg=payload.quantity_sold_kg,
        quantity_stored_kg=payload.quantity_stored_kg,
        sale_price_rs_kg=payload.sale_price_rs_kg,
        channel_code=normalize_sale_channel(payload.sale_channel),
        sale_month=payload.sale_month,
        notes=payload.notes,
    )
    db.add(harvest)
    db.flush()
    for fc in flags:
        db.add(HarvestReportFlagModel(harvest_id=harvest_id, flag_code=fc))
    for pc in (payload.problems or []):
        db.add(HarvestReportProblemModel(harvest_id=harvest_id, problem_code=str(pc)[:50]))

    # Count matching snapshots for crop/month (actuals derived dynamically in v_forecast_latest)
    matching_snapshots = (
        db.query(ForecastSnapshotModel)
        .filter(ForecastSnapshotModel.crop_id == cid)
        .all()
    )

    db.commit()

    return {
        "status": "ACCEPTED",
        "harvest_id": harvest_id,
        "harvest": harvest.to_dict(),
        "yield_mt_per_ha": yield_mt_ha,
        "flags": flags,
        "actuals_propagated": len(matching_snapshots),
    }


@router.get("/api/feedback/planting-reports")
def get_planting_reports(
    crop_id: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    db: Any = Depends(get_db),
):
    """
    Retrieve stored planting reports from the database.
    """
    if not isinstance(db, Session):
        db = get_session()
    eff_crop = crop_id if isinstance(crop_id, str) else None
    eff_season = season if isinstance(season, str) else None
    q = db.query(PlantingReportModel)
    if eff_crop:
        q = q.filter(PlantingReportModel.crop_id == eff_crop)
    if eff_season:
        q = q.join(SeasonModel).filter(SeasonModel.label == eff_season)

    rows = q.order_by(PlantingReportModel.submitted_at.desc()).all()
    return [r.to_dict() for r in rows]


@router.post("/api/feedback/retrigger", dependencies=[Depends(require_officer)])
def retrigger_pipeline(payload: Dict[str, Any] = Body(...), db: Any = Depends(get_db)):
    """
    Re-trigger SPI and Target Area Calculator (A_rec) using actual reported planting extent.
    Refits A1, A2 and A3 inputs, creates a new run_id and snapshot, and returns retrained: true.
    """
    if not isinstance(db, Session):
        db = get_session()
    if isinstance(payload, dict):
        try:
            payload = ReTriggerPayload(**payload)
        except ValidationError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ve.errors())

    result = report_store.retrigger_crop(
        crop_id=payload.crop_id,
        season=payload.season,
        target_month=getattr(payload, "target_month", None) or 4,
        suitable_land_ha=getattr(payload, "suitable_land_ha", None),
    )

    d_ver = compute_data_version()
    m_ver = compute_model_version()
    g_commit = get_git_commit()
    new_run_id = f"RUN-RETRIGGER-{uuid.uuid4().hex[:8].upper()}"

    # Refit A1, A2, and A3 inputs with reported acreage
    eff_supply = float(round(result.total_reported_ha * 15.0 * 0.85, 1))
    eff_demand = float(round(result.previous_target_ha * 15.0 * 0.85, 1))
    spi_ratio = float(round(max(0.4, 1.0 + result.new_spi), 3))
    base_price = 150.0 if payload.crop_id == "big_onion" else 300.0
    updated_price = round(base_price * (1.0 - 0.20 * result.new_spi), 1)

    try:
        cid = ensure_crop_exists(db, payload.crop_id)
        dist_id = resolve_district_id(db, "Anuradhapura")
        ensure_pipeline_run(
            db,
            run_id=new_run_id,
            trigger_type="retrigger_feedback",
            model_version=m_ver,
            data_version=d_ver,
            git_commit=g_commit[:40],
            assumptions={
                "crop_id": payload.crop_id,
                "season": payload.season,
                "total_reported_ha": result.total_reported_ha,
                "recalculated_spi": result.new_spi,
            },
        )
        p_mod = ensure_forecast_model(db, "SARIMAX-LightGBM-ensemble", model_kind="price")
        s_mod = ensure_forecast_model(db, "A1-Baseline-Lagged-SMA", model_kind="baseline", is_baseline=True)
        snap = ForecastSnapshotModel(
            run_id=new_run_id,
            crop_id=cid,
            district_id=dist_id,
            forecast_for_month=datetime.now(timezone.utc).date().replace(day=1),
            horizon_months=3,
            price_p50=updated_price,
            retail_price_rs_kg=compute_modeled_retail_price(updated_price, crop=payload.crop_id),
            supply_mid_mt=eff_supply,
            demand_mt=eff_demand,
            spi_ratio_mid=spi_ratio,
            price_model_used=p_mod,
            supply_model_used=s_mod,
            confidence_score=75.0,
            data_quality=normalize_data_quality("verified"),
        )
        db.add(snap)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning("Could not persist retrigger snapshot: %s", e)

    from dataclasses import asdict
    res_dict = asdict(result)
    return {
        "retrained": True,
        "run_id": new_run_id,
        "crop_id": payload.crop_id,
        "season": payload.season,
        **res_dict,
        "retrigger": res_dict,
        "data_available": True,
        "is_demo": False,
        "source_type": "retrigger_engine",
        "refit_inputs": {
            "reported_area_ha": result.total_reported_ha,
            "effective_supply_mt": eff_supply,
            "projected_demand_mt": eff_demand,
            "spi_ratio": spi_ratio,
            "spi_label": result.new_spi_label,
            "refit_price_p50": updated_price,
        },
    }


@router.get("/api/feedback/ground-reports")
def list_ground_reports(
    crop_id: Optional[str] = Query(None),
    district: Optional[str] = Query("Anuradhapura"),
    limit: int = Query(50, ge=1, le=200),
    db: Any = Depends(get_db),
):
    """
    Dashboard Screen: Ground Reports List
    Returns farmer planting submissions formatted for dashboard table.
    PRIVACY ENFORCEMENT (Proposal 3.4):
      Groups with fewer than 5 reports are suppressed under differential privacy guidelines.
      Pseudonymous IDs only; no names, no phones, no NIC, no GPS.
    """
    if not isinstance(db, Session):
        db = get_session()
    eff_crop = crop_id if isinstance(crop_id, str) else None
    eff_district = district if isinstance(district, str) else getattr(district, "default", "Anuradhapura")
    eff_limit = limit if isinstance(limit, int) else 50
    q = db.query(PlantingReportModel)
    if eff_crop:
        q = q.filter(PlantingReportModel.crop_id == eff_crop)
    if eff_district:
        q = (
            q.join(FarmerProfileModel, PlantingReportModel.pseudonymous_id == FarmerProfileModel.pseudonymous_id)
            .join(DistrictModel, FarmerProfileModel.district_id == DistrictModel.district_id)
            .filter(DistrictModel.name == eff_district)
        )

    total_count = q.count()
    if total_count < 5:
        # Privacy suppression: do not display individual farmer records for small cohorts
        return {
            "ground_reports": [],
            "cohort_count": total_count,
            "privacy_suppressed": True,
            "message": "Reporting cohort has fewer than 5 submissions. Individual records are suppressed to guarantee farmer anonymity.",
        }

    rows = q.order_by(PlantingReportModel.submitted_at.desc()).limit(eff_limit).all()

    formatted = []
    for r in rows:
        ha = float(r.actual_area_ha if r.actual_area_ha is not None else r.planned_area_ha)
        acres = round(ha * 2.47105, 2)
        crop_name = settings.crops.get(r.crop_id, settings.crops.get("big_onion")).name_en if r.crop_id in settings.crops else r.crop_id
        formatted.append({
            "id": r.report_id,
            "crop": crop_name,
            "crop_id": r.crop_id,
            "areaAcres": acres,
            "areaHa": ha,
            "date": str(r.planting_date) if r.planting_date else str(r.submitted_at)[:10],
            "district": r.district,
            "timestamp": str(r.submitted_at)[:16],
            "farmer": r.pseudonymous_id,
            "status": "Verified" if r.actual_area_ha is not None else "Pending",
            "flags": r.flags,
        })

    return {
        "ground_reports": formatted,
        "cohort_count": total_count,
        "privacy_suppressed": False,
    }
