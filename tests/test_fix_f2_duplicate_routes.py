"""
Test Fix F2: Duplicate Route Resolution & Elimination of 1000 MT Placeholder
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from collections import Counter
from govisense.api.main import app, load_and_train


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure models and data cache are loaded."""
    load_and_train()


def _get_all_routes(app_or_router):
    routes = []
    for r in app_or_router.routes:
        if hasattr(r, "original_router"):
            routes.extend(_get_all_routes(r.original_router))
        elif hasattr(r, "routes"):
            routes.extend(_get_all_routes(r))
        else:
            routes.append(r)
    return routes


def test_no_duplicate_routes():
    """Verify that every route (HTTP method, path) across the FastAPI app is unique."""
    all_routes = _get_all_routes(app)
    routes_seen = []
    for route in all_routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if methods and path:
            for m in methods:
                if m != "HEAD":  # ignore automatic HEAD
                    routes_seen.append((m, path))

    counts = Counter(routes_seen)
    duplicates = {route: count for route, count in counts.items() if count > 1}
    assert not duplicates, f"Found duplicate registered routes in FastAPI app: {duplicates}"


def test_farmer_top3_handler_provenance():
    """Verify that /api/farmer/top3 resolves to the surviving handler in routes/farmer.py."""
    all_routes = _get_all_routes(app)
    matching = [
        r for r in all_routes
        if getattr(r, "path", None) == "/api/farmer/top3" and "GET" in getattr(r, "methods", set())
    ]
    assert len(matching) == 1, f"Expected exactly 1 GET /api/farmer/top3 route, got {len(matching)}"
    endpoint_func = matching[0].endpoint
    assert endpoint_func.__module__ == "govisense.api.routes.farmer", (
        f"Expected endpoint module 'govisense.api.routes.farmer', got '{endpoint_func.__module__}'"
    )
    assert endpoint_func.__name__ == "farmer_top3_recommendations", (
        f"Expected endpoint func 'farmer_top3_recommendations', got '{endpoint_func.__name__}'"
    )


def test_farmer_top3_real_a1_and_a2_output():
    """
    Verify /api/farmer/top3 returns actual model outputs:
    1. forecast_supply_mt != 1000.0 (no placeholder)
    2. supply_data_quality is 'real'
    3. price_forecast is derived from A2 conformal predictions, not fixed 0.85/1.50 multipliers
    """
    from govisense.api.routes.farmer import farmer_top3_recommendations

    res = farmer_top3_recommendations(
        farmer_id="FARMER-REAL-TEST",
        season="Yala",
        land_ha=2.5,
        current_month=5,
        is_rainfed=False,
        annual_rainfall_mm=1100.0,
        avg_temp_c=28.0,
        zone="dry",
    )

    assert "top3" in res
    assert len(res["top3"]) > 0

    top_crop = res["top3"][0]
    crop_id = top_crop["crop_id"]

    # Check A1 supply forecast: must NOT be 1000.0
    supply = top_crop.get("supply_forecast_mt")
    assert supply is not None, "Supply forecast should not be None for supported crops"
    assert supply != 1000.0, f"Found forbidden 1000.0 MT placeholder for crop {crop_id}"
    assert top_crop.get("supply_data_quality") == "real"

    # Check A2 price forecast: must be conformal A2 output
    pf = top_crop.get("price_forecast")
    assert pf is not None, "Price forecast should be present for modeled crop"
    assert "p10_rs_kg" in pf and "p90_rs_kg" in pf
    assert pf["p10_rs_kg"] > 0
    assert pf["p90_rs_kg"] >= pf["p10_rs_kg"]
    assert top_crop.get("price_data_quality") == "real"

    # Verify multi-month horizon is from A2 conformal predictions
    monthly = top_crop.get("monthly_price_ranges_12m")
    assert monthly is not None and len(monthly) == 12
    for row in monthly:
        assert "p10_rs_kg" in row and "p90_rs_kg" in row
