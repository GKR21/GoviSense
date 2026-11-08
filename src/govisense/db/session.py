"""
Database Engine & Session Management for GoviSense
Team DARKBITE · ModelX 2.0
Pilot: Anuradhapura (Big Onion, Chilli)

Supports PostgreSQL via SQLAlchemy and psycopg2 with automatic connection pooling.
Falls back to SQLite for local standalone development/testing if PostgreSQL server is offline.
"""

from __future__ import annotations

import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from govisense.config import settings
from govisense.db.models import Base

logger = logging.getLogger("govisense.db")

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


def get_engine(force_new: bool = False) -> Engine:
    """
    Returns the active SQLAlchemy Engine.
    Attempts connection to PostgreSQL first; falls back to SQLite if unreachable.
    """
    global _ENGINE, _SESSION_FACTORY, _ACTIVE_DIALECT

    if _ENGINE is not None and not force_new:
        return _ENGINE

    target_url = _normalize_db_url(settings.database_url)
    
    # Configure connection arguments based on database dialect
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
            # Test immediate connectivity
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
                connect_args={"check_same_thread": False},
                echo=settings.db_echo,
            )
            _ACTIVE_DIALECT = "sqlite"
    else:
        _ENGINE = create_engine(
            target_url,
            connect_args={"check_same_thread": False} if "sqlite" in target_url else {},
            echo=settings.db_echo,
        )
        _ACTIVE_DIALECT = "sqlite" if "sqlite" in target_url else "other"

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


def get_active_dialect() -> str:
    """Returns 'postgresql' or 'sqlite'."""
    if _ENGINE is None:
        get_engine()
    return _ACTIVE_DIALECT


def init_db(engine: Optional[Engine] = None) -> None:
    """
    Creates all defined database tables in PostgreSQL / database engine.
    """
    eng = engine or get_engine()
    Base.metadata.create_all(bind=eng)
    logger.info("Database schema initialized with tables: %s", list(Base.metadata.tables.keys()))

