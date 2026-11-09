"""
Alerts Routes Module for GoviSense
Provides in-app multilingual alerts, acknowledgments, and farmer inquiry endpoints (Task 10).
Languages supported: English (en), Sinhala (si), Tamil (ta).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from govisense.db.session import get_db, get_db_session
from govisense.db.models import Alert, AlertInteraction
from govisense.api.auth import require_officer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

TEMPLATES_PATH = Path(__file__).resolve().parent.parent.parent / "i18n" / "templates.json"


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class AlertAcknowledgeRequest(BaseModel):
    farmer_id: str = Field(..., description="Pseudonymous farmer identifier")


class AlertQuestionRequest(BaseModel):
    farmer_id: str = Field(..., description="Pseudonymous farmer identifier")
    question: str = Field(..., description="Farmer question or clarification to agrarian officer")


class CreateAlertPayload(BaseModel):
    alert_id: Optional[str] = None
    crop_id: str
    severity: str = "warning"  # "info", "warning", "critical"
    target_role: str = "all"   # "farmer", "officer", "all"
    title_en: str
    title_si: Optional[str] = None
    title_ta: Optional[str] = None
    message_en: str
    message_si: Optional[str] = None
    message_ta: Optional[str] = None


# ---------------------------------------------------------------------------
# Alert Seed Helper
# ---------------------------------------------------------------------------

def seed_alerts_from_templates(session: Optional[Session] = None) -> int:
    """
    Seeds baseline multilingual alerts from i18n/templates.json if missing from DB.
    """
    if not TEMPLATES_PATH.exists():
        logger.warning(f"Templates file not found at: {TEMPLATES_PATH}")
        return 0

    try:
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            templates = data.get("templates", [])
    except Exception as e:
        logger.error(f"Error reading templates.json: {e}")
        return 0

    close_session = False
    if session is None:
        db = next(get_db())
        close_session = True
    else:
        db = session

    try:
        existing_ids = {a.alert_id for a in db.query(Alert.alert_id).all()}
        added_count = 0
        for t in templates:
            a_id = t["template_id"]
            if a_id not in existing_ids:
                alert = Alert(
                    alert_id=a_id,
                    crop_id=t.get("crop_id", "all"),
                    severity=t.get("severity", "warning"),
                    target_role=t.get("target_role", "all"),
                    title_en=t.get("title_en", ""),
                    title_si=t.get("title_si"),
                    title_ta=t.get("title_ta"),
                    message_en=t.get("message_en", ""),
                    message_si=t.get("message_si"),
                    message_ta=t.get("message_ta"),
                    status="active",
                )
                db.add(alert)
                added_count += 1
        if added_count > 0:
            db.commit()
            logger.info(f"Seeded {added_count} multilingual alerts from templates.json.")
        return added_count
    finally:
        if close_session:
            db.close()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("")
def list_alerts(
    crop_id: Optional[str] = Query(None, description="Filter by crop (e.g. 'big_onion', 'chilli')"),
    severity: Optional[str] = Query(None, description="Filter by severity ('info', 'warning', 'critical')"),
    target_role: Optional[str] = Query(None, description="Filter by role ('farmer', 'officer', 'all')"),
    lang: str = Query("en", description="Preferred localization language ('en', 'si', 'ta')"),
    farmer_id: Optional[str] = Query(None, description="Optional farmer ID to include acknowledgment status"),
    db: Session = Depends(get_db),
):
    """
    Returns active localized alerts in English, Sinhala, or Tamil.
    Optionally decorates each alert with the farmer's interaction state.
    """
    query = db.query(Alert).filter(Alert.status == "active")
    if crop_id and crop_id != "all":
        query = query.filter((Alert.crop_id == crop_id) | (Alert.crop_id == "all"))
    if severity:
        query = query.filter(Alert.severity == severity)
    if target_role and target_role != "all":
        query = query.filter((Alert.target_role == target_role) | (Alert.target_role == "all"))

    alerts = query.order_by(Alert.created_at.desc()).all()

    # Look up interactions if farmer_id provided
    acknowledged_set = set()
    questions_map = {}
    if farmer_id:
        interactions = (
            db.query(AlertInteraction)
            .filter(AlertInteraction.farmer_id == farmer_id)
            .all()
        )
        for inter in interactions:
            if inter.acknowledged:
                acknowledged_set.add(inter.alert_id)
            if inter.question:
                questions_map[inter.alert_id] = {
                    "question": inter.question,
                    "officer_response": inter.officer_response,
                }

    results = []
    for a in alerts:
        d = a.to_dict(lang=lang)
        d["acknowledged"] = a.alert_id in acknowledged_set
        d["inquiry"] = questions_map.get(a.alert_id)
        results.append(d)

    return {
        "total": len(results),
        "language": lang,
        "alerts": results,
        "data_available": True,
        "is_demo": False,
        "source_type": "alerts_system",
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
):
    """
    Marks an alert as acknowledged by a farmer (Task 10 & 16).
    """
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found.",
        )

    interaction = (
        db.query(AlertInteraction)
        .filter(
            AlertInteraction.alert_id == alert_id,
            AlertInteraction.farmer_id == payload.farmer_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)
    if interaction:
        interaction.acknowledged = True
        interaction.updated_at = now
    else:
        interaction = AlertInteraction(
            alert_id=alert_id,
            farmer_id=payload.farmer_id,
            acknowledged=True,
            created_at=now,
            updated_at=now,
        )
        db.add(interaction)

    db.commit()
    return {
        "status": "ACKNOWLEDGED",
        "alert_id": alert_id,
        "farmer_id": payload.farmer_id,
        "acknowledged": True,
        "timestamp": now.isoformat(),
        "data_available": True,
        "is_demo": False,
        "source_type": "alert_interaction",
    }


@router.post("/{alert_id}/ask")
def ask_officer_question(
    alert_id: str,
    payload: AlertQuestionRequest,
    db: Session = Depends(get_db),
):
    """
    Allows a farmer to submit an inquiry to field officers regarding an alert (Task 16).
    """
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found.",
        )

    interaction = (
        db.query(AlertInteraction)
        .filter(
            AlertInteraction.alert_id == alert_id,
            AlertInteraction.farmer_id == payload.farmer_id,
        )
        .first()
    )

    now = datetime.now(timezone.utc)
    if interaction:
        interaction.question = payload.question
        interaction.updated_at = now
    else:
        interaction = AlertInteraction(
            alert_id=alert_id,
            farmer_id=payload.farmer_id,
            acknowledged=False,
            question=payload.question,
            created_at=now,
            updated_at=now,
        )
        db.add(interaction)

    db.commit()
    return {
        "status": "SUBMITTED",
        "alert_id": alert_id,
        "farmer_id": payload.farmer_id,
        "question": payload.question,
        "timestamp": now.isoformat(),
        "data_available": True,
        "is_demo": False,
        "source_type": "alert_inquiry",
    }


@router.post("", dependencies=[Depends(require_officer)])
def create_alert(
    payload: CreateAlertPayload,
    db: Session = Depends(get_db),
):
    """
    Officer or Admin creates a new multilingual alert.
    Protected: requires 'officer' or 'admin' role.
    """
    alert_id = payload.alert_id or f"ALT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    new_alert = Alert(
        alert_id=alert_id,
        crop_id=payload.crop_id,
        severity=payload.severity,
        target_role=payload.target_role,
        title_en=payload.title_en,
        title_si=payload.title_si,
        title_ta=payload.title_ta,
        message_en=payload.message_en,
        message_si=payload.message_si,
        message_ta=payload.message_ta,
        status="active",
    )
    db.add(new_alert)
    db.commit()
    return {
        "status": "CREATED",
        "alert": new_alert.to_dict(),
        "data_available": True,
        "is_demo": False,
        "source_type": "alerts_system",
    }

