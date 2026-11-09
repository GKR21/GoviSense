"""
Comprehensive End-to-End Verification of Core System Checks (Task 20):
1. Auth & RBAC (farmer, officer, admin roles, token refresh, password hashing)
2. CORS (whitelisted origins allowed, unlisted origins blocked)
3. Alerts (multilingual fetching, acknowledgment, officer inquiry)
4. Mobile Prices Screen (CBSL/HARTI benchmarks, category filtering, data provenance)
"""

import pytest
from fastapi.testclient import TestClient
from govisense.api.main import app, load_and_train
from govisense.db.session import init_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_system():
    init_db()
    load_and_train()


# ==============================================================================
# 1. AUTH & RBAC SANITY CHECKS
# ==============================================================================
def test_task_20_auth_rbac_full_lifecycle():
    # A. Farmer Login
    res_farmer = client.post("/api/auth/login", json={"username": "farmer_kamal", "password": "Farmer@123"})
    assert res_farmer.status_code == 200, f"Farmer login failed: {res_farmer.text}"
    farmer_data = res_farmer.json()
    assert farmer_data["user"]["role"] == "farmer"
    farmer_token = farmer_data["access_token"]
    farmer_refresh = farmer_data["refresh_token"]

    # B. Officer Login
    res_officer = client.post("/api/auth/login", json={"username": "officer_anuradhapura", "password": "Officer@123"})
    assert res_officer.status_code == 200, f"Officer login failed: {res_officer.text}"
    officer_data = res_officer.json()
    assert officer_data["user"]["role"] == "officer"
    officer_token = officer_data["access_token"]

    # C. Admin Login
    res_admin = client.post("/api/auth/login", json={"username": "admin_govisense", "password": "Admin@123"})
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.text}"
    admin_data = res_admin.json()
    assert admin_data["user"]["role"] == "admin"
    admin_token = admin_data["access_token"]

    # D. Me endpoint check
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {farmer_token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "farmer_kamal"
    assert res_me.json()["role"] == "farmer"

    # E. Token Refresh
    res_refresh = client.post("/api/auth/refresh", json={"refresh_token": farmer_refresh})
    assert res_refresh.status_code == 200
    assert "access_token" in res_refresh.json()

    # F. RBAC Role Protection Enforcement
    # Officer route forbidden to farmer
    action_payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "officer_id": "OFF-AUDIT-99",
        "action_type": "PLANT_EXPANSION",
        "quantity": 800.0,
        "unit": "MT",
        "rationale": "Expanding recommended seedling distribution in Mahaweli H zone",
        "assumptions": {"loss_pct": 0.12, "safety_buffer": 0.05},
    }
    res_forbidden = client.post(
        "/api/history/log-action",
        headers={"Authorization": f"Bearer {farmer_token}"},
        json=action_payload,
    )
    assert res_forbidden.status_code == 403, "Farmer must not be allowed to access officer routes"

    # Officer route allowed to officer
    res_officer_action = client.post(
        "/api/history/log-action",
        headers={"Authorization": f"Bearer {officer_token}"},
        json=action_payload,
    )
    assert res_officer_action.status_code == 200
    assert res_officer_action.json()["status"] == "RECORDED"

    # Admin route forbidden to officer
    res_admin_forbidden = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_admin_forbidden.status_code == 403, "Officer must not be allowed to invoke database re-init"

    # Admin route allowed to admin
    res_admin_allowed = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin_allowed.status_code == 200
    assert res_admin_allowed.json()["status"] == "INITIALIZED"


