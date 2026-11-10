"""
Authentication and Role-Based Access Control (RBAC) Module for GoviSense
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)

Provides:
  - Password hashing and verification using passlib[bcrypt]
  - JWT token generation and verification using python-jose (HS256)
  - 30-minute access tokens and 7-day refresh tokens
  - Role enforcement dependencies (farmer and officer) via FastAPI Depends
  - Protected Auth Endpoints:
      POST /api/auth/login   → Returns access + refresh token pair
      POST /api/auth/refresh → Validates refresh token and returns new token pair
      GET  /api/auth/me      → Current authenticated user details
"""

from __future__ import annotations

import os
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError, jwt
import bcrypt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from govisense.db.session import get_db
from govisense.db.models import User, hash_password as _db_hash_pw, verify_password as _db_verify_pw

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "govisense-production-secret-key-pilot-anuradhapura-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password context handled directly via bcrypt (avoids passlib 1.7.4 + bcrypt >=4.0 wrap bug)
pwd_context = None

# OAuth2 scheme - allows optional token in header (auto_error=False to provide custom messages)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username of the officer or farmer")
    password: str = Field(..., description="Plain-text password")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username or email")
    password: str = Field(..., min_length=8, max_length=72, description="At least 8 characters")
    full_name: str = Field(..., min_length=2, max_length=128)
    role: str = Field(..., description="farmer or officer")
    district: str = Field(default="Anuradhapura")
    phone_number: Optional[str] = Field(default=None, max_length=32)
    officer_code: Optional[str] = Field(default=None, description="Required for officers only if OFFICER_SIGNUP_CODE is set")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid refresh token")


class UserProfile(BaseModel):
    id: int
    username: str
    role: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    district: Optional[str] = "Anuradhapura"
    is_active: bool = True
    created_at: Optional[str] = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Access token expiry in seconds (30 mins)")
    user: Optional[UserProfile] = None


# ---------------------------------------------------------------------------
# Password Utilities
# ---------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    Supports bcrypt ($2b$/$2a$) and gracefully falls back to SHA-256 for initial seed records.
    """
    if not hashed_password:
        return False
    return _db_verify_pw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt hash for a given password."""
    return _db_hash_pw(password)


# ---------------------------------------------------------------------------
# JWT Utilities
# ---------------------------------------------------------------------------

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed HS256 JWT access token (default 30 minutes)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Creates a signed HS256 JWT refresh token (default 7 days)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "refresh",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises HTTPException 401 if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI RBAC Dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and verifies the bearer access token,
    and returns the authenticated User record from the database.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: Optional[str] = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


class RoleChecker:
    """
    FastAPI dependency callable for role-based authorization.
    Allows users matching any of the specified roles (or 'admin').
    """
    def __init__(self, allowed_roles: Union[List[str], str]):
        if isinstance(allowed_roles, str):
            self.allowed_roles = [allowed_roles]
        else:
            self.allowed_roles = list(allowed_roles)

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: role '{current_user.role}' not permitted for this resource. Required: {self.allowed_roles}",
            )
        return current_user


def require_role(role: Union[List[str], str]) -> RoleChecker:
    """Factory helper to construct role dependencies."""
    return RoleChecker(role)


# Predefined role dependencies for clean endpoint declarations
require_farmer = RoleChecker("farmer")
require_officer = RoleChecker("officer")
require_admin = RoleChecker("admin")
require_officer_or_admin = RoleChecker(["officer", "admin"])
require_authenticated = RoleChecker(["farmer", "officer", "admin"])


def get_current_farmer(user: User = Depends(require_farmer)) -> User:
    """Dependency specifically returning an authorized farmer User."""
    return user


def get_current_officer(user: User = Depends(require_officer)) -> User:
    """Dependency specifically returning an authorized officer User."""
    return user


def get_current_admin(user: User = Depends(require_admin)) -> User:
    """Dependency specifically returning an authorized admin User."""
    return user


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------

