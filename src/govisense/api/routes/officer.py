"""
Field Officer & Policy Decision Routes for GoviSense (Task 11)
Provides audit decision logging, confidence badge assessment, and policy simulation.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query

from govisense.api.auth import require_officer
from govisense.api.schemas import (
    DecisionLogPayload,
    SimulationRequest,
    ReTriggerPayload,
)

router = APIRouter(tags=["Officer & Policy"])


@router.post("/api/history/log-action", dependencies=[Depends(require_officer)])
def log_officer_action(payload: DecisionLogPayload):
    """
    Saves an officer action with model version, data version, assumptions, and hash snapshot.
    Protected: requires 'officer' or 'admin' role.
    """
    from govisense.api import main as api_main
    return api_main.log_officer_action(payload)


@router.get("/api/history/decisions")
def get_decision_history(
    crop_id: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """
    Retrieves audit decision log records with run_id, hash, model, and assumption snapshots.
    """
    from govisense.api import main as api_main
    return api_main.get_decision_history(crop_id=crop_id, season=season, limit=limit)


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


@router.post("/api/simulate", dependencies=[Depends(require_officer)])
def simulate_scenario(req: SimulationRequest):
    """
    Allows agricultural officers to simulate acreage, yield, loss, and import scenarios.
    Protected: requires 'officer' or 'admin' role.
    """
    from govisense.api import main as api_main
    return api_main.simulate_scenario(req)

