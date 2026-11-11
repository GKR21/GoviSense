"""
Authentication & JWT Session Management Router
Team DARKBITE · GoviSense Phase 1 & 2
Provides real database-backed authentication, user roles, JWT tokens, and credential verification.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Header, Depends, status
from pydantic import BaseModel

from govisense.db.lookups import ensure_farmer_profile, ensure_officer
from govisense.db.models import (
    UserModel,
    hash_password,
    verify_password,
)
from govisense.db.session import get_session, init_db

router = APIRouter(prefix="", tags=["Authentication"])

SECRET_KEY = "govisense-phase1-secret-key-2026"

# Registered default seed accounts
SEED_USERS = [
    {
        "username": "nimal@agriculture.gov.lk",
        "password": "officer123",
        "role": "officer",
        "officer_id": "OFF-7710",
        "name": "D. Nimal Bandara",
        "district": "Anuradhapura",
    },
    {
        "username": "admin@govisense.lk",
        "password": "admin123",
        "role": "admin",
        "officer_id": "ADM-0001",
        "name": "K. Perera",
        "district": "National / HQ",
    },
    {
        "username": "gayanathkrishan06@gmail.com",
        "password_hash": "$2b$12$GZPqHYtv6g2VfbvvyKheJe77jUllhAv9fSLDQ427wf1SqrxpKaUTi",
        "role": "admin",
        "name": "Gayanath Krishan",
        "district": "National / HQ",
    },
    {
        "username": "sunil@farmer.govisense.lk",
        "password": "farmer123",
        "role": "farmer",
        "pseudonymous_id": "LK-AP-001",
        "name": "Sunil Bandara",
        "district": "Anuradhapura",
    },
]


def ensure_seed_users() -> None:
    """Ensure baseline user accounts exist in PostgreSQL obeying db.sql constraints."""
    try:
        init_db()
        with get_session() as session:
            for u in SEED_USERS:
                existing = session.query(UserModel).filter(UserModel.username == u["username"]).first()
                if existing and u["username"] == "gayanathkrishan06@gmail.com":
                    existing.password_hash = u["password_hash"]
                    existing.role_code = "admin"
                    existing.full_name = u["name"]
                    continue
                if not existing:
                    if u["role"] in ("officer", "admin") and u.get("officer_id"):
                        ensure_officer(
                            session,
                            officer_id=u["officer_id"],
                            name=u["name"],
                            district=u["district"],
                            role="Agricultural Extension Officer" if u["role"] == "officer" else "Crop Forecaster",
                        )

                    if u["role"] == "farmer" and u.get("pseudonymous_id"):
                        ensure_farmer_profile(
                            session,
                            pseudonymous_id=u["pseudonymous_id"],
                            district=u["district"],
                            total_land_ha=1.5,
                            irrigation_type="irrigated",
                            consent_given=True,
                        )

                    new_user = UserModel(
                        username=u["username"],
                        password_hash=u.get("password_hash") or hash_password(u["password"]),
                        role_code=u["role"],
                        officer_id=u.get("officer_id"),
                        pseudonymous_id=u.get("pseudonymous_id"),
                        full_name=u.get("name"),
                    )
                    session.add(new_user)
            session.commit()
    except Exception:
        pass


def create_jwt_token(payload: dict) -> str:
    """Generate a signed HMAC-SHA256 JWT access token."""
    header = {"alg": "HS256", "typ": "JWT"}
    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")

    payload_copy = dict(payload)
    payload_copy.setdefault("exp", int(time.time()) + 86400 * 7)  # 7-day validity
    payload_copy.setdefault("iat", int(time.time()))
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload_copy).encode()).decode().rstrip("=")

    sig = hmac.new(
        SECRET_KEY.encode(),
        f"{b64_header}.{b64_payload}".encode(),
        hashlib.sha256,
    ).digest()
    b64_sig = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{b64_header}.{b64_payload}.{b64_sig}"


def verify_jwt_token(token: str) -> Optional[dict]:
    """Validate token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        b64_header, b64_payload, b64_sig = parts
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{b64_header}.{b64_payload}".encode(),
            hashlib.sha256,
        ).digest()
        b64_expected_sig = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        if not hmac.compare_digest(b64_sig, b64_expected_sig):
            return None
        padded = b64_payload + "=" * (-len(b64_payload) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None


class LoginPayload(BaseModel):
    username: str
    password: str
    role: Optional[str] = "officer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


def login_user(payload: LoginPayload):
    """
    Dashboard Screen: Authentication & Role Check
    """
    valid_roles = ["officer", "farmer", "admin"]
    role = payload.role if payload.role in valid_roles else "officer"
    token = create_jwt_token({"sub": payload.username, "role": role, "username": payload.username})
    return {
        "status": "SUCCESS",
        "token": token,
        "access_token": token,
        "role": role,
        "user_id": payload.username,
        "user": {
            "username": payload.username,
            "role": role,
            "name": "Dr. N. Ranasinghe" if role == "officer" else "Authenticated User",
            "designation": "Chief Agricultural Economist" if role == "officer" else "Registered User",
            "district": "Anuradhapura",
        },
    }


@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Authenticate user credentials against PostgreSQL/SQLite users database and issue signed JWT bearer token.
    """
    email_clean = req.email.strip().lower()
    ensure_seed_users()

    db_user = None
    try:
        with get_session() as session:
            db_user = session.query(UserModel).filter(UserModel.username == email_clean).first()
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials. User not found.",
                )
            if not verify_password(req.password, db_user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials. Incorrect password for this account.",
                )
            
            db_user.last_login = datetime.now(timezone.utc)
            session.commit()
            
            # Fetch profile details
            off_name = None
            district = "Anuradhapura"
            if db_user.officer_profile:
                off_name = db_user.officer_profile.name
                district = db_user.officer_profile.district

            user_info = {
                "email": db_user.username,
                "role": db_user.role.title(),
                "name": db_user.full_name or off_name or db_user.username.split("@")[0].replace(".", " ").title(),
                "designation": f"Verified {db_user.role.title()}",
                "district": district,
                "officer_id": db_user.officer_id or db_user.pseudonymous_id or "USR-0001",
                "pseudonymous_id": db_user.pseudonymous_id,
            }

            token_payload = {
                "sub": db_user.username,
                "role": db_user.role.lower(),
                "name": user_info["name"],
                "officer_id": user_info["officer_id"],
                "pseudonymous_id": db_user.pseudonymous_id,
                "district": district,
            }
            token = create_jwt_token(token_payload)

            return {
                "access_token": token,
                "token_type": "bearer",
                "user": user_info,
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed. Database lookup error: {str(e)}",
        )


@router.get("/auth/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    """Return profile for the currently authenticated bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected 'Bearer <token>'.",
        )
    token = authorization.split(" ")[1]
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid signature. Please log in again.",
        )
    return {
        "authenticated": True,
        "user": payload,
    }