@router.post("/login", response_model=TokenPair)
async def login(
    request: Request,
    payload: Optional[LoginRequest] = None,
    db: Session = Depends(get_db),
) -> TokenPair:
    """
    POST /api/auth/login
    Authenticates a user via JSON payload or OAuth2 form-data and returns
    a 30-minute access token and a 7-day refresh token.
    """
    username: Optional[str] = None
    password: Optional[str] = None

    if payload is not None:
        username = payload.username
        password = payload.password
    else:
        # Check form-data or raw JSON from request
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                body = await request.json()
                username = body.get("username") or body.get("email")
                password = body.get("password")
            except Exception:
                pass
        else:
            try:
                form = await request.form()
                username = form.get("username") or form.get("email")
                password = form.get("password")
            except Exception:
                pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    user = db.query(User).filter(User.username == username).first()
    stored_hash = (user.hashed_password or user.password_hash) if user else ""
    if not user or not verify_password(password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Token payload claims
    claims = {
        "sub": user.username,
        "role": user.role,
        "user_id": user.user_id,
        "id": user.id or 1,
        "name": user.full_name or user.username.split("@")[0],
        "district": user.district or "Anuradhapura",
    }

    access_token = create_access_token(claims)
    refresh_token = create_refresh_token(claims)

    user_profile = UserProfile(
        id=user.id or 1,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        phone_number=user.phone_number,
        district=user.district,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_profile,
    )


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenPair:
    """
    POST /api/auth/register
    Self-service sign-up for farmers and officers (admins cannot self-register).
    Creates the linked farmer/officer profile and returns a token pair (auto sign-in).
    """
    import uuid
    from sqlalchemy import func
    from govisense.db.lookups import ensure_farmer_profile, ensure_officer

    role = payload.role.strip().lower()
    if role not in ("farmer", "officer"):
        raise HTTPException(status_code=400, detail="Role must be 'farmer' or 'officer'")

    username = payload.username.strip()
    if db.query(User).filter(func.lower(User.username) == username.lower()).first():
        raise HTTPException(status_code=409, detail="That username is already registered")

    if role == "officer":
        required = os.getenv("OFFICER_SIGNUP_CODE")
        if required and not hmac.compare_digest(payload.officer_code or "", required):
            raise HTTPException(status_code=403, detail="Invalid officer registration code")

    suffix = uuid.uuid4().hex[:8].upper()
    try:
        if role == "farmer":
            fp = ensure_farmer_profile(db, pseudonymous_id=f"LK-FM-{suffix}", district=payload.district)
            user = User(username=username, password_hash=get_password_hash(payload.password),
                        role_code="farmer", pseudonymous_id=fp.pseudonymous_id,
                        full_name=payload.full_name.strip(), phone_number=payload.phone_number)
        else:
            off = ensure_officer(db, officer_id=f"OFF-{suffix}", name=payload.full_name.strip(),
                                 district=payload.district)
            user = User(username=username, password_hash=get_password_hash(payload.password),
                        role_code="officer", officer_id=off.officer_id,
                        full_name=payload.full_name.strip(), phone_number=payload.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create account. Check the district and details.")

    claims = {
        "sub": user.username, "role": user.role, "user_id": user.user_id, "id": user.id or 1,
        "name": user.full_name or user.username, "district": user.district or payload.district,
    }
    return TokenPair(
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims),
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfile(id=user.id or 1, username=user.username, role=user.role,
                         full_name=user.full_name, phone_number=user.phone_number,
                         district=user.district, is_active=True,
                         created_at=user.created_at.isoformat() if user.created_at else None),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: Request,
    payload: Optional[RefreshRequest] = None,
    db: Session = Depends(get_db),
) -> TokenPair:
    """
    POST /api/auth/refresh
    Accepts a valid refresh token, validates it, and issues a new access + refresh token pair.
    """
    token_str: Optional[str] = None
    if payload and payload.refresh_token:
        token_str = payload.refresh_token
    else:
        # Check Authorization header or JSON body
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_str = auth_header.replace("Bearer ", "", 1).strip()
        else:
            try:
                body = await request.json()
                token_str = body.get("refresh_token")
            except Exception:
                pass

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
        )

    decoded = decode_token(token_str)
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = decoded.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    claims = {
        "sub": user.username,
        "role": user.role,
        "user_id": user.user_id,
        "id": user.id or 1,
        "name": user.full_name or user.username.split("@")[0],
        "district": user.district or "Anuradhapura",
    }

    new_access_token = create_access_token(claims)
    new_refresh_token = create_refresh_token(claims)

    user_profile = UserProfile(
        id=user.id or 1,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        phone_number=user.phone_number,
        district=user.district,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )

    return TokenPair(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_profile,
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfile:
    """
    GET /api/auth/me
    Returns profile information for the currently authenticated user.
    """
    return UserProfile(
        id=current_user.id or 1,
        username=current_user.username,
        role=current_user.role,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        district=current_user.district,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )

