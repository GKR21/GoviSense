"""
Confidence Badge & Decision History Audit Module (Item 8)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  1. Multi-factor Confidence Badge evaluation rules:
     - Data recency / age
     - Area-reported share
     - Model beats statistical baseline on WAPE
     - SPI validation pass
     - Soil data present
  2. Audit Decision History Store:
     - Saves model version, data version, key assumptions, officer actions per run.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Any, List, Optional

from govisense.config import PROCESSED_DATA_DIR
from govisense.db.session import get_session, init_db
from govisense.db.models import DecisionRecordModel


_DEFAULT_HISTORY_PATH = PROCESSED_DATA_DIR / "decision_history.json"


# ---------------------------------------------------------------------------
# Confidence Badge Evaluator
# ---------------------------------------------------------------------------

@dataclass
class ConfidenceBadgeEvaluation:
    crop_id: str
    badge: str                 # "high", "medium", "low"
    score_pct: float          # 0 to 100%
    data_fresh: bool
    area_reported_share_adequate: bool
    model_beats_baseline: bool
    spi_validation_passed: bool
    soil_data_present: bool
    reasons: List[str]


def evaluate_confidence_badge(
    crop_id: str,
    data_age_days: int = 15,
    area_reported_share: float = 0.35,  # 35% of district target reported
    model_wape: float = 0.15,
    baseline_wape: float = 0.20,
    spi_validated: bool = True,
    soil_ph_available: bool = True,
) -> ConfidenceBadgeEvaluation:
    """
    Evaluates confidence badge based on 5 rigorous operational rules:
      1. Data age: <= 45 days fresh.
      2. Area reported share: >= 20% of district land confirmed by farmers.
      3. Model beats baseline: model WAPE < baseline WAPE.
      4. SPI validation pass: economic price inverse correlation confirmed.
      5. Soil test data present: lab/agronomic soil pH data available.
    """
    reasons = []

    # Rule 1: Data age
    data_fresh = data_age_days <= 45
    if data_fresh:
        reasons.append(f"Data is fresh ({data_age_days} days old, limit 45 days).")
    else:
        reasons.append(f"Data is aging ({data_age_days} days old, exceeds 45 days limit).")

    # Rule 2: Area reported share
    area_ok = area_reported_share >= 0.20
    if area_ok:
        reasons.append(f"Ground acreage coverage adequate ({area_reported_share*100:.1f}% reported, min 20%).")
    else:
        reasons.append(f"Low ground coverage ({area_reported_share*100:.1f}% reported, below 20% threshold).")

    # Rule 3: Model beats baseline
    model_ok = model_wape < baseline_wape
    if model_ok:
        reasons.append(f"Production model beats baseline (WAPE {model_wape:.3f} vs baseline {baseline_wape:.3f}).")
    else:
        reasons.append(f"Serving statistical baseline (Model WAPE {model_wape:.3f} >= baseline {baseline_wape:.3f}).")

    # Rule 4: SPI validation
    spi_ok = bool(spi_validated)
    if spi_ok:
        reasons.append("SPI thesis verified against historical price changes.")
    else:
        reasons.append("SPI thesis unverified or price pressure did not follow SPI.")

    # Rule 5: Soil data
    soil_ok = bool(soil_ph_available)
    if soil_ok:
        reasons.append("Site soil pH agronomic data verified.")
    else:
        reasons.append("Soil pH missing — soil suitability component estimated.")

    passed_rules = sum([data_fresh, area_ok, model_ok, spi_ok, soil_ok])
    score_pct = round((passed_rules / 5.0) * 100.0, 1)

    # Decouple chilli if SPI unverified
    if crop_id == "chilli" and not spi_ok:
        badge = "low"
    elif passed_rules >= 4 and data_fresh:
        badge = "high"
    elif passed_rules >= 2:
        badge = "medium"
    else:
        badge = "low"

    return ConfidenceBadgeEvaluation(
        crop_id=crop_id,
        badge=badge,
        score_pct=score_pct,
        data_fresh=data_fresh,
        area_reported_share_adequate=area_ok,
        model_beats_baseline=model_ok,
        spi_validation_passed=spi_ok,
        soil_data_present=soil_ok,
        reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Decision History Store
# ---------------------------------------------------------------------------

@dataclass
class DecisionRecord:
    """Audit log entry for officer policy decisions and pipeline runs."""
    crop_id: str
    season: str
    officer_id: str
    action_type: str        # e.g. "PLANT_EXPANSION", "HOLD_STORAGE", "DEFER_IMPORT", "MAINTAIN"
    quantity: float
    unit: str
    rationale: str
    model_version: str = "GoviSense v2.0"
    data_version: str = "Harti-DoA-2024.12"
    assumptions: Dict[str, Any] = field(default_factory=lambda: {
        "loss_pct": 0.15,
        "safety_buffer": 0.05,
        "spi_bands": 0.15,
        "max_single_crop_share": 0.60,
    })
    decision_id: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class DecisionHistoryStore:
    """
    Persistent audit ledger for decisions, assumptions, and model runs.
    Saves to PostgreSQL (or SQLite fallback) as primary storage,
    maintaining a synced JSON audit snapshot file.
    """

    def __init__(self, storage_path: Optional[Path] = None, sync_db: Optional[bool] = None):
        self.storage_path = storage_path or _DEFAULT_HISTORY_PATH
        self.sync_db = sync_db if sync_db is not None else (storage_path is None)
        self._records: List[DecisionRecord] = []
        if self.sync_db:
            try:
                init_db()
            except Exception:
                pass
        self._load()

    def _load(self) -> None:
        # 1. Try loading from PostgreSQL database if sync_db enabled
        loaded_from_db = False
        if self.sync_db:
            try:
                with get_session() as session:
                    db_records = session.query(DecisionRecordModel).order_by(DecisionRecordModel.timestamp.desc()).all()
                    if db_records:
                        self._records = [
                            DecisionRecord(
                                crop_id=r.crop_id,
                                season=r.season,
                                officer_id=r.officer_id,
                                action_type=r.action_type,
                                quantity=float(r.quantity),
                                unit=r.unit,
                                rationale=r.rationale,
                                model_version=r.model_version,
                                data_version=r.data_version,
                                assumptions=r.assumptions or {},
                                decision_id=r.decision_id,
                                timestamp=r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
                            )
                            for r in db_records
                        ]
                        loaded_from_db = True
            except Exception:
                loaded_from_db = False

        # 2. If DB was empty or failed, load from JSON file snapshot
        if not loaded_from_db and self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self._records = [DecisionRecord(**item) for item in raw_data]
                    if self.sync_db:
                        self._sync_to_db()
            except Exception:
                self._records = []

    def _sync_to_db(self) -> None:
        """Seed DB with in-memory records."""
        if not self.sync_db:
            return
        try:
            with get_session() as session:
                for r in self._records:
                    ts = None
                    if r.timestamp:
                        try:
                            ts = datetime.fromisoformat(r.timestamp.replace("Z", "+00:00"))
                        except Exception:
                            ts = datetime.now(timezone.utc)
                    else:
                        ts = datetime.now(timezone.utc)
                    db_model = DecisionRecordModel(
                        decision_id=r.decision_id,
                        crop_id=r.crop_id,
                        season=r.season,
                        officer_id=r.officer_id,
                        action_type=r.action_type,
                        quantity=r.quantity,
                        unit=r.unit,
                        rationale=r.rationale,
                        model_version=r.model_version,
                        data_version=r.data_version,
                        assumptions=r.assumptions,
                        timestamp=ts,
                    )
                    session.merge(db_model)
                session.commit()
        except Exception:
            pass

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self._records], f, indent=2)

    def log_decision(self, record: DecisionRecord) -> Dict[str, Any]:
        """Record an officer action with snapshot of model version and assumptions."""
        self._records.append(record)
        self._save()

        # Persist to PostgreSQL database
        if self.sync_db:
            try:
                with get_session() as session:
                    ts = None
                    if record.timestamp:
                        try:
                            ts = datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))
                        except Exception:
                            ts = datetime.now(timezone.utc)
                    else:
                        ts = datetime.now(timezone.utc)
                    db_model = DecisionRecordModel(
                        decision_id=record.decision_id,
                        crop_id=record.crop_id,
                        season=record.season,
                        officer_id=record.officer_id,
                        action_type=record.action_type,
                        quantity=record.quantity,
                        unit=record.unit,
                        rationale=record.rationale,
                        model_version=record.model_version,
                        data_version=record.data_version,
                        assumptions=record.assumptions,
                        timestamp=ts,
                    )
                    session.merge(db_model)
                    session.commit()
            except Exception:
                pass

        return {
            "status": "RECORDED",
            "decision_id": record.decision_id,
            "crop_id": record.crop_id,
            "action_type": record.action_type,
            "timestamp": record.timestamp,
        }

    def list_decisions(
        self,
        crop_id: Optional[str] = None,
        season: Optional[str] = None,
        limit: int = 50,
    ) -> List[DecisionRecord]:
        """List historical decisions, newest first."""
        if self.sync_db:
            try:
                with get_session() as session:
                    q = session.query(DecisionRecordModel)
                    if crop_id:
                        q = q.filter(DecisionRecordModel.crop_id == crop_id)
                    if season:
                        q = q.filter(DecisionRecordModel.season == season)
                    rows = q.order_by(DecisionRecordModel.timestamp.desc()).limit(limit).all()
                    if rows:
                        return [
                            DecisionRecord(
                                crop_id=r.crop_id,
                                season=r.season,
                                officer_id=r.officer_id,
                                action_type=r.action_type,
                                quantity=float(r.quantity),
                                unit=r.unit,
                                rationale=r.rationale,
                                model_version=r.model_version,
                                data_version=r.data_version,
                                assumptions=r.assumptions or {},
                                decision_id=r.decision_id,
                                timestamp=r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
                            )
                            for r in rows
                        ]
            except Exception:
                pass

        records = self._records
        if crop_id:
            records = [r for r in records if r.crop_id == crop_id]
        if season:
            records = [r for r in records if r.season == season]
        records = sorted(records, key=lambda r: r.timestamp, reverse=True)
        lim = int(limit) if isinstance(limit, int) else 50
        return records[:lim]

