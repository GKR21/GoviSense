"""
Tests for Task 6: Database Models, Sessions, Migrations, and Concurrent-Write Safety
Team DARKBITE · ModelX 2.0 Phase 2
Pilot: Anuradhapura (Big Onion, Chilli)
"""

import threading
import uuid
import pytest
from datetime import datetime, timezone

from govisense.db.lookups import ensure_crop_exists, ensure_officer, ensure_user_for_actor, resolve_district_id
from govisense.db.models import (
    Alert,
    AlertInteraction,
    AlertQuestionModel,
    AlertTranslationModel,
    Base,
    DecisionHistoryRecord,
    MarketPriceRecord,
    PlantingReportRecord,
    User,
)
from govisense.db.session import (
    db_write_lock,
    get_db_session,
    get_engine,
    init_db,
    migrate_legacy_json_files,
)
from govisense.feedback.planting_reports import PlantingReport, PlantingReportStore
from govisense.db.history import DecisionRecord, DecisionHistoryStore


def test_init_db_and_tables_created():
    """Verify tables are created and default data seeded."""
    init_db()
    with get_db_session() as db:
        user_count = db.query(User).count()
        assert user_count >= 2
        officer = db.query(User).filter(User.username == "officer_anuradhapura").first()
        assert officer is not None
        assert officer.role == "officer"


def test_planting_report_db_roundtrip():
    """Verify PlantingReportStore writes to and reads from DB with full audit trail."""
    store = PlantingReportStore()  # Uses DB
    rep_id = f"REP-TEST-{uuid.uuid4().hex[:6].upper()}"
    pseudo_id = f"PSEUDO-DB-{uuid.uuid4().hex[:6].upper()}"
    report = PlantingReport(
        crop_id="big_onion",
        season="Maha 2025/2026",
        planned_area_ha=3.0,
        actual_area_ha=3.5,
        consent_given=True,
        pseudonymous_id=pseudo_id,
        harvest_outcome_mt=50.0,
        sale_price_rs_kg=130.0,
        sale_channel="Dambulla DEC",
        notes="High quality harvest",
        report_id=rep_id,
    )

    res = store.submit_report(report)
    assert res["status"] == "ACCEPTED"
    assert res["report_id"] == rep_id

    # Verify retrieval from database
    reports = store.get_reports(crop_id="big_onion", season="Maha 2025/2026")
    found = [r for r in reports if r.report_id == rep_id]
    assert len(found) == 1
    assert found[0].actual_area_ha == 3.5
    assert found[0].harvest_outcome_mt == 50.0


def test_decision_history_db_roundtrip():
    """Verify DecisionHistoryStore writes to and reads from DB."""
    store = DecisionHistoryStore()  # Uses DB
    dec_id = f"DEC-TEST-{uuid.uuid4().hex[:6].upper()}"
    record = DecisionRecord(
        crop_id="big_onion",
        season="Maha 2025/2026",
        officer_id="OFFICER-TEST-99",
        action_type="HOLD_STORAGE",
        quantity=2500.0,
        unit="MT",
        rationale="Floor price stabilization test",
        model_version="LightGBM-v2.1+HiGHS-LP",
        data_version="CBSL-HARTI-DOA-2024.12",
        assumptions={"loss_pct": 0.12, "buffer": 0.05},
        decision_id=dec_id,
    )

    res = store.log_decision(record)
    assert res["status"] == "RECORDED"
    assert res["decision_id"] == dec_id

    history = store.list_decisions(crop_id="big_onion", limit=100)
    found = [r for r in history if r.decision_id == dec_id]
    assert len(found) == 1
    assert found[0].quantity == 2500.0
    assert found[0].assumptions["loss_pct"] == 0.12


def test_concurrent_writes_safety():
    """
    Simulates high concurrency across 20 threads submitting planting reports
    and decision logs concurrently to verify WAL mode & thread safety without SQLite locking errors.
    """
    store = PlantingReportStore()
    history_store = DecisionHistoryStore()
    errors = []
    run_tag = uuid.uuid4().hex[:6].upper()

    def worker(worker_id: int):
        try:
            # 1. Submit planting report
            rep = PlantingReport(
                crop_id="big_onion",
                season="Maha 2025/2026",
                planned_area_ha=1.0 + worker_id,
                actual_area_ha=1.2 + worker_id,
                consent_given=True,
                pseudonymous_id=f"CONCURRENT-FARMER-{worker_id}-{run_tag}",
                report_id=f"REP-CONC-{worker_id}-{uuid.uuid4().hex[:4].upper()}",
            )
            store.submit_report(rep)

            # 2. Log decision record
            dec = DecisionRecord(
                crop_id="big_onion",
                season="Maha 2025/2026",
                officer_id=f"OFFICER-CONC-{worker_id}",
                action_type="MAINTAIN",
                quantity=100.0 * worker_id,
                unit="MT",
                rationale=f"Concurrent stress test {worker_id}",
                decision_id=f"DEC-CONC-{worker_id}-{uuid.uuid4().hex[:4].upper()}",
            )
            history_store.log_decision(dec)
        except Exception as e:
            errors.append((worker_id, str(e)))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent write errors encountered: {errors}"


def test_alerts_and_interactions_models():
    """Verify normalized Alert, AlertTranslation, AlertStatus, and AlertQuestion models operate cleanly."""
    with get_db_session() as db:
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        cid = ensure_crop_exists(db, "big_onion")
        dist_id = resolve_district_id(db, "Anuradhapura")
        alert = Alert(
            alert_id=alert_id,
            crop_id=cid,
            district_id=dist_id,
            type_code="GLUT_WARNING",
            severity="warning",
            message_key="GLUT_WARNING",
            target_role="farmer",
            status="active",
        )
        db.add(alert)
        db.flush()
        db.add_all(
            [
                AlertTranslationModel(
                    alert_id=alert_id,
                    lang_code="en",
                    title="High Supply Warning",
                    message="Projected supply exceeds local hub capacity by 15%.",
                ),
                AlertTranslationModel(
                    alert_id=alert_id,
                    lang_code="si",
                    title="අධික සැපයුම් අනතුරු ඇඟවීම",
                    message="ඇස්තමේන්තුගත සැපයුම කලාපීය ධාරිතාව ඉක්මවයි.",
                ),
                AlertTranslationModel(
                    alert_id=alert_id,
                    lang_code="ta",
                    title="அதிக விநியோக எச்சரிக்கை",
                    message="மதிப்பிடப்பட்ட விநியோகம் கொள்ளளவை விட அதிகமாக உள்ளது.",
                ),
            ]
        )

        uid = ensure_user_for_actor(db, "FARMER-TEST-001", default_role="farmer")
        off = ensure_officer(db, officer_id="OFF-ALERT-TEST")
        now = datetime.now(timezone.utc)
        interaction = AlertInteraction(
            alert_id=alert_id,
            user_id=uid,
            read_at=now,
            acknowledged_at=now,
        )
        db.add(interaction)
        db.add(
            AlertQuestionModel(
                alert_id=alert_id,
                user_id=uid,
                question="Should I store in cool room?",
                answered_by=off.officer_id,
                officer_response="Yes, hold for 2 weeks until prices recover.",
            )
        )
        db.commit()

        fetched_alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
        assert fetched_alert is not None
        assert fetched_alert.to_dict(lang="si")["title"] == "අධික සැපයුම් අනතුරු ඇඟවීම"

        fetched_interaction = db.query(AlertInteraction).filter(AlertInteraction.alert_id == alert_id).first()
        assert fetched_interaction is not None
        assert fetched_interaction.acknowledged is True

