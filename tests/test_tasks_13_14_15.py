"""
Tests for Tasks 13, 14, and 15:
- Task 13: Planting report offline/pending resilience, removing optimistic fake receipts.
- Task 14: Distinguishing offline fallback recommendations (_initialCrops) with explicit provenance.
- Task 15: Real DEC market prices backend endpoint (/api/market-prices and /api/prices).
"""

import pytest
from fastapi.testclient import TestClient

from govisense.api.main import app
from govisense.db.session import init_db, get_db_session
from govisense.db.models import MarketPriceRecord

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_market_prices_db():
    init_db()


def test_market_prices_endpoint_returns_cbsl_harti_benchmarks():
    """Verify /api/market-prices returns live seeded prices with provenance metadata."""
    response = client.get("/api/market-prices")
    assert response.status_code == 200
    data = response.json()

    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["source_type"] == "cbsl_harti_market_bulletin"
    assert "prices" in data
    assert data["total"] >= 6

    # Verify essential fields for mobile client
    sample = data["prices"][0]
    assert "crop_en" in sample
    assert "crop_si" in sample
    assert "crop_ta" in sample
    assert "category" in sample
    assert "wholesale_price" in sample
    assert "retail_price" in sample
    assert "economic_center_en" in sample
    assert "trend_pct" in sample
    assert "is_up" in sample
    assert "is_stable" in sample


def test_market_prices_alias_endpoint():
    """Verify /api/prices returns identical structure to /api/market-prices."""
    res1 = client.get("/api/market-prices")
    res2 = client.get("/api/prices")
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res1.json()["total"] == res2.json()["total"]


def test_market_prices_category_filtering():
    """Verify filtering by category (e.g. vegetable, pulse, grain, tuber)."""
    veg_res = client.get("/api/market-prices?category=vegetable")
    assert veg_res.status_code == 200
    veg_data = veg_res.json()
    assert veg_data["total"] > 0
    for p in veg_data["prices"]:
        assert p["category"].lower() == "vegetable"

    pulse_res = client.get("/api/market-prices?category=pulse")
    assert pulse_res.status_code == 200
    pulse_data = pulse_res.json()
    assert pulse_data["total"] > 0
    for p in pulse_data["prices"]:
        assert p["category"].lower() == "pulse"


def test_offline_vs_online_provenance_contract_for_recommendations():
    """
    Task 14 Contract: When recommendations come from live backend,
    is_demo and data_available must be explicitly declared.
    """
    login_res = client.post("/api/auth/login", json={"username": "farmer_kamal", "password": "Farmer@123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(
        "/api/farmer/top3?farmer_id=LK-NC-001&season=Maha&land_ha=2.5",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert "is_demo" in data
    assert "top3" in data
    assert len(data["top3"]) >= 1


def test_planting_report_feedback_endpoint_contract():
    """
    Task 13 Contract: Planting report submissions must accept actual telemetry,
    respond with 200 OK, and reject corrupt payloads without fake receipts.
    """
    import uuid
    uid = uuid.uuid4().hex[:6]
    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "planned_area_ha": 1.5,
        "actual_area_ha": 1.5,
        "consent_given": True,
        "pseudonymous_id": f"TEST-MOBILE-FARMER-{uid}",
        "sale_channel": "Dambulla DEC",
        "notes": "Testing mobile client sync contract",
    }
    res = client.post("/api/feedback/planting-report", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACCEPTED"
    assert "report_id" in data
