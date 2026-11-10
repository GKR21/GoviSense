"""
Officer Governance, Simulations, and Decision Ledger Router
Team DARKBITE · ModelX 2.0 Proposal Specification
Implements policy logging, what-if sandbox simulation, and full run traceability.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from govisense.api.deps import get_db, require_officer
from govisense.config import settings
from govisense.db.lookups import (
    ensure_crop_exists,
    ensure_officer,
    ensure_pipeline_run,
    normalize_decision_action,
    resolve_season_id,
)
from govisense.db.session import get_session
from govisense.db.models import (
    PipelineRunModel,
    DecisionRecordModel,
    ForecastSnapshotModel,
    OfficerModel,
    SeasonModel,
    compute_sha256_hash,
)
from govisense.db.history import DecisionHistoryStore, DecisionRecord
from govisense.provenance import compute_data_version, compute_model_version, get_git_commit

logger = logging.getLogger("govisense.api.officer")
router = APIRouter(prefix="", tags=["Officer Operations"])

decision_store = DecisionHistoryStore()


class SimulationRequest(BaseModel):
    crop: str
    custom_planted_extent_ha: Optional[float] = None
    custom_yield_mt_ha: Optional[float] = None
    custom_import_volume_mt: Optional[float] = None
    custom_loss_pct: Optional[float] = None
    custom_glut_ratio_threshold: Optional[float] = None
    custom_shortage_ratio_threshold: Optional[float] = None


class DecisionPayload(BaseModel):
    crop_id: str
    season: str
    officer_id: str
    action_type: str
    quantity: float
    unit: str = "MT"
    rationale: str
    model_recommended_action: Optional[str] = None
    officer_response: str = "accepted"
    run_id: Optional[str] = None


@router.post("/api/simulate", dependencies=[Depends(require_officer)])
def simulate_scenario(req: SimulationRequest):
    """
    Officer What-If Sandbox: simulate custom acreage, yield, loss, and import scenarios.
    Computes SPI ratio live using primary formula S / D with configurable bands.
    """
    from govisense.models.a3_supply_pressure import SupplyPressureEngine
    from govisense.models.demand_estimator import DemandEstimator

    crop = req.crop
    if crop not in settings.crops:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported crop '{crop}'. Valid crops: {list(settings.crops.keys())}",
        )

    # Base agronomic defaults
    area_ha = req.custom_planted_extent_ha if req.custom_planted_extent_ha is not None else 1800.0
    yield_mt = req.custom_yield_mt_ha if req.custom_yield_mt_ha is not None else 15.0
    loss_val = req.custom_loss_pct if req.custom_loss_pct is not None else 0.15
    import_vol = req.custom_import_volume_mt if req.custom_import_volume_mt is not None else 0.0

    sim_supply = area_ha * yield_mt * (1.0 - loss_val)

    spi_engine = SupplyPressureEngine()
    spi_res = spi_engine.compute_spi(
        crop=crop,
        forecast_supply_mt=sim_supply,
        month=8,
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

    return {
        "crop": crop,
        "simulated_supply_mt": round(sim_supply, 1),
        "simulated_spi": spi_res.spi_score,
        "simulated_spi_ratio": spi_res.spi_ratio,
        "primary_spi_ratio": spi_res.spi_ratio,
        "simulated_label": spi_res.spi_label,
        "primary_spi_label": spi_res.spi_label,
        "simulated_gap_mt": spi_res.gap_mt,
        "area_ha": area_ha,
        "yield_mt_ha": yield_mt,
        "loss_pct": loss_val,
        "import_volume_mt": import_vol,
        "scenarios": scenarios_data,
        "run_id": f"RUN-{g_commit[:7]}",
        "data_version": d_ver,
        "model_version": m_ver,
        "data_quality": "real",
        "data_available": True,
        "is_demo": False,
        "source_type": "scenario_simulation",
        "served_model": "LightGBM + Baseline Selector",
        "assumptions_ref": "docs/assumptions.md",
    }


@router.post("/api/decide")
@router.post("/api/decision/history")
def record_officer_decision(
    payload: DecisionPayload,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_officer),
):
    """
    Officer Decision Ledger (Proposal 3.1 & 7.2):
    Records policy action with cryptographic SHA-256 hash across inputs, versions, and assumptions.
    Links decision directly to pipeline run_id.
    """
    # Verify officer exists or create record
    officer_id = payload.officer_id or (current_user.get("officer_id") if current_user else "OFF-001")
    ensure_officer(
        db,
        officer_id=officer_id,
        name=current_user.get("name", "Officer in Charge") if current_user else "Officer in Charge",
        district="Anuradhapura",
        role="Agricultural Extension Officer",
    )

    m_ver = compute_model_version()
    d_ver = compute_data_version()
    assumptions = {
        "loss_pct": 0.15,
        "import_lead_weeks": settings.import_lead_time_weeks.get(payload.crop_id, 7),
        "spi_bands": [0.8, 1.2],
        "cif_colombo": settings.cif_colombo_rs_per_mt.get(payload.crop_id, 140000.0),
    }

    run_id = payload.run_id
    if not run_id:
        latest_run = db.query(PipelineRunModel).order_by(PipelineRunModel.created_at.desc()).first()
        run_id = latest_run.run_id if latest_run else f"RUN-{get_git_commit()[:7]}"
    run_id = ensure_pipeline_run(
        db,
        run_id=run_id,
        trigger_type="api",
        model_version=m_ver,
        data_version=d_ver,
        assumptions=assumptions,
    )

    cid = ensure_crop_exists(db, payload.crop_id)
    season_id = resolve_season_id(db, payload.season)
    action_code = normalize_decision_action(payload.action_type) or "NO_ACTION"
    rec_action = normalize_decision_action(payload.model_recommended_action)
    resp_val = payload.officer_response if payload.officer_response in ("accepted", "modified", "rejected") else "accepted"

    hash_payload = {
        "crop_id": cid,
        "season": payload.season,
        "officer_id": officer_id,
        "action_type": action_code,
        "quantity": payload.quantity,
        "model_version": m_ver,
        "data_version": d_ver,
        "assumptions": assumptions,
    }
    record_hash = compute_sha256_hash(hash_payload)

    decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc)

    db_decision = DecisionRecordModel(
        decision_id=decision_id,
        run_id=run_id,
        record_hash=record_hash,
        crop_id=cid,
        season_id=season_id,
        officer_id=officer_id,
        model_recommended_action=rec_action,
        officer_response=resp_val,
        action_type=action_code,
        quantity=payload.quantity,
        unit=payload.unit,
        rationale=payload.rationale,
        decided_at=now,
    )
    db.add(db_decision)
    db.commit()

    return {
        "status": "RECORDED",
        "decision_id": decision_id,
        "run_id": run_id,
        "record_hash": record_hash,
        "action_type": action_code,
        "quantity": payload.quantity,
        "timestamp": now.isoformat(),
    }


@router.get("/api/decisions")
@router.get("/api/decision/history")
def list_decisions(
    crop_id: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_officer),
):
    """
    Retrieve historical officer decisions with cryptographic audit hashes and version provenance.
    """
    if not isinstance(db, Session):
        db = get_session()
    eff_crop = crop_id if isinstance(crop_id, str) else None
    eff_season = season if isinstance(season, str) else None
    eff_limit = limit if isinstance(limit, int) else getattr(limit, "default", 50)
    q = db.query(DecisionRecordModel)
    if eff_crop:
        q = q.filter(DecisionRecordModel.crop_id == eff_crop)
    if eff_season:
        q = q.join(SeasonModel).filter(SeasonModel.label == eff_season)

    records = q.order_by(DecisionRecordModel.decided_at.desc()).limit(eff_limit).all()
    return [r.to_dict() for r in records]


@router.get("/api/runs")
def list_runs(
    limit: int = Query(20, ge=1, le=100),
    db: Any = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_officer),
):
    """
    Dashboard Screen: Run Traceability
    Lists pipeline executions with git commit, model version, and exact assumptions snapshot.
    """
    if not isinstance(db, Session):
        db = get_session()
    eff_limit = limit if isinstance(limit, int) else getattr(limit, "default", 20)
    runs = db.query(PipelineRunModel).order_by(PipelineRunModel.created_at.desc()).limit(eff_limit).all()
    if not runs:
        baseline_run = PipelineRunModel(
            run_id=f"RUN-{get_git_commit()[:7]}",
            trigger_type="api",
            model_version=compute_model_version(),
            data_version=compute_data_version(),
            assumptions={
                "loss_pct": 0.15,
                "import_lead_weeks": 7,
                "spi_glut_threshold": 1.2,
                "spi_shortage_threshold": 0.8,
            },
            git_commit=get_git_commit()[:40],
        )
        db.add(baseline_run)
        db.commit()
        runs = [baseline_run]

    return [r.to_dict() for r in runs]


@router.get("/api/runs/{run_id}")
def get_run_detail(
    run_id: str,
    db: Any = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(require_officer),
):
    """
    Fetches full audit details of a specific pipeline execution run.
    """
    if not isinstance(db, Session):
        db = get_session()
    run = db.query(PipelineRunModel).filter(PipelineRunModel.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")

    data = run.to_dict()
    data["forecast_count"] = db.query(ForecastSnapshotModel).filter(ForecastSnapshotModel.run_id == run_id).count()
    data["decision_count"] = db.query(DecisionRecordModel).filter(DecisionRecordModel.run_id == run_id).count()
    data["snapshots"] = [s.to_dict() for s in run.forecasts]
    data["decisions"] = [d.to_dict() for d in run.decisions]
    return data


# Backwards compatibility aliases
list_pipeline_runs = list_runs
get_pipeline_run_detail = get_run_detail
get_officer_decision_history = list_decisions
save_decision_action = record_officer_decision


@router.get("/api/confidence/badge")
def get_confidence_badge(
    crop_id: str = Query("big_onion"),
    data_age_days: int = Query(15),
    area_reported_share: float = Query(0.35),
    soil_ph_available: bool = Query(True),
):
    """
    Multi-factor confidence badge evaluation using the 5 operational rules.
    """
    from govisense.api import main as api_main
    return api_main.get_confidence_badge(
        crop_id=crop_id,
        data_age_days=data_age_days,
        area_reported_share=area_reported_share,
        soil_ph_available=soil_ph_available,
    )

