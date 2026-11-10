"""
SQLAlchemy Persistent PostgreSQL Database Architecture for GoviSense
Aligned 1-to-1 with data/database/db.sql (PostgreSQL 14+ 3NF Schema).

Key Design Principles:
  1. Strict Data Privacy: Farmer profiles use pseudonymous IDs only (no names or phone numbers).
  2. Complete Auditability: Every run, forecast snapshot, and decision links to `runs`
     with real SHA-256 hash tracking and model/data version provenance.
  3. Pre- and Post-Harvest Feedback Split: `planting_reports` (planting stage)
     and `harvest_reports` (yield, storage, loss, sale stage).
  4. Third Normal Form (3NF): Reference lookups, *_translations tables, and child
     flag/problem tables match data/database/db.sql directly.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import bcrypt
from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

from govisense.provenance import (
    compute_data_version,
    compute_model_version,
    get_git_commit,
)

Base = declarative_base()


def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash or fallback to legacy SHA-256 for transition."""
    if not hashed_password:
        return False
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False
    sha = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(sha, hashed_password)


def validate_season_format(season: str) -> bool:
    """Validates season format: e.g. Maha 2024/2025, Yala 2025."""
    import re

    if not season or not isinstance(season, str):
        return False
    return bool(re.match(r"^(Maha\s+\d{4}/\d{4}|Yala\s+\d{4})$", season.strip(), re.IGNORECASE))


