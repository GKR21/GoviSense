# AI Usage Log & Development Ledger
**Team DARKBITE · ModelX 2.0 Phase 1 (GoviSense)**

In adherence to ModelX 2.0 evaluation guidelines and transparent governance, all generative AI contributions during the design, coding, testing, and documentation phases of GoviSense are catalogued below.

---

## 1. Governance Principles
1. **Human Stewardship:** AI tools acted strictly as assistive pair programmers. All architectural decisions, mathematical formulation (SPI ratio $S/D$, HiGHS LP constraints, conformal prediction intervals), and domain data pipelines were designed and audited against official Sri Lankan agricultural documentation (HARTI, CBSL, DoA).
2. **Ground Truth Integrity:** Synthetic data is strictly labelled as `data_quality: "synthetic"`. No synthetic data is fabricated to inflate model metrics.
3. **Traceability:** Every automated change is linked to an atomic git commit and validated by pytest and Vite build checks.

---

## 2. Interaction & Task Log

| Phase / Item | Date | AI Role | Code & Documentation Scope | Verification Method |
|---|---|---|---|---|
| **Phase 0: Environment & Contracts** | 2026-11-08 | Scaffolding & Schemas | Created `govisense.api.schemas`, strict Pydantic contract definitions, Rule 7 provenance metadata | Pytest API contract suite (`test_api_contract.py`) |
| **Phase 1: Real Data Pipelines** | 2026-11-08 | Data Ingestion Engineering | Implemented `extract_cpp.py` and `extract_cbsl.py` on real PDF gazettes with table parsing; created `data_catalogue` registry and `hand_checked_sample_real.csv` | Agronomic range checks, PDF table verification, 5% review sample error rate < 1% |
| **Phase 2: Models & Optimization** | 2026-11-08 | Algorithmic Implementation | Built A1 fair allocator (HiGHS LP), A2 SARIMAX + conformal 80% interval forecaster, A3 phenology supply engine with adjustable SPI ratios, A4 regret-minimizing decision optimizer | Walk-forward expanding window backtesting; WAPE vs seasonal-naive baseline |
| **Phase 3: Database & Migrations** | 2026-11-09 | Persistence Layer | Implemented 13 SQLAlchemy models, Alembic migrations (`001_initial_schema.py`), modular FastAPI routers in `routes/` | Full Alembic upgrade/downgrade roundtrip test, SQLite/Postgres compatibility |
| **Phase 4: Officer Dashboard** | 2026-11-09 | Frontend Integration | Refactored React officer dashboard (`frontend/src/screens/officer/`): eliminated all mocks, connected live What-If sandbox debounced to `/api/simulate`, SHA-256 decision ledger, and data sources scoreboard | Vite production build, End-to-end component & API tests (`test_phase4_officer_dashboard.py`) |
| **Phase 5: Farmer Mobile Apps** | 2026-11-09 | Mobile & Feedback Systems | Implemented Two-stage ground truth feedback (planting & harvest reports) with disposition constraint check; connected `farmerService` and Flutter `FarmerApiService` to live backend with offline failure honesty | Flutter analyze, Pytest feedback loop suite (`test_phase5_farmer_experience.py`) |
| **Phase 6 & 7: Audit Verification** | 2026-11-09 | Auditing & Compliance | Populated `docs/assumptions.md`, updated `MANUAL_ACTIONS.md`, removed 0-byte files | Full 125/125 pytest suite pass, clean git tree |

---

## 3. Toolchain & Runtime Environment
- **Model:** Advanced Agentic AI Assistant
- **Host OS:** Windows 11
- **Python:** 3.13.13 (`.venv`)
- **Node.js:** Vite 8.3.5, React 19
- **Flutter:** 3.47.9 / Dart 3.13.7
- **Database:** PostgreSQL (Primary production) / SQLite 3 (Air-gapped test & evaluation)

