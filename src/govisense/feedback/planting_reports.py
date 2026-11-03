"""
Feedback Loop Module (WP7 / Item 7)
Team DARKBITE · ModelX 2.0 Phase 1
Pilot: Anuradhapura (Big Onion, Chilli)

Enables farmers and ground agricultural officers to submit actual planting reports.
On report ingestion:
  1. Validates farmer consent and pseudonymous ID.
  2. Replaces planned / estimated area with farmer-reported area.
  3. Re-triggers SPI and Target Area Calculator (A_rec).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

from govisense.config import PROCESSED_DATA_DIR, settings
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


class PlantingReportStore:
    """
    In-memory and persistent JSON storage for planting reports.
    Provides aggregation and automatic pipeline re-triggering.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or _DEFAULT_STORE_PATH
        self._reports: List[PlantingReport] = []
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self._reports = [PlantingReport(**item) for item in raw_data]
            except Exception:
                self._reports = []

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self._reports], f, indent=2)

    def submit_report(self, report: PlantingReport) -> Dict[str, Any]:
        """
        Validates and records a planting report.
        Strict privacy rule: consent must be explicitly given.
        """
        if not report.consent_given:
            raise ValueError(
                "Consent is required: farmer data cannot be collected or used without explicit consent."
            )
        if report.actual_area_ha < 0 or report.planned_area_ha < 0:
            raise ValueError("Planted areas cannot be negative.")
        if not report.pseudonymous_id.strip():
            raise ValueError("A pseudonymous ID is required for auditability and privacy.")

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
        }

    def get_reports(
        self,
        crop_id: Optional[str] = None,
        season: Optional[str] = None,
    ) -> List[PlantingReport]:
        """Retrieve stored reports, optionally filtered by crop and season."""
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
        demand_est = DemandEstimator()
        dem_res = demand_est.estimate(crop_id, target_month)
        # Seasonal demand (e.g. 4 months duration)
        season_demand = dem_res.demand_mt * 4.0

        # Crop parameters
        reqs = get_crop_requirements()
        req = reqs.get(crop_id)
        yield_mid = req.yield_mid_mt_ha if req else 15.5
        loss_pct = req.loss_pct if req else 0.15

        target_calc = TargetAreaCalculator()

        # Previous baseline (before reported acreage)
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

        # Actual cumulative reported acreage
        total_reported = self.get_total_reported_area(crop_id, season)

        # New target area with actual reported acreage
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

        # Supply Pressure Index before and after
        spi_engine = SupplyPressureEngine()
        prev_supply = prev_ta.a_target_ha * yield_mid * (1.0 - loss_pct)
        new_supply = total_reported * yield_mid * (1.0 - loss_pct)

        prev_spi = spi_engine.compute_spi(
            crop=crop_id,
            forecast_supply_mt=prev_supply / 4.0,  # monthly rate
            month=target_month,
        )
        new_spi = spi_engine.compute_spi(
            crop=crop_id,
            forecast_supply_mt=new_supply / 4.0,  # monthly rate
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
