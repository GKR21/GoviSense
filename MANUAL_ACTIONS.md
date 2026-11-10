# GoviSense Manual Actions & Data Sourcing Guide
**Team DARKBITE · ModelX 2.0 Phase 1**

This document catalogues external datasets, government publications, and manual reviewer tasks that require human action or air-gapped data transfers in compliance with project rules.

## Current workspace verification — 2026-11-10

**BLOCKED:** the raw files described as STAGED below are absent in this checkout;
`data/raw` contains only `.gitkeep`. Earlier staging notes do not establish local
availability. Restore the original CBSL daily CSV, WFP CSV and CPP/CBSL PDFs;
do not substitute generated observations.

The November farmer season filter returns brinjal and tomato. Both currently
lack A1/A2 model coverage, supply forecasts, price forecasts, expected profit
and SPI ratios. Obtain traceable commodity price histories, district planting
and harvest/yield observations, and demand inputs for these crops before
claiming economic or supply advice on the default screen. June admits big onion
and green chilli, which have existing models; their synthetic supply inputs
still require explicit provenance labeling (A5), not a claim of measured supply.

`as_of` now validates an ISO date and selects its planting month; omitted dates
use today's UTC date. It does not retrain historical models or establish that
old training data can predict the requested calendar year. Forecast cutoff and
freshness handling remain part of A5/contract implementation.

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

---

## 3. Retrieval Guides for Missing Official Primary Sources

The Phase 0 audit confirmed that historical planted area (2018-2023), yield (2018-2023), and import volume series were derived via simulation rather than observed records. To replace simulated series with official ground-truth observations, follow the step-by-step procedures below:

### 3.1 Sri Lanka Customs & Department of Commerce Import Volumes
* **Missing Series**: Monthly import volume (MT) for Big Onion (HS Code: 0703.10) and Green/Dry Chilli (HS Code: 0709.60 / 0710.80) from 2018-01 through 2024-12.
* **Official Publisher**: Sri Lanka Customs, Trade Information Portal & Central Bank of Sri Lanka External Sector Statistics.
* **Retrieval Steps**:
  1. Access the Sri Lanka Customs Trade Data Portal: `https://customs.gov.lk` or CBSL External Sector Monthly Trade Tables: `https://www.cbsl.gov.lk/en/statistics/economic-indicators/external-sector`.
  2. Request/Download External Trade Performance reports for major agricultural import items (Section 2 - Vegetable Products).
  3. Extract monthly aggregated net mass (metric tons) and CIF value for Anuradhapura/Colombo ports of entry.
  4. Save raw CSV to `data/raw/customs/sri_lanka_customs_imports_2018_2024.csv`.
  5. Run `python scripts/ingest_customs.py` to update `data/processed/monthly_master.csv` provenance column `prov_import` from `synthetic` to `real`.

### 3.2 Department of Agriculture AgStat Progress Reports (2018–2023 Realized Area & Yield)
* **Missing Series**: District-level realized planted area (ha) and realized harvest yield (MT/ha) for Maha and Yala seasons 2018–2023 (Pilot district: Anuradhapura; Secondary: Matale).
* **Official Publisher**: Socio Economics and Planning Centre (SEPC), Department of Agriculture, Peradeniya.
* **Publication Title**: *AgStat: Agricultural Statistics of Sri Lanka* (Annual Volumes XV through XXI) and *Seasonal Performance Reports of Other Field Crops (OFC)*.
* **Retrieval Steps**:
  1. Visit the DOA SEPC Publications repository: `https://www.doa.gov.lk/sepc-publications/`.
  2. Download PDF annual volumes for years 2018, 2019, 2020, 2021, 2022, and 2023.
  3. Locate Table 2.4 (*Cultivated Extent and Production of OFC by District*) for Anuradhapura and Matale.
  4. Save PDF files to `data/raw/cpp/agstat_2018_2023/`.
  5. Run `python scripts/extract_agstat.py` to disaggregate seasonal achievements into monthly realized extent and yield.

### 3.3 CBSL Historical Commodity Prices Bulk Export Procedure
* **Existing File**: `data/raw/cbsl/cbsl_daily_prices_historical.csv` (2,455 daily market records from Macro Lab / Pettah market).
* **Retrieval Procedure**:
  1. Navigate to the CBSL Data Library: `https://www.cbsl.gov.lk/en/statistics/statistical-data-library`.
  2. Select *Prices and Wages* -> *Daily Wholesale and Retail Prices of Selected Agricultural Commodities*.
  3. Select date range `2018-01-01` to `2024-12-31`, commodities `Big Onion`, `Green Chilli`, `Red Onion`, `Potato`, markets `Pettah` and `Dambulla DEC`.
  4. Export CSV with daily price range (`wholesale_price_rs_kg`, `retail_price_rs_kg`).
  5. Validate SHA-256 and confirm record count aligns with calendar trading days.
