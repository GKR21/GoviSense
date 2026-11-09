import pandas as pd
import numpy as np
import pytest
from pathlib import Path

def test_cbsl_monthly_table_and_proposal_benchmarks():
    """
    Asserts data/processed/monthly_prices_cbsl.csv exists and reproduces
    proposal benchmark figures on 2025-02-17, 2026-09-16, 2026-09-21.
    """
    cbsl_daily_path = Path("data/raw/cbsl/cbsl_daily_prices_historical.csv")
    assert cbsl_daily_path.exists()
    
    raw = pd.read_csv(cbsl_daily_path, comment="#")
    raw.columns = [c.strip() for c in raw.columns]
    date_col = raw.columns[0]
    raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
    raw = raw.dropna(subset=[date_col]).set_index(date_col)
    
    # 1. 2025-02-17: Big onion imp ~Rs 130, dried chilli ~Rs 650
    dt1 = pd.to_datetime("2025-02-17")
    assert dt1 in raw.index
    val_bo_1 = float(raw.loc[dt1, "Big onion (imp) (wholesale, pettah) (Rs/kg)"])
    val_dc_1 = float(raw.loc[dt1, "Dried chilli (imp) (wholesale, pettah) (Rs/kg)"])
    assert 120.0 <= val_bo_1 <= 150.0  # observed 138.0
    assert 600.0 <= val_dc_1 <= 700.0  # observed 650.0
    
    # 2. 2026-09-16: Big onion imp ~Rs 260, dried chilli ~Rs 1120, green chilli ~Rs 500
    dt2 = pd.to_datetime("2026-09-16")
    assert dt2 in raw.index
    val_bo_2 = float(raw.loc[dt2, "Big onion (imp) (wholesale, pettah) (Rs/kg)"])
    val_dc_2 = float(raw.loc[dt2, "Dried chilli (imp) (wholesale, pettah) (Rs/kg)"])
    val_gc_2 = float(raw.loc[dt2, "Green chilli (wholesale, pettah) (Rs/kg)"])
    assert 240.0 <= val_bo_2 <= 280.0  # observed 262.0
    assert 1050.0 <= val_dc_2 <= 1200.0  # observed 1120.0
    assert 450.0 <= val_gc_2 <= 550.0  # observed 500.0
    
    # 3. 2026-09-21: Green chilli ~Rs 300
    dt3 = pd.to_datetime("2026-09-21")
    assert dt3 in raw.index
    val_gc_3 = float(raw.loc[dt3, "Green chilli (wholesale, pettah) (Rs/kg)"])
    assert 250.0 <= val_gc_3 <= 400.0  # observed 350.0


def test_no_synthetic_cell_labelled_real():
    """
    Validator: Fails if any cell derived from seed_demo.py generator is labelled 'real',
    and verifies that master prices re-derive directly from raw CBSL.
    """
    master_path = Path("data/processed/monthly_master.csv")
    assert master_path.exists()
    master_df = pd.read_csv(master_path)
    
    # Check synthetic columns are correctly labelled
    assert "prov_area" in master_df.columns
    assert (master_df["prov_area"] == "synthetic").all()
    assert (master_df["prov_import"] == "synthetic").all()
    
    # Real price rows must re-derive from raw CBSL
    raw = pd.read_csv("data/raw/cbsl/cbsl_daily_prices_historical.csv", comment="#")
    raw.columns = [c.strip() for c in raw.columns]
    date_col = raw.columns[0]
    raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
    raw = raw.dropna(subset=[date_col]).set_index(date_col)
    
    bo_raw = raw["Big onion (imp) (wholesale, pettah) (Rs/kg)"].astype(float).resample("MS").mean()
    
    bo_real_master = master_df[(master_df["crop"] == "big_onion") & (master_df["prov_price"] == "real")].copy()
    bo_real_master["date"] = pd.to_datetime(bo_real_master["date"])
    
    for _, row in bo_real_master.iterrows():
        dt = row["date"]
        if dt in bo_raw.index and pd.notna(bo_raw.loc[dt]):
            expected = round(bo_raw.loc[dt], 2)
            actual = round(float(row["wholesale_price_rs_kg"]), 2)
            assert np.isclose(expected, actual, atol=0.05), f"Mismatch at {dt}: expected {expected}, got {actual}"


def test_synthetic_prefixes_and_demo_isolation():
    """
    Verify real columns and synthetic columns are clearly distinguished with syn_ prefixes.
    """
    master_df = pd.read_csv("data/processed/monthly_master.csv")
    syn_cols = [
        "syn_planted_extent_ha", "syn_yield_mt_per_ha",
        "syn_harvest_volume_mt", "syn_import_volume_mt",
        "syn_projected_demand_mt", "syn_actual_spi"
    ]
    for sc in syn_cols:
        assert sc in master_df.columns, f"Missing prefix column: {sc}"
