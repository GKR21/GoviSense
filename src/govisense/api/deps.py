"""
FastAPI Dependencies, JWT Authentication, Role Guards, and Rate Limiting
Team DARKBITE · ModelX 2.0
"""

from __future__ import annotations

import time
from typing import Optional, Dict, Any, Generator
from collections import defaultdict

from fastapi import Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session

from govisense.api.routes.auth import verify_jwt_token
from govisense.db.session import get_db

# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

_RATE_LIMIT_BUCKET: Dict[str, list] = defaultdict(list)
_RATE_LIMIT_MAX_REQUESTS = 30  # Max 30 submissions per window
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
# User Authentication & Role Guards
# ---------------------------------------------------------------------------

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the JWT Bearer token.
    Raises 401 UNAUTHORIZED if missing, expired, or signature is invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or token is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional bearer auth for endpoints accessible both publicly and authenticated."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    return verify_jwt_token(token)


def require_officer(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Role Guard: Requires Officer or Admin privileges.
    Raises 403 FORBIDDEN if the user is a farmer or unprivileged account.
    """
    role = str(current_user.get("role", "")).lower()
    if role not in ("officer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Officer authorization required. Your role does not permit this action.",
        )
    return current_user


def require_farmer(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Role Guard: Requires Farmer, Officer, or Admin privileges.
    """
    role = str(current_user.get("role", "")).lower()
    if role not in ("farmer", "officer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmer account required. Your role does not permit this action.",
        )
    return current_user


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Role Guard: Requires Admin privileges.
    """
    role = str(current_user.get("role", "")).lower()
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator authorization required.",
        )
    return current_user
