# Heshan: Software Implementation Role

## Data Pipeline
- **P0**: Fix the source label (`download_data.py:171`). 96.4% of rows say real but come from `seed_demo.py`. Use `real`, `anchor`, `interpolated` and `synthetic`, plus an `is_demo` flag, and tell Nayana.
- **P1**: Replace synthetic price, area, yield and import series with real ones: CPP, CBSL, HARTI, WFP and customs imports.
- **P1**: Fix the CPP column-offset alignment, add Sri Lanka national figures, and re-run the 5% hand-check against the real extraction.
- **P1**: Confirm `catalogue.csv` has the `licence` column.

## Backend
- **5. P0**: Replace the hardcoded 64/24/12 adoption counts (`main.py:976-988`) with an explicit `data_available: false` response.
- **6. P0**: Make the API return the hash and run ID (the old `DecisionRecord` dataclass drops them), and bind `model_version` to the running model instead of a fixed string.
- **7. P0**: Add `is_demo`, `data_available` and `source_type` fields to API responses, so the dashboard and app can say what’s real.
- **8. P1**: JWT login with officer, farmer and admin roles. Protect `/api/history/log-action`, `/api/database/init`, `/api/feedback/retrigger` and `/api/simulate`. Replace the wildcard CORS with listed origins.
- **9. P1**: Add the endpoints Rashmika needs: catalogue, adoption summary, decision list with hash and run ID, and run info.
- **10. P1**: Alerts backend: `routes/alerts.py`, `i18n/templates.json` in English, Sinhala and Tamil, `/api/alerts` and an acknowledge endpoint.
- **11. P1**: Replace `@app.on_event` with lifespan (`main.py:81`), split `main.py` into routes, and fill or delete `deps.py`, `schemas.py` and the empty route files.
- **12. P1**: Farmer ID checks: rate limit and duplicate-report handling, and a documented note that registry verification is future work.

## Mobile App
- **13. P0**: Remove the fake success receipt (`farmer_repository.dart:346-373`). On a failed submit, save the report as “pending” and retry, and tell the farmer.
- **14. P1**: Show a clear banner when recommendations come from the offline `_initialCrops`.
- **15. P1**: Verify the market prices screen reads the API, and wire it if not.
- **16. P1**: Build the alert inbox with Acknowledge and Ask an officer, and check that every screen is translated.
- **17. P1**: Check the two-stage form (planting and harvest reports) matches the schema.

## Quality
- **18. P1**: TestClient tests for each endpoint, bad-input and concurrency tests (20 parallel reports), and a data-validation test on the source label.
- **19. P2**: Fill `.github/workflows/ci.yml`, `docker-compose.yml`, `Makefile`, `.env.example`, `docs/assumptions.md` and `docs/ai-usage-log.md`.
- **20. P1**: Run the unverified checks: auth, CORS, alerts, and the mobile prices screen.
