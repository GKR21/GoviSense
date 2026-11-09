# GoviSense AI Usage & Engineering Audit Log

**Project: GoviSense — Agricultural Forecasting & Prescriptive Decision Support**  
**Team: Team DARKBITE · ModelX 2.0 Phase 2**  
**Documentation Version: 2.0.0**  
**Last Updated: November 2026**

---

## 1. System AI Architecture Overview

GoviSense embeds four specialized, interoperable AI modules designed to transform raw agro-climatic and market indicators into timely, actionable farmer advisories and policy recommendations:

```
┌─────────────────────────┐       ┌─────────────────────────┐
│   AI 1: Harvest Model   │       │   AI 2: Price Forecast  │
│  LightGBM Yield Predict │       │ Auto-ARIMA / Statsmodels│
└────────────┬────────────┘       └────────────┬────────────┘
             │                                 │
             └───────────────┬─────────────────┘
                             ▼
              ┌─────────────────────────────┐
              │    AI 3: Supply Pressure    │
              │     Index (SPI) Engine      │
              └──────────────┬──────────────┘
                             ▼
              ┌─────────────────────────────┐
              │     AI 4: Prescriptive      │
              │  Optimization Engine (PuLP) │
              └─────────────────────────────┘
```

### Module Specifications:
1. **AI 1 — Harvest & Production Forecaster**:
   - **Framework**: `LightGBM` regressor with quantile regression ($10\text{th}$, $50\text{th}$, and $90\text{th}$ percentiles).
   - **Inputs**: Cumulative rainfall anomalies, solar radiation, temperature variations, historical acreage, and ground farmer declarations.
   - **Output**: Point harvest forecast (metric tons) with $80\%$ uncertainty confidence intervals.
2. **AI 2 — Wholesale Price Forecaster**:
   - **Framework**: Time-series forecasting utilizing `statsmodels` SARIMAX alongside LightGBM baseline ensembles.
   - **Inputs**: Historical wholesale market prices (CBSL & HARTI Pettah / Dambulla DEC), monthly seasonality, and import tariff policies.
   - **Output**: 1-month and 3-month forward wholesale price distributions (Rs/kg), trend direction, and directional confidence.
3. **AI 3 — Supply Pressure Index (SPI) Engine**:
   - **Framework**: Empirical supply-demand balancing algorithm with scenario simulation (e.g. low/expected/high import regimes).
   - **Formula**:
     $$\text{SPI} = \frac{\text{Domestic Forecast Supply} + \text{Planned Imports}}{\text{National Monthly Demand Baseline}}$$
   - **Output**: SPI ratio, deficit/surplus tonnage gap, and risk band classification (`Shortage`, `Balanced`, `Severe Surplus/Glut`).
4. **AI 4 — Prescriptive Optimization & Allocation Engine**:
   - **Framework**: Mixed-Integer Linear Programming (MILP) formulated in `PuLP` and solved with CBC.
   - **Objective**: Maximize collective farmer profitability while constraining aggregate production within sustainable market absorption limits to prevent catastrophic price crashes.
   - **Output**: Optimal target acreage allocations per crop and GN division, farmer Top 3 crop recommendations, and acreage caps.

---

## 2. Generative AI Pair Programming & Development Log

During the implementation of ModelX 2.0 Phase 2, modern AI coding agents (Google DeepMind Antigravity / Gemini 2.5) were utilized as pair-programming assistants under human architectural oversight.

### Engineering Scope of AI Assistance:
- **Data Digitization & Extraction**:
  - Automated regex and tabular parsing logic (`pdfplumber` / `pdfminer.six`) for Central Bank of Sri Lanka (CBSL) and Department of Agriculture Cost of Cultivation (CPP) seasonal PDFs.
  - Column offset normalization and automated 5% hand-check sample audit framework.
- **Backend Modularization & RBAC**:
  - Migration of monolithic `@app.on_event` startup routines to asynchronous FastAPI `lifespan` architecture.
  - Creation of JWT authentication module (`auth.py`) implementing HS256 encryption, access/refresh token rotation, and bcrypt password hashing.
  - Implementation of route-level Role-Based Access Control (RBAC) separating `farmer`, `officer`, and `admin` permissions.
- **Mobile Integration & Offline Resilience**:
  - Flutter / Dart client refactoring to replace optimistic mock receipts with a robust two-stage local queue (`pending` -> `verified`).
  - Implementation of offline recommendation fallback indicators and live DEC market prices feed integration.
  - Trilingual translation integration across English, Sinhala, and Tamil.
- **Test-Driven Quality Verification**:
  - Synthesis of comprehensive test suites (`test_task_18_comprehensive_quality.py`, `test_auth_and_rbac.py`, `test_extract.py`, etc.) totaling 103 automated tests covering 20 parallel thread concurrency, bad-input handling, and data provenance constraints.

---

## 3. Human-in-the-Loop Verification Checkpoints

All code and algorithmic logic generated or suggested by AI tools underwent rigorous human review and automated validation:

| Verification Stage | Methodology | Verification Result |
| :--- | :--- | :--- |
| **Data Integrity** | Hand-check audit of 5% sample digitized against original physical CBSL and CPP records | Error rate achieved $\le 10.0\%$ (Task 3 & Task 18 verified) |
| **Provenance Truthfulness** | 4-tier taxonomy audit (`real`, `anchor`, `interpolated`, `synthetic`) across `monthly_master.csv` | Zero misleading "real" flags on synthetic demo seeds |
| **Concurrency Safety** | Multi-threaded stress testing (20 concurrent workers submitting planting reports) | 100% database lock prevention via SQLite WAL mode |
| **Security & RBAC** | Penetration simulation against protected officer and database administration routes | 401 Unauthorized / 403 Forbidden properly enforced on all invalid calls |
| **Offline Resilience** | Network disconnect simulation in Flutter client | Graceful fallback banner displayed; pending queue retried upon reconnect |

---

## 4. Ethical Considerations, Fairness & Data Privacy

1. **Farmer Privacy & Anonymity**:
   - Ground telemetry does not persist national identity card (NIC) numbers or telephone numbers directly in public logs. Data is stored under pseudonymous identifiers (`pseudonymous_id`).
2. **Transparent Algorithmic Governance**:
   - Every API recommendation and decision log persists the exact `run_id`, SHA256 input checksum, `model_version`, and `data_version` to provide a complete audit trail for agricultural officers.
3. **Equitable Multi-Language Access**:
   - All farmer alerts and advisories are rendered trilingually (Sinhala, Tamil, English) to ensure accessibility across all agricultural communities in Sri Lanka.
4. **No Deceptive Fallbacks**:
   - When models operate offline or under default baselines, the system explicitly displays `is_demo: false` with `data_available: false` or offline warning banners rather than fabricating synthetic metrics as live telemetry.

