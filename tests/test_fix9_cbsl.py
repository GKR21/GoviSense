from pathlib import Path
from govisense.data.extract_cbsl import CBSLPriceExtractor


def test_cbsl_extractor_on_real_pdf_october_30():
    pdf_path = Path("data/raw/cbsl/price_report_20261030_e.pdf")
    assert pdf_path.exists(), "Test PDF file missing"

    extractor = CBSLPriceExtractor()
    records = extractor.extract_from_pdf(pdf_path)

    assert len(records) > 0, "No records extracted from CBSL PDF"

    # Verify no None values for commodity or market_center
    for r in records:
        assert r["commodity"] in ("big_onion", "chilli", "red_onion", "potato")
        assert r["market_center"] in ("Dambulla DEC", "Pettah")
        assert r["wholesale_price_rs_kg"] is not None
        assert r["retail_price_rs_kg"] is not None
        assert r["wholesale_price_rs_kg"] > 0
        assert r["retail_price_rs_kg"] > 0

    # Verify Dambulla DEC specific values for October 30, 2026
    green_chilli = [
        r for r in records
        if r["market_center"] == "Dambulla DEC" and r["commodity"] == "chilli" and "green" in r["raw_item"].lower()
    ]
    assert len(green_chilli) == 1
    assert green_chilli[0]["wholesale_price_rs_kg"] == 175.0
    assert green_chilli[0]["retail_price_rs_kg"] == 205.0

    big_onion_local = [
        r for r in records
        if r["market_center"] == "Dambulla DEC" and r["commodity"] == "big_onion" and "local" in r["raw_item"].lower()
    ]
    assert len(big_onion_local) == 1
    assert big_onion_local[0]["wholesale_price_rs_kg"] == 350.0
    assert big_onion_local[0]["retail_price_rs_kg"] == 370.0

    potato_local = [
        r for r in records
        if r["market_center"] == "Dambulla DEC" and r["commodity"] == "potato" and "local" in r["raw_item"].lower()
    ]
    assert len(potato_local) == 1
    assert potato_local[0]["wholesale_price_rs_kg"] == 225.0
    assert potato_local[0]["retail_price_rs_kg"] == 245.0
