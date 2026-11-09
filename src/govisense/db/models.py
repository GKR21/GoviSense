"""
SQLAlchemy Persistent Database Architecture for GoviSense
Team DARKBITE · ModelX 2.0 Proposal Specification
Pilot: Anuradhapura (Big Onion, Chilli)

Key Design Principles:
  1. Strict Data Privacy: Farmer profiles use pseudonymous IDs only (no names or phone numbers).
  2. Complete Auditability: Every run, forecast snapshot, and decision links to `runs`
     with real SHA-256 hash tracking and model/data version provenance.
  3. Pre- and Post-Harvest Feedback Split: `planting_reports` (planting stage)
     and `harvest_reports` (yield, storage, loss, sale stage).
  4. Ratio-Based SPI: Supply / Demand with 0.8 (shortage) and 1.2 (glut) thresholds.
  5. Cross-Database Compatibility: Uses SQLAlchemy JSON type for PostgreSQL and SQLite.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    Date,
    Text,
    Integer,
    JSON,
    ForeignKey,
    UniqueConstraint,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def compute_sha256_hash(data: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hexadecimal hash for audit records."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ===========================================================================
# 1. Pipeline Runs & Audit Governance
# ===========================================================================

class PipelineRunModel(Base):
    """
    Audit Foundation: Logs every execution of the forecasting & optimization pipeline.
    Corresponds to PostgreSQL table: runs
    """
    __tablename__ = "runs"

    run_id = Column(String(36), primary_key=True, default=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    trigger = Column(String(30), nullable=False, default="scheduled")  # scheduled, retrigger, officer
    model_version = Column(String(100), nullable=False, default="GoviSense-v2.0-baseline")
    data_version = Column(String(100), nullable=False, default="CBSL-HARTI-DOA-2024.12")
    assumptions = Column(JSON, nullable=False, default=dict)
    git_commit = Column(String(40), nullable=True)

    # Relationships
    decisions = relationship("DecisionRecordModel", back_populates="run", cascade="all, delete-orphan")
    forecasts = relationship("ForecastSnapshotModel", back_populates="run", cascade="all, delete-orphan")
    alerts = relationship("AlertModel", back_populates="run", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
            "trigger": self.trigger,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "assumptions": self.assumptions or {},
            "git_commit": self.git_commit,
        }


class DecisionRecordModel(Base):
    """
    Officer Policy Decision Audit Ledger with SHA-256 provenance hash.
    Corresponds to PostgreSQL table: decision_history
    """
    __tablename__ = "decision_history"

    decision_id = Column(String(36), primary_key=True, default=lambda: f"DEC-{uuid.uuid4().hex[:8].upper()}")
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=True, index=True)
    record_hash = Column(String(64), nullable=False, default="")
    crop_id = Column(String(50), nullable=False, index=True)
    season = Column(String(50), nullable=False, index=True)
    officer_id = Column(String(50), ForeignKey("officers.officer_id"), nullable=False, index=True)
    
    # Model proposal vs Officer response
    model_recommended_action = Column(String(50), nullable=True)  # IMPORT_NOW, IMPORT_LATER, DELAY_IMPORT, STORE, etc.
    officer_response = Column(String(20), nullable=False, default="accepted")  # accepted, modified, rejected
    action_type = Column(String(50), nullable=False)  # IMPORT_NOW, IMPORT_LATER, DELAY_IMPORT, STORE, RESTRICT_EXPANSION, ENCOURAGE_PLANTING
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="MT")  # MT, ha
    rationale = Column(Text, nullable=False)
    
    model_version = Column(String(100), nullable=False)
    data_version = Column(String(100), nullable=False, default="CBSL-HARTI-DOA-2024.12")
    assumptions = Column(JSON, nullable=False, default=dict)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    run = relationship("PipelineRunModel", back_populates="decisions")
    officer = relationship("OfficerModel", back_populates="decisions")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.record_hash:
            payload = {
                "crop_id": self.crop_id,
                "season": self.season,
                "officer_id": self.officer_id,
                "action_type": self.action_type,
                "quantity": self.quantity,
                "model_version": self.model_version,
                "data_version": self.data_version,
                "assumptions": self.assumptions or {},
            }
            self.record_hash = compute_sha256_hash(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "run_id": self.run_id,
            "record_hash": self.record_hash,
            "crop_id": self.crop_id,
            "season": self.season,
            "officer_id": self.officer_id,
            "model_recommended_action": self.model_recommended_action,
            "officer_response": self.officer_response,
            "action_type": self.action_type,
            "quantity": float(self.quantity) if self.quantity is not None else 0.0,
            "unit": self.unit,
            "rationale": self.rationale,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "assumptions": self.assumptions or {},
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
        }


# ===========================================================================
# 2. Farmers, Officers & Authentication
# ===========================================================================

class FarmerProfileModel(Base):
    """
    Strictly Pseudonymous Farmer Profile.
    Adheres to proposal privacy guarantee: NO name and NO phone stored.
    Corresponds to PostgreSQL table: farmer_profiles
    """
    __tablename__ = "farmer_profiles"

    pseudonymous_id = Column(String(50), primary_key=True)  # e.g., LK-AP-001
    district = Column(String(50), nullable=False, default="Anuradhapura", index=True)
    divisional_secretariat = Column(String(100), nullable=True)
    total_land_ha = Column(Float, nullable=False, default=1.0)
    irrigation_type = Column(String(20), nullable=False, default="irrigated")  # irrigated or rainfed
    irrigation_subtype = Column(String(30), nullable=True)  # major, minor, lift
    soil_type = Column(String(50), nullable=True)  # RBE, LHG, Noncalcic Brown
    soil_ph = Column(Float, nullable=True)
    consent_given = Column(Boolean, nullable=False, default=True)
    consent_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    language = Column(String(10), nullable=False, default="si")  # en, si, ta
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    planting_reports = relationship("PlantingReportModel", back_populates="farmer", cascade="all, delete-orphan")
    harvest_reports = relationship("HarvestReportModel", back_populates="farmer", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="farmer_profile", uselist=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pseudonymous_id": self.pseudonymous_id,
            "district": self.district,
            "divisional_secretariat": self.divisional_secretariat,
            "total_land_ha": float(self.total_land_ha),
            "irrigation_type": self.irrigation_type,
            "irrigation_subtype": self.irrigation_subtype,
            "soil_type": self.soil_type,
            "soil_ph": float(self.soil_ph) if self.soil_ph is not None else None,
            "consent_given": bool(self.consent_given),
            "consent_at": self.consent_at.isoformat() if hasattr(self.consent_at, "isoformat") else str(self.consent_at),
            "language": self.language,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class OfficerModel(Base):
    """
    Agricultural Extension Officers & Regional Decision Makers.
    Corresponds to PostgreSQL table: officers
    """
    __tablename__ = "officers"

    officer_id = Column(String(50), primary_key=True)  # e.g., OFFICER-001
    name = Column(String(100), nullable=False)
    district = Column(String(50), nullable=False, default="Anuradhapura")
    division = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False, default="Agricultural Extension Officer")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    decisions = relationship("DecisionRecordModel", back_populates="officer")
    user = relationship("UserModel", back_populates="officer_profile", uselist=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "officer_id": self.officer_id,
            "name": self.name,
            "district": self.district,
            "division": self.division,
            "role": self.role,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class UserModel(Base):
    """
    System User Accounts with Role-Based Access Control.
    Corresponds to PostgreSQL table: users
    """
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # officer, farmer, admin
    pseudonymous_id = Column(String(50), ForeignKey("farmer_profiles.pseudonymous_id"), nullable=True)
    officer_id = Column(String(50), ForeignKey("officers.officer_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    farmer_profile = relationship("FarmerProfileModel", back_populates="user")
    officer_profile = relationship("OfficerModel", back_populates="user")
    alert_statuses = relationship("AlertStatusModel", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "pseudonymous_id": self.pseudonymous_id,
            "officer_id": self.officer_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


# ===========================================================================
# 3. Two-Stage Farmer Feedback: Planting & Harvest Reports
# ===========================================================================

class PlantingReportModel(Base):
    """
    Stage 1: Pre-Harvest / Before Growth Planting Report.
    Captured at planting or intention-to-plant phase.
    Corresponds to PostgreSQL table: planting_reports
    """
    __tablename__ = "planting_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: f"REP-{uuid.uuid4().hex[:8].upper()}")
    pseudonymous_id = Column(String(50), ForeignKey("farmer_profiles.pseudonymous_id"), nullable=False, index=True)
    crop_id = Column(String(50), nullable=False, index=True)
    season = Column(String(50), nullable=False, index=True)  # e.g., Maha 2025/2026, Yala 2025
    
    planned_area_ha = Column(Float, nullable=False)
    actual_area_ha = Column(Float, nullable=True)  # Nullable if reported before planting completed
    
    district = Column(String(50), nullable=False, default="Anuradhapura")
    irrigation_type = Column(String(20), nullable=False, default="irrigated")  # irrigated or rainfed
    soil_ph = Column(Float, nullable=True)
    
    planting_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    
    # Recommendation adherence tracking
    recommended_crop_shown = Column(String(50), nullable=True)
    followed_recommendation = Column(String(20), nullable=True)  # yes, partly, no
    reason = Column(Text, nullable=True)
    expected_price_rs_kg = Column(Float, nullable=True)
    
    # Governance & Metadata
    consent_given = Column(Boolean, nullable=False, default=True)
    app_version = Column(String(20), nullable=False, default="1.0.0")
    language = Column(String(10), nullable=False, default="si")
    source = Column(String(30), nullable=False, default="farmer_report")  # always farmer_report
    flags = Column(JSON, nullable=False, default=list)  # automated validation anomaly flags
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        UniqueConstraint("pseudonymous_id", "crop_id", "season", name="uq_farmer_crop_season"),
        Index("idx_reports_crop_season", "crop_id", "season"),
    )

    # Relationships
    farmer = relationship("FarmerProfileModel", back_populates="planting_reports")
    harvest_reports = relationship("HarvestReportModel", back_populates="planting_report", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "pseudonymous_id": self.pseudonymous_id,
            "crop_id": self.crop_id,
            "season": self.season,
            "planned_area_ha": float(self.planned_area_ha),
            "actual_area_ha": float(self.actual_area_ha) if self.actual_area_ha is not None else None,
            "district": self.district,
            "irrigation_type": self.irrigation_type,
            "soil_ph": float(self.soil_ph) if self.soil_ph is not None else None,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "recommended_crop_shown": self.recommended_crop_shown,
            "followed_recommendation": self.followed_recommendation,
            "reason": self.reason,
            "expected_price_rs_kg": float(self.expected_price_rs_kg) if self.expected_price_rs_kg is not None else None,
            "consent_given": bool(self.consent_given),
            "app_version": self.app_version,
            "language": self.language,
            "source": self.source,
            "flags": self.flags or [],
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
        }


class HarvestReportModel(Base):
    """
    Stage 2: Post-Harvest / After Growth Report.
    Captures realized yield, storage, post-harvest losses, and market prices.
    Corresponds to PostgreSQL table: harvest_reports
    """
    __tablename__ = "harvest_reports"

    harvest_id = Column(String(36), primary_key=True, default=lambda: f"HVST-{uuid.uuid4().hex[:8].upper()}")
    planting_report_id = Column(String(36), ForeignKey("planting_reports.report_id"), nullable=False, index=True)
    pseudonymous_id = Column(String(50), ForeignKey("farmer_profiles.pseudonymous_id"), nullable=False, index=True)
    crop_id = Column(String(50), nullable=False, index=True)
    season = Column(String(50), nullable=False, index=True)

    area_harvested_ha = Column(Float, nullable=False)
    harvest_date = Column(Date, nullable=True)
    harvest_quantity_kg = Column(Float, nullable=False)
    
    # Disposition breakdown
    loss_kg = Column(Float, nullable=False, default=0.0)
    quantity_sold_kg = Column(Float, nullable=False, default=0.0)
    quantity_stored_kg = Column(Float, nullable=False, default=0.0)
    
    # Financial realization
    sale_price_rs_kg = Column(Float, nullable=True)
    sale_channel = Column(String(50), nullable=True)  # Dambulla DEC, Dedicated Economic Centre, Trader
    sale_month = Column(Integer, nullable=True)  # 1-12

    problems = Column(JSON, nullable=False, default=list)  # pests, drought, flooding, fertilizer_shortage
    notes = Column(Text, nullable=True)
    flags = Column(JSON, nullable=False, default=list)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        CheckConstraint("harvest_quantity_kg >= 0", name="chk_harvest_qty_positive"),
        CheckConstraint("area_harvested_ha > 0", name="chk_harvest_area_positive"),
        Index("idx_harvest_crop_season", "crop_id", "season"),
    )

    # Relationships
    planting_report = relationship("PlantingReportModel", back_populates="harvest_reports")
    farmer = relationship("FarmerProfileModel", back_populates="harvest_reports")

    @property
    def yield_mt_per_ha(self) -> float:
        """Calculates realized yield in Metric Tons per hectare."""
        if self.area_harvested_ha and self.area_harvested_ha > 0:
            return round((self.harvest_quantity_kg / 1000.0) / self.area_harvested_ha, 2)
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "harvest_id": self.harvest_id,
            "planting_report_id": self.planting_report_id,
            "pseudonymous_id": self.pseudonymous_id,
            "crop_id": self.crop_id,
            "season": self.season,
            "area_harvested_ha": float(self.area_harvested_ha),
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "harvest_quantity_kg": float(self.harvest_quantity_kg),
            "yield_mt_per_ha": self.yield_mt_per_ha,
            "loss_kg": float(self.loss_kg),
            "quantity_sold_kg": float(self.quantity_sold_kg),
            "quantity_stored_kg": float(self.quantity_stored_kg),
            "sale_price_rs_kg": float(self.sale_price_rs_kg) if self.sale_price_rs_kg is not None else None,
            "sale_channel": self.sale_channel,
            "sale_month": self.sale_month,
            "problems": self.problems or [],
            "notes": self.notes,
            "flags": self.flags or [],
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
        }


# ===========================================================================
# 4. Forecast Snapshots & Model Transparency
# ===========================================================================

class ForecastSnapshotModel(Base):
    """
    Comprehensive Forecast Run Snapshot with Ratio-Based SPI (0.8 / 1.2 bands).
    Corresponds to PostgreSQL table: forecast_snapshots
    """
    __tablename__ = "forecast_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=True, index=True)
    crop_id = Column(String(50), nullable=False, index=True)
    district = Column(String(50), nullable=False, default="Anuradhapura")
    season = Column(String(50), nullable=False)
    forecast_for_month = Column(String(10), nullable=False, index=True)  # YYYY-MM
    horizon_months = Column(Integer, nullable=False, default=3)

    # Probabilistic Price Forecast (Farmgate)
    price_p10 = Column(Float, nullable=True)
    price_p50 = Column(Float, nullable=False)  # predicted farmgate price
    price_p90 = Column(Float, nullable=True)
    retail_price_rs_kg = Column(Float, nullable=True)
    retail_price_p10 = Column(Float, nullable=True)
    retail_price_p90 = Column(Float, nullable=True)

    # Supply and Demand Scenarios (MT)
    supply_low_mt = Column(Float, nullable=True)
    supply_mid_mt = Column(Float, nullable=False)
    supply_high_mt = Column(Float, nullable=True)
    demand_mt = Column(Float, nullable=False)

    # Proposal SPI Specification: Supply / Demand Ratio (Bands: < 0.8 SHORTAGE, > 1.2 GLUT)
    spi_ratio_low = Column(Float, nullable=True)
    spi_ratio_mid = Column(Float, nullable=False)
    spi_ratio_high = Column(Float, nullable=True)
    spi_label = Column(String(20), nullable=False)  # GLUT, SHORTAGE, BALANCED
    spi_delta_mid = Column(Float, nullable=True)    # Optional (S - D) / D

    # Optimization Gap & Decision Deadlines
    gap_best_mt = Column(Float, nullable=True)
    gap_worst_mt = Column(Float, nullable=True)
    decision_deadline = Column(Date, nullable=True)
    import_lead_weeks = Column(Integer, nullable=False, default=7)
    recommended_action = Column(String(50), nullable=True)  # IMPORT_NOW, STORE, DELAY_IMPORT, RESTRICT_EXPANSION

    # Model Transparency & Quality Metrics
    price_model_used = Column(String(50), nullable=False, default="SARIMAX-LightGBM-ensemble")
    supply_model_used = Column(String(50), nullable=False, default="A1-Baseline-Lagged-SMA")
    confidence_badge = Column(String(20), nullable=False, default="medium")  # high, medium, low
    confidence_score = Column(Float, nullable=False, default=60.0)  # 0 to 100%
    is_demo = Column(Boolean, nullable=False, default=False)

    # Evaluation Ground Truth (Filled post-harvest for walk-forward validation)
    actual_price_rs_kg = Column(Float, nullable=True)
    actual_production_mt = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("idx_forecast_crop_month", "crop_id", "forecast_for_month"),
    )

    # Relationships
    run = relationship("PipelineRunModel", back_populates="forecasts")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "crop_id": self.crop_id,
            "district": self.district,
            "season": self.season,
            "forecast_for_month": self.forecast_for_month,
            "horizon_months": self.horizon_months,
            "price_p10": float(self.price_p10) if self.price_p10 is not None else None,
            "price_p50": float(self.price_p50),
            "price_p90": float(self.price_p90) if self.price_p90 is not None else None,
            "retail_price_rs_kg": float(self.retail_price_rs_kg) if self.retail_price_rs_kg is not None else None,
            "supply_low_mt": float(self.supply_low_mt) if self.supply_low_mt is not None else None,
            "supply_mid_mt": float(self.supply_mid_mt),
            "supply_high_mt": float(self.supply_high_mt) if self.supply_high_mt is not None else None,
            "demand_mt": float(self.demand_mt),
            "spi_ratio_low": float(self.spi_ratio_low) if self.spi_ratio_low is not None else None,
            "spi_ratio_mid": float(self.spi_ratio_mid),
            "spi_ratio_high": float(self.spi_ratio_high) if self.spi_ratio_high is not None else None,
            "spi_label": self.spi_label,
            "spi_delta_mid": float(self.spi_delta_mid) if self.spi_delta_mid is not None else None,
            "gap_best_mt": float(self.gap_best_mt) if self.gap_best_mt is not None else None,
            "gap_worst_mt": float(self.gap_worst_mt) if self.gap_worst_mt is not None else None,
            "decision_deadline": self.decision_deadline.isoformat() if self.decision_deadline else None,
            "import_lead_weeks": self.import_lead_weeks,
            "recommended_action": self.recommended_action,
            "price_model_used": self.price_model_used,
            "supply_model_used": self.supply_model_used,
            "confidence_badge": self.confidence_badge,
            "confidence_score": float(self.confidence_score),
            "is_demo": bool(self.is_demo),
            "actual_price_rs_kg": float(self.actual_price_rs_kg) if self.actual_price_rs_kg is not None else None,
            "actual_production_mt": float(self.actual_production_mt) if self.actual_production_mt is not None else None,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


# ===========================================================================
# 5. Cleaned Data Repository & Data Catalogue
# ===========================================================================

class DataCatalogueModel(Base):
    """
    Data Provenance, Licences, and Source Metadata.
    Corresponds to PostgreSQL table: data_catalogue
    """
    __tablename__ = "data_catalogue"

    dataset_id = Column(String(50), primary_key=True)  # e.g., cbsl_weekly_retail_2020_2024
    title = Column(String(150), nullable=False)
    publisher = Column(String(100), nullable=False)  # Central Bank of Sri Lanka (CBSL), HARTI, DOA
    source_url = Column(String(255), nullable=True)
    licence = Column(String(100), nullable=False, default="Open Government Data")
    date_retrieved = Column(String(30), nullable=True)
    temporal_range = Column(String(50), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "title": self.title,
            "publisher": self.publisher,
            "source_url": self.source_url,
            "licence": self.licence,
            "date_retrieved": self.date_retrieved,
            "temporal_range": self.temporal_range,
            "is_primary": bool(self.is_primary),
        }


class MonthlyDataModel(Base):
    """
    Standardized Monthly Master Dataset with strict source transparency.
    Flag: source_type in ("real", "interpolated", "synthetic").
    Corresponds to PostgreSQL table: monthly_data
    """
    __tablename__ = "monthly_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crop_id = Column(String(50), nullable=False, index=True)
    district = Column(String(50), nullable=False, index=True)
    month = Column(String(10), nullable=False, index=True)  # YYYY-MM
    
    planted_area_ha = Column(Float, nullable=True)
    harvested_area_ha = Column(Float, nullable=True)
    yield_mt_ha = Column(Float, nullable=True)
    production_mt = Column(Float, nullable=True)
    
    wholesale_price_rs_kg = Column(Float, nullable=True)
    retail_price_rs_kg = Column(Float, nullable=True)
    farmgate_price_rs_kg = Column(Float, nullable=True)
    imports_mt = Column(Float, nullable=True)
    weather_rainfall_anomaly = Column(Float, nullable=True)
    
    # Transparency
    source_type = Column(String(20), nullable=False, default="real")  # real, interpolated, synthetic
    dataset_id = Column(String(50), ForeignKey("data_catalogue.dataset_id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("crop_id", "district", "month", name="uq_crop_district_month"),
        Index("idx_monthly_crop_district_month", "crop_id", "district", "month"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "district": self.district,
            "month": self.month,
            "planted_area_ha": float(self.planted_area_ha) if self.planted_area_ha is not None else None,
            "harvested_area_ha": float(self.harvested_area_ha) if self.harvested_area_ha is not None else None,
            "yield_mt_ha": float(self.yield_mt_ha) if self.yield_mt_ha is not None else None,
            "production_mt": float(self.production_mt) if self.production_mt is not None else None,
            "wholesale_price_rs_kg": float(self.wholesale_price_rs_kg) if self.wholesale_price_rs_kg is not None else None,
            "retail_price_rs_kg": float(self.retail_price_rs_kg) if self.retail_price_rs_kg is not None else None,
            "farmgate_price_rs_kg": float(self.farmgate_price_rs_kg) if self.farmgate_price_rs_kg is not None else None,
            "imports_mt": float(self.imports_mt) if self.imports_mt is not None else None,
            "source_type": self.source_type,
            "dataset_id": self.dataset_id,
        }


# ===========================================================================
# 6. In-App Notifications & Extension Officer Inquiries
# ===========================================================================

class AlertModel(Base):
    """
    Market Alert Broadcasts (Glut, Shortage, Import Window Deadlines).
    Corresponds to PostgreSQL table: alerts
    """
    __tablename__ = "alerts"

    alert_id = Column(String(36), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}")
    crop_id = Column(String(50), nullable=False, index=True)
    district = Column(String(50), nullable=False, default="Anuradhapura")
    season = Column(String(50), nullable=True)
    month = Column(String(10), nullable=True)
    type = Column(String(30), nullable=False)  # GLUT_WARNING, SHORTAGE_RISK, IMPORT_WINDOW_CLOSING
    severity = Column(String(20), nullable=False, default="warning")  # info, warning, critical
    message_key = Column(String(100), nullable=False)
    params = Column(JSON, nullable=True, default=dict)
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    run = relationship("PipelineRunModel", back_populates="alerts")
    statuses = relationship("AlertStatusModel", back_populates="alert", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "crop_id": self.crop_id,
            "district": self.district,
            "season": self.season,
            "month": self.month,
            "type": self.type,
            "severity": self.severity,
            "message_key": self.message_key,
            "params": self.params or {},
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class AlertStatusModel(Base):
    """
    User-specific alert interactions (Acknowledge, Ask Officer).
    Corresponds to PostgreSQL table: alert_status
    """
    __tablename__ = "alert_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(36), ForeignKey("alerts.alert_id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    ask_officer = Column(Boolean, nullable=False, default=False)
    officer_note = Column(Text, nullable=True)

    # Relationships
    alert = relationship("AlertModel", back_populates="statuses")
    user = relationship("UserModel", back_populates="alert_statuses")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "ask_officer": bool(self.ask_officer),
            "officer_note": self.officer_note,
        }
