"""Deterministic receipts for the currently persisted planting declaration."""
import hashlib
import json
from decimal import Decimal


def planting_receipt(report):
    """Hash stored fields, excluding mutable farmer profile and harvest relations.

    This is an integrity checksum verifiable online, not a digital signature.
    Updating a report changes its checksum and invalidates the previous QR.
    """
    def area(value):
        return format(Decimal(str(value)).quantize(Decimal("0.01")), "f") if value is not None else None

    payload = {
        "schema": "govisense.planting.v1",
        "report_id": report.report_id,
        "pseudonymous_id": report.pseudonymous_id,
        "crop_id": report.crop_id,
        "season_id": report.season_id,
        "planned_area_ha": area(report.planned_area_ha),
        "actual_area_ha": area(report.actual_area_ha),
        "irrigation_code": report.irrigation_code,
        "planting_date": report.planting_date.isoformat() if report.planting_date else None,
        "expected_harvest_date": report.expected_harvest_date.isoformat() if report.expected_harvest_date else None,
        "recommended_crop_shown": report.recommended_crop_shown,
        "reason": report.reason,
        "expected_price_rs_kg": area(report.expected_price_rs_kg),
        "consent_given": bool(report.consent_given),
        "notes": report.notes,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {"report_id": report.report_id,
            "receipt_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest()}
