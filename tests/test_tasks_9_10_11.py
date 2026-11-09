"""
Tests for Tasks 9, 10, and 11
- Task 9 (P1): Endpoints for Rashmika (Catalogue, Adoption Summary, Decision List with Hash/Run ID, Pipeline Run Info)
- Task 10 (P1): Alerts backend (routes/alerts.py, i18n/templates.json in EN/SI/TA, /api/alerts, /acknowledge, /ask)
- Task 11 (P1): Architectural modernization (FastAPI lifespan, modular routes, populated deps.py & schemas.py)
"""

import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient

from govisense.api.main import app, load_and_train
from govisense.api.auth import create_access_token


@pytest.fixture(scope="module", autouse=True)
def setup_test_pipeline():
    load_and_train()
    from govisense.api.routes.alerts import seed_alerts_from_templates
    seed_alerts_from_templates()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def officer_token():
    return create_access_token({"sub": "officer_anuradhapura", "role": "officer"})


@pytest.fixture
def farmer_token():
    return create_access_token({"sub": "farmer_kamal", "role": "farmer"})


# ===========================================================================
# Task 9 Tests: Endpoints for Rashmika
# ===========================================================================

def test_catalogue_endpoint(client):
    """Verifies that GET /api/catalogue returns catalogue datasets with licences and source URLs."""
    res = client.get("/api/catalogue")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is True
    assert data["is_demo"] is False
    assert data["total_datasets"] > 0
    assert len(data["datasets"]) > 0

    first = data["datasets"][0]
    assert "dataset_id" in first
    assert "publisher" in first
    assert "licence" in first
    assert "source_url" in first


def test_catalogue_single_dataset(client):
    """Verifies that GET /api/catalogue/{dataset_id} returns a single dataset record."""
    res = client.get("/api/catalogue/cbsl_daily_prices")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset"]["dataset_id"].lower() == "cbsl_daily_prices"
    assert "Central Bank" in data["dataset"]["publisher"]

    # Not found
    res_404 = client.get("/api/catalogue/unknown_dataset_xyz")
    assert res_404.status_code == 404


def test_pipeline_run_info_endpoint(client):
    """Verifies that GET /api/pipeline/run-info returns active pipeline metadata and run ID."""
    res = client.get("/api/pipeline/run-info")
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["run_id"].startswith("RUN-")
    assert "model_version" in data
    assert "data_version" in data
    assert data["pilot_district"] == "Anuradhapura"
    assert data["crops"] == ["big_onion", "chilli"]
    assert data["models_loaded"] is True
    assert data["source_type"] == "pipeline_metadata"


def test_adoption_summary_for_rashmika(client):
    """Verifies adoption summary endpoint returns explicit data_available: false."""
    res = client.get("/api/simulation/adoption-summary?crop_id=big_onion")
    assert res.status_code == 200
    data = res.json()
    assert data["data_available"] is False
    assert data["counts"]["coordinated_adopters"] is None
    assert "not available" in data["message"].lower()

    # Alias check
    res_alias = client.get("/api/adoption/summary?crop_id=chilli")
    assert res_alias.status_code == 200
    assert res_alias.json()["data_available"] is False


def test_decision_history_with_hash_and_run_id_for_rashmika(client):
    """Verifies that GET /api/history/decisions returns records with hash and run ID."""
    res = client.get("/api/history/decisions?limit=10")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    item = items[0]
    assert "decision_id" in item
    assert "run_id" in item
    assert "hash" in item
    assert "model_version" in item


# ===========================================================================
# Task 10 Tests: Multilingual Alerts Backend & Farmer Interactions
# ===========================================================================

def test_i18n_templates_json_exists_and_valid():
    """Verifies that src/govisense/i18n/templates.json contains valid EN, SI, and TA templates."""
    path = Path("src/govisense/i18n/templates.json")
    assert path.exists()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "templates" in data
    assert len(data["templates"]) >= 3
    for t in data["templates"]:
        assert "template_id" in t
        assert "crop_id" in t
        assert "title_en" in t and len(t["title_en"]) > 0
        assert "title_si" in t and len(t["title_si"]) > 0
        assert "title_ta" in t and len(t["title_ta"]) > 0
        assert "message_en" in t and len(t["message_en"]) > 0
        assert "message_si" in t and len(t["message_si"]) > 0
        assert "message_ta" in t and len(t["message_ta"]) > 0


def test_get_alerts_multilingual(client):
    """Verifies GET /api/alerts returns localized titles and messages in EN, SI, and TA."""
    # English
    res_en = client.get("/api/alerts?lang=en")
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["total"] > 0
    assert data_en["language"] == "en"
    assert any("Big Onion" in a["title"] or "Chilli" in a["title"] for a in data_en["alerts"])

    # Sinhala
    res_si = client.get("/api/alerts?lang=si")
    assert res_si.status_code == 200
    data_si = res_si.json()
    assert data_si["language"] == "si"
    # Ensure Sinhala characters are present
    assert any("ලොකු" in a["title"] or "මිරිස්" in a["title"] for a in data_si["alerts"])

    # Tamil
    res_ta = client.get("/api/alerts?lang=ta")
    assert res_ta.status_code == 200
    data_ta = res_ta.json()
    assert data_ta["language"] == "ta"
    # Ensure Tamil characters are present
    assert any("வெங்காய" in a["title"] or "மிளகாய்" in a["title"] for a in data_ta["alerts"])


