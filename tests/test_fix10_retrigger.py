from govisense.api.main import get_latest_forecasts
from govisense.api.routes.feedback import submit_planting_report, retrigger_pipeline, PlantingReportPayload, ReTriggerPayload
from govisense.db.session import init_db


def test_posted_report_triggers_refit_and_changes_latest_forecast():
    init_db()

    # 1. Baseline forecast before new report
    before_forecast = get_latest_forecasts()
    bo_before = before_forecast["crops"]["big_onion"]["ai3_supply_pressure_index"]
    supply_before = bo_before["scenarios"]["mid"]["supply_mt"]
    gap_before = bo_before["gap_mt"]

    # 2. Post a real farmer planting report
    payload = PlantingReportPayload(
        crop="big_onion",
        crop_id="big_onion",
        district="Anuradhapura",
        season="Maha 2025/2026",
        planned_area_ha=30.0,
        actual_area_ha=30.0,
        consent_given=True,
        pseudonymous_id="RETRIGGER-VERIFY-001"
    )
    post_res = submit_planting_report(payload)
    assert post_res["status"] == "ACCEPTED"
    assert "report_id" in post_res

    # 3. Call retrigger endpoint and check refit
    retrigger_payload = ReTriggerPayload(
        crop_id="big_onion",
        season="Maha 2025/2026",
        target_month=5,
    )
    retrigger_res = retrigger_pipeline(retrigger_payload)
    assert retrigger_res["retrained"] is True
    assert "RUN-RETRIGGER-" in retrigger_res["run_id"]
    assert "refit_inputs" in retrigger_res
    assert retrigger_res["refit_inputs"]["reported_area_ha"] >= 30.0
    assert retrigger_res["refit_inputs"]["effective_supply_mt"] > 0

    # 4. Verify /api/forecasts/latest changed!
    after_forecast = get_latest_forecasts()
    bo_after = after_forecast["crops"]["big_onion"]["ai3_supply_pressure_index"]
    supply_after = bo_after["scenarios"]["mid"]["supply_mt"]
    gap_after = bo_after["gap_mt"]

    # The supply and supply gap must have increased
    assert supply_after > supply_before, f"Supply did not increase: before={supply_before}, after={supply_after}"
    assert gap_after > gap_before, f"Supply gap did not increase: before={gap_before}, after={gap_after}"

