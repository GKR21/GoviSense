"""
Task 18 Quality & Validation Test Suite:
1. TestClient tests for EACH individual API endpoint.
2. Bad-input tests (422 validation errors, 401 auth, 403 RBAC, 409 duplicate, 429 rate limits).
3. Concurrency tests (20 parallel report submissions).
4. Data-validation tests on the source label taxonomy.
"""

import threading
import uuid
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from govisense.api.main import app, load_and_train
from govisense.db.session import init_db
from govisense.data.clean import PROCESSED_DATA_DIR
from govisense.data.validate import validate_master_dataset, audit_hand_checked_sample

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    load_and_train()


@pytest.fixture(scope="module")
def tokens():
    # Farmer login
    res_f = client.post("/api/auth/login", json={"username": "farmer_kamal", "password": "Farmer@123"})
    farmer_token = res_f.json()["access_token"]
    refresh_token = res_f.json()["refresh_token"]

    # Officer login
    res_o = client.post("/api/auth/login", json={"username": "officer_anuradhapura", "password": "Officer@123"})
    officer_token = res_o.json()["access_token"]

    # Admin login
    res_a = client.post("/api/auth/login", json={"username": "admin_govisense", "password": "Admin@123"})
    admin_token = res_a.json()["access_token"]

    return {
        "farmer": farmer_token,
        "officer": officer_token,
        "admin": admin_token,
        "refresh": refresh_token,
    }


# ===========================================================================
# 1. TestClient Tests for EACH Endpoint
# ===========================================================================

def test_endpoint_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["app"] == "GoviSense"


def test_endpoint_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_endpoint_auth_me(tokens):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tokens['farmer']}"})
    assert res.status_code == 200
    assert res.json()["role"] == "farmer"


def test_endpoint_auth_refresh(tokens):
    res = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh"]})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_endpoint_forecasts_latest():
    res = client.get("/api/forecasts/latest")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert "crops" in data
    assert "big_onion" in data["crops"]
    assert "ai1_harvest_forecast" in data["crops"]["big_onion"]


def test_endpoint_pipeline_run_info():
    res1 = client.get("/api/pipeline/run-info")
    res2 = client.get("/api/run-info")
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert "run_id" in res1.json()


