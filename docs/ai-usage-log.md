# GoviSense AI Usage & Engineering Audit Log

**Project: GoviSense — Agricultural Forecasting & Prescriptive Decision Support**  
**Team: Team DARKBITE · ModelX 2.0 Phase 1 & 2**  
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
   - **Framework**: `LightGBM` regressor with quantile regression ($10\text{th}$, $50\text{th}$, and $90\text{th}$ percentiles) combined with transparent agronomic accounting ($A \times Y \times (1 - \text{loss})$).
   - **Inputs**: Cumulative rainfall anomalies, solar radiation, temperature variations, historical acreage, and ground farmer declarations.
   - **Output**: Point harvest forecast (metric tons) with $80\%$ uncertainty confidence intervals.
2. **AI 2 — Wholesale Price Forecaster**:
   - **Framework**: Time-series forecasting utilizing `statsmodels` SARIMAX alongside LightGBM quantile regression ensembles and conformal calibration.
   - **Inputs**: Historical wholesale market prices (CBSL & HARTI Pettah / Dambulla DEC), monthly seasonality, and import tariff policies.
   - **Output**: 1-month and 3-month forward wholesale price distributions (Rs/kg), trend direction, and directional confidence.
3. **AI 3 — Supply Pressure Index (SPI) Engine**:
   - **Framework**: Empirical supply-demand balancing algorithm with scenario simulation (e.g. low/expected/high import regimes).
   - **Formula**:
     $$\text{SPI} = \frac{\text{Domestic Forecast Supply} + \text{Planned Imports}}{\text{National Monthly Demand Baseline}}$$
   - **Output**: SPI ratio, deficit/surplus tonnage gap, and risk band classification (`Shortage`, `Balanced`, `Severe Surplus/Glut`).
4. **AI 4 — Prescriptive Optimization & Allocation Engine**:
   - **Framework**: Mixed-Integer Linear Programming (MILP) formulated in `PuLP` and solved with CBC / HiGHS.
   - **Objective**: Maximize collective farmer profitability while constraining aggregate production within sustainable market absorption limits to prevent catastrophic price crashes.
   - **Output**: Optimal target acreage allocations per crop and GN division, farmer Top 3 crop recommendations, and acreage caps.

---

## 2. Generative AI Pair Programming & Interaction Log

| Phase / Item | Date | AI Role | Code & Documentation Scope | Verification Method |
|---|---|---|---|---|
| **Phase 0: Environment & Contracts** | 2026-11-08 | Scaffolding & Schemas | Created `govisense.api.schemas`, strict Pydantic contract definitions, Rule 7 provenance metadata | Pytest API contract suite (`test_api_contract.py`) |
| **Phase 1: Real Data Pipelines** | 2026-11-08 | Data Ingestion Engineering | Implemented `extract_cpp.py` and `extract_cbsl.py` on real PDF gazettes with table parsing; created `data_catalogue` registry and `hand_checked_sample_real.csv` | Agronomic range checks, PDF table verification, 5% review sample error rate < 1% |
| **Phase 2: Models & Optimization** | 2026-11-08 | Algorithmic Implementation | Built A1 fair allocator (HiGHS LP), A2 SARIMAX + conformal 80% interval forecaster, A3 phenology supply engine with adjustable SPI ratios, A4 regret-minimizing decision optimizer | Walk-forward expanding window backtesting; WAPE vs seasonal-naive baseline |
| **Phase 3: Database & Migrations** | 2026-11-09 | Persistence Layer | Implemented 13 SQLAlchemy models, Alembic migrations (`001_initial_schema.py`), modular FastAPI routers in `routes/` | Full Alembic upgrade/downgrade roundtrip test, SQLite/Postgres compatibility |
| **Phase 4: Officer Dashboard** | 2026-11-09 | Frontend Integration | Refactored React officer dashboard (`frontend/src/screens/officer/`): connected live What-If sandbox debounced to `/api/simulate`, SHA-256 decision ledger, and data sources scoreboard | Vite production build, End-to-end component & API tests (`test_phase4_officer_dashboard.py`) |
| **Phase 5: Farmer Mobile Apps** | 2026-11-09 | Mobile & Feedback Systems | Implemented Two-stage ground truth feedback (planting & harvest reports) with disposition constraint check; connected `farmerService` and Flutter `FarmerApiService` to live backend with offline failure honesty | Flutter analyze, Pytest feedback loop suite (`test_phase5_farmer_experience.py`) |
| **Phase 6 & 7: Audit Verification** | 2026-11-09 | Auditing & Compliance | Populated `docs/assumptions.md`, updated `MANUAL_ACTIONS.md`, removed 0-byte files | Full pytest suite pass, clean git tree |

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

1. **Farmer Privacy & Anonymity**: Ground telemetry does not persist national identity card (NIC) numbers or telephone numbers directly in public logs. Data is stored under pseudonymous identifiers (`pseudonymous_id`).
2. **Transparent Algorithmic Governance**: Every API recommendation and decision log persists the exact `run_id`, SHA256 input checksum, `model_version`, and `data_version` to provide a complete audit trail for agricultural officers.
3. **Equitable Multi-Language Access**: All farmer alerts and advisories are rendered trilingually (Sinhala, Tamil, English) to ensure accessibility across all agricultural communities in Sri Lanka.
4. **No Deceptive Fallbacks**: When models operate offline or under default baselines, the system explicitly displays `is_demo: false` with `data_available: false` or offline warning banners rather than fabricating synthetic metrics as live telemetry.
