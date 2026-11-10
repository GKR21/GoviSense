"""
Feedback Loop Module (WP7 / Item 7)
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)

Enables farmers and ground agricultural officers to submit actual planting reports.
Database-backed (SQLite with WAL or PostgreSQL) with concurrent-write safety.
On report ingestion:
  1. Validates farmer consent and pseudonymous ID.
  2. Records report with ACID transaction and thread safety.
  3. Re-triggers SPI and Target Area Calculator (A_rec).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("govisense.feedback")

from govisense.config import PROCESSED_DATA_DIR, settings
from govisense.db.session import get_session, get_db_session, sqlite_write_lock, init_db
from govisense.db.models import PlantingReportModel
from govisense.models.target_area import TargetAreaCalculator, TargetAreaResult
from govisense.models.a3_supply_pressure import SupplyPressureEngine, SPIResult
from govisense.models.demand_estimator import DemandEstimator
from govisense.data.crop_requirements import get_crop_requirements


_DEFAULT_STORE_PATH = PROCESSED_DATA_DIR / "planting_reports.json"


@dataclass
class PlantingReport:
    """Farmer or Field Officer planting report submission."""
    crop_id: str
    season: str
    planned_area_ha: float
    actual_area_ha: float
    consent_given: bool
    pseudonymous_id: str
    harvest_outcome_mt: Optional[float] = None
    sale_price_rs_kg: Optional[float] = None
    sale_channel: Optional[str] = None
    notes: Optional[str] = None
    report_id: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.report_id:
            self.report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ReTriggerResult:
    """Output of pipeline re-trigger after incorporating new planting reports."""
    crop_id: str
    season: str
    total_reported_ha: float
    previous_target_ha: float
    new_a_rec_ha: float
    previous_spi: float
    new_spi: float
    previous_spi_label: str
    new_spi_label: str
    oversupply_stop_triggered: bool
    action_summary: str


REGISTRY_VERIFICATION_NOTE = (
    "NOTE: Live national farmer registry verification with the Department of Agrarian Development "
    "(DAD) / Agrarian Services Department is documented as future work for Phase 3. "
    "Current pilot verification relies on pseudonymous ID consistency, local sliding-window rate limiting, "
    "and duplicate report rejection."
)


class PlantingReportStore:
    """
    Persistent storage for planting reports in PostgreSQL (or SQLite fallback),
    with synced JSON snapshot and pipeline re-triggering.
    """

    def __init__(self, storage_path: Optional[Path] = None, sync_db: Optional[bool] = None):
        self.storage_path = storage_path or _DEFAULT_STORE_PATH
        self.sync_db = sync_db if sync_db is not None else (storage_path is None)
        self._use_db = self.sync_db
        self._reports: List[PlantingReport] = []
        self._rate_limits: Dict[str, List[float]] = {}
        if self.sync_db:
            try:
                init_db()
            except Exception:
                pass
        self._load()

    def check_rate_limit(
        self,
        pseudonymous_id: str,
        max_requests: int = 5,
        window_seconds: float = 60.0,
    ) -> None:
        """
        Enforces local sliding-window rate limiting per farmer ID (Task 12).
        Raises ValueError if farmer exceeds max_requests within window_seconds.
        """
        now = datetime.now(timezone.utc).timestamp()
        timestamps = self._rate_limits.setdefault(pseudonymous_id, [])
        valid_timestamps = [t for t in timestamps if now - t < window_seconds]
        if len(valid_timestamps) >= max_requests:
            self._rate_limits[pseudonymous_id] = valid_timestamps
            raise ValueError(
                f"Rate limit exceeded: farmer '{pseudonymous_id}' exceeded {max_requests} submissions per minute."
            )
        valid_timestamps.append(now)
        self._rate_limits[pseudonymous_id] = valid_timestamps

    def check_duplicate(self, report: PlantingReport) -> None:
        """
        Rejects duplicate planting reports for the same farmer, crop, season, and area (Task 12).
        """
        if self.sync_db:
            with get_db_session() as db:
                existing = (
                    db.query(PlantingReportModel)
                    .filter(
                        PlantingReportModel.pseudonymous_id == report.pseudonymous_id,
                        PlantingReportModel.crop_id == report.crop_id,
                        PlantingReportModel.season == report.season,
                        PlantingReportModel.actual_area_ha == report.actual_area_ha,
                    )
                    .first()
                )
                if existing:
                    raise ValueError(
                        f"Duplicate planting report detected for farmer '{report.pseudonymous_id}', "
                        f"crop '{report.crop_id}', season '{report.season}', area {report.actual_area_ha} ha."
                    )
        else:
            for existing in self._reports:
                if (
                    existing.pseudonymous_id == report.pseudonymous_id
                    and existing.crop_id == report.crop_id
                    and existing.season == report.season
                    and existing.actual_area_ha == report.actual_area_ha
                ):
                    raise ValueError(
                        f"Duplicate planting report detected for farmer '{report.pseudonymous_id}', "
                        f"crop '{report.crop_id}', season '{report.season}', area {report.actual_area_ha} ha."
                    )

    def _load(self) -> None:
        # 1. Try loading from PostgreSQL database if sync_db is enabled
        loaded_from_db = False
        if self.sync_db:
            try:
                with get_session() as session:
                    db_reports = session.query(PlantingReportModel).order_by(PlantingReportModel.timestamp.desc()).all()
                    if db_reports:
                        self._reports = [
                            PlantingReport(
                                crop_id=r.crop_id,
                                season=r.season,
                                planned_area_ha=float(r.planned_area_ha or 0.0),
                                actual_area_ha=float(r.actual_area_ha or 0.0),
                                consent_given=bool(r.consent_given),
                                pseudonymous_id=r.pseudonymous_id,
                                harvest_outcome_mt=getattr(r, "harvest_outcome_mt", None),
                                sale_price_rs_kg=getattr(r, "sale_price_rs_kg", None),
                                sale_channel=getattr(r, "sale_channel", None),
                                notes=r.notes,
                                report_id=r.report_id,
                                timestamp=r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
                            )
                            for r in db_reports
                        ]
                        loaded_from_db = True
            except Exception:
                loaded_from_db = False

        # 2. If DB is empty, load from JSON file and sync to DB
        if not loaded_from_db and self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self._reports = [PlantingReport(**item) for item in raw_data]
                    if self.sync_db:
                        self._sync_to_db()
            except Exception:
                self._reports = []

    def _sync_to_db(self) -> None:
        """Seed DB from in-memory reports."""
        if not self.sync_db:
            return
        try:
            with get_session() as session:
                for r in self._reports:
                    ts = None
                    if r.timestamp:
                        try:
                            ts = datetime.fromisoformat(r.timestamp.replace("Z", "+00:00"))
                        except Exception:
                            ts = datetime.now(timezone.utc)
                    else:
                        ts = datetime.now(timezone.utc)
                    model = PlantingReportModel(
                        report_id=r.report_id,
                        crop_id=r.crop_id,
                        season=r.season,
                        planned_area_ha=r.planned_area_ha,
                        actual_area_ha=r.actual_area_ha,
                        consent_given=r.consent_given,
                        pseudonymous_id=r.pseudonymous_id,
                        harvest_outcome_mt=r.harvest_outcome_mt,
                        sale_price_rs_kg=r.sale_price_rs_kg,
                        sale_channel=r.sale_channel,
                        notes=r.notes,
                        timestamp=ts,
                    )
                    session.merge(model)
                session.commit()
        except Exception:
            pass

    def _save(self) -> None:
        if self.sync_db:
            return  # Production path: DB only, no runtime write to json
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self._reports], f, indent=2)

    def submit_report(self, report: PlantingReport) -> Dict[str, Any]:
        """
        Validates and records a planting report with concurrent-write safety.
        Strict privacy rule: consent must be explicitly given.
        Enforces farmer ID rate limiting and duplicate-report detection (Task 12).
        Note: Verification against the DAD national registry is slated as future work.
        """
        if not report.consent_given:
            raise ValueError(
                "Consent is required: farmer data cannot be collected or used without explicit consent."
            )
        if report.actual_area_ha < 0 or report.planned_area_ha < 0:
            raise ValueError("Planted areas cannot be negative.")
        if not report.pseudonymous_id or not report.pseudonymous_id.strip():
            raise ValueError("A pseudonymous ID is required for auditability and privacy.")

        with sqlite_write_lock:
            # 1. Rate limiting check (Task 12)
            self.check_rate_limit(report.pseudonymous_id)

            # 2. Duplicate report check (Task 12)
            self.check_duplicate(report)

            if self.sync_db:
                with get_db_session() as db:
                    ts = None
                    if report.timestamp:
                        try:
                            ts = datetime.fromisoformat(report.timestamp.replace("Z", "+00:00"))
                        except Exception:
                            ts = datetime.now(timezone.utc)
                    else:
                        ts = datetime.now(timezone.utc)
                    model = PlantingReportModel(
                        report_id=report.report_id,
                        crop_id=report.crop_id,
                        season=report.season,
                        planned_area_ha=report.planned_area_ha,
                        actual_area_ha=report.actual_area_ha,
                        consent_given=report.consent_given,
                        pseudonymous_id=report.pseudonymous_id,
                        harvest_outcome_mt=report.harvest_outcome_mt,
                        sale_price_rs_kg=report.sale_price_rs_kg,
                        sale_channel=report.sale_channel,
                        notes=report.notes,
                        timestamp=ts,
                    )
                    db.merge(model)
                    db.commit()
            else:
                self._reports.append(report)
                self._save()

        total_actual = self.get_total_reported_area(report.crop_id, report.season)
        return {
            "status": "ACCEPTED",
            "report_id": report.report_id,
            "crop_id": report.crop_id,
            "season": report.season,
            "actual_area_ha": report.actual_area_ha,
            "cumulative_reported_ha": total_actual,
            "timestamp": report.timestamp,
            "registry_verification_note": REGISTRY_VERIFICATION_NOTE,
            "data_available": True,
            "is_demo": False,
            "source_type": "farmer_field_report",
        }

    def get_reports(
        self,
        crop_id: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[PlantingReport]:
        """Retrieve stored reports, optionally filtered by crop and season."""
        # Query PostgreSQL database
        if self.sync_db:
            try:
                with get_session() as session:
                    q = session.query(PlantingReportModel)
                    if crop_id:
                        q = q.filter(PlantingReportModel.crop_id == crop_id)
                    if season:
                        q = q.filter(PlantingReportModel.season == season)
                    db_rows = q.order_by(PlantingReportModel.timestamp.desc()).all()
                    return [
                        PlantingReport(
                            crop_id=r.crop_id,
                            season=r.season,
                            planned_area_ha=float(r.planned_area_ha or 0.0),
                            actual_area_ha=float(r.actual_area_ha or 0.0),
                            consent_given=bool(r.consent_given),
                            pseudonymous_id=r.pseudonymous_id,
                            harvest_outcome_mt=getattr(r, "harvest_outcome_mt", None),
                            sale_price_rs_kg=getattr(r, "sale_price_rs_kg", None),
                            sale_channel=getattr(r, "sale_channel", None),
                            notes=r.notes,
                            report_id=r.report_id,
                            timestamp=r.timestamp.isoformat() if hasattr(r.timestamp, "isoformat") else str(r.timestamp),
                        )
                        for r in db_rows
                    ]
            except Exception as e:
                logger.error("Failed to query planting reports from database: %s", e)
                raise RuntimeError(f"Database error querying planting reports: {e}")

        results = self._reports
        if crop_id:
            results = [r for r in results if r.crop_id == crop_id]
        if season:
            results = [r for r in results if r.season == season]
        return results

    def get_total_reported_area(self, crop_id: str, season: str) -> float:
        """
        Returns sum of actual_area_ha for the given crop and season.
        If actual_area_ha is 0, falls back to planned_area_ha.
        """
        matched = self.get_reports(crop_id=crop_id, season=season)
        total = sum(
            r.actual_area_ha if r.actual_area_ha > 0 else r.planned_area_ha
            for r in matched
        )
        return round(total, 1)

    def retrigger_crop(
        self,
        crop_id: str,
        season: str,
        target_month: int = 4,
        suitable_land_ha: Optional[float] = None,
    ) -> ReTriggerResult:
        """
        Replaces planned area with reported area and recalculates SPI + A_rec.
        """
        from govisense.models.target_area import TargetAreaCalculator
        from govisense.models.a3_supply_pressure import SupplyPressureEngine
        from govisense.models.demand_estimator import DemandEstimator
        from govisense.data.crop_requirements import get_crop_requirements

        demand_est = DemandEstimator()
        dem_res = demand_est.estimate(crop_id, target_month)
        season_demand = dem_res.demand_mt * 4.0

        reqs = get_crop_requirements()
        req = reqs.get(crop_id)
        yield_mid = req.yield_mid_mt_ha if req else 15.5
        loss_pct = req.loss_pct if req else 0.15

        target_calc = TargetAreaCalculator()

        prev_ta = target_calc.compute(
            crop=crop_id,
            season=season,
            demand_mt=season_demand,
            yield_mid=yield_mid,
            loss_pct=loss_pct,
            buffer=0.05,
            a_reported=0.0,
            suitable_land_ha=suitable_land_ha,
        )

        total_reported = self.get_total_reported_area(crop_id, season)

        new_ta = target_calc.compute(
            crop=crop_id,
            season=season,
            demand_mt=season_demand,
            yield_mid=yield_mid,
            loss_pct=loss_pct,
            buffer=0.05,
            a_reported=total_reported,
            suitable_land_ha=suitable_land_ha,
        )

        spi_engine = SupplyPressureEngine()
        prev_supply = prev_ta.a_target_ha * yield_mid * (1.0 - loss_pct)
        new_supply = total_reported * yield_mid * (1.0 - loss_pct)

        prev_spi = spi_engine.compute_spi(
            crop=crop_id,
            forecast_supply_mt=prev_supply / 4.0,
            month=target_month,
        )
        new_spi = spi_engine.compute_spi(
            crop=crop_id,
            forecast_supply_mt=new_supply / 4.0,
            month=target_month,
        )

        oversupply_stop = total_reported >= 1.10 * new_ta.a_target_ha

        if oversupply_stop:
            summary = (
                f"STOP: Reported extent ({total_reported:.1f} ha) exceeds 110% of target "
                f"({new_ta.a_target_ha:.1f} ha). A_rec set to 0 to prevent price collapse."
            )
        else:
            summary = (
                f"Reported {total_reported:.1f} ha of {new_ta.a_target_ha:.1f} ha target. "
                f"Remaining recommended planting: {new_ta.a_rec_ha:.1f} ha."
            )

        return ReTriggerResult(
            crop_id=crop_id,
            season=season,
            total_reported_ha=total_reported,
            previous_target_ha=prev_ta.a_target_ha,
            new_a_rec_ha=new_ta.a_rec_ha,
            previous_spi=prev_spi.spi_score,
            new_spi=new_spi.spi_score,
            previous_spi_label=prev_spi.spi_label,
            new_spi_label=new_spi.spi_label,
            oversupply_stop_triggered=oversupply_stop,
            action_summary=summary,
        )