# ==============================================================================
# 2. CORS SANITY CHECKS
# ==============================================================================
def test_task_20_cors_origin_whitelisting():
    # Whitelisted origin: http://localhost:3000
    headers_allowed = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    res_allowed = client.options("/api/health", headers=headers_allowed)
    assert res_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    # Whitelisted origin: http://localhost:5173
    headers_vite = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    res_vite = client.options("/api/health", headers=headers_vite)
    assert res_vite.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Unlisted malicious / unknown origin: http://evil-phishing-site.com
    headers_unlisted = {
        "Origin": "http://evil-phishing-site.com",
        "Access-Control-Request-Method": "GET",
    }
    res_unlisted = client.options("/api/health", headers=headers_unlisted)
    assert res_unlisted.headers.get("access-control-allow-origin") != "http://evil-phishing-site.com"
    assert res_unlisted.headers.get("access-control-allow-origin") != "*"


# ==============================================================================
# 3. ALERTS MULTILINGUAL & LIFECYCLE CHECKS
# ==============================================================================
def test_task_20_alerts_multilingual_and_actions():
    # A. English Alerts
    res_en = client.get("/api/alerts?lang=en")
    assert res_en.status_code == 200
    en_data = res_en.json()
    assert en_data["total"] >= 1
    sample_id = en_data["alerts"][0]["alert_id"]
    assert any("Glut" in a["title"] or "Price" in a["title"] or "Advisory" in a["title"] for a in en_data["alerts"])

    # B. Sinhala Alerts
    res_si = client.get("/api/alerts?lang=si")
    assert res_si.status_code == 200
    si_data = res_si.json()
    assert si_data["total"] >= 1
    # Check that title contains Sinhala characters
    assert any(any("\u0d80" <= c <= "\u0dff" for c in a["title"]) for a in si_data["alerts"])

    # C. Tamil Alerts
    res_ta = client.get("/api/alerts?lang=ta")
    assert res_ta.status_code == 200
    ta_data = res_ta.json()
    assert ta_data["total"] >= 1
    # Check that title contains Tamil characters
    assert any(any("\u0b80" <= c <= "\u0bff" for c in a["title"]) for a in ta_data["alerts"])

    # D. Acknowledge Alert Endpoint
    res_ack = client.post(f"/api/alerts/{sample_id}/acknowledge", json={"farmer_id": "ANU-FARMER-001"})
    assert res_ack.status_code == 200
    assert res_ack.json()["status"] == "ACKNOWLEDGED"
    assert res_ack.json()["alert_id"] == sample_id
    assert res_ack.json()["farmer_id"] == "ANU-FARMER-001"

    # E. Ask Officer Endpoint
    res_ask = client.post(
        f"/api/alerts/{sample_id}/ask",
        json={"farmer_id": "ANU-FARMER-001", "question": "Should I hold my harvested onion stock in cold storage until next month?"},
    )
    assert res_ask.status_code == 200
    assert res_ask.json()["status"] == "SUBMITTED"
    assert "cold storage" in res_ask.json()["question"]


# ==============================================================================
# 4. MOBILE MARKET PRICES SCREEN CHECKS
# ==============================================================================
def test_task_20_market_prices_screen_contract():
    # A. Market Prices Endpoint
    res = client.get("/api/market-prices")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "cbsl_harti_market_bulletin"
    assert "prices" in data
    assert len(data["prices"]) >= 5

    # Check key commodities expected on mobile
    commodities = [p["crop_en"].lower() for p in data["prices"]]
    assert any("onion" in c for c in commodities), "Big Onion must be present in DEC market prices"
    assert any("chilli" in c for c in commodities), "Chilli must be present in DEC market prices"

    # B. Category Filtering Check
    res_spices = client.get("/api/market-prices?category=spices")
    assert res_spices.status_code == 200
    spices_data = res_spices.json()
    for item in spices_data["prices"]:
        assert item["category"] == "spices"

    # C. Price Schema Structure verification (Contract with Mobile MarketPriceItem)
    first_item = data["prices"][0]
    required_fields = ["crop_en", "crop_si", "crop_ta", "category", "wholesale_price", "retail_price", "economic_center_en", "trend_pct", "is_up", "is_stable"]
    for field in required_fields:
        assert field in first_item, f"Mobile MarketPriceItem missing required field '{field}'"
        assert first_item[field] is not None
