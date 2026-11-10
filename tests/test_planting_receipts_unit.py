"""Dependency-free checks for the checksum of persisted report fields."""
import unittest
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from govisense.feedback.receipts import planting_receipt


class PlantingReceiptTests(unittest.TestCase):
    def report(self):
        return SimpleNamespace(report_id="REP-server", pseudonymous_id="FARMER-001",
            crop_id="big_onion", season_id=1, planned_area_ha=Decimal("0.81"),
            actual_area_ha=Decimal("0.81"), irrigation_code="minor_tank",
            planting_date=date(2026, 11, 10), expected_harvest_date=None,
            recommended_crop_shown=None, reason=None, expected_price_rs_kg=None,
            consent_given=True, notes="Declaration")

    def test_receipt_is_deterministic_and_has_real_sha256_length(self):
        report = self.report()
        receipt = planting_receipt(report)
        self.assertEqual(receipt, planting_receipt(self.report()))
        self.assertEqual(receipt["report_id"], "REP-server")
        self.assertRegex(receipt["receipt_hash"], r"^[0-9a-f]{64}$")

    def test_reloading_numeric_columns_does_not_change_checksum(self):
        original = planting_receipt(self.report())
        report = self.report()
        report.planned_area_ha = 0.81
        report.actual_area_ha = Decimal("0.8100")
        self.assertEqual(original, planting_receipt(report))

    def test_report_changes_invalidate_the_previous_receipt(self):
        original = planting_receipt(self.report())["receipt_hash"]
        for name, value in [("actual_area_ha", Decimal("1.20")),
                            ("planting_date", date(2026, 12, 1)),
                            ("pseudonymous_id", "FARMER-002"),
                            ("consent_given", False), ("notes", "changed")]:
            report = self.report()
            setattr(report, name, value)
            self.assertNotEqual(original, planting_receipt(report)["receipt_hash"])

    def test_receipt_response_does_not_expose_farmer_data(self):
        self.assertEqual(set(planting_receipt(self.report())), {"report_id", "receipt_hash"})