def test_endpoint_catalogue():
    res = client.get("/api/catalogue")
    assert res.status_code == 200
    data = res.json()
    assert "datasets" in data
    assert len(data["datasets"]) > 0

    # Single dataset
    first_id = data["datasets"][0]["dataset_id"]
    res_single = client.get(f"/api/catalogue/{first_id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert "dataset" in single_data
    assert single_data["dataset"]["dataset_id"].upper() == first_id.upper()


def test_endpoint_simulation_and_adoption(tokens):
    # What-if simulate (requires officer/admin)
    sim_res = client.post(
        "/api/simulate",
        json={"crop": "big_onion", "custom_planted_extent_ha": 3000.0},
        headers={"Authorization": f"Bearer {tokens['officer']}"},
    )
    assert sim_res.status_code == 200
    assert "simulated_supply_mt" in sim_res.json()

    # Multi-agent adoption simulation
    adopt_res = client.get("/api/simulation/adoption?crop_id=big_onion")
    assert adopt_res.status_code == 200

    # Adoption summary (Task 5: data_available=False)
    sum_res = client.get("/api/simulation/adoption-summary?crop_id=big_onion")
    assert sum_res.status_code == 200
    assert sum_res.json()["data_available"] is False


def test_endpoint_farmer_top3_and_confidence(tokens):
    # Top-3 farmer recommendation
    top3_res = client.get(
        "/api/farmer/top3?farmer_id=LK-TEST-T18&season=Maha&land_ha=2.5",
        headers={"Authorization": f"Bearer {tokens['farmer']}"},
    )
    assert top3_res.status_code == 200
    assert "top3" in top3_res.json()

    # Confidence badge
    badge_res = client.get("/api/confidence/badge?crop=big_onion")
    assert badge_res.status_code == 200
    assert "badge" in badge_res.json()


def test_endpoint_planting_report_and_retrigger(tokens):
    # Submit report
    rep_res = client.post(
        "/api/feedback/planting-report",
        json={
            "crop_id": "big_onion",
            "season": "Maha 2025/2026",
            "planned_area_ha": 1.5,
            "actual_area_ha": 1.5,
            "consent_given": True,
            "pseudonymous_id": f"FARMER-T18-{uuid.uuid4().hex[:6]}",
        },
    )
    assert rep_res.status_code == 200
    assert rep_res.json()["status"] == "ACCEPTED"

    # Retrigger allocation optimizer (officer only)
    ret_res = client.post(
        "/api/feedback/retrigger",
        json={"crop_id": "big_onion", "season": "Maha 2025/2026"},
        headers={"Authorization": f"Bearer {tokens['officer']}"},
    )
    assert ret_res.status_code == 200


def test_endpoint_history_decisions(tokens):
    # Log decision (officer only)
    log_res = client.post(
        "/api/history/log-action",
        json={
            "crop_id": "big_onion",
            "season": "Maha 2025/2026",
            "officer_id": "OFFICER-T18",
            "action_type": "HOLD_STORAGE",
            "quantity": 1200.0,
            "unit": "MT",
            "rationale": "Quality test log",
        },
        headers={"Authorization": f"Bearer {tokens['officer']}"},
    )
    assert log_res.status_code == 200
    assert "hash" in log_res.json()

    # List decisions
    hist_res = client.get("/api/history/decisions?crop_id=big_onion")
    assert hist_res.status_code == 200
    assert isinstance(hist_res.json(), list)


def test_endpoint_alerts_lifecycle(tokens):
    # List alerts
    alerts_res = client.get("/api/alerts?lang=si")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()["alerts"]
    assert len(alerts) > 0
    first_id = alerts[0]["alert_id"]

    # Acknowledge alert
    ack_res = client.post(f"/api/alerts/{first_id}/acknowledge", json={"farmer_id": "FARMER-T18-ACK"})
    assert ack_res.status_code == 200
    assert ack_res.json()["acknowledged"] is True

    # Ask officer
    ask_res = client.post(
        f"/api/alerts/{first_id}/ask",
        json={"farmer_id": "FARMER-T18-ASK", "question": "Is storage available in Rajanganaya?"},
    )
    assert ask_res.status_code == 200
    assert ask_res.json()["status"] == "SUBMITTED"
    assert ask_res.json()["question"] == "Is storage available in Rajanganaya?"


def test_endpoint_market_prices():
    res = client.get("/api/market-prices")
    assert res.status_code == 200
    assert res.json()["data_available"] is True
    assert res.json()["total"] >= 6


def test_endpoint_database_init_admin(tokens):
    res = client.post("/api/database/init", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    assert res.json()["status"] == "INITIALIZED"


# ===========================================================================
# 2. Bad-Input & Security Tests
# ===========================================================================

def test_bad_input_missing_required_fields(tokens):
    # Planting report missing required crop_id
    res = client.post("/api/feedback/planting-report", json={"actual_area_ha": 2.5})
    assert res.status_code == 422

    # Retrigger missing crop_id
    res_ret = client.post(
        "/api/feedback/retrigger",
        json={},
        headers={"Authorization": f"Bearer {tokens['officer']}"},
    )
    assert res_ret.status_code == 422


def test_bad_input_invalid_types():
    # String passed for float field
    res = client.post(
        "/api/feedback/planting-report",
        json={
            "crop_id": "big_onion",
            "planned_area_ha": "not_a_valid_number",
            "actual_area_ha": 2.5,
            "consent_given": True,
            "pseudonymous_id": "BAD-INPUT-001",
        },
    )
    assert res.status_code == 422


def test_bad_input_unauthenticated_protected_endpoints():
    # Require officer
    res_sim = client.post("/api/simulate", json={"crop": "big_onion"})
    assert res_sim.status_code == 401

    # Require admin
    res_init = client.post("/api/database/init")
    assert res_init.status_code == 401

    # Require farmer
    res_f = client.get("/api/farmer/top3?farmer_id=LK-001")
    assert res_f.status_code == 401


def test_bad_input_role_forbidden(tokens):
    # Farmer attempting officer endpoint -> 403
    res = client.post(
        "/api/simulate",
        json={"crop": "big_onion"},
        headers={"Authorization": f"Bearer {tokens['farmer']}"},
    )
    assert res.status_code == 403

    # Officer attempting admin-only database init -> 403
    res_admin = client.post(
        "/api/database/init",
        headers={"Authorization": f"Bearer {tokens['officer']}"},
    )
    assert res_admin.status_code == 403


def test_bad_input_duplicate_report_rejection():
    unique_id = f"FARMER-DUP-{uuid.uuid4().hex[:6]}"
    payload = {
        "crop_id": "big_onion",
        "season": "Maha 2025/2026",
        "planned_area_ha": 2.0,
        "actual_area_ha": 2.0,
        "consent_given": True,
        "pseudonymous_id": unique_id,
    }
    # First submit accepted
    res1 = client.post("/api/feedback/planting-report", json=payload)
    assert res1.status_code == 200
    assert res1.json()["status"] == "ACCEPTED"

    # Second identical submit rejected as duplicate
    res2 = client.post("/api/feedback/planting-report", json=payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "ERROR"
    assert "duplicate" in res2.json()["message"].lower()


def test_bad_input_rate_limiting_per_farmer():
    farmer_id = f"FARMER-RATE-{uuid.uuid4().hex[:6]}"
    responses = []
    # Submit 6 reports with varying areas in rapid succession
    for i in range(6):
        res = client.post(
            "/api/feedback/planting-report",
            json={
                "crop_id": "big_onion",
                "season": "Maha 2025/2026",
                "planned_area_ha": 1.0 + (i * 0.1),
                "actual_area_ha": 1.0 + (i * 0.1),
                "consent_given": True,
                "pseudonymous_id": farmer_id,
            },
        )
        responses.append(res.json())

    # 6th report exceeds the sliding window limit of 5/min
    last_res = responses[-1]
    assert last_res["status"] == "ERROR"
    assert "rate limit" in last_res["message"].lower()


# ===========================================================================
# 3. Concurrency Tests (20 Parallel Reports)
# ===========================================================================

def test_concurrency_20_parallel_reports_through_api():
    """
    Submits 20 reports simultaneously across 20 threads through FastAPI TestClient.
    Verifies that WAL mode handles concurrent writes without database lock errors.
    """
    errors = []
    successes = []
    run_token = uuid.uuid4().hex[:6]

    def worker(worker_id: int):
        try:
            res = client.post(
                "/api/feedback/planting-report",
                json={
                    "crop_id": "big_onion",
                    "season": "Maha 2025/2026",
                    "planned_area_ha": 1.0 + (worker_id * 0.2),
                    "actual_area_ha": 1.2 + (worker_id * 0.2),
                    "consent_given": True,
                    "pseudonymous_id": f"CONCURRENT-API-{worker_id}-{run_token}",
                    "sale_channel": "Dambulla DEC",
                    "notes": f"Concurrency test thread {worker_id}",
                },
            )
            if res.status_code == 200:
                successes.append(worker_id)
            else:
                errors.append((worker_id, res.status_code, res.text))
        except Exception as e:
            errors.append((worker_id, "exception", str(e)))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent submission errors encountered: {errors}"
    assert len(successes) == 20


# ===========================================================================
# 4. Data-Validation Test on Source Label
# ===========================================================================

def test_source_label_data_validation():
    """
    Validates that monthly_master.csv complies with the 4-tier source taxonomy
    (real, anchor, interpolated, synthetic) and that is_demo is False.
    """
    master_path = PROCESSED_DATA_DIR / "monthly_master.csv"
    assert master_path.exists(), "monthly_master.csv does not exist"

    df = pd.read_csv(master_path)
    res = validate_master_dataset(df)
    assert res["is_valid"] is True, f"Master dataset validation failed: {res.get('issues')}"

    # Verify source label values
    allowed_sources = {"real", "anchor", "interpolated", "synthetic"}
    actual_sources = set(df["source"].unique())
    assert actual_sources.issubset(allowed_sources), f"Unexpected source labels: {actual_sources - allowed_sources}"

    # Ensure real ground-truth rows dominate the empirical dataset
    real_count = (df["source"] == "real").sum()
    total_count = len(df)
    assert real_count / total_count > 0.80, f"Real empirical rows ({real_count}) under 80% of total ({total_count})"

    # Verify is_demo flag is strictly False on real production data
    assert (df["is_demo"] == False).all()


def test_hand_checked_sample_ground_truth_honesty():
    """
    Verifies that the audited error rate on the 5% hand-checked sample
    meets the required threshold (<= 10.0%).
    """
    audit_res = audit_hand_checked_sample()
    assert audit_res.pass_status is True
    assert audit_res.error_rate_pct <= 10.0
    assert audit_res.total_fields_checked >= 20
