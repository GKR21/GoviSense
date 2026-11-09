"""
Test Fix F6: Calibrated CBSL Retail Price Ratios & Elimination of Arbitrary Multipliers
Team DARKBITE · ModelX 2.0 Completion
"""

import pytest
from govisense.models.a2_price_forecast import (
    compute_modeled_retail_price,
    CBSL_MEDIAN_RETAIL_RATIOS,
)
from govisense.api.main import get_price_outlook, load_and_train


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    """Ensure baseline models are loaded."""
    load_and_train()


def test_cbsl_median_retail_ratios():
    """
    Verify single calibrated method:
    - Big onion median ratio: 1.22 (derived from 2,268 CBSL Pettah market days)
    - Green chilli median ratio: 1.19
    No arbitrary 0.22 floor or 1.35x arbitrary multipliers.
    """
    assert CBSL_MEDIAN_RETAIL_RATIOS["big_onion"] == 1.22
    assert CBSL_MEDIAN_RETAIL_RATIOS["chilli"] == 1.19

    wholesale_base = 100.0
    onion_retail = compute_modeled_retail_price(wholesale_base, crop="big_onion")
    assert onion_retail == 122.0

    chilli_retail = compute_modeled_retail_price(wholesale_base, crop="chilli")
    assert chilli_retail == 119.0


def test_price_outlook_retail_uses_cbsl_model():
    """
    Verify get_price_outlook calculates retail price quantiles
    using compute_modeled_retail_price for p10, p50, and p90,
    rather than hardcoded p10 * 1.3 and p90 * 1.4.
    """
    res = get_price_outlook(crop_id="big_onion")
    assert "big_onion" in res["crops"]
    bo = res["crops"]["big_onion"]

    farmgate = bo["farmgate_price"]
    retail = bo["retail_price"]

    # Verify retail p10, p50, p90 are calculated via compute_modeled_retail_price
    expected_p10 = compute_modeled_retail_price(farmgate["p10"], crop="big_onion")
    expected_p50 = compute_modeled_retail_price(farmgate["p50"], crop="big_onion")
    expected_p90 = compute_modeled_retail_price(farmgate["p90"], crop="big_onion")

    assert retail["p10"] == expected_p10
    assert retail["p50"] == expected_p50
    assert retail["p90"] == expected_p90

