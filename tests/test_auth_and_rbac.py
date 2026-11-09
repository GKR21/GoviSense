"""
Tests for GoviSense Authentication and Role-Based Access Control (RBAC)
Team DARKBITE · ModelX 2.0 Phase 2
Task 7: Real auth in auth.py (JWT + roles)

Verifies:
  1. Password hashing with passlib[bcrypt] and verification
  2. JWT token generation, expiration, and payload decoding
  3. POST /api/auth/login for farmer and officer (returns token pair)
  4. POST /api/auth/refresh (refreshes token pair)
  5. GET  /api/auth/me (returns current user profile)
  6. GET  /api/farmer/* (requires farmer role: 401 without token, 403 with officer token, 200 with farmer token)
  7. POST /api/history/log-action (requires officer role: 401 without token, 403 with farmer token, 200 with officer token)
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from jose import jwt

from govisense.api.main import app
from govisense.api.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from govisense.db.session import init_db, get_db_session
from govisense.db.models import User

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database_and_users():
    """Ensure database tables exist and test accounts are provisioned."""
    init_db()
    with get_db_session() as db:
        # Verify or create farmer user
        farmer = db.query(User).filter(User.username == "test_farmer").first()
        if not farmer:
            farmer = User(
                username="test_farmer",
                hashed_password=get_password_hash("FarmerSecret123!"),
                role="farmer",
                full_name="Test Farmer Kamal",
                phone_number="+94771112233",
                district="Anuradhapura",
                is_active=True,
            )
            db.add(farmer)

        # Verify or create officer user
        officer = db.query(User).filter(User.username == "test_officer").first()
        if not officer:
            officer = User(
                username="test_officer",
                hashed_password=get_password_hash("OfficerSecret123!"),
                role="officer",
                full_name="Test Officer Kavinda",
                phone_number="+94774445566",
                district="Anuradhapura",
                is_active=True,
            )
            db.add(officer)

        # Deactivated user to test inactive account rejection
        inactive = db.query(User).filter(User.username == "test_inactive").first()
        if not inactive:
            inactive = User(
                username="test_inactive",
                hashed_password=get_password_hash("Inactive123!"),
                role="farmer",
                full_name="Inactive User",
                phone_number="+94779998877",
                district="Anuradhapura",
                is_active=False,
            )
            db.add(inactive)

        db.commit()


# ---------------------------------------------------------------------------
# 1. Password Hashing & Verification Tests
# ---------------------------------------------------------------------------

def test_password_hashing_and_verification():
    raw_password = "SecurePassword@2026"
    hashed = get_password_hash(raw_password)

    # Must be valid bcrypt hash string starting with $2b$ or $2a$
    assert hashed.startswith("$2")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False


def test_password_legacy_sha256_compatibility():
    import hashlib
    raw = "LegacyPassword123"
    sha_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # Legacy seeded password fallback verification
    assert verify_password(raw, sha_hash) is True
    assert verify_password("WrongLegacy", sha_hash) is False


# ---------------------------------------------------------------------------
# 2. JWT Generation & Decoding Tests
# ---------------------------------------------------------------------------

def test_jwt_access_token_creation_and_decoding():
    claims = {"sub": "test_officer", "role": "officer", "district": "Anuradhapura"}
    token = create_access_token(claims)
    payload = decode_token(token)

    assert payload["sub"] == "test_officer"
    assert payload["role"] == "officer"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_refresh_token_creation_and_decoding():
    claims = {"sub": "test_farmer", "role": "farmer"}
    token = create_refresh_token(claims)
    payload = decode_token(token)

    assert payload["sub"] == "test_farmer"
    assert payload["role"] == "farmer"
    assert payload["type"] == "refresh"


def test_jwt_expired_token():
    claims = {"sub": "expired_user", "role": "farmer"}
    # Token expired 10 minutes ago
    expired_token = create_access_token(claims, expires_delta=timedelta(minutes=-10))

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_token(expired_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# 3. POST /api/auth/login Tests
# ---------------------------------------------------------------------------

def test_login_success_farmer():
    res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "FarmerSecret123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == ACCESS_TOKEN_EXPIRE_MINUTES * 60
    assert data["user"]["username"] == "test_farmer"
    assert data["user"]["role"] == "farmer"


def test_login_success_officer():
    res = client.post("/api/auth/login", json={
        "username": "test_officer",
        "password": "OfficerSecret123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "test_officer"
    assert data["user"]["role"] == "officer"


def test_login_invalid_password():
    res = client.post("/api/auth/login", json={
        "username": "test_officer",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
    assert "incorrect" in res.json()["detail"].lower()


def test_login_nonexistent_user():
    res = client.post("/api/auth/login", json={
        "username": "non_existent_user_999",
        "password": "AnyPassword"
    })
    assert res.status_code == 401


def test_login_inactive_user():
    res = client.post("/api/auth/login", json={
        "username": "test_inactive",
        "password": "Inactive123!"
    })
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 4. POST /api/auth/refresh Tests
# ---------------------------------------------------------------------------

def test_refresh_token_success():
    login_res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "FarmerSecret123!"
    })
    refresh_token = login_res.json()["refresh_token"]

    res = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["username"] == "test_farmer"


def test_refresh_with_access_token_fails():
    login_res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "FarmerSecret123!"
    })
    access_token = login_res.json()["access_token"]

    # Passing an access token to the refresh endpoint must fail
    res = client.post("/api/auth/refresh", json={
        "refresh_token": access_token
    })
    assert res.status_code == 401
    assert "refresh token required" in res.json()["detail"].lower()


# ---------------------------------------------------------------------------
# 5. GET /api/auth/me Tests
# ---------------------------------------------------------------------------

def test_auth_me_endpoint():
    login_res = client.post("/api/auth/login", json={
        "username": "test_officer",
        "password": "OfficerSecret123!"
    })
    access_token = login_res.json()["access_token"]

    # With valid token
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "test_officer"
    assert data["role"] == "officer"

    # Without token
    res_no_auth = client.get("/api/auth/me")
    assert res_no_auth.status_code == 401


# ---------------------------------------------------------------------------
# 6. Role Protection on GET /api/farmer/*
# ---------------------------------------------------------------------------

def test_farmer_endpoint_unprotected_access_denied():
    # Calling GET /api/farmer/top3 without credentials must return 401
    res = client.get("/api/farmer/top3?farmer_id=LK-001&season=Maha&land_ha=2.0")
    assert res.status_code == 401
    assert "token is required" in res.json()["detail"].lower()


def test_farmer_endpoint_officer_role_forbidden():
    # Officer attempting to access farmer-only endpoint must return 403 Forbidden
    login_res = client.post("/api/auth/login", json={
        "username": "test_officer",
        "password": "OfficerSecret123!"
    })
    officer_token = login_res.json()["access_token"]

    res = client.get(
        "/api/farmer/top3?farmer_id=LK-001&season=Maha&land_ha=2.0",
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert res.status_code == 403
    assert "not permitted" in res.json()["detail"].lower()


def test_farmer_endpoint_farmer_role_allowed():
    # Farmer role must succeed (200 OK)
    login_res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "FarmerSecret123!"
    })
    farmer_token = login_res.json()["access_token"]

    res = client.get(
        "/api/farmer/top3?farmer_id=LK-001&season=Maha&land_ha=2.0",
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["farmer_id"] == "LK-001"
    assert "top3" in data


# ---------------------------------------------------------------------------
# 7. Role Protection on POST /api/history/log-action
# ---------------------------------------------------------------------------

def test_officer_endpoint_unprotected_access_denied():
    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "officer_id": "OFFICER-001",
        "action_type": "HOLD_STORAGE",
        "quantity": 500.0,
        "unit": "MT",
        "rationale": "Buffer hold test without token",
    }
    res = client.post("/api/history/log-action", json=payload)
    assert res.status_code == 401


def test_officer_endpoint_farmer_role_forbidden():
    login_res = client.post("/api/auth/login", json={
        "username": "test_farmer",
        "password": "FarmerSecret123!"
    })
    farmer_token = login_res.json()["access_token"]

    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "officer_id": "FARMER-TAMPER",
        "action_type": "HOLD_STORAGE",
        "quantity": 500.0,
        "unit": "MT",
        "rationale": "Unauthorized farmer action",
    }
    res = client.post(
        "/api/history/log-action",
        json=payload,
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert res.status_code == 403
    assert "not permitted" in res.json()["detail"].lower()


def test_officer_endpoint_officer_role_allowed():
    login_res = client.post("/api/auth/login", json={
        "username": "test_officer",
        "password": "OfficerSecret123!"
    })
    officer_token = login_res.json()["access_token"]

    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "officer_id": "OFFICER-001",
        "action_type": "HOLD_STORAGE",
        "quantity": 1200.0,
        "unit": "MT",
        "rationale": "Storage retention to defend floor price",
    }
    res = client.post(
        "/api/history/log-action",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "RECORDED"
    assert "decision_id" in data

