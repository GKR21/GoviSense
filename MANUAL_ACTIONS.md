# GoviSense Manual Actions & Data Sourcing Guide
**Team DARKBITE · ModelX 2.0 Phase 1**

This document catalogues external datasets, government publications, and manual reviewer tasks that require human action or air-gapped data transfers in compliance with project rules.

---

## 1. External Real Datasets & Download URLs

| Source | Edition / Snapshot Date | Description | URL / Retrieval Instruction | Local Path | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DOA SEPC (CPP)** | 2026 Season Plan (2025-11) | Crop Production Programme 2026 (Area, Yield, Production by District & National) | [https://www.doa.gov.lk/sepc](https://www.doa.gov.lk/sepc) | `data/raw/cpp/doa_cpp_seasonal_2026.pdf` | **STAGED (877 KB)** |
| **DOA SEPC (CPP)** | 2024/2025 Seasonal (2024-11) | Progress of Crop Production Programme 2024/25 Maha & Yala | [https://www.doa.gov.lk/sepc](https://www.doa.gov.lk/sepc) | `data/raw/cpp/doa_cpp_seasonal_2024_2025.pdf` | **STAGED (677 KB)** |
| **CBSL Daily Prices** | 2026-10-30 to 2026-11-06 | Daily Price Reports (Wholesale & Retail for Pettah, Dambulla, Narahenpita) | [https://www.cbsl.gov.lk/en/statistics/economic-indicators/price-report](https://www.cbsl.gov.lk/en/statistics/economic-indicators/price-report) | `data/raw/cbsl/price_report_*.pdf` | **STAGED (6 Bulletins)** |
| **CBSL Historical Prices** | 2018-01 to 2024-12 | Historical commodity daily prices (Wholesale & Retail) | Central Bank of Sri Lanka Economic Statistics Database | `data/raw/cbsl/cbsl_daily_prices_historical.csv` | **STAGED (1.65 MB)** |
| **WFP / HDX** | 2004 to 2024 | Sri Lanka Food Prices (Wholesale & Retail by Market & Commodity) | [https://data.humdata.org/dataset/wfp-food-prices-for-sri-lanka](https://data.humdata.org/dataset/wfp-food-prices-for-sri-lanka) | `data/raw/wfp/wfp_food_prices_lka.csv` | **STAGED (4.4 MB)** |
| **NASA POWER Agroclimatology** | 2018-01 to 2024-12 | Monthly precipitation, temperature & anomalies (Anuradhapura 8.3114° N, 80.4037° E) | [https://power.larc.nasa.gov/api/temporal/monthly/point](https://power.larc.nasa.gov/api/temporal/monthly/point) | `data/raw/weather/anuradhapura_nasa_power_monthly.csv` | **STAGED (7.7 KB)** |
| **HARTI Weekly Bulletins** | Current 2026 Weeks | Hector Kobbekaduwa Agrarian Research and Training Institute (Food Information Bulletin) | [http://www.harti.gov.lk/index.php/en/market-information/food-information-bulletin](http://www.harti.gov.lk/index.php/en/market-information/food-information-bulletin) | `data/raw/harti/harti_weekly_bulletin_latest.pdf` | **ACTION REQUIRED BY HUMAN** |

### Human Action for HARTI Bulletins:
1. Navigate to the official HARTI Food Information Bulletin repository at [http://www.harti.gov.lk/index.php/en/market-information/food-information-bulletin](http://www.harti.gov.lk/index.php/en/market-information/food-information-bulletin).
2. Download the latest monthly or weekly bulletin PDF.
3. Save the PDF to `data/raw/harti/harti_weekly_bulletin_latest.pdf`.
4. Run `python scripts/download_data.py` to ingest and validate the bulletin.

---

## 2. 5% Ground-Truth Hand-Checked Review Sheet

Per Proposal Section 5.2 and Item 1.5, a 5% random sample of extracted values from real PDF publications must be independently verified by a human reviewer.

* **Audit CSV File**: [`data/interim/hand_checked_sample_real.csv`](file:///d:/GoviSence/data/interim/hand_checked_sample_real.csv)
* **Instructions for Reviewer**:
  1. Open the cited PDF (`data/raw/cpp/doa_cpp_seasonal_2026.pdf` or `data/raw/cbsl/price_report_*.pdf`) at the specified page.
  2. Locate the commodity and metric (e.g., Big Onion planted extent in Matale, Anuradhapura, or National).
  3. Enter the exact printed number in the `reviewer_verified_value` column.
  4. Enter `PASS` or `FAIL` in the `verdict` column.
  5. The CI test in `tests/test_extract.py` computes the exact error rate:
     $$\text{Error Rate} = \frac{\sum |\text{extracted} - \text{verified}|}{\sum \text{verified}} \times 100\%$$

