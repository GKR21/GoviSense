"""
FastAPI Dependencies, JWT Authentication, Role Guards, and Rate Limiting
Team DARKBITE · ModelX 2.0
Provides database sessions, user identity, rate limiting, and RBAC authorization dependencies.
"""

from __future__ import annotations

import time
from typing import Optional, Dict, Any, Generator
from collections import defaultdict

from fastapi import Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session

from govisense.db.session import get_db, get_db_session
from govisense.api.auth import (
    get_current_user,
    require_farmer,
    require_officer,
    require_admin,
    require_officer_or_admin,
    require_authenticated,
    require_role,
    get_current_farmer,
    get_current_officer,
    get_current_admin,
    RoleChecker,
    decode_token,
    oauth2_scheme,
)

# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

_RATE_LIMIT_BUCKET: Dict[str, list] = defaultdict(list)
_RATE_LIMIT_MAX_REQUESTS = 120  # Max 120 submissions per window
_RATE_LIMIT_WINDOW_SECONDS = 60  # 1 minute window


def rate_limiter(request: Request, authorization: Optional[str] = Header(None)):
    """
    In-memory token bucket rate limiter for write endpoints.
    Tracks client IP or user token. Rejects with 429 when threshold exceeded.
    """
    client_key = request.client.host if request.client else "unknown"
    if authorization and authorization.startswith("Bearer "):
        client_key = authorization.split(" ")[1][:16]

    now = time.time()
    timestamps = _RATE_LIMIT_BUCKET[client_key]

    # Filter out entries older than window
    valid_timestamps = [ts for ts in timestamps if now - ts < _RATE_LIMIT_WINDOW_SECONDS]
    _RATE_LIMIT_BUCKET[client_key] = valid_timestamps

    if len(valid_timestamps) >= _RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down and try again.",
        )

    _RATE_LIMIT_BUCKET[client_key].append(now)


# ---------------------------------------------------------------------------
# User Authentication Helpers
# ---------------------------------------------------------------------------

def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional bearer auth for endpoints accessible both publicly and authenticated."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        from govisense.api.routes.auth import verify_jwt_token
        return verify_jwt_token(token)
    except Exception:
        return None


__all__ = [
    "get_db",
    "get_db_session",
    "get_current_user",
    "get_optional_current_user",
    "require_farmer",
    "require_officer",
    "require_admin",
    "require_officer_or_admin",
    "require_authenticated",
    "require_role",
    "get_current_farmer",
    "get_current_officer",
    "get_current_admin",
    "RoleChecker",
    "decode_token",
    "oauth2_scheme",
    "rate_limiter",
]
