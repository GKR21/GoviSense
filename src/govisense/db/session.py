"""
Database Session and Engine Configuration for GoviSense
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  - Database engine supporting SQLite (with WAL mode & busy timeout) and PostgreSQL
  - Concurrent-write safety for SQLite via WAL, timeout, and thread lock
  - SessionLocal factory and FastAPI dependency get_db()
  - Database initialization and automated legacy JSON data migration
"""

from __future__ import annotations

import os
import json
import logging
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

from govisense.config import PROCESSED_DATA_DIR
from govisense.db.models import (
    Base,
    User,
    PlantingReportRecord,
    DecisionHistoryRecord,
    Alert,
    MarketPriceRecord,
)

logger = logging.getLogger("govisense.db")

# Thread lock to serialize SQLite writes across worker threads
sqlite_write_lock = threading.Lock()

# Database URL configuration
DEFAULT_DB_PATH = PROCESSED_DATA_DIR / "govisense.db"
_raw_url = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Standardize postgres URI for SQLAlchemy
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = _raw_url

# Configure engine with concurrent-write safety
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs = {
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30.0,  # 30 seconds busy wait
        }
    }
else:
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)


# Enable WAL mode and pragma configurations for SQLite on connect
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")  # 30,000 ms
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for non-HTTP workflows and internal services."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def migrate_legacy_json_files(db: Session) -> None:
    """
    Migrates legacy planting_reports.json and decision_history.json
    into SQLite/PostgreSQL if database tables are currently empty.
    """
    # 1. Planting Reports Migration
    planting_json_path = PROCESSED_DATA_DIR / "planting_reports.json"
    if planting_json_path.exists():
        existing_count = db.query(PlantingReportRecord).count()
        if existing_count == 0:
            try:
                with open(planting_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        PlantingReportRecord(
                            report_id=item.get("report_id", ""),
                            crop_id=item.get("crop_id", "big_onion"),
                            season=item.get("season", "Maha 2025/2026"),
                            planned_area_ha=float(item.get("planned_area_ha", 0.0)),
                            actual_area_ha=float(item.get("actual_area_ha", 0.0)),
                            consent_given=bool(item.get("consent_given", True)),
                            pseudonymous_id=item.get("pseudonymous_id", "ANON"),
                            harvest_outcome_mt=item.get("harvest_outcome_mt"),
                            sale_price_rs_kg=item.get("sale_price_rs_kg"),
                            sale_channel=item.get("sale_channel"),
                            notes=item.get("notes"),
                            timestamp=item.get("timestamp", ""),
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info(f"Migrated {len(records)} planting reports from JSON to database.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to migrate planting_reports.json: {e}")

    # 2. Decision History Migration
    history_json_path = PROCESSED_DATA_DIR / "decision_history.json"
    if history_json_path.exists():
        existing_count = db.query(DecisionHistoryRecord).count()
        if existing_count == 0:
            try:
                with open(history_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        DecisionHistoryRecord(
                            decision_id=item.get("decision_id", ""),
                            crop_id=item.get("crop_id", "big_onion"),
                            season=item.get("season", "Maha 2025/2026"),
                            officer_id=item.get("officer_id", "OFFICER-001"),
                            action_type=item.get("action_type", "HOLD_STORAGE"),
                            quantity=float(item.get("quantity", 0.0)),
                            unit=item.get("unit", "MT"),
                            rationale=item.get("rationale", ""),
                            model_version=item.get("model_version", "LightGBM-v2.1+HiGHS-LP"),
                            data_version=item.get("data_version", "CBSL-HARTI-DOA-2024.12"),
                            assumptions=item.get("assumptions", {}),
                            timestamp=item.get("timestamp", ""),
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info(f"Migrated {len(records)} decision history items from JSON to database.")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to migrate decision_history.json: {e}")


def seed_default_users(db: Session) -> None:
    """Seeds demo officer, farmer, and admin accounts if not already present."""
    try:
        from govisense.api.auth import get_password_hash
        hash_func = get_password_hash
    except Exception:
        import hashlib
        def hash_func(pw: str) -> str:
            return hashlib.sha256(pw.encode()).hexdigest()

    existing_usernames = {u.username for u in db.query(User.username).all()}

    demo_users = [
        User(
            username="admin_govisense",
            hashed_password=hash_func("Admin@123"),
            role="admin",
            full_name="System Administrator (National)",
            phone_number="+94112345678",
            district="National",
            is_active=True,
        ),
        User(
            username="officer_anuradhapura",
            hashed_password=hash_func("Officer@123"),
            role="officer",
            full_name="Kavinda Perera (Agricultural Officer)",
            phone_number="+94771234567",
            district="Anuradhapura",
            is_active=True,
        ),
        User(
            username="farmer_kamal",
            hashed_password=hash_func("Farmer@123"),
            role="farmer",
            full_name="Kamal Gunaratne",
            phone_number="+94777654321",
            district="Anuradhapura",
            is_active=True,
        ),
    ]

    users_to_add = [u for u in demo_users if u.username not in existing_usernames]
    if users_to_add:
        db.bulk_save_objects(users_to_add)
        db.commit()
        logger.info(f"Seeded default users: {[u.username for u in users_to_add]}.")


def migrate_db_columns() -> None:
    """Migrates missing columns in existing SQLite tables (e.g. run_id, hash, is_demo, market_prices)."""
    try:
        with engine.connect() as conn:
            # 1. Migrate decision_history
            res = conn.execute(text("PRAGMA table_info(decision_history);")).fetchall()
            existing_cols = {row[1] for row in res}
            if existing_cols:
                cols_to_add = [
                    ("run_id", "VARCHAR(64)"),
                    ("hash", "VARCHAR(64)"),
                    ("is_demo", "BOOLEAN DEFAULT 0 NOT NULL"),
                    ("data_available", "BOOLEAN DEFAULT 1 NOT NULL"),
                    ("source_type", "VARCHAR(64) DEFAULT 'officer_audit_log' NOT NULL"),
                ]
                for col_name, col_type in cols_to_add:
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE decision_history ADD COLUMN {col_name} {col_type};"))
                conn.commit()

            # 2. Migrate market_prices
            res_prices = conn.execute(text("PRAGMA table_info(market_prices);")).fetchall()
            existing_price_cols = {row[1] for row in res_prices}
            if existing_price_cols:
                price_cols_to_add = [
                    ("crop_en", "VARCHAR(128)"),
                    ("crop_si", "VARCHAR(128)"),
                    ("crop_ta", "VARCHAR(128)"),
                    ("category", "VARCHAR(64) DEFAULT 'vegetable' NOT NULL"),
                    ("economic_center_en", "VARCHAR(128)"),
                    ("economic_center_si", "VARCHAR(128)"),
                    ("economic_center_ta", "VARCHAR(128)"),
                    ("wholesale_price_display", "VARCHAR(64)"),
                    ("retail_price_display", "VARCHAR(64)"),
                    ("trend_pct", "VARCHAR(64) DEFAULT '±0% (Stable)' NOT NULL"),
                    ("is_up", "BOOLEAN DEFAULT 0 NOT NULL"),
                    ("is_stable", "BOOLEAN DEFAULT 1 NOT NULL"),
                ]
                for col_name, col_type in price_cols_to_add:
                    if col_name not in existing_price_cols:
                        conn.execute(text(f"ALTER TABLE market_prices ADD COLUMN {col_name} {col_type};"))
                conn.commit()
    except Exception as e:
        logger.warning(f"Column migration warning: {e}")


def seed_market_prices(db: Session) -> None:
    """Seeds CBSL & HARTI benchmark DEC market prices if table is empty."""
    try:
        count = db.query(MarketPriceRecord).count()
        if count == 0:
            prices = [
                MarketPriceRecord(
                    crop_id="big_onion",
                    crop_name="Big Onion (Local Dambulla)",
                    crop_en="Big Onion (Local Dambulla)",
                    crop_si="ලොකු ළූණු (දේශීය දඹුල්ල)",
                    crop_ta="பெரிய வெங்காயம் (உள்ளூர்)",
                    category="vegetable",
                    market_center="Dambulla DEC",
                    economic_center_en="Dambulla DEC",
                    economic_center_si="දඹුල්ල ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="தம்புள்ளை பொருளாதார மையம்",
                    wholesale_price=342.5,
                    retail_price=440.0,
                    wholesale_price_display="Rs 320 – 365 / kg",
                    retail_price_display="Rs 420 – 460 / kg",
                    trend_pct="+4% (Firming)",
                    is_up=True,
                    is_stable=False,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
                MarketPriceRecord(
                    crop_id="chilli",
                    crop_name="Green Chilli (MICH 1)",
                    crop_en="Green Chilli (MICH 1)",
                    crop_si="අමු මිරිස් (MICH 1)",
                    crop_ta="பச்சை மிளகாய் (MICH 1)",
                    category="vegetable",
                    market_center="Dambulla DEC",
                    economic_center_en="Dambulla DEC",
                    economic_center_si="දඹුල්ල ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="தம்புள்ளை பொருளாதார மையம்",
                    wholesale_price=260.0,
                    retail_price=380.0,
                    wholesale_price_display="Rs 240 – 280 / kg",
                    retail_price_display="Rs 350 – 410 / kg",
                    trend_pct="±1% (Stable)",
                    is_up=False,
                    is_stable=True,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
                MarketPriceRecord(
                    crop_id="green_gram",
                    crop_name="Green Gram (MI-5 / MI-6)",
                    crop_en="Green Gram (MI-5 / MI-6)",
                    crop_si="මුං ඇට (MI-5 / MI-6)",
                    crop_ta="பச்சைப் பயறு (MI-5)",
                    category="pulse",
                    market_center="Keppetipola DEC",
                    economic_center_en="Keppetipola DEC",
                    economic_center_si="කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="கெப்பெட்டிபொல பொருளாதார மையம்",
                    wholesale_price=415.0,
                    retail_price=535.0,
                    wholesale_price_display="Rs 390 – 440 / kg",
                    retail_price_display="Rs 510 – 560 / kg",
                    trend_pct="+2% (Upward)",
                    is_up=True,
                    is_stable=False,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
                MarketPriceRecord(
                    crop_id="maize",
                    crop_name="Maize (Feed Grade)",
                    crop_en="Maize (Feed Grade)",
                    crop_si="බඩඉරිඟු (සත්ත්ව ආහාර)",
                    crop_ta="மக்காச்சோளம் (தீவனம்)",
                    category="grain",
                    market_center="Anuradhapura DEC",
                    economic_center_en="Anuradhapura DEC",
                    economic_center_si="අනුරාධපුර ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="அனுராதபுர பொருளாதார மையம்",
                    wholesale_price=121.5,
                    retail_price=155.0,
                    wholesale_price_display="Rs 115 – 128 / kg",
                    retail_price_display="Rs 145 – 165 / kg",
                    trend_pct="±0% (Stable)",
                    is_up=False,
                    is_stable=True,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
                MarketPriceRecord(
                    crop_id="red_onion",
                    crop_name="Red Onion (Jaffna / Puttalam)",
                    crop_en="Red Onion (Jaffna / Puttalam)",
                    crop_si="රතු ළූණු (යාපනය / පුත්තලම)",
                    crop_ta="சின்ன வெங்காயம் (யாழ்ப்பாணம்)",
                    category="vegetable",
                    market_center="Meegoda DEC",
                    economic_center_en="Meegoda DEC",
                    economic_center_si="මීගොඩ ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="மீகொட பொருளாதார மையம்",
                    wholesale_price=315.0,
                    retail_price=420.0,
                    wholesale_price_display="Rs 290 – 340 / kg",
                    retail_price_display="Rs 390 – 450 / kg",
                    trend_pct="+3% (Upward)",
                    is_up=True,
                    is_stable=False,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
                MarketPriceRecord(
                    crop_id="potato",
                    crop_name="Potato (Nuwara Eliya)",
                    crop_en="Potato (Nuwara Eliya)",
                    crop_si="අර්තාපල් (නුවරඑළිය)",
                    crop_ta="உருளைக்கிழங்கு (நுவரெலியா)",
                    category="tuber",
                    market_center="Keppetipola DEC",
                    economic_center_en="Keppetipola DEC",
                    economic_center_si="කැප්පෙටිපොල ආර්ථික මධ්‍යස්ථානය",
                    economic_center_ta="கெப்பெட்டிபொல பொருளாதார மையம்",
                    wholesale_price=310.0,
                    retail_price=410.0,
                    wholesale_price_display="Rs 290 – 330 / kg",
                    retail_price_display="Rs 380 – 440 / kg",
                    trend_pct="-3% (Downward)",
                    is_up=False,
                    is_stable=False,
                    price_date="2026-11-08",
                    source="CBSL/HARTI",
                ),
            ]
            db.bulk_save_objects(prices)
            db.commit()
            logger.info("Seeded 6 benchmark DEC market prices from CBSL/HARTI.")
    except Exception as e:
        db.rollback()
        logger.warning(f"Error seeding market prices: {e}")


def init_db() -> None:
    """Initializes tables, sets up WAL pragmas, and runs initial data migrations."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    migrate_db_columns()
    with get_db_session() as db:
        migrate_legacy_json_files(db)
        seed_default_users(db)
        seed_market_prices(db)

