# Handoff outside farmer mobile AI scope

## Hosted backend — BLOCKED

The owner confirmed on 2026-11-10 that the backend is not hosted. Supply the
actual HTTPS origin and deploy it before verifying the release configuration.
Do not assume the proposed api.govisense.lk domain is operational.

## Auth/security — excluded from this task

The full baseline has an existing seed-user login failure. The mobile profile
does not obtain a verified pseudonymous farmer ID from /api/auth/me. The auth
owner should expose or provide a supported way to resolve that identity.

The request for an in-app release backend override conflicts with the existing
release policy that disables it. The security owner must resolve that policy;
do not weaken HTTPS validation. INTERNET permission and cleartext restrictions
must remain enforced. Farmer-only navigation also requires coordinating with
AuthRepository.home, which currently routes officer/admin roles to /officer.

## Missing source files — BLOCKED

Restore the independently obtained CBSL daily CSV, WFP food-price CSV and
original PDFs/source tables expected by the data tests. data/raw currently
contains only .gitkeep. Do not reconstruct claimed observations from processed
monthly means or generate replacements. Exact latest-row verification requires
the original observations.

## Existing baseline failures

See mobile-ai-audit.md for the actual full-suite result: 261 passed, 12 failed,
2 skipped out of 275. Investigate authentication and direct-call database
session leakage without changing schemas or bypassing tests. Web dashboard,
CI, authentication and security changes remain outside this task.

---

## Earlier handoff (retained; audit findings above take precedence)

# GoviSense AI/Model Architecture & API Handoff Document
**Team DARKBITE · ModelX 2.0 Phase 1 Completion**
**Audience:** Frontend, Mobile (Flutter), Backend/Security, and Data Engineers

---

## 1. Executive Summary & Design Principles
All models, decision algorithms, backtesting engines, and endpoints now run strictly on genuine, traceable real-world inputs:
- **Price Series:** Daily trading reports from the Central Bank of Sri Lanka (CBSL) Pettah Wholesale and Retail markets (August 2016 – October 2026, 2,455 trading days).
- **Agro-Climatic Data:** NASA POWER daily satellite agro-meteorology for Anuradhapura and Matale agricultural zones.
- **Planned Agricultural Extent:** Department of Agriculture Crop Planting Plans (CPP) 2024/25 and 2026.
- **Zero Fallback/Placeholder Policy:** All placeholders (`1000.0 MT`, `5000 MT`, `1.3x/1.4x` multipliers, `0.85/1.50` floor multipliers) have been removed. When a crop lacks empirical data or an external service fails, the API responds with `null` fields, `data_quality: "no_data"` / `"no_price_data"`, or raises HTTP 503 Service Unavailable.

---

## 2. API Contract & Response Schema Updates

### 2.1 GET `/api/forecasts/latest`
Provides high-level real-time forecast outputs across pilot crops.

#### New / Updated Root Fields
- `data_quality` (`string`): Provenance flag indicating the freshness and health of the underlying data pipeline.
  - `"real"`: Data is current (within 90 days).
  - `"outdated"`: Data is older than 90 days; warning badge surfaced.
  - `"db_unavailable"`: Database offline during snapshot write; serving from cache.
  - `"no_data"`: Required input tables empty or uninitialized.
- `data_age_days` (`integer`): Calendar days between latest observation date and runtime `today`.
- `data_source` (`string`): Traceable identifier (e.g. `"CBSL_Daily_Prices_NASA_POWER_Real"`).

#### Crop Object Updates (`crops.<crop_id>`)
- **`ai1_harvest_forecast`**:
  - `model_classification` (`string`): Explicitly exposes `"A1 Harvest Volume Accounting Model"`.
  - `point_forecast_mt` (`float`): Seasonally weighted yield-to-harvest point estimate.
  - `lower_bound_mt` / `upper_bound_mt` (`float`): Conformal uncertainty interval.
- **`ai2_price_forecast`**:
  - `served_model` (`string`): `"lightgbm"`, `"sarimax"`, `"ets"`, or `"seasonal_naive"`. Baseline is automatically served and labeled if LightGBM fails to beat it on held-out folds.
  - `direction` (`string`): `"up"`, `"down"`, or `"flat"` relative to last observed wholesale price (+/- 5% threshold).
  - `direction_reliable` (`boolean`): Set to `true` ONLY if the directional model beats the majority-class baseline on held-out validation. If `false`, UI must present directional arrows with a cautionary indicator.
  - `p10_forecast`, `p50_forecast`, `p90_forecast` (`float`): Quantile forecasts (Rs/kg).
  - `modeled_retail_price` (`float`): Wholesale forecast multiplied by dynamic trailing 12-month CBSL Pettah retail-to-wholesale median ratio.
  - `retail_method` (`string`): `"12m_cbsl_median_ratio"`.
  - `retail_band_low` / `retail_band_high` (`float`): Empirical 10th and 90th percentile retail bands.
  - `retail_n` (`integer`): Number of active trading months in margin sample (typically 12).
- **`ai3_supply_pressure_index`**:
  - `spi_score` (`float`): Clipped display SPI score (-1.0 to +1.0).
  - `spi_score_raw` (`float`): Raw unclipped difference metric.
  - `spi_ratio` (`float`): Supply-to-demand ratio (1.0 = balanced, >1.2 = glut, <0.8 = shortage).
  - `spi_ratio_raw` (`float`): Unclipped supply-to-demand ratio.
  - `spi_label` (`string`): `"Glut"`, `"Balanced"`, or `"Shortage"`.
  - `confidence_badge` (`string`): `"high"`, `"medium"`, or `"low"` based on 5 rigorous data and thesis rules.

