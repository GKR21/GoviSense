# GoviSense – Agricultural Market Supply Pressure & Price Forecasting

**Team DARKBITE** · ModelX 2.0 Phase 1  
**Domain:** Cost of Living and Everyday Economics  
**Pilot District:** Anuradhapura (Big Onion, Chilli)

---

## 1. Executive Summary & Core Idea

Agricultural markets in Sri Lanka suffer from recurrent cycles of **severe gluts** (bumper harvests causing farm-gate price collapse and farmer impoverishment) and **acute shortages** (supply failure causing steep consumer price spikes).

**GoviSense** bridges this information gap by predicting, per crop and per month, market pressure using the headline metric:

$$\text{Supply Pressure Index (SPI)} = \frac{\text{Forecast Supply} - \text{Projected Demand}}{\text{Projected Demand}}$$

### SPI Decision Bands
| SPI Range | Label | Market Meaning | Recommended Authority Action |
|---|---|---|---|
| **$> +0.15$** | **Glut Risk** | Oversupply, farm-gate price crash likely | Divert into ventilated storage/buffers; stop/defer import quotas |
| **$-0.15$ to $+0.15$** | **Balanced** | Stable market equilibrium | Maintain regular marketing and planting calendar |
| **$< -0.15$** | **Shortage Risk** | Undersupply, consumer price spike likely | Nudge farmers toward planting expansion; plan targeted imports |

---

## 2. The Four AI Features

Only these four components constitute the AI core:

```
[ Historical Data & Open-Meteo ]
               │
               ▼
   [ AI 1: Harvest Volume Forecast ] ──┐
   (LightGBM + Lag/Weather + CI)        │
                                        ▼
   [ Population Demand Model ] ────► [ AI 3: Supply Pressure Index (SPI) ]
   (HIES Per-Capita x Calendar)         │   (Glut / Balanced / Shortage)
                                        │               │
               ┌────────────────────────┘               ▼
               ▼                           [ AI 4: Decision Optimizer ]
   [ AI 2: Price Forecast (1-3m) ]         (Linear Programming - HiGHS)
   (SARIMAX Baseline vs LightGBM)          - Next season hectare adjustments
   - Wholesale & Retail Prices             - Storage buffer hold quantity
   - Direction (UP / DOWN / FLAT)          - Targeted import quotas
```

1. **AI 1 – Harvest Volume Forecast ([a1_allocation.py](file:///d:/GoviSence/src/govisense/models/a1_allocation.py)):**
   * Predicts monthly harvest volume in Metric Tons (MT) for the pilot district.
   * Model: LightGBM Regressor using planting lags (~3 months), rolling yield averages, and weather anomalies.
   * Baseline: Seasonal-Naive ($y_t = y_{t-12}$).
   * Output: Point forecast + 80% prediction interval (10th and 90th percentiles).

2. **AI 3 – Supply Pressure Index ([a3_supply_pressure.py](file:///d:/GoviSence/src/govisense/models/a3_supply_pressure.py)):**
   * Compares AI 1 forecast supply against population-based consumption demand adjusted for seasonal festivals (Sinhala/Tamil New Year, Christmas).
   * Validates economic thesis: high SPI is negatively correlated with subsequent price changes.

3. **AI 2 – Wholesale & Retail Price Forecast ([a2_price_forecast.py](file:///d:/GoviSence/src/govisense/models/a2_price_forecast.py)):**
   * Forecasts wholesale and retail prices 1 to 3 months ahead ($t+1, t+2, t+3$).
   * Model: Competes `statsmodels.SARIMAX` against `LightGBM` using SPI lags, import volumes, and festival flags.
   * Output: Best forecast, confidence interval, and direction indicator (`UP`, `DOWN`, `FLAT`).

4. **AI 4 – Gap-Filling Recommendation Optimizer ([a4_gap_deadline.py](file:///d:/GoviSence/src/govisense/models/a4_gap_deadline.py)):**
   * Linear Optimization (using `scipy.optimize.linprog` with the HiGHS solver).
   * Minimizes total supply gap across crops subject to arable land limits (4,000 ha max seasonal reallocation) and minimum fair farmgate price protection.
   * Output: Actionable policy and farmer advisory timeline.

---

## 3. Data Integrity & Provenance (30% Scoring Criteria)

To uphold the 30% evaluation criterion for data honesty and transparency:
* **Missing Data / Freezes:** Explicitly marked in the data grid with `is_interpolated = True` (e.g., Q2 2020 COVID market lockdown).
* **Data Sources:**
  * CBSL (Central Bank of Sri Lanka) Daily Price Reports
  * HARTI (Hector Kobbekaduwa Agrarian Research and Training Institute) Bulletins
  * DCS (Department of Census and Statistics) Agricultural Statistics & HIES Consumption Data
  * Open-Meteo Historical Weather API (Anuradhapura Dry Zone coordinates)
  * WFP Humanitarian Data Exchange Food Prices

---

## 4. How to Run

### Activate Environment
```powershell
.venv\Scripts\activate
```

### 1. Seed or Regenerate Historical Master Data
```powershell
python scripts/seed_demo.py
```

### 2. Run the Full End-to-End Pipeline
Executes data preprocessing, thesis validation, walk-forward evaluation, live forecast generation, and optimization:
```powershell
python scripts/run_pipeline.py
```

### 3. Run Unit Tests
```powershell
python -m pytest tests/
```
