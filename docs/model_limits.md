# GoviSense Empirical Model Limits & Operational Boundaries
**Team DARKBITE · ModelX 2.0 Phase 1 Audit & Verification**
**Data Baseline:** CBSL Daily Trading Records (2016–2026), NASA POWER Agro-Meteorology, DOA CPP Bulletins

---

## 1. Overview
This document records the empirical boundaries, structural limitations, and operational risks of the predictive models in GoviSense. In accordance with DARKBITE auditing standards, every assertion is grounded in observed statistical properties on held-out test data rather than theoretical assumptions.

---

## 2. Crop-Specific Market Realities & Supply-Price Decoupling

### 2.1 Big Onion (Import Parity vs Domestic Supply)
- **Market Structure:** Sri Lanka consumes approximately 24,000–28,000 MT of big onion monthly. Domestic harvest occurs almost exclusively during the Yala season (August–October) in Anuradhapura, Matale, and Dambulla, producing ~35,000–82,000 MT annually.
- **Import Dominance:** 85% to 90% of annual national consumption is met through imports (predominantly from Maharashtra, India).
- **Price Mechanism:** Pettah wholesale prices are dictated by:
  1. Indian Government trade interventions (export bans, Minimum Export Price / MEP mandates).
  2. Colombo CIF import invoice rates and freight costs.
  3. Ministry of Finance Special Commodity Levy (SCL) adjustments (e.g., Rs 10 to Rs 50/kg).
- **Model Limitation:** Because domestic production satisfies only 2–3 months of consumption, domestic Supply Pressure Index (SPI) does not exhibit a continuous negative correlation with wholesale prices throughout the 12-month calendar ($r = +0.22$ on raw CBSL series across 2018–2024). Consequently:
  - Big Onion price forecasting relies on LightGBM quantile regression with import parity features (`local_vs_import_gap`, CIF tariffs, and autoregressive price momentum).
  - Domestic A3 supply forecasts serve baseline seasonal naive when empirical WAPE fails to beat baseline ($0.5969$ vs $0.1723$).

### 2.2 Chilli (Green Fresh vs Dry Import Split)
- **Perishability & Price Volatility:** Green chilli cannot be stored long-term without cold chain infrastructure. Prices fluctuate dramatically within single weeks (e.g., jumping from Rs 350 to Rs 1,120/kg during severe monsoon rain anomalies in Pettah and Dambulla).
- **Import Parity:** Dried chilli is imported in massive volumes (~50,000 MT/year) from Guntur, India. When dried chilli tariffs change, food manufacturers and commercial caterers substitute green chilli, causing cross-elasticity price shocks.
- **Thesis Finding:** While green chilli local supply heavily influences short-term farmgate prices, Pettah wholesale prices reflect national hub aggregation. On held-out testing, LightGBM achieves WAPE = $0.1008$ beating SARIMAX ($0.1323$), with 80% conformal interval coverage.

---

## 3. Data Lineage & Provenance Classifications

In `data/processed/monthly_master.csv`, data fields are partitioned into strictly documented provenance categories:

| Column Group | Provenance | Source Authority | Nature of Data |
| :--- | :--- | :--- | :--- |
| `wholesale_price_rs_kg`, `retail_price_rs_kg` | `real` / `anchor` | CBSL Daily Bulletins & Macro Lab | **Observed daily transactions** averaged monthly (2,455 trading days). |
| `rainfall_mm`, `temp_celsius`, anomalies | `real` | NASA POWER Agro-Climatic Satellite API | **Observed physical satellite grid** point readings. |
| `syn_planted_extent_ha` | `synthetic` / `planned` | DOA Crop Planting Plans (CPP) | **Seasonal targets & plans**, not census actuals. |
| `syn_harvest_volume_mt` | `modelled` | Agronomic Disaggregation Formula | **Calculated formula:** $\text{Extent} \times \text{Yield} \times \text{Window Weight}$. |
| `syn_actual_spi` | `modelled` | Formula Ratio / Difference | **Simulated index** based on modelled supply and population norm demand. |

---

## 4. Multi-Horizon Uncertainty & Conformal Calibration

### 4.1 Coverage vs Horizon Degradation
- **Horizon $t+1$:** LightGBM achieves conformal prediction interval coverage of 80.0% for big onion and chilli wholesale prices on expanding-window walk-forward backtests.
- **Horizons $t+2$ and $t+3$:** Forecast uncertainty compounds due to macroeconomic inflation, currency fluctuations (LKR/USD), and external trade policy adjustments. Conformal bounds expand by $+5\%$ per horizon step to prevent overconfident narrow bands.
- **Operational Rule:** Officers and policy planners must evaluate the P10–P90 spread for horizons $> 1$ month rather than treating the P50 point forecast as deterministic.

### 4.2 Directional Accuracy & Baseline Fallback Rule
- Directional calls (`"up"`, `"down"`, `"flat"`) are computed relative to the previous month's wholesale quote with a $\pm 5\%$ indifference margin.
- If the model's directional hit rate on held-out folds fails to beat the majority-class baseline (e.g. during flat price regimes), the system explicitly flags `direction_reliable = false`.

---

## 5. Decision Optimizer (A4) Assumptions
1. **Lead Time Sensitivity:** GoviSense assumes a standard sea freight lead time of 7 weeks for onion and 6 weeks for chilli from regional ports (Tuticorin, JNPT, Chennai) to Colombo Port, including customs clearance and NPQS phytosanitary inspection.
2. **Storage Constraints:** Sri Lanka's temperature-controlled onion storage capacity is bounded at approximately 15,000 MT across Dambulla, CWE, and private warehouses. If projected surplus exceeds capacity, the system triggers `DELAY` / regional distribution actions rather than `STORE`.
3. **Regret Function:** Linear programming objective optimizes total economic cost in real Sri Lankan Rupees (LKR) rather than dimensionless abstract penalty units.