def test_alert_acknowledge_lifecycle(client):
    """Verifies alert acknowledgment lifecycle for a farmer."""
    # 1. Fetch active alerts
    res = client.get("/api/alerts?farmer_id=LK-FARMER-999")
    alerts = res.json()["alerts"]
    assert len(alerts) > 0
    target_alert_id = alerts[0]["alert_id"]
    assert alerts[0]["acknowledged"] is False

    # 2. Acknowledge alert
    ack_res = client.post(
        f"/api/alerts/{target_alert_id}/acknowledge",
        json={"farmer_id": "LK-FARMER-999"},
    )
    assert ack_res.status_code == 200
    ack_data = ack_res.json()
    assert ack_data["status"] == "ACKNOWLEDGED"
    assert ack_data["acknowledged"] is True
    assert ack_data["farmer_id"] == "LK-FARMER-999"

    # 3. Query alerts again with farmer_id -> acknowledged must be True
    res_after = client.get("/api/alerts?farmer_id=LK-FARMER-999")
    alerts_after = res_after.json()["alerts"]
    matched = [a for a in alerts_after if a["alert_id"] == target_alert_id][0]
    assert matched["acknowledged"] is True


def test_alert_ask_officer_question(client):
    """Verifies that farmer can submit a question regarding an alert."""
    res = client.get("/api/alerts")
    target_alert_id = res.json()["alerts"][0]["alert_id"]

    ask_res = client.post(
        f"/api/alerts/{target_alert_id}/ask",
        json={
            "farmer_id": "LK-FARMER-888",
            "question": "Should I store in ventilated plastic crates or gunny bags?",
        },
    )
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert ask_data["status"] == "SUBMITTED"
    assert "ventilated" in ask_data["question"]


def test_create_alert_by_officer(client, officer_token, farmer_token):
    """Verifies that creating an alert requires officer/admin role."""
    payload = {
        "crop_id": "big_onion",
        "severity": "critical",
        "target_role": "all",
        "title_en": "Dambulla Market Storage Capacity Reached",
        "title_si": "දඹුල්ල වෙළඳපොළ ගබඩා ධාරිතාව උපරිම මට්ටමට",
        "title_ta": "தம்புள்ளை சந்தை சேமிப்பு கொள்ளளவு உச்சத்தை எட்டியுள்ளது",
        "message_en": "Holding facilities at Dambulla dedicated economic centre have reached 95% occupancy.",
        "message_si": "දඹුල්ල ආර්ථික මධ්‍යස්ථානයේ ගබඩා පහසුකම් 95% කින් පිරී ඇත.",
        "message_ta": "தம்புள்ளை பொருளாதார மையத்தில் உள்ள சேமிப்பு வசதிகள் 95% நிரம்பியுள்ளன.",
    }

    # 1. Farmer forbidden -> 403
    res_farm = client.post(
        "/api/alerts",
        json=payload,
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert res_farm.status_code == 403

    # 2. Officer allowed -> 200
    res_off = client.post(
        "/api/alerts",
        json=payload,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert res_off.status_code == 200
    assert res_off.json()["status"] == "CREATED"


# ===========================================================================
# Task 11 Tests: Lifespan & Modular API Structure
# ===========================================================================

def test_fastapi_lifespan_configured():
    """Verifies that FastAPI router uses lifespan context manager instead of on_event."""
    assert hasattr(app, "router")
    assert app.router.lifespan_context is not None


def test_deps_module_exports():
    """Verifies that govisense.api.deps exports all required dependencies."""
    from govisense.api import deps
    assert hasattr(deps, "get_db")
    assert hasattr(deps, "get_current_user")
    assert hasattr(deps, "require_farmer")
    assert hasattr(deps, "require_officer")
    assert hasattr(deps, "require_admin")
    assert hasattr(deps, "require_officer_or_admin")
    assert hasattr(deps, "require_authenticated")


def test_schemas_module_exports():
    """Verifies that govisense.api.schemas exports standard data transfer contracts."""
    from govisense.api import schemas
    assert hasattr(schemas, "ProvenanceMeta")
    assert hasattr(schemas, "DecisionLogPayload")
    assert hasattr(schemas, "DecisionRecordResponse")
    assert hasattr(schemas, "SimulationRequest")
    assert hasattr(schemas, "PlantingReportPayload")
    assert hasattr(schemas, "ReTriggerPayload")
    assert hasattr(schemas, "AdoptionSummaryResponse")