def compute_sha256_hash(data: Dict[str, Any]) -> str:
    """Computes a deterministic SHA-256 hexadecimal hash for audit records."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ===========================================================================
# 1. Reference / Lookup Tables (22 tables matching db.sql Section 1)
# ===========================================================================


class RoleModel(Base):
    __tablename__ = "roles"

    role_code = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)


class LanguageModel(Base):
    __tablename__ = "languages"

    lang_code = Column(String(10), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)


class DistrictModel(Base):
    __tablename__ = "districts"

    district_id = Column(SmallInteger, Identity(always=True), primary_key=True)
    name = Column(String(50), nullable=False, unique=True)


class DsDivisionModel(Base):
    __tablename__ = "ds_divisions"

    division_id = Column(Integer, Identity(always=True), primary_key=True)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    name = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("district_id", "name"),
        UniqueConstraint("division_id", "district_id"),
    )


class CropCategoryModel(Base):
    __tablename__ = "crop_categories"

    category_code = Column(String(30), primary_key=True)
    name = Column(String(60), nullable=False)


class CropModel(Base):
    __tablename__ = "crops"

    crop_id = Column(String(50), primary_key=True)
    scientific_name = Column(String(100), nullable=True)
    category_code = Column(String(30), ForeignKey("crop_categories.category_code"), nullable=False)

    translations = relationship("CropTranslationModel", back_populates="crop", cascade="all, delete-orphan")


class CropTranslationModel(Base):
    __tablename__ = "crop_translations"

    crop_id = Column(String(50), ForeignKey("crops.crop_id", ondelete="CASCADE"), primary_key=True)
    lang_code = Column(String(10), ForeignKey("languages.lang_code"), primary_key=True)
    name = Column(String(128), nullable=False)

    crop = relationship("CropModel", back_populates="translations")


class SeasonModel(Base):
    __tablename__ = "seasons"

    season_id = Column(SmallInteger, Identity(always=True), primary_key=True)
    label = Column(String(50), nullable=False, unique=True)
    season_type = Column(String(10), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)


class IrrigationTypeModel(Base):
    __tablename__ = "irrigation_types"

    irrigation_code = Column(String(30), primary_key=True)
    name = Column(String(60), nullable=False)
    water_class = Column(String(10), nullable=False)


class SoilTypeModel(Base):
    __tablename__ = "soil_types"

    soil_code = Column(String(30), primary_key=True)
    name = Column(String(60), nullable=False)


class SaleChannelModel(Base):
    __tablename__ = "sale_channels"

    channel_code = Column(String(30), primary_key=True)
    name = Column(String(80), nullable=False)


class DataSourceTypeModel(Base):
    __tablename__ = "data_source_types"

    source_type = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)
    is_demo = Column(Boolean, nullable=False)


class DataQualityLevelModel(Base):
    __tablename__ = "data_quality_levels"

    quality_code = Column(String(30), primary_key=True)
    description = Column(String(200), nullable=False)


class AlertTypeModel(Base):
    __tablename__ = "alert_types"

    type_code = Column(String(30), primary_key=True)
    description = Column(String(200), nullable=False)


class SeverityLevelModel(Base):
    __tablename__ = "severity_levels"

    severity_code = Column(String(20), primary_key=True)
    rank = Column(SmallInteger, nullable=False, unique=True)


class SpiBandModel(Base):
    __tablename__ = "spi_bands"

    band_code = Column(String(20), primary_key=True)
    min_ratio = Column(Numeric(6, 3), nullable=True)
    max_ratio = Column(Numeric(6, 3), nullable=True)


class ConfidenceLevelModel(Base):
    __tablename__ = "confidence_levels"

    level_code = Column(String(10), primary_key=True)
    min_score = Column(Numeric(5, 1), nullable=False, unique=True)


class DecisionActionModel(Base):
    __tablename__ = "decision_actions"

    action_code = Column(String(50), primary_key=True)
    description = Column(String(200), nullable=False)


class ForecastModelRef(Base):
    __tablename__ = "forecast_models"

    model_name = Column(String(60), primary_key=True)
    model_kind = Column(String(12), nullable=False)
    is_baseline = Column(Boolean, nullable=False, default=False)


class MarketCenterModel(Base):
    __tablename__ = "market_centers"

    center_id = Column(Integer, Identity(always=True), primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=True)

    district = relationship("DistrictModel")
    translations = relationship("MarketCenterTranslationModel", back_populates="center", cascade="all, delete-orphan")


class MarketCenterTranslationModel(Base):
    __tablename__ = "market_center_translations"

    center_id = Column(Integer, ForeignKey("market_centers.center_id", ondelete="CASCADE"), primary_key=True)
    lang_code = Column(String(10), ForeignKey("languages.lang_code"), primary_key=True)
    name = Column(String(128), nullable=False)

    center = relationship("MarketCenterModel", back_populates="translations")


class OfficerDesignationModel(Base):
    __tablename__ = "officer_designations"

    designation_id = Column(SmallInteger, Identity(always=True), primary_key=True)
    name = Column(String(80), nullable=False, unique=True)


# ===========================================================================
# 2. Identity & People (officers, farmer_profiles, users)
# ===========================================================================


class OfficerModel(Base):
    __tablename__ = "officers"

    officer_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    division_id = Column(Integer, nullable=True)
    designation_id = Column(SmallInteger, ForeignKey("officer_designations.designation_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        ForeignKeyConstraint(["division_id", "district_id"], ["ds_divisions.division_id", "ds_divisions.district_id"]),
    )

    district_rel = relationship("DistrictModel", lazy="joined")
    division_rel = relationship("DsDivisionModel", lazy="joined", foreign_keys=[division_id])
    designation_rel = relationship("OfficerDesignationModel", lazy="joined")
    decisions = relationship("DecisionRecordModel", back_populates="officer")
    user = relationship("UserModel", back_populates="officer_profile", uselist=False)

    @property
    def district(self) -> str:
        return self.district_rel.name if self.district_rel else "Anuradhapura"

    @property
    def division(self) -> Optional[str]:
        return self.division_rel.name if self.division_rel else None

    @property
    def role(self) -> str:
        return self.designation_rel.name if self.designation_rel else "Agricultural Extension Officer"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "officer_id": self.officer_id,
            "name": self.name,
            "district_id": self.district_id,
            "district": self.district,
            "division_id": self.division_id,
            "division": self.division,
            "designation_id": self.designation_id,
            "role": self.role,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class FarmerProfileModel(Base):
    __tablename__ = "farmer_profiles"

    pseudonymous_id = Column(String(50), primary_key=True)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    division_id = Column(Integer, nullable=True)
    total_land_ha = Column(Numeric(8, 2), nullable=False)
    irrigation_code = Column(String(30), ForeignKey("irrigation_types.irrigation_code"), nullable=False)
    soil_code = Column(String(30), ForeignKey("soil_types.soil_code"), nullable=True)
    soil_ph = Column(Numeric(3, 1), nullable=True)
    consent_given = Column(Boolean, nullable=False)
    consent_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    lang_code = Column(String(10), ForeignKey("languages.lang_code"), nullable=False, default="si")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        ForeignKeyConstraint(["division_id", "district_id"], ["ds_divisions.division_id", "ds_divisions.district_id"]),
    )

    district_rel = relationship("DistrictModel", lazy="joined")
    division_rel = relationship("DsDivisionModel", lazy="joined", foreign_keys=[division_id])
    soil_rel = relationship("SoilTypeModel", lazy="joined")
    planting_reports = relationship("PlantingReportModel", back_populates="farmer", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="farmer_profile", uselist=False)

    @property
    def district(self) -> str:
        return self.district_rel.name if self.district_rel else "Anuradhapura"

    @property
    def divisional_secretariat(self) -> Optional[str]:
        return self.division_rel.name if self.division_rel else None

    @property
    def irrigation_type(self) -> str:
        return self.irrigation_code

    @property
    def soil_type(self) -> Optional[str]:
        return self.soil_rel.name if self.soil_rel else self.soil_code

    @property
    def language(self) -> str:
        return self.lang_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pseudonymous_id": self.pseudonymous_id,
            "district_id": self.district_id,
            "district": self.district,
            "division_id": self.division_id,
            "divisional_secretariat": self.divisional_secretariat,
            "total_land_ha": float(self.total_land_ha),
            "irrigation_code": self.irrigation_code,
            "irrigation_type": self.irrigation_code,
            "soil_code": self.soil_code,
            "soil_type": self.soil_type,
            "soil_ph": float(self.soil_ph) if self.soil_ph is not None else None,
            "consent_given": bool(self.consent_given),
            "consent_at": self.consent_at.isoformat() if hasattr(self.consent_at, "isoformat") else str(self.consent_at),
            "lang_code": self.lang_code,
            "language": self.lang_code,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, "isoformat") else str(self.updated_at),
        }


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_code = Column(String(20), ForeignKey("roles.role_code"), nullable=False)
    pseudonymous_id = Column(String(50), ForeignKey("farmer_profiles.pseudonymous_id"), unique=True, nullable=True)
    officer_id = Column(String(50), ForeignKey("officers.officer_id"), unique=True, nullable=True)
    full_name = Column(String(128), nullable=True)
    phone_number = Column(String(32), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)

    farmer_profile = relationship("FarmerProfileModel", back_populates="user", lazy="joined")
    officer_profile = relationship("OfficerModel", back_populates="user", lazy="joined")
    alert_statuses = relationship("AlertStatusModel", back_populates="user", cascade="all, delete-orphan")
    alert_questions = relationship(
        "AlertQuestionModel",
        back_populates="user",
        foreign_keys="AlertQuestionModel.user_id",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        if "hashed_password" in kwargs and "password_hash" not in kwargs:
            kwargs["password_hash"] = kwargs.pop("hashed_password")
        else:
            kwargs.pop("hashed_password", None)
        if "role" in kwargs and "role_code" not in kwargs:
            kwargs["role_code"] = kwargs.pop("role")
        else:
            kwargs.pop("role", None)
        kwargs.pop("id", None)
        kwargs.pop("district", None)
        if not kwargs.get("user_id"):
            kwargs["user_id"] = str(uuid.uuid4())
        super().__init__(**kwargs)

    @property
    def id(self) -> int:
        return abs(hash(self.user_id)) % 2_000_000_000 or 1

    @property
    def role(self) -> str:
        return self.role_code

    @role.setter
    def role(self, value: str) -> None:
        self.role_code = value

    @property
    def hashed_password(self) -> str:
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value: str) -> None:
        self.password_hash = value

    @property
    def district(self) -> str:
        if self.officer_profile is not None:
            return self.officer_profile.district
        if self.farmer_profile is not None:
            return self.farmer_profile.district
        if self.role_code == "admin":
            return "National"
        return "Anuradhapura"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role_code,
            "role_code": self.role_code,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "district": self.district,
            "is_active": bool(self.is_active),
            "pseudonymous_id": self.pseudonymous_id,
            "officer_id": self.officer_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


# ===========================================================================
# 3. Data Provenance, Pipeline Runs, Monthly Data & Market Prices
# ===========================================================================


class DataCatalogueModel(Base):
    __tablename__ = "data_catalogue"

    dataset_id = Column(String(50), primary_key=True)
    title = Column(String(150), nullable=False)
    publisher = Column(String(100), nullable=False)
    source_url = Column(String(255), nullable=True)
    licence = Column(String(100), nullable=False)
    date_retrieved = Column(Date, nullable=True)
    temporal_range = Column(String(50), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "title": self.title,
            "publisher": self.publisher,
            "source_url": self.source_url,
            "licence": self.licence,
            "date_retrieved": self.date_retrieved.isoformat() if self.date_retrieved else None,
            "temporal_range": self.temporal_range,
            "is_primary": bool(self.is_primary),
        }


class PipelineRunModel(Base):
    __tablename__ = "runs"

    run_id = Column(String(36), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    trigger_type = Column(String(30), nullable=False, default="api")
    model_version = Column(String(100), nullable=False, default=lambda: compute_model_version())
    data_version = Column(String(100), nullable=False, default=lambda: compute_data_version())
    assumptions = Column(JSONB, nullable=False, default=dict)
    git_commit = Column(String(40), nullable=True, default=lambda: get_git_commit()[:40])

    decisions = relationship("DecisionRecordModel", back_populates="run")
    forecasts = relationship("ForecastSnapshotModel", back_populates="run")
    alerts = relationship("AlertModel", back_populates="run")
    evaluations = relationship("EvaluationResultModel", back_populates="run")

    def __init__(self, **kwargs):
        if "trigger" in kwargs and "trigger_type" not in kwargs:
            kwargs["trigger_type"] = kwargs.pop("trigger")
        else:
            kwargs.pop("trigger", None)
        if not kwargs.get("run_id"):
            kwargs["run_id"] = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().__init__(**kwargs)

    @property
    def trigger(self) -> str:
        return self.trigger_type

    @trigger.setter
    def trigger(self, value: str) -> None:
        self.trigger_type = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
            "trigger": self.trigger_type,
            "trigger_type": self.trigger_type,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "assumptions": self.assumptions or {},
            "git_commit": self.git_commit,
        }


class MonthlyDataModel(Base):
    __tablename__ = "monthly_data"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    month = Column(Date, nullable=False)
    planted_area_ha = Column(Float, nullable=True)
    harvested_area_ha = Column(Float, nullable=True)
    production_mt = Column(Float, nullable=True)
    wholesale_price_rs_kg = Column(Float, nullable=True)
    retail_price_rs_kg = Column(Float, nullable=True)
    farmgate_price_rs_kg = Column(Float, nullable=True)
    imports_mt = Column(Float, nullable=True)
    weather_rainfall_anomaly = Column(Float, nullable=True)
    source_type = Column(String(20), ForeignKey("data_source_types.source_type"), nullable=False)
    dataset_id = Column(String(50), ForeignKey("data_catalogue.dataset_id"), nullable=True)

    district_rel = relationship("DistrictModel", lazy="joined")

    @property
    def district(self) -> str:
        return self.district_rel.name if self.district_rel else "Anuradhapura"

    @property
    def yield_mt_ha(self) -> Optional[float]:
        if self.production_mt is not None and self.harvested_area_ha and self.harvested_area_ha > 0:
            return round(float(self.production_mt) / float(self.harvested_area_ha), 3)
        if self.production_mt is not None and self.planted_area_ha and self.planted_area_ha > 0:
            return round(float(self.production_mt) / float(self.planted_area_ha), 3)
        return None

    def to_dict(self) -> Dict[str, Any]:
        m_str = self.month.strftime("%Y-%m") if hasattr(self.month, "strftime") else str(self.month)
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "district_id": self.district_id,
            "district": self.district,
            "month": m_str,
            "planted_area_ha": float(self.planted_area_ha) if self.planted_area_ha is not None else None,
            "harvested_area_ha": float(self.harvested_area_ha) if self.harvested_area_ha is not None else None,
            "yield_mt_ha": self.yield_mt_ha,
            "production_mt": float(self.production_mt) if self.production_mt is not None else None,
            "wholesale_price_rs_kg": float(self.wholesale_price_rs_kg) if self.wholesale_price_rs_kg is not None else None,
            "retail_price_rs_kg": float(self.retail_price_rs_kg) if self.retail_price_rs_kg is not None else None,
            "farmgate_price_rs_kg": float(self.farmgate_price_rs_kg) if self.farmgate_price_rs_kg is not None else None,
            "imports_mt": float(self.imports_mt) if self.imports_mt is not None else None,
            "weather_rainfall_anomaly": float(self.weather_rainfall_anomaly) if self.weather_rainfall_anomaly is not None else None,
            "source_type": self.source_type,
            "dataset_id": self.dataset_id,
        }


class MarketPriceRecord(Base):
    __tablename__ = "market_prices"

    price_id = Column(BigInteger, Identity(always=True), primary_key=True)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    center_id = Column(Integer, ForeignKey("market_centers.center_id"), nullable=False)
    price_date = Column(Date, nullable=False)
    wholesale_price = Column(Numeric(10, 2), nullable=True)
    retail_price = Column(Numeric(10, 2), nullable=True)
    dataset_id = Column(String(50), ForeignKey("data_catalogue.dataset_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    crop_rel = relationship("CropModel", lazy="joined")
    center_rel = relationship("MarketCenterModel", lazy="joined")

    @property
    def id(self) -> int:
        return self.price_id

    @property
    def category(self) -> str:
        return self.crop_rel.category_code if self.crop_rel else "vegetable"

    def _translation(self, translations: list, lang: str, fallback: str) -> str:
        for t in translations or []:
            if t.lang_code == lang:
                return t.name
        return fallback

    def to_dict(self) -> Dict[str, Any]:
        crop_trans = self.crop_rel.translations if self.crop_rel else []
        center_trans = self.center_rel.translations if self.center_rel else []
        center_name = self.center_rel.name if self.center_rel else "Dambulla DEC"

        crop_en = self._translation(crop_trans, "en", self.crop_id.replace("_", " ").title())
        crop_si = self._translation(crop_trans, "si", crop_en)
        crop_ta = self._translation(crop_trans, "ta", crop_en)

        ec_en = self._translation(center_trans, "en", center_name)
        ec_si = self._translation(center_trans, "si", center_name)
        ec_ta = self._translation(center_trans, "ta", center_name)

        w_val = float(self.wholesale_price) if self.wholesale_price is not None else None
        r_val = float(self.retail_price) if self.retail_price is not None else None

        return {
            "id": self.price_id,
            "crop_id": self.crop_id,
            "crop_name": crop_en,
            "crop_en": crop_en,
            "crop_si": crop_si,
            "crop_ta": crop_ta,
            "category": self.category,
            "market_center": center_name,
            "economic_center_en": ec_en,
            "economic_center_si": ec_si,
            "economic_center_ta": ec_ta,
            "wholesale_price": f"Rs {int(round(w_val))} / kg" if w_val is not None else "N/A",
            "retail_price": f"Rs {int(round(r_val))} / kg" if r_val is not None else "N/A",
            "wholesale_val": w_val,
            "retail_val": r_val,
            "trend_pct": "±0% (Stable)",
            "is_up": False,
            "is_stable": True,
            "price_date": self.price_date.isoformat() if isinstance(self.price_date, date) else str(self.price_date),
            "source": self.dataset_id or "CBSL/HARTI",
        }


# ===========================================================================
# 4. Forecasting & Evaluation (forecast_snapshots, evaluation_results)
# ===========================================================================


class ForecastSnapshotModel(Base):
    __tablename__ = "forecast_snapshots"

    forecast_id = Column(BigInteger, Identity(always=True), primary_key=True)
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=False)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    forecast_for_month = Column(Date, nullable=False)
    horizon_months = Column(SmallInteger, nullable=False, default=3)
    price_p10 = Column(Float, nullable=True)
    price_p50 = Column(Float, nullable=False)
    price_p90 = Column(Float, nullable=True)
    retail_price_rs_kg = Column(Float, nullable=True)
    retail_price_method = Column(String(50), nullable=False, default="CBSL-calibrated-margin")
    retail_price_p10 = Column(Float, nullable=True)
    retail_price_p90 = Column(Float, nullable=True)
    supply_low_mt = Column(Float, nullable=True)
    supply_mid_mt = Column(Float, nullable=False)
    supply_high_mt = Column(Float, nullable=True)
    demand_mt = Column(Float, nullable=False)
    spi_ratio_low = Column(Float, nullable=True)
    spi_ratio_mid = Column(Float, nullable=False)
    spi_ratio_high = Column(Float, nullable=True)
    spi_raw = Column(Float, nullable=True)
    spi_delta_mid = Column(Float, nullable=True)
    gap_best_mt = Column(Float, nullable=True)
    gap_worst_mt = Column(Float, nullable=True)
    decision_deadline = Column(Date, nullable=True)
    import_lead_weeks = Column(SmallInteger, nullable=False, default=0)
    recommended_action = Column(String(50), ForeignKey("decision_actions.action_code"), nullable=True)
    price_model_used = Column(String(60), ForeignKey("forecast_models.model_name"), nullable=False, default="SARIMAX-LightGBM-ensemble")
    supply_model_used = Column(String(60), ForeignKey("forecast_models.model_name"), nullable=False, default="A1-Baseline-Lagged-SMA")
    confidence_score = Column(Numeric(5, 1), nullable=False, default=60.0)
    data_quality = Column(String(30), ForeignKey("data_quality_levels.quality_code"), nullable=False, default="verified")
    is_demo = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    run = relationship("PipelineRunModel", back_populates="forecasts")
    district_rel = relationship("DistrictModel", lazy="joined")

    @property
    def id(self) -> int:
        return self.forecast_id

    @property
    def district(self) -> str:
        return self.district_rel.name if self.district_rel else "Anuradhapura"

    @property
    def spi_label(self) -> str:
        r = float(self.spi_ratio_mid or 1.0)
        if r < 0.85:
            return "Shortage"
        if r >= 1.15:
            return "Glut"
        return "Balanced"

    @property
    def confidence_badge(self) -> str:
        s = float(self.confidence_score or 0.0)
        if s >= 80.0:
            return "high"
        if s >= 40.0:
            return "medium"
        return "low"

    def to_dict(self) -> Dict[str, Any]:
        month_str = (
            self.forecast_for_month.strftime("%Y-%m")
            if hasattr(self.forecast_for_month, "strftime")
            else str(self.forecast_for_month)
        )
        return {
            "id": self.forecast_id,
            "forecast_id": self.forecast_id,
            "run_id": self.run_id,
            "crop_id": self.crop_id,
            "district_id": self.district_id,
            "district": self.district,
            "forecast_for_month": month_str,
            "horizon_months": self.horizon_months,
            "price_p10": float(self.price_p10) if self.price_p10 is not None else None,
            "price_p50": float(self.price_p50),
            "price_p90": float(self.price_p90) if self.price_p90 is not None else None,
            "retail_price_rs_kg": float(self.retail_price_rs_kg) if self.retail_price_rs_kg is not None else None,
            "retail_price_method": self.retail_price_method,
            "retail_price_p10": float(self.retail_price_p10) if self.retail_price_p10 is not None else None,
            "retail_price_p90": float(self.retail_price_p90) if self.retail_price_p90 is not None else None,
            "supply_low_mt": float(self.supply_low_mt) if self.supply_low_mt is not None else None,
            "supply_mid_mt": float(self.supply_mid_mt),
            "supply_high_mt": float(self.supply_high_mt) if self.supply_high_mt is not None else None,
            "demand_mt": float(self.demand_mt),
            "spi_ratio_low": float(self.spi_ratio_low) if self.spi_ratio_low is not None else None,
            "spi_ratio_mid": float(self.spi_ratio_mid),
            "spi_ratio_high": float(self.spi_ratio_high) if self.spi_ratio_high is not None else None,
            "spi_label": self.spi_label,
            "spi_raw": float(self.spi_raw) if self.spi_raw is not None else None,
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
            "data_quality": self.data_quality,
            "is_demo": bool(self.is_demo),
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class EvaluationResultModel(Base):
    __tablename__ = "evaluation_results"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=False)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    model_name = Column(String(60), ForeignKey("forecast_models.model_name"), nullable=False)
    metric_name = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    baseline_name = Column(String(60), ForeignKey("forecast_models.model_name"), nullable=True)
    baseline_value = Column(Float, nullable=True)
    beat_baseline = Column(Boolean, nullable=False)
    evaluation_period = Column(String(50), nullable=True)
    details = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    run = relationship("PipelineRunModel", back_populates="evaluations")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "crop_id": self.crop_id,
            "model_name": self.model_name,
            "metric_name": self.metric_name,
            "metric_value": float(self.metric_value),
            "baseline_name": self.baseline_name,
            "baseline_value": float(self.baseline_value) if self.baseline_value is not None else None,
            "beat_baseline": bool(self.beat_baseline),
            "evaluation_period": self.evaluation_period,
            "details": self.details or {},
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


# ===========================================================================
# 5. Farmer Feedback Loop (planting_reports, harvest_reports, flags, problems)
# ===========================================================================


class PlantingReportFlagModel(Base):
    __tablename__ = "planting_report_flags"

    report_id = Column(String(36), ForeignKey("planting_reports.report_id", ondelete="CASCADE"), primary_key=True)
    flag_code = Column(String(50), primary_key=True)

    report = relationship("PlantingReportModel", back_populates="flag_rows")


class PlantingReportModel(Base):
    __tablename__ = "planting_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: f"REP-{uuid.uuid4().hex[:8].upper()}")
    pseudonymous_id = Column(String(50), ForeignKey("farmer_profiles.pseudonymous_id"), nullable=False)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    season_id = Column(SmallInteger, ForeignKey("seasons.season_id"), nullable=False)
    planned_area_ha = Column(Numeric(8, 2), nullable=False)
    actual_area_ha = Column(Numeric(8, 2), nullable=True)
    irrigation_code = Column(String(30), ForeignKey("irrigation_types.irrigation_code"), nullable=False, default="irrigated")
    planting_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    recommended_crop_shown = Column(String(50), ForeignKey("crops.crop_id"), nullable=True)
    reason = Column(Text, nullable=True)
    expected_price_rs_kg = Column(Numeric(10, 2), nullable=True)
    consent_given = Column(Boolean, nullable=False)
    app_version = Column(String(20), nullable=False, default="1.0.0")
    lang_code = Column(String(10), ForeignKey("languages.lang_code"), nullable=False, default="si")
    source = Column(String(30), nullable=False, default="farmer_report")
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    farmer = relationship("FarmerProfileModel", back_populates="planting_reports", lazy="joined")
    season_rel = relationship("SeasonModel", lazy="joined")
    harvest_reports = relationship("HarvestReportModel", back_populates="planting_report", cascade="all, delete-orphan")
    flag_rows = relationship("PlantingReportFlagModel", back_populates="report", cascade="all, delete-orphan", lazy="joined")

    @property
    def season(self) -> str:
        return self.season_rel.label if self.season_rel else ""

    @property
    def district(self) -> str:
        return self.farmer.district if self.farmer else "Anuradhapura"

    @property
    def irrigation_type(self) -> str:
        return self.irrigation_code

    @property
    def language(self) -> str:
        return self.lang_code

    @property
    def soil_ph(self) -> Optional[float]:
        return float(self.farmer.soil_ph) if (self.farmer and self.farmer.soil_ph is not None) else None

    @property
    def followed_recommendation(self) -> Optional[str]:
        if self.recommended_crop_shown is None:
            return None
        return "yes" if self.crop_id == self.recommended_crop_shown else "no"

    @property
    def flags(self) -> List[str]:
        return [f.flag_code for f in (self.flag_rows or [])]

    @property
    def timestamp(self) -> datetime:
        return self.submitted_at

    def to_dict(self) -> Dict[str, Any]:
        from govisense.feedback.receipts import planting_receipt
        first_harvest = self.harvest_reports[0] if self.harvest_reports else None
        return {
            **planting_receipt(self),
            "pseudonymous_id": self.pseudonymous_id,
            "crop_id": self.crop_id,
            "season_id": self.season_id,
            "season": self.season,
            "planned_area_ha": float(self.planned_area_ha),
            "actual_area_ha": float(self.actual_area_ha) if self.actual_area_ha is not None else None,
            "harvest_outcome_mt": round(first_harvest.harvest_quantity_kg / 1000.0, 3) if first_harvest else None,
            "sale_price_rs_kg": float(first_harvest.sale_price_rs_kg) if (first_harvest and first_harvest.sale_price_rs_kg is not None) else None,
            "sale_channel": first_harvest.channel_code if first_harvest else None,
            "district": self.district,
            "irrigation_type": self.irrigation_code,
            "irrigation_code": self.irrigation_code,
            "soil_ph": self.soil_ph,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "expected_harvest_date": self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            "recommended_crop_shown": self.recommended_crop_shown,
            "followed_recommendation": self.followed_recommendation,
            "reason": self.reason,
            "expected_price_rs_kg": float(self.expected_price_rs_kg) if self.expected_price_rs_kg is not None else None,
            "consent_given": bool(self.consent_given),
            "app_version": self.app_version,
            "language": self.lang_code,
            "lang_code": self.lang_code,
            "source": self.source,
            "flags": self.flags,
            "notes": self.notes,
            "submitted_at": self.submitted_at.isoformat() if hasattr(self.submitted_at, "isoformat") else str(self.submitted_at),
            "timestamp": self.submitted_at.isoformat() if hasattr(self.submitted_at, "isoformat") else str(self.submitted_at),
        }


class HarvestReportFlagModel(Base):
    __tablename__ = "harvest_report_flags"

    harvest_id = Column(String(36), ForeignKey("harvest_reports.harvest_id", ondelete="CASCADE"), primary_key=True)
    flag_code = Column(String(50), primary_key=True)

    harvest = relationship("HarvestReportModel", back_populates="flag_rows")


class HarvestReportProblemModel(Base):
    __tablename__ = "harvest_report_problems"

    harvest_id = Column(String(36), ForeignKey("harvest_reports.harvest_id", ondelete="CASCADE"), primary_key=True)
    problem_code = Column(String(50), primary_key=True)

    harvest = relationship("HarvestReportModel", back_populates="problem_rows")


class HarvestReportModel(Base):
    __tablename__ = "harvest_reports"

    harvest_id = Column(String(36), primary_key=True, default=lambda: f"HVST-{uuid.uuid4().hex[:8].upper()}")
    planting_report_id = Column(String(36), ForeignKey("planting_reports.report_id"), nullable=False)
    area_harvested_ha = Column(Numeric(8, 2), nullable=False)
    harvest_date = Column(Date, nullable=True)
    harvest_quantity_kg = Column(Float, nullable=False)
    loss_kg = Column(Float, nullable=False, default=0.0)
    quantity_sold_kg = Column(Float, nullable=False, default=0.0)
    quantity_stored_kg = Column(Float, nullable=False, default=0.0)
    sale_price_rs_kg = Column(Numeric(10, 2), nullable=True)
    channel_code = Column(String(30), ForeignKey("sale_channels.channel_code"), nullable=True)
    sale_month = Column(SmallInteger, nullable=True)
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    planting_report = relationship("PlantingReportModel", back_populates="harvest_reports", lazy="joined")
    flag_rows = relationship("HarvestReportFlagModel", back_populates="harvest", cascade="all, delete-orphan", lazy="joined")
    problem_rows = relationship("HarvestReportProblemModel", back_populates="harvest", cascade="all, delete-orphan", lazy="joined")

    @property
    def pseudonymous_id(self) -> Optional[str]:
        return self.planting_report.pseudonymous_id if self.planting_report else None

    @property
    def crop_id(self) -> Optional[str]:
        return self.planting_report.crop_id if self.planting_report else None

    @property
    def season(self) -> str:
        return self.planting_report.season if self.planting_report else ""

    @property
    def sale_channel(self) -> Optional[str]:
        return self.channel_code

    @property
    def flags(self) -> List[str]:
        return [f.flag_code for f in (self.flag_rows or [])]

    @property
    def problems(self) -> List[str]:
        return [p.problem_code for p in (self.problem_rows or [])]

    @property
    def timestamp(self) -> datetime:
        return self.submitted_at

    @property
    def yield_mt_per_ha(self) -> float:
        area = float(self.area_harvested_ha or 0.0)
        if area > 0:
            return round((float(self.harvest_quantity_kg) / 1000.0) / area, 2)
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
            "sale_channel": self.channel_code,
            "channel_code": self.channel_code,
            "sale_month": self.sale_month,
            "problems": self.problems,
            "notes": self.notes,
            "flags": self.flags,
            "submitted_at": self.submitted_at.isoformat() if hasattr(self.submitted_at, "isoformat") else str(self.submitted_at),
            "timestamp": self.submitted_at.isoformat() if hasattr(self.submitted_at, "isoformat") else str(self.submitted_at),
        }


# ===========================================================================
# 6. Officer Decisions (decision_history — append-only)
# ===========================================================================


class DecisionRecordModel(Base):
    __tablename__ = "decision_history"

    decision_id = Column(String(36), primary_key=True, default=lambda: f"DEC-{uuid.uuid4().hex[:8].upper()}")
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=False)
    record_hash = Column(CHAR(64), nullable=False, unique=True)
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    season_id = Column(SmallInteger, ForeignKey("seasons.season_id"), nullable=False)
    officer_id = Column(String(50), ForeignKey("officers.officer_id"), nullable=False)
    model_recommended_action = Column(String(50), ForeignKey("decision_actions.action_code"), nullable=True)
    officer_response = Column(String(20), nullable=False, default="accepted")
    action_type = Column(String(50), ForeignKey("decision_actions.action_code"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="MT")
    rationale = Column(Text, nullable=False)
    is_demo = Column(Boolean, nullable=False, default=False)
    data_available = Column(Boolean, nullable=False, default=True)
    source_type = Column(String(64), nullable=False, default="officer_audit_log")
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    run = relationship("PipelineRunModel", back_populates="decisions", lazy="joined")
    officer = relationship("OfficerModel", back_populates="decisions")
    season_rel = relationship("SeasonModel", lazy="joined")

    def __init__(self, **kwargs):
        passed_hash = kwargs.pop("hash", None)
        if passed_hash and not kwargs.get("record_hash"):
            kwargs["record_hash"] = passed_hash
        if "timestamp" in kwargs and "decided_at" not in kwargs:
            kwargs["decided_at"] = kwargs.pop("timestamp")
        else:
            kwargs.pop("timestamp", None)
        # Drop legacy denormalized fields (now on runs) if passed directly
        kwargs.pop("model_version", None)
        kwargs.pop("data_version", None)
        kwargs.pop("assumptions", None)
        super().__init__(**kwargs)

    @property
    def hash(self) -> str:
        return (self.record_hash or "").strip()

    @hash.setter
    def hash(self, value: str) -> None:
        self.record_hash = value

    @property
    def timestamp(self) -> datetime:
        return self.decided_at

    @property
    def season(self) -> str:
        return self.season_rel.label if self.season_rel else ""

    @property
    def model_version(self) -> str:
        return self.run.model_version if self.run else ""

    @property
    def data_version(self) -> str:
        return self.run.data_version if self.run else ""

    @property
    def assumptions(self) -> Dict[str, Any]:
        return (self.run.assumptions or {}) if self.run else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "run_id": self.run_id,
            "record_hash": self.hash,
            "hash": self.hash,
            "crop_id": self.crop_id,
            "season_id": self.season_id,
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
            "assumptions": self.assumptions,
            "is_demo": bool(self.is_demo),
            "data_available": bool(self.data_available),
            "source_type": self.source_type or "officer_audit_log",
            "decided_at": self.decided_at.isoformat() if hasattr(self.decided_at, "isoformat") else str(self.decided_at),
            "timestamp": self.decided_at.isoformat() if hasattr(self.decided_at, "isoformat") else str(self.decided_at),
        }


# ===========================================================================
# 7. Alerts, Translations, Status, Questions & Generic Audit Log
# ===========================================================================


class AlertTranslationModel(Base):
    __tablename__ = "alert_translations"

    alert_id = Column(String(36), ForeignKey("alerts.alert_id", ondelete="CASCADE"), primary_key=True)
    lang_code = Column(String(10), ForeignKey("languages.lang_code"), primary_key=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    alert = relationship("AlertModel", back_populates="translations")


class AlertModel(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(36), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}")
    crop_id = Column(String(50), ForeignKey("crops.crop_id"), nullable=False)
    district_id = Column(SmallInteger, ForeignKey("districts.district_id"), nullable=False)
    season_id = Column(SmallInteger, ForeignKey("seasons.season_id"), nullable=True)
    month = Column(Date, nullable=True)
    type_code = Column(String(30), ForeignKey("alert_types.type_code"), nullable=False)
    severity = Column(String(20), ForeignKey("severity_levels.severity_code"), nullable=False, default="warning")
    message_key = Column(String(100), nullable=False)
    params = Column(JSONB, nullable=False, default=dict)
    run_id = Column(String(36), ForeignKey("runs.run_id"), nullable=True)
    target_role = Column(String(20), ForeignKey("roles.role_code"), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    run = relationship("PipelineRunModel", back_populates="alerts")
    district_rel = relationship("DistrictModel", lazy="joined")
    season_rel = relationship("SeasonModel", lazy="joined")
    translations = relationship("AlertTranslationModel", back_populates="alert", cascade="all, delete-orphan", lazy="joined")
    statuses = relationship("AlertStatusModel", back_populates="alert", cascade="all, delete-orphan")
    questions = relationship("AlertQuestionModel", back_populates="alert", cascade="all, delete-orphan")

    @property
    def type(self) -> str:
        return self.type_code

    @property
    def district(self) -> str:
        return self.district_rel.name if self.district_rel else "Anuradhapura"

    @property
    def season(self) -> Optional[str]:
        return self.season_rel.label if self.season_rel else None

    def _tr(self, lang: str) -> Optional[AlertTranslationModel]:
        for t in self.translations or []:
            if t.lang_code == lang:
                return t
        return None

    def to_dict(self, lang: str = "en") -> Dict[str, Any]:
        tr_en = self._tr("en")
        tr_si = self._tr("si")
        tr_ta = self._tr("ta")
        tr_req = self._tr(lang) or tr_en

        return {
            "alert_id": self.alert_id,
            "crop_id": self.crop_id,
            "district_id": self.district_id,
            "district": self.district,
            "season_id": self.season_id,
            "season": self.season,
            "month": self.month.strftime("%Y-%m") if hasattr(self.month, "strftime") else None,
            "type": self.type_code,
            "type_code": self.type_code,
            "severity": self.severity,
            "title": tr_req.title if tr_req else (self.type_code or "Alert"),
            "message": tr_req.message if tr_req else "",
            "title_en": tr_en.title if tr_en else "",
            "title_si": tr_si.title if tr_si else None,
            "title_ta": tr_ta.title if tr_ta else None,
            "message_en": tr_en.message if tr_en else "",
            "message_si": tr_si.message if tr_si else None,
            "message_ta": tr_ta.message if tr_ta else None,
            "target_role": self.target_role or "all",
            "status": self.status,
            "message_key": self.message_key,
            "params": self.params or {},
            "run_id": self.run_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }


class AlertStatusModel(Base):
    __tablename__ = "alert_status"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    alert_id = Column(String(36), ForeignKey("alerts.alert_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("alert_id", "user_id", name="uq_alert_user"),)

    alert = relationship("AlertModel", back_populates="statuses")
    user = relationship("UserModel", back_populates="alert_statuses")

    @property
    def acknowledged(self) -> bool:
        return self.acknowledged_at is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "acknowledged": self.acknowledged,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }


class AlertQuestionModel(Base):
    __tablename__ = "alert_questions"

    question_id = Column(BigInteger, Identity(always=True), primary_key=True)
    alert_id = Column(String(36), ForeignKey("alerts.alert_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    asked_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    answered_by = Column(String(50), ForeignKey("officers.officer_id"), nullable=True)
    officer_response = Column(Text, nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    alert = relationship("AlertModel", back_populates="questions")
    user = relationship("UserModel", back_populates="alert_questions", foreign_keys=[user_id])


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    audit_id = Column(BigInteger, Identity(always=True), primary_key=True)
    table_name = Column(String(63), nullable=False)
    record_pk = Column(Text, nullable=False)
    action = Column(String(6), nullable=False)
    changed_by = Column(Text, nullable=False)
    old_data = Column(JSONB, nullable=True)
    new_data = Column(JSONB, nullable=True)
    changed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# Backward compatibility aliases
User = UserModel
Officer = OfficerModel
FarmerProfile = FarmerProfileModel
PlantingReport = PlantingReportModel
PlantingReportRecord = PlantingReportModel
HarvestReport = HarvestReportModel
PipelineRun = PipelineRunModel
ForecastSnapshot = ForecastSnapshotModel
DecisionRecord = DecisionRecordModel
DecisionHistoryRecord = DecisionRecordModel
MonthlyData = MonthlyDataModel
DataCatalogue = DataCatalogueModel
Alert = AlertModel
AlertInteraction = AlertStatusModel
AlertStatus = AlertStatusModel
EvaluationResult = EvaluationResultModel
