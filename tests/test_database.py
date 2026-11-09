"""
Tests for GoviSense Persistent PostgreSQL Database Architecture
Team DARKBITE · ModelX 2.0 Proposal Specification
"""

import pytest
from datetime import datetime, date, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from govisense.db.models import (
    Base,
    compute_sha256_hash,
    PipelineRunModel,
    DecisionRecordModel,
    FarmerProfileModel,
    OfficerModel,
    UserModel,
    PlantingReportModel,
    HarvestReportModel,
    ForecastSnapshotModel,
    DataCatalogueModel,
    MonthlyDataModel,
    AlertModel,
    AlertStatusModel,
)
from govisense.db.session import _normalize_db_url, init_db, get_session, get_active_dialect
from govisense.db.history import DecisionHistoryStore, DecisionRecord
from govisense.feedback.planting_reports import PlantingReportStore, PlantingReport


@pytest.fixture(scope="module")
def test_engine():
    """Create in-memory SQLite engine to test SQLAlchemy models and queries."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Provide a transactional session for testing."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_url_normalization():
    """Verify PostgreSQL URL conversion to psycopg2 dialect."""
    raw_pg = "postgres://user:pass@localhost:5432/govisense"
    assert _normalize_db_url(raw_pg).startswith("postgresql+psycopg2://")

    raw_pg2 = "postgresql://user:pass@localhost:5432/govisense"
    assert _normalize_db_url(raw_pg2).startswith("postgresql+psycopg2://")

    sqlite = "sqlite:///:memory:"
    assert _normalize_db_url(sqlite) == sqlite


def test_runs_and_decision_hash_audit(test_session):
    """Verify runs table and real SHA-256 audit hash generation on decisions."""
    run = PipelineRunModel(
        run_id="RUN-TEST-001",
        trigger="officer",
        model_version="LightGBM-v2.1+HiGHS-LP",
        data_version="CBSL-HARTI-DOA-2024.12",
        assumptions={"loss_pct": 0.15, "lead_time_weeks": 7},
        git_commit="c74caf1",
    )
    officer = OfficerModel(
        officer_id="OFF-TEST-01",
        name="Officer Bandara",
        district="Anuradhapura",
    )
    test_session.add_all([run, officer])
    test_session.commit()

    decision = DecisionRecordModel(
        decision_id="DEC-TEST-001",
        run_id=run.run_id,
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id=officer.officer_id,
        model_recommended_action="STORE",
        officer_response="accepted",
        action_type="STORE",
        quantity=3000.0,
        unit="MT",
        rationale="Buffer storage defense for floor price",
        model_version="LightGBM-v2.1+HiGHS-LP",
        data_version="CBSL-HARTI-DOA-2024.12",
        assumptions={"loss_pct": 0.15, "fair_floor": 120.0},
    )
    test_session.add(decision)
    test_session.commit()

    retrieved = test_session.query(DecisionRecordModel).filter_by(decision_id="DEC-TEST-001").first()
    assert retrieved is not None
    assert len(retrieved.record_hash) == 64  # Real SHA-256 hash length
    assert retrieved.model_recommended_action == "STORE"
    assert retrieved.officer_response == "accepted"
    assert retrieved.action_type == "STORE"
    assert retrieved.run.git_commit == "c74caf1"


def test_pseudonymous_farmer_profiles(test_session):
    """Verify strict privacy: No name, No phone; pseudonymous_id is the primary key."""
    farmer = FarmerProfileModel(
        pseudonymous_id="LK-AP-999",
        district="Anuradhapura",
        divisional_secretariat="Galnewa",
        total_land_ha=2.8,
        irrigation_type="irrigated",
        irrigation_subtype="major",
        soil_type="Reddish Brown Earths (RBE)",
        soil_ph=6.7,
        consent_given=True,
        language="si",
    )
    test_session.add(farmer)
    test_session.commit()

    retrieved = test_session.query(FarmerProfileModel).filter_by(pseudonymous_id="LK-AP-999").first()
    assert retrieved is not None
    assert retrieved.pseudonymous_id == "LK-AP-999"
    assert retrieved.irrigation_type == "irrigated"
    assert retrieved.consent_given is True
    # Ensure no name or phone attributes exist on model
    assert not hasattr(farmer, "name")
    assert not hasattr(farmer, "phone")


def test_two_stage_feedback_planting_and_harvest(test_session):
    """Verify Stage 1 (Planting) and Stage 2 (Harvest) feedback tables with constraints."""
    farmer = FarmerProfileModel(
        pseudonymous_id="LK-AP-STAGE-TEST",
        district="Anuradhapura",
        total_land_ha=3.0,
        irrigation_type="irrigated",
    )
    test_session.add(farmer)
    test_session.commit()

    # Stage 1: Planting Report
    planting = PlantingReportModel(
        report_id="REP-STG1-001",
        pseudonymous_id=farmer.pseudonymous_id,
        crop_id="chilli",
        season="Maha 2025/2026",
        planned_area_ha=2.0,
        actual_area_ha=None,  # Nullable before planting is complete
        district="Anuradhapura",
        irrigation_type="irrigated",
        recommended_crop_shown="chilli",
        followed_recommendation="yes",
        expected_price_rs_kg=400.0,
        consent_given=True,
    )
    test_session.add(planting)
    test_session.commit()

    # Stage 2: Harvest Report
    harvest = HarvestReportModel(
        harvest_id="HVST-STG2-001",
        planting_report_id=planting.report_id,
        pseudonymous_id=farmer.pseudonymous_id,
        crop_id="chilli",
        season="Maha 2025/2026",
        area_harvested_ha=2.0,
        harvest_quantity_kg=10400.0,
        loss_kg=400.0,
        quantity_sold_kg=8000.0,
        quantity_stored_kg=2000.0,
        sale_price_rs_kg=425.0,
        sale_channel="Dambulla DEC",
        problems=["minor_leaf_curl"],
    )
    test_session.add(harvest)
    test_session.commit()

    h_out = test_session.query(HarvestReportModel).filter_by(harvest_id="HVST-STG2-001").first()
    assert h_out is not None
    # Realized yield MT/ha = (10400 / 1000) / 2.0 = 5.2 MT/ha
    assert h_out.yield_mt_per_ha == 5.2
    assert h_out.sale_channel == "Dambulla DEC"
    assert h_out.planting_report.crop_id == "chilli"


def test_forecast_snapshot_with_ratio_spi(test_session):
    """Verify forecast snapshots store ratio SPI with 0.8/1.2 bands and probabilistic prices."""
    snap = ForecastSnapshotModel(
        crop_id="big_onion",
        district="Anuradhapura",
        season="Maha 2025/2026",
        forecast_for_month="2026-04",
        horizon_months=3,
        price_p10=115.0,
        price_p50=138.0,
        price_p90=162.0,
        retail_price_rs_kg=210.0,
        supply_low_mt=24000.0,
        supply_mid_mt=32000.0,
        supply_high_mt=38000.0,
        demand_mt=25000.0,
        # Ratio SPI: Supply / Demand
        spi_ratio_low=0.96,
        spi_ratio_mid=1.28,   # > 1.2 => GLUT
        spi_ratio_high=1.52,
        spi_label="GLUT",
        gap_best_mt=-1000.0,
        gap_worst_mt=13000.0,
        import_lead_weeks=7,
        price_model_used="SARIMAX-Ensemble",
        supply_model_used="A1-VolumeForecaster",
        confidence_badge="high",
        confidence_score=85.0,
        is_demo=False,
    )
    test_session.add(snap)
    test_session.commit()

    retrieved = test_session.query(ForecastSnapshotModel).filter_by(forecast_for_month="2026-04").first()
    assert retrieved is not None
    assert retrieved.spi_ratio_mid == 1.28
    assert retrieved.spi_label == "GLUT"
    assert retrieved.price_p50 == 138.0
    assert retrieved.import_lead_weeks == 7


def test_data_catalogue_and_monthly_data(test_session):
    """Verify Data Catalogue and Monthly Data with source_type transparency."""
    cat = DataCatalogueModel(
        dataset_id="cbsl_prices_2024",
        title="CBSL Daily/Weekly Prices",
        publisher="Central Bank of Sri Lanka",
        licence="OGL-LK",
        is_primary=True,
    )
    test_session.add(cat)
    test_session.commit()

    monthly = MonthlyDataModel(
        crop_id="big_onion",
        district="Anuradhapura",
        month="2024-06",
        planted_area_ha=1200.0,
        harvested_area_ha=1150.0,
        production_mt=18000.0,
        farmgate_price_rs_kg=140.0,
        source_type="real",
        dataset_id=cat.dataset_id,
    )
    test_session.add(monthly)
    test_session.commit()

    m_out = test_session.query(MonthlyDataModel).filter_by(month="2024-06").first()
    assert m_out.source_type == "real"
    assert m_out.dataset_id == "cbsl_prices_2024"


def test_alerts_and_status(test_session):
    """Verify in-app alerts and acknowledge/ask-officer tracking."""
    user = UserModel(
        user_id="USR-FARMER-01",
        username="farmer_anura",
        password_hash="pbkdf2_sha256$test$hashedpassword",
        role="farmer",
    )
    test_session.add(user)
    test_session.commit()

    alert = AlertModel(
        alert_id="ALT-GLUT-001",
        crop_id="big_onion",
        district="Anuradhapura",
        type="GLUT_WARNING",
        severity="critical",
        message_key="alert.glut.delay_planting",
        params={"spi": 1.35, "month": "2026-05"},
    )
    test_session.add(alert)
    test_session.commit()

    status = AlertStatusModel(
        alert_id=alert.alert_id,
        user_id=user.user_id,
        acknowledged_at=datetime.now(timezone.utc),
        ask_officer=True,
        officer_note="Can I hold big onion in storage for 4 weeks?",
    )
    test_session.add(status)
    test_session.commit()

    s_out = test_session.query(AlertStatusModel).filter_by(alert_id=alert.alert_id).first()
    assert s_out.ask_officer is True
    assert "storage" in s_out.officer_note


def test_decision_history_store_db_persistence(tmp_path):
    """Verify DecisionHistoryStore records decisions with SHA-256 hash into DB."""
    store = DecisionHistoryStore(storage_path=tmp_path / "decisions.json", sync_db=True)
    record = DecisionRecord(
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id="OFF-001",
        action_type="RESTRICT_EXPANSION",
        quantity=500.0,
        unit="ha",
        rationale="Prevent price collapse",
    )
    result = store.log_decision(record)
    assert result["status"] == "RECORDED"
    assert result["decision_id"] == record.decision_id

    retrieved = store.list_decisions(crop_id="big_onion")
    assert len(retrieved) >= 1
    assert any(r.decision_id == record.decision_id for r in retrieved)


def test_planting_report_store_db_persistence(tmp_path):
    """Verify PlantingReportStore records planting reports into DB."""
    store = PlantingReportStore(storage_path=tmp_path / "reports.json", sync_db=True)
    report = PlantingReport(
        crop_id="chilli",
        season="Maha 2025/2026",
        planned_area_ha=2.0,
        actual_area_ha=2.2,
        consent_given=True,
        pseudonymous_id="LK-DB-TEST-01",
    )
    res = store.submit_report(report)
    assert res["status"] == "ACCEPTED"
    assert res["report_id"] == report.report_id


def test_api_database_endpoints():
    """Verify FastAPI database management, health reporting, and CRUD endpoint functions."""
    from govisense.api.main import (
        health,
        initialize_database,
        register_farmer,
        list_farmers,
        register_officer,
        list_officers,
        submit_harvest_report,
        FarmerPayload,
        OfficerPayload,
        HarvestReportPayload,
    )

    # 1. Health check includes database info and fallback detection
    res = health()
    assert res["status"] == "ok"
    assert "database" in res
    assert res["database"]["status"] == "connected"
    assert "dialect" in res["database"]
    assert "is_fallback" in res["database"]

    # 2. Database init endpoint
    init_res = initialize_database()
    assert init_res["status"] == "INITIALIZED"
    assert "runs" in init_res["tables"]
    assert "harvest_reports" in init_res["tables"]
    assert "alerts" in init_res["tables"]

    # 3. Register and query pseudonymous farmer profile
    f_res = register_farmer(
        FarmerPayload(
            pseudonymous_id="LK-AP-F100",
            district="Anuradhapura",
            divisional_secretariat="Kekirawa",
            total_land_ha=4.5,
            irrigation_type="irrigated",
            irrigation_subtype="major",
            soil_type="RBE",
            soil_ph=6.5,
            consent_given=True,
            language="si",
        )
    )
    assert f_res["status"] == "SUCCESS"
    assert f_res["farmer"]["pseudonymous_id"] == "LK-AP-F100"

    farmers = list_farmers(district="Anuradhapura")
    assert any(f["pseudonymous_id"] == "LK-AP-F100" for f in farmers)

    # 4. Register and query officer
    o_res = register_officer(
        OfficerPayload(
            officer_id="OFF-100",
            name="Dr. Chandupa",
            district="Anuradhapura",
            division="Provincial Dept",
            role="Crop Forecaster",
        )
    )
    assert o_res["status"] == "SUCCESS"
    assert o_res["officer"]["officer_id"] == "OFF-100"

    officers = list_officers(district="Anuradhapura")
    assert any(o["officer_id"] == "OFF-100" for o in officers)

    # 5. Submit harvest report with validation
    h_res = submit_harvest_report(
        HarvestReportPayload(
            planting_report_id="REP-SAMPLE-01",
            pseudonymous_id="LK-AP-F100",
            crop_id="big_onion",
            season="Maha 2025/2026",
            area_harvested_ha=2.0,
            harvest_quantity_kg=30000.0,
            loss_kg=1500.0,
            quantity_sold_kg=25000.0,
            quantity_stored_kg=3500.0,
            sale_price_rs_kg=135.0,
            sale_channel="Dambulla DEC",
            sale_month=4,
        )
    )
    assert h_res["status"] == "ACCEPTED"
    assert h_res["harvest"]["yield_mt_per_ha"] == 15.0

    # 6. Dashboard: Gap & Import Timeline
    from govisense.api.main import (
        get_gap_timeline,
        get_price_outlook,
        get_adoption_summary,
        list_ground_reports,
        list_data_catalogue,
        get_sources_summary,
        list_pipeline_runs,
        list_alerts,
        acknowledge_alert,
        login_user,
        LoginPayload,
        AlertAckPayload,
    )
    gap_data = get_gap_timeline(crop_id="big_onion")
    assert "timelines" in gap_data
    assert len(gap_data["timelines"]) == 1
    assert "decision_deadline" in gap_data["timelines"][0]
    assert gap_data["timelines"][0]["import_lead_weeks"] == 7

    # 7. Dashboard: Price Outlook
    price_data = get_price_outlook(crop_id="big_onion")
    assert "crops" in price_data
    assert "big_onion" in price_data["crops"]
    assert "p50" in price_data["crops"]["big_onion"]["farmgate_price"]

    # 8. Dashboard: Adoption Summary
    adopt_data = get_adoption_summary(crop_id="big_onion")
    assert "acreage" in adopt_data
    assert "recommendation_adherence" in adopt_data
    assert "predicted_vs_actual" in adopt_data

    # 9. Dashboard: Ground reports
    gr_data = list_ground_reports()
    assert "ground_reports" in gr_data

    # 10. Dashboard: Data Sources
    cat_data = list_data_catalogue()
    assert len(cat_data) >= 1
    src_data = get_sources_summary()
    assert "real_pct" in src_data

    # 11. Dashboard: Run Traceability
    runs_data = list_pipeline_runs()
    assert len(runs_data) >= 1

    # 12. Dashboard: Alerts & Acknowledge
    alerts_data = list_alerts()
    assert len(alerts_data) >= 1
    ack_res = acknowledge_alert(
        alert_id=alerts_data[0]["alert_id"],
        payload=AlertAckPayload(user_id="OFFICER-001", ask_officer=True, officer_note="Testing ack"),
    )
    assert ack_res["status"] == "ACKNOWLEDGED"

    # 13. Dashboard: Login
    login_res = login_user(LoginPayload(username="officer_anura", password="password123", role="officer"))
    assert login_res["status"] == "SUCCESS"
    assert "token" in login_res

