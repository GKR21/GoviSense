"""
Database Engine & Session Management for GoviSense
Team DARKBITE · ModelX 2.0
Pilot: Anuradhapura (Big Onion, Chilli)

Supports PostgreSQL via SQLAlchemy and psycopg2 with automatic connection pooling.
Falls back to SQLite for local standalone development/testing if PostgreSQL server is offline,
with SQLite WAL mode, 30s busy timeout, and thread write lock for concurrent-write safety.
"""

from __future__ import annotations

import json
import logging
import threading
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, Engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from govisense.config import settings, PROCESSED_DATA_DIR
from govisense.db.models import (
    Base,
    UserModel,
    PlantingReportModel,
    DecisionRecordModel,
    MarketPriceRecord,
)

logger = logging.getLogger("govisense.db")

# Thread lock to serialize SQLite writes across worker threads
sqlite_write_lock = threading.Lock()

_ENGINE: Optional[Engine] = None
_SESSION_FACTORY: Optional[sessionmaker] = None
_ACTIVE_DIALECT: str = "unknown"


def _normalize_db_url(url: str) -> str:
    """Normalize Postgres URLs to use psycopg2 dialect."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _attach_sqlite_wal_listener(eng: Engine) -> None:
    """Enable WAL mode, normal sync, and 30s busy timeout for SQLite connections."""
    @event.listens_for(eng, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


def get_engine(force_new: bool = False) -> Engine:
    """
    Returns the active SQLAlchemy Engine.
    Attempts connection to PostgreSQL first; falls back to SQLite if unreachable.
    """
    global _ENGINE, _SESSION_FACTORY, _ACTIVE_DIALECT

    if _ENGINE is not None and not force_new:
        return _ENGINE

    target_url = _normalize_db_url(settings.database_url)

    if "postgresql" in target_url:
        try:
            pg_engine = create_engine(
                target_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.db_echo,
                connect_args={"connect_timeout": 3},
            )
            with pg_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _ENGINE = pg_engine
            _ACTIVE_DIALECT = "postgresql"
            logger.info("Successfully connected to PostgreSQL database at %s", target_url.split("@")[-1])
        except (OperationalError, Exception) as exc:
            logger.warning(
                "PostgreSQL server not accessible (%s). Falling back to local persistent SQLite (%s).",
                str(exc).split("\n")[0],
                settings.fallback_sqlite_url,
            )
            sqlite_url = settings.fallback_sqlite_url
            _ENGINE = create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False, "timeout": 30.0},
                echo=settings.db_echo,
            )
            _attach_sqlite_wal_listener(_ENGINE)
            _ACTIVE_DIALECT = "sqlite"
    else:
        is_sqlite = "sqlite" in target_url
        _ENGINE = create_engine(
            target_url,
            connect_args={"check_same_thread": False, "timeout": 30.0} if is_sqlite else {},
            echo=settings.db_echo,
        )
        if is_sqlite:
            _attach_sqlite_wal_listener(_ENGINE)
        _ACTIVE_DIALECT = "sqlite" if is_sqlite else "other"

    _SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)
    return _ENGINE


def get_session() -> Session:
    """Creates a new SQLAlchemy session."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None or _ENGINE is None:
        get_engine()
    return _SESSION_FACTORY()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session,
    committing on clean exit and closing automatically.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for non-HTTP workflows and internal services."""
    db = get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_active_dialect() -> str:
    """Returns 'postgresql' or 'sqlite'."""
    if _ENGINE is None:
        get_engine()
    return _ACTIVE_DIALECT


def seed_master_data_if_empty(eng: Engine) -> None:
    """Seeds monthly_data table from monthly_master.csv if table is empty."""
    import pandas as pd
    from govisense.db.models import MonthlyDataModel

    master_csv = PROCESSED_DATA_DIR / "monthly_master.csv"
    if not master_csv.exists():
        return

    SessionMaker = sessionmaker(bind=eng)
    with SessionMaker() as session:
        try:
            cnt = session.query(MonthlyDataModel).count()
            if cnt == 0:
                df = pd.read_csv(master_csv)
                records = []
                for _, r in df.iterrows():
                    m = MonthlyDataModel(
                        crop_id=str(r["crop"]),
                        district=str(r["district"]),
                        month=str(r["year_month"]),
                        planted_area_ha=float(r["planted_extent_ha"]) if pd.notnull(r["planted_extent_ha"]) else None,
                        yield_mt_ha=float(r["yield_mt_per_ha"]) if pd.notnull(r["yield_mt_per_ha"]) else None,
                        production_mt=float(r["harvest_volume_mt"]) if pd.notnull(r["harvest_volume_mt"]) else None,
                        wholesale_price_rs_kg=float(r["wholesale_price_rs_kg"]) if pd.notnull(r["wholesale_price_rs_kg"]) else None,
                        retail_price_rs_kg=float(r["retail_price_rs_kg"]) if pd.notnull(r["retail_price_rs_kg"]) else None,
                        farmgate_price_rs_kg=float(r["farmgate_price_rs_kg"]) if pd.notnull(r["farmgate_price_rs_kg"]) else None,
                        imports_mt=float(r["import_volume_mt"]) if pd.notnull(r["import_volume_mt"]) else None,
                        weather_rainfall_anomaly=float(r["rainfall_anomaly_mm"]) if pd.notnull(r["rainfall_anomaly_mm"]) else None,
                        source_type=str(r.get("source_type", "real")),
                    )
                    records.append(m)
                session.add_all(records)
                session.commit()
                logger.info("Loaded %d master rows into monthly_data table.", len(records))
        except Exception as exc:
            logger.warning("Could not auto-seed monthly_data table: %s", exc)


def migrate_db_columns(eng: Optional[Engine] = None) -> None:
    """Migrates missing columns in existing SQLite tables gracefully."""
    target_eng = eng or get_engine()
    if target_eng.dialect.name != "sqlite":
        return
    try:
        with target_eng.connect() as conn:
            migrations = {
                "users": [
                    ("id", "INTEGER"),
                    ("hashed_password", "VARCHAR(255)"),
                    ("full_name", "VARCHAR(128)"),
                    ("phone_number", "VARCHAR(32)"),
                    ("district", "VARCHAR(64) DEFAULT 'Anuradhapura'"),
                    ("is_active", "BOOLEAN DEFAULT 1 NOT NULL"),
                    ("updated_at", "DATETIME"),
                ],
                "planting_reports": [
                    ("harvest_outcome_mt", "FLOAT"),
                    ("sale_price_rs_kg", "FLOAT"),
                    ("sale_channel", "VARCHAR(64)"),
                ],
                "decision_history": [
                    ("is_demo", "BOOLEAN DEFAULT 0 NOT NULL"),
                    ("data_available", "BOOLEAN DEFAULT 1 NOT NULL"),
                    ("source_type", "VARCHAR(64) DEFAULT 'officer_audit_log' NOT NULL"),
                ],
                "alerts": [
                    ("title_en", "VARCHAR(255)"),
                    ("title_si", "VARCHAR(255)"),
                    ("title_ta", "VARCHAR(255)"),
                    ("message_en", "TEXT"),
                    ("message_si", "TEXT"),
                    ("message_ta", "TEXT"),
                    ("target_role", "VARCHAR(32) DEFAULT 'all'"),
                    ("status", "VARCHAR(32) DEFAULT 'active'"),
                ],
                "alert_status": [
                    ("farmer_id", "VARCHAR(64)"),
                    ("acknowledged", "BOOLEAN DEFAULT 0 NOT NULL"),
                    ("question", "TEXT"),
                    ("officer_response", "TEXT"),
                    ("created_at", "DATETIME"),
                    ("updated_at", "DATETIME"),
                ],
                "market_prices": [
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
                ],
            }
            for tbl, cols in migrations.items():
                res = conn.execute(text(f"PRAGMA table_info({tbl});")).fetchall()
                existing_cols = {row[1] for row in res}
                if existing_cols:
                    for col_name, col_type in cols:
                        if col_name not in existing_cols:
                            conn.execute(text(f"ALTER TABLE {tbl} ADD COLUMN {col_name} {col_type};"))
            conn.commit()
    except Exception as e:
        logger.warning("Column migration warning: %s", e)


def migrate_legacy_json_files(db: Session) -> None:
    """
    Migrates legacy planting_reports.json and decision_history.json
    into SQLite/PostgreSQL if database tables are currently empty.
    """
    planting_json_path = PROCESSED_DATA_DIR / "planting_reports.json"
    if planting_json_path.exists():
        try:
            if db.query(PlantingReportModel).count() == 0:
                with open(planting_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        PlantingReportModel(
                            report_id=item.get("report_id") or None,
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
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info("Migrated %d planting reports from JSON to database.", len(records))
        except Exception as e:
            db.rollback()
            logger.warning("Failed to migrate planting_reports.json: %s", e)

    history_json_path = PROCESSED_DATA_DIR / "decision_history.json"
    if history_json_path.exists():
        try:
            if db.query(DecisionRecordModel).count() == 0:
                with open(history_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                records = []
                for item in data:
                    records.append(
                        DecisionRecordModel(
                            decision_id=item.get("decision_id") or None,
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
                        )
                    )
                if records:
                    db.bulk_save_objects(records)
                    db.commit()
                    logger.info("Migrated %d decision history items from JSON to database.", len(records))
        except Exception as e:
            db.rollback()
            logger.warning("Failed to migrate decision_history.json: %s", e)


def seed_default_users(db: Session) -> None:
    """Seeds demo officer, farmer, and admin accounts if not already present."""
    try:
        from govisense.api.auth import get_password_hash
        hash_func = get_password_hash
    except Exception:
        from govisense.db.models import hash_password
        hash_func = hash_password

    existing_usernames = {u.username for u in db.query(UserModel.username).all()}

    demo_users = [
        UserModel(
            username="admin_govisense",
            hashed_password=hash_func("Admin@123"),
            role="admin",
            full_name="System Administrator (National)",
            phone_number="+94112345678",
            district="National",
            is_active=True,
        ),
        UserModel(
            username="officer_anuradhapura",
            hashed_password=hash_func("Officer@123"),
            role="officer",
            full_name="Kavinda Perera (Agricultural Officer)",
            phone_number="+94771234567",
            district="Anuradhapura",
            is_active=True,
        ),
        UserModel(
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
        db.add_all(users_to_add)
        db.commit()
        logger.info("Seeded default users: %s", [u.username for u in users_to_add])


def seed_market_prices(db: Session) -> None:
    """Seeds CBSL & HARTI benchmark DEC market prices if table is empty."""
    try:
        if db.query(MarketPriceRecord).count() == 0:
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
            db.add_all(prices)
            db.commit()
            logger.info("Seeded 6 benchmark DEC market prices from CBSL/HARTI.")
    except Exception as e:
        db.rollback()
        logger.warning("Error seeding market prices: %s", e)


def init_db(engine: Optional[Engine] = None) -> None:
    """
    Creates all defined database tables, configures WAL pragmas, and runs baseline seeders.
    """
    eng = engine or get_engine()
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=eng)
    migrate_db_columns(eng)
    logger.info("Database schema initialized with tables: %s", list(Base.metadata.tables.keys()))
    seed_master_data_if_empty(eng)
    with get_db_session() as db:
        migrate_legacy_json_files(db)
        seed_default_users(db)
        seed_market_prices(db)


engine = get_engine()
