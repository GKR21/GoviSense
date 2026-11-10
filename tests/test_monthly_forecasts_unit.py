"""Dependency-free checks for the mobile monthly forecast adapter."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from govisense.api.monthly_forecasts import build_monthly_series


class MonthlyForecastTests(unittest.TestCase):
    def test_uses_model_and_pressure_engine_for_each_dated_period(self):
        model = Mock()
        model.predict_row.return_value = SimpleNamespace(point_forecast=1000)
        engine = Mock()
        engine.compute_spi.return_value = SimpleNamespace(scenarios={
            "mid": SimpleNamespace(supply_mt=850, demand_mt=500, spi_ratio=1.7)
        })
        rows = [{"month": month, "year_month": f"2026-{month:02}", "import_volume_mt": 10}
                for month in range(1, 13)]
        points = build_monthly_series(rows, model, engine, "big_onion")
        self.assertEqual(len(points), 12)
        self.assertEqual(points[0], {"period": "2026-01", "supply_mt": 850,
                                    "demand_mt": 500, "spi_ratio": 1.7})
        self.assertEqual(points[-1]["period"], "2026-12")
        self.assertEqual(model.predict_row.call_count, 12)
        engine.compute_spi.assert_called_with(crop="big_onion", forecast_supply_mt=1000,
                                              month=12, target_date="2026-12", import_volume_mt=10)

    def test_missing_periods_are_not_fabricated(self):
        self.assertEqual(build_monthly_series([], Mock(), Mock(), "big_onion"), [])

    def test_model_failure_is_not_replaced_with_demo_data(self):
        model = Mock()
        model.predict_row.side_effect = RuntimeError("Model unavailable")
        with self.assertRaises(RuntimeError):
            build_monthly_series([{}], model, Mock(), "big_onion")
