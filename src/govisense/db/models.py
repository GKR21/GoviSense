"""
Database Models for GoviSense
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)

Defines relational tables replacing legacy JSON storage:
  1. User (Authentication & RBAC)
  2. PlantingReportRecord (Farmer feedback loop)
  3. DecisionHistoryRecord (Policy audit trail)
  4. Alert & AlertInteraction (Multilingual alerts & farmer inbox)
  5. MarketPriceRecord (Wholesale & retail price series)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User account for Officers and Farmers with role-based access control."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="farmer")  # "officer", "farmer", "admin"
    full_name = Column(String(128), nullable=True)
    phone_number = Column(String(32), nullable=True)
    district = Column(String(64), nullable=True, default="Anuradhapura")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "district": self.district,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PlantingReportRecord(Base):
    """Farmer or Field Officer planting report submission."""
    __tablename__ = "planting_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(32), unique=True, index=True, nullable=False)
    crop_id = Column(String(64), index=True, nullable=False)
    season = Column(String(64), index=True, nullable=False)
    planned_area_ha = Column(Float, nullable=False, default=0.0)
    actual_area_ha = Column(Float, nullable=False, default=0.0)
    consent_given = Column(Boolean, nullable=False, default=False)
    pseudonymous_id = Column(String(64), index=True, nullable=False)
    harvest_outcome_mt = Column(Float, nullable=True)
    sale_price_rs_kg = Column(Float, nullable=True)
    sale_channel = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_planting_crop_season", "crop_id", "season"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "crop_id": self.crop_id,
            "season": self.season,
            "planned_area_ha": self.planned_area_ha,
            "actual_area_ha": self.actual_area_ha,
            "consent_given": self.consent_given,
            "pseudonymous_id": self.pseudonymous_id,
            "harvest_outcome_mt": self.harvest_outcome_mt,
            "sale_price_rs_kg": self.sale_price_rs_kg,
            "sale_channel": self.sale_channel,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }


class DecisionHistoryRecord(Base):
    """Audit log entry for officer policy decisions and pipeline runs."""
    __tablename__ = "decision_history"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String(32), unique=True, index=True, nullable=False)
    run_id = Column(String(64), nullable=True, index=True)
    hash = Column(String(64), nullable=True)
    crop_id = Column(String(64), index=True, nullable=False)
    season = Column(String(64), index=True, nullable=False)
    officer_id = Column(String(64), index=True, nullable=False)
    action_type = Column(String(64), nullable=False)  # "PLANT_EXPANSION", "HOLD_STORAGE", "DEFER_IMPORT", "MAINTAIN"
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(32), nullable=False, default="MT")
    rationale = Column(Text, nullable=False)
    model_version = Column(String(64), nullable=False, default="LightGBM-v2.1+HiGHS-LP")
    data_version = Column(String(64), nullable=False, default="CBSL-HARTI-DOA-2024.12")
    assumptions = Column(JSON, nullable=True)
    is_demo = Column(Boolean, nullable=False, default=False)
    data_available = Column(Boolean, nullable=False, default=True)
    source_type = Column(String(64), nullable=False, default="officer_audit_log")
    timestamp = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_decision_crop_season", "crop_id", "season"),
        Index("idx_decision_run_id", "run_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        assumptions_val = self.assumptions
        if isinstance(assumptions_val, str):
            try:
                assumptions_val = json.loads(assumptions_val)
            except Exception:
                pass
        return {
            "decision_id": self.decision_id,
            "run_id": self.run_id or "",
            "hash": self.hash or "",
            "crop_id": self.crop_id,
            "season": self.season,
            "officer_id": self.officer_id,
            "action_type": self.action_type,
            "quantity": self.quantity,
            "unit": self.unit,
            "rationale": self.rationale,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "assumptions": assumptions_val or {},
            "is_demo": bool(self.is_demo) if self.is_demo is not None else False,
            "data_available": bool(self.data_available) if self.data_available is not None else True,
            "source_type": self.source_type or "officer_audit_log",
            "timestamp": self.timestamp,
        }


class Alert(Base):
    """In-app multilingual alert notifications for farmers and officers."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(32), unique=True, index=True, nullable=False)
    crop_id = Column(String(64), index=True, nullable=False)
    severity = Column(String(32), default="warning", nullable=False)  # "info", "warning", "critical"
    title_en = Column(String(255), nullable=False)
    title_si = Column(String(255), nullable=True)
    title_ta = Column(String(255), nullable=True)
    message_en = Column(Text, nullable=False)
    message_si = Column(Text, nullable=True)
    message_ta = Column(Text, nullable=True)
    target_role = Column(String(32), default="all", nullable=False)  # "farmer", "officer", "all"
    status = Column(String(32), default="active", nullable=False)  # "active", "archived"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self, lang: str = "en") -> Dict[str, Any]:
        title = self.title_en
        message = self.message_en
        if lang == "si" and self.title_si:
            title = self.title_si
            message = self.message_si or self.message_en
        elif lang == "ta" and self.title_ta:
            title = self.title_ta
            message = self.message_ta or self.message_en

        return {
            "alert_id": self.alert_id,
            "crop_id": self.crop_id,
            "severity": self.severity,
            "title": title,
            "message": message,
            "title_en": self.title_en,
            "title_si": self.title_si,
            "title_ta": self.title_ta,
            "message_en": self.message_en,
            "message_si": self.message_si,
            "message_ta": self.message_ta,
            "target_role": self.target_role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AlertInteraction(Base):
    """Farmer interactions with alerts (Acknowledge / Ask an officer)."""
    __tablename__ = "alert_interactions"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(32), index=True, nullable=False)
    farmer_id = Column(String(64), index=True, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    question = Column(Text, nullable=True)
    officer_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_alert_farmer", "alert_id", "farmer_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "farmer_id": self.farmer_id,
            "acknowledged": self.acknowledged,
            "question": self.question,
            "officer_response": self.officer_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MarketPriceRecord(Base):
    """Market wholesale and retail price records."""
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(String(64), index=True, nullable=False)
    crop_name = Column(String(128), nullable=False)
    market_center = Column(String(128), index=True, nullable=False)  # e.g. "Dambulla", "Pettah", "Thambuttegama"
    wholesale_price = Column(Float, nullable=True)
    retail_price = Column(Float, nullable=True)
    price_date = Column(String(32), index=True, nullable=False)
    source = Column(String(64), default="HARTI/CBSL", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_price_crop_date", "crop_id", "price_date"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "market_center": self.market_center,
            "wholesale_price": self.wholesale_price,
            "retail_price": self.retail_price,
            "price_date": self.price_date,
            "source": self.source,
        }

