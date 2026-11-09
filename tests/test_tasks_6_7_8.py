"""
Tests for Tasks 6, 7, and 8
- Task 6 (P0): Decision hash and run ID returns, dynamic running model version binding
- Task 7 (P0): Provenance metadata flags (is_demo, data_available, source_type) across endpoints
- Task 8 (P1): JWT login with officer, farmer, and admin roles, endpoint RBAC protection, and strict CORS whitelist
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from govisense.api.main import app, load_and_train
from govisense.db.history import DecisionRecord, DecisionHistoryStore, get_running_model_version
from govisense.api.auth import create_access_token


@pytest.fixture(scope="module", autouse=True)
def setup_test_pipeline():
    load_and_train()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin_govisense", "role": "admin"})


@pytest.fixture
def officer_token():
    return create_access_token({"sub": "officer_anuradhapura", "role": "officer"})


@pytest.fixture
def farmer_token():
    return create_access_token({"sub": "farmer_kamal", "role": "farmer"})


# ===========================================================================
# Task 6 Tests: Decision Hash & Run ID + Dynamic Model Version Binding
# ===========================================================================

def test_decision_record_auto_generates_run_id_and_hash():
    """Verifies that DecisionRecord automatically populates run_id and sha256 hash."""
    rec = DecisionRecord(
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id="OFF-TEST-1",
        action_type="HOLD_STORAGE",
        quantity=1500.0,
        unit="MT",
        rationale="Defending farmgate floor against early distress sale",
    )
    assert rec.run_id.startswith("RUN-")
    assert len(rec.hash) == 64  # SHA-256 hexdigest length
    assert rec.model_version is not None
    assert "HiGHS-LP" in rec.model_version


def test_log_action_endpoint_returns_hash_and_run_id(client, officer_token):
    """Verifies that POST /api/history/log-action returns decision_id, run_id, and cryptographic hash."""
    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "officer_id": "OFF-AUDIT-99",
        "action_type": "PLANT_EXPANSION",
        "quantity": 800.0,
        "unit": "MT",
        "rationale": "Expanding recommended seedling distribution in Mahaweli H zone",
        "assumptions": {"loss_pct": 0.12, "safety_buffer": 0.05},
    }
    res = client.post(
        "/api/history/log-action",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "RECORDED"
    assert "run_id" in data
    assert data["run_id"].startswith("RUN-")
    assert "hash" in data
    assert len(data["hash"]) == 64
    assert data["model_version"].startswith("GoviSense")


def test_decision_history_list_includes_hash_run_id_and_provenance(client):
    """Verifies that GET /api/history/decisions includes run_id, hash, and provenance metadata."""
    res = client.get("/api/history/decisions?limit=5")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    latest = items[0]
    assert "run_id" in latest
    assert "hash" in latest
    assert "is_demo" in latest
    assert latest["is_demo"] is False
    assert "data_available" in latest
    assert latest["data_available"] is True
    assert "source_type" in latest
    assert latest["source_type"] == "officer_audit_log"


# ===========================================================================
# Task 7 Tests: is_demo, data_available, and source_type Across Endpoints
# ===========================================================================

def test_forecasts_latest_provenance_flags(client):
    """Verifies that /api/forecasts/latest contains top-level and per-crop provenance flags."""
    res = client.get("/api/forecasts/latest")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "empirical_pipeline"

    for crop in ["big_onion", "chilli"]:
        crop_data = data["crops"][crop]
        assert crop_data["data_available"] is True
        assert crop_data["is_demo"] is False
        assert crop_data["source_type"] == "empirical_pipeline"
        assert crop_data["ai1_harvest_forecast"]["data_available"] is True
        assert crop_data["ai3_supply_pressure_index"]["data_available"] is True
        assert crop_data["ai2_price_forecast"]["data_available"] is True


def test_simulate_scenario_provenance_flags(client, officer_token):
    """Verifies provenance flags on POST /api/simulate."""
    payload = {
        "crop": "big_onion",
        "custom_planted_extent_ha": 3200.0,
        "custom_yield_mt_ha": 15.0,
    }
    res = client.post(
        "/api/simulate",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "scenario_simulation"


def test_farmer_top3_provenance_flags(client, farmer_token):
    """Verifies provenance flags on GET /api/farmer/top3."""
    res = client.get(
        "/api/farmer/top3?farmer_id=LK-NC-001&season=Maha&land_ha=2.5",
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "empirical_recommendation"
    for item in data["top3"]:
        assert item["data_available"] is True
        assert item["is_demo"] is False


def test_confidence_badge_provenance_flags(client):
    """Verifies provenance flags on GET /api/confidence/badge."""
    res = client.get("/api/confidence/badge?crop_id=big_onion")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "confidence_rules_engine"


# ===========================================================================
# Task 8 Tests: RBAC on Protected Endpoints & Restricted CORS Whitelist
# ===========================================================================

def test_admin_user_login(client):
    """Verifies that admin account logs in and receives admin role claims."""
    res = client.post("/api/auth/login", json={
        "username": "admin_govisense",
        "password": "Admin@123",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "admin"
    assert "access_token" in data


def test_database_init_protection(client, farmer_token, officer_token, admin_token):
    """Verifies that POST /api/database/init requires admin role."""
    # 1. Unauthenticated -> 401
    res = client.post("/api/database/init")
    assert res.status_code == 401

    # 2. Farmer role -> 403 Forbidden
    res = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert res.status_code == 403

    # 3. Officer role -> 403 Forbidden (init is admin-only)
    res = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 403

    # 4. Admin role -> 200 OK
    res = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "INITIALIZED"
    assert data["source_type"] == "database_admin"


def test_simulate_protection(client, farmer_token, officer_token):
    """Verifies that POST /api/simulate requires officer or admin role."""
    payload = {"crop": "big_onion", "custom_planted_extent_ha": 3000.0}

    # 1. Unauthenticated -> 401
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 401

    # 2. Farmer role -> 403 Forbidden
    res = client.post(
        "/api/simulate",
        json=payload,
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert res.status_code == 403

    # 3. Officer role -> 200 OK
    res = client.post(
        "/api/simulate",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 200


def test_feedback_retrigger_protection(client, farmer_token, officer_token):
    """Verifies that POST /api/feedback/retrigger requires officer or admin role."""
    payload = {"crop_id": "big_onion", "season": "Maha 2025/2026", "target_month": 4}

    # 1. Unauthenticated -> 401
    res = client.post("/api/feedback/retrigger", json=payload)
    assert res.status_code == 401

    # 2. Farmer role -> 403 Forbidden
    res = client.post(
        "/api/feedback/retrigger",
        json=payload,
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert res.status_code == 403

    # 3. Officer role -> 200 OK
    res = client.post(
        "/api/feedback/retrigger",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "new_a_rec_ha" in data
    assert data["source_type"] == "retrigger_engine"


def test_cors_whitelisted_vs_unlisted_origins(client):
    """Verifies that only whitelisted origins receive CORS access headers."""
    # Whitelisted origin: http://localhost:8443
    res_allowed = client.options(
        "/api/forecasts/latest",
        headers={
            "Origin": "http://localhost:8443",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:8443"

    # Whitelisted origin: http://localhost:5173
    res_vite = client.options(
        "/api/forecasts/latest",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_vite.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Disallowed origin: http://evil-spoof-site.com
    res_blocked = client.options(
        "/api/forecasts/latest",
        headers={
            "Origin": "http://evil-spoof-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_blocked.headers.get("access-control-allow-origin") != "http://evil-spoof-site.com"