---

### 2.2 GET `/api/gap`
Linear programming decision engine output calculating national deficits/surpluses, procurement deadlines, and optimal policy options.

#### Query Parameters
- `crop` (`string`, default: `"big_onion"`): Crop identifier.
- `lead_weeks` (`integer`, optional): Override import lead time (defaults to 7 for big onion, 6 for chilli, potato, red onion).
- `storage_capacity_mt` (`float`, optional): Warehouse buffer limit (defaults to 15,000 MT).

#### Response Schema
```json
{
  "crop": "big_onion",
  "gap_mt": -1200.0,
  "mid_case_gap_mt": -1200.0,
  "best_case_gap_mt": -1800.0,
  "worst_case_gap_mt": -600.0,
  "decision_deadline": "2026-05-18",
  "decision_deadline_date": "2026-05-18",
  "days_until_deadline": 24,
  "is_deadline_passed": false,
  "import_lead_time_weeks": 7,
  "policy_option": "STORE",
  "action_summary": "Surplus projected: Activate storage buffers and price support."
}
```

#### Reachable Policy Options
1. `IMPORT_NOW`: Deficit projected ($\text{gap} > 200\text{ MT}$) and decision deadline is imminent ($\le 14$ days).
2. `IMPORT_LATER`: Deficit projected ($\text{gap} > 200\text{ MT}$), but decision deadline is $> 14$ days away.
3. `STORE`: Surplus projected ($\text{gap} < -150\text{ MT}$) and surplus is within national storage capacity.
4. `DELAY`: Marginal gap within uncertainty band ($\pm 150\text{ MT}$) or storage buffer exhausted.

---

### 2.3 GET `/api/farmer/top3`
Personalized agronomic and economic crop recommendation engine for farmers.

#### Query Parameters
- `farmer_id` (`string`, required): Pseudonymous farmer identifier.
- `season` (`string`, optional): `"Maha"` or `"Yala"`.
- `land_ha` (`float`, optional): Total arable holding.
- `current_month` (`integer`, optional): 1..12.
- `is_rainfed` (`boolean`, optional): `true` if farm lacks irrigation canal/well access.
- `as_of` (`string`, optional): Reference date `YYYY-MM-DD` for reproducible backtesting.

#### Per-Crop Recommendations in `top3`
- `crop_id` (`string`) and `crop_name` (`string`): Crop details.
- `allocated_ha` / `recommended_ha` (`float`): Land allocation adhering to 60% single-crop cap and unallocated target acreage.
- `fit_score` (`float`): 0.0–100.0 agronomic suitability score.
- `confidence_badge` (`string`): `"high"`, `"medium"`, or `"low"`.
- `price_forecast` (`object` or `null`): Conformal P10/P50/P90 wholesale price predictions (null with `price_data_quality: "no_price_data"` if unmodeled).
- `monthly_price_ranges_12m` (`array` of 12 monthly P10/P50/P90 ranges, or `null`): 12-month forward horizon.
- `expected_net_profit_per_acre`:
  - `p10_rs_per_acre`, `p90_rs_per_acre` (`float`): Per-acre net return range after production costs.
  - `p10_total_profit_lkr`, `p90_total_profit_lkr` (`float`): Total estimated net income in LKR for the recommended parcel size.
- `remaining_target_ha` (`float`): Unclaimed seasonal district target extent.
- `is_target_full` (`boolean`) & `target_full_warning` (`string` or `null`): Set when ground planting reports reach $\ge 110\%$ of seasonal target. Recommended area drops to 0 ha.
- `spi_band_at_harvest` (`string`): `"Glut"`, `"Balanced"`, `"Shortage"`, or `"Unknown"`.

---

### 2.4 GET `/api/evaluation/scoreboard`
Auditable scoreboard backed by database persistence in the `evaluation_results` table.

#### Schema
```json
{
  "run_id": "RUN-bfdb255",
  "data_version": "7fd582fe",
  "model_version": "2.0.0",
  "scoreboard": [
    {
      "crop": "big_onion",
      "module": "A2 Price Forecast",
      "horizon": "t+1",
      "metric": "WAPE",
      "model_wape": 0.1474,
      "baseline_wape": 0.3334,
      "baseline_name": "SARIMAX",
      "served_model": "LightGBM",
      "beat_baseline": true,
      "sample_size": 48,
      "interval_coverage_80": 0.80,
      "usable_status": "Usable"
    }
  ]
}
```

---

## 3. Recommended UI Enhancements for Dashboard & Mobile
1. **Confidence & Data Age Badges:** Render the `data_age_days` and `data_quality` pill on the Officer Dashboard header. If `data_age_days > 90`, display a prominent amber badge ("Data Latency Warning").
2. **Directional Arrow Disclaimer:** When `direction_reliable == false`, render the price trend indicator with an alert tooltip: *"Price directional accuracy on held-out testing did not beat naive baseline; rely primarily on the P10–P90 interval band."*
3. **Deadline Urgency Pill:** On the Decision Matrix, badge `decision_deadline` as Red if `days_until_deadline <= 14` and `policy_option == "IMPORT_NOW"`.
4. **Farmer Profit in Local Currency:** In the Farmer Mobile PWA, highlight `p10_total_profit_lkr` and `p90_total_profit_lkr` so farmers can assess absolute earnings for their specific land parcel.
