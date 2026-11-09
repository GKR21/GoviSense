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
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

from govisense.config import settings
from govisense.db.models import PlantingReportRecord
from govisense.db.session import get_db_session, sqlite_write_lock


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
    Database-backed storage for planting reports with concurrent-write safety.
    Provides aggregation, rate-limiting, duplicate prevention, and automatic pipeline re-triggering.

    Registry Verification Note (Task 12):
      Live verification against the Agrarian Services Department national farmer registry
      is future work. In this pilot, farmer authentication is enforced via pseudonymous IDs,
      sliding-window rate limits, and duplicate submission rejection.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path
        self._use_db = storage_path is None
        self._records: List[PlantingReport] = []
        self._rate_limits: Dict[str, List[float]] = {}

        if not self._use_db:
            self._load_json()

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
            raise ValueError(
                f"Rate limit exceeded for farmer '{pseudonymous_id}': "
                f"maximum {max_requests} planting reports allowed per {int(window_seconds)} seconds. "
                f"Please wait before submitting another report."
            )
        valid_timestamps.append(now)
        self._rate_limits[pseudonymous_id] = valid_timestamps

    def check_duplicate(self, report: PlantingReport) -> None:
        """
        Rejects duplicate planting reports for the same farmer, crop, season, and area (Task 12).
        """
        if self._use_db:
            with get_db_session() as db:
                existing = (
                    db.query(PlantingReportRecord)
                    .filter(
                        PlantingReportRecord.pseudonymous_id == report.pseudonymous_id,
                        PlantingReportRecord.crop_id == report.crop_id,
                        PlantingReportRecord.season == report.season,
                        PlantingReportRecord.actual_area_ha == report.actual_area_ha,
                    )
                    .first()
                )
                if existing:
                    raise ValueError(
                        f"Duplicate planting report detected: an identical report for farmer '{report.pseudonymous_id}', "
                        f"crop '{report.crop_id}', and season '{report.season}' with {report.actual_area_ha} ha "
                        f"already exists (Report ID: {existing.report_id})."
                    )
        else:
            for r in self._records:
                if (
                    r.pseudonymous_id == report.pseudonymous_id
                    and r.crop_id == report.crop_id
                    and r.season == report.season
                    and abs(r.actual_area_ha - report.actual_area_ha) < 1e-4
                ):
                    raise ValueError(
                        f"Duplicate planting report detected: an identical report for farmer '{report.pseudonymous_id}', "
                        f"crop '{report.crop_id}', and season '{report.season}' with {report.actual_area_ha} ha "
                        f"already exists (Report ID: {r.report_id})."
                    )

    def _load_json(self) -> None:
        if self.storage_path and self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self._records = [PlantingReport(**item) for item in raw_data]
            except Exception:
                self._records = []

    def _save_json(self) -> None:
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([asdict(r) for r in self._records], f, indent=2)

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

            if self._use_db:
                with get_db_session() as db:
                    rec = PlantingReportRecord(
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
                        timestamp=report.timestamp,
                    )
                    db.add(rec)
                    db.commit()
            else:
                self._records.append(report)
                self._save_json()

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
        if self._use_db:
            with get_db_session() as db:
                query = db.query(PlantingReportRecord)
                if crop_id:
                    query = query.filter(PlantingReportRecord.crop_id == crop_id)
                if season:
                    query = query.filter(PlantingReportRecord.season == season)
                records = query.order_by(PlantingReportRecord.id.desc()).all()
                return [
                    PlantingReport(
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
                        report_id=r.report_id,
                        timestamp=r.timestamp,
                    )
                    for r in records
                ]
        else:
            results = self._records
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
