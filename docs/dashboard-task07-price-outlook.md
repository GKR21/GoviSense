# Dashboard Task 7: price outlook

- Farmgate and retail P10/P50/P90 values come from `/api/forecasts/price-outlook`.
- The page shows the backend model name, target period, data quality, data version and data age.
- Baseline status is shown only when the backend explicitly reports baseline metadata; the UI does not infer it from a model name.
- Interval coverage is shown only when the backend supplies a coverage field; otherwise it remains unavailable.
- Chilli has no direction label. Other crops show the backend direction when present.
- Missing intervals and missing metadata remain visible as unavailable values rather than local estimates.
- The restored light dashboard presentation and mobile files were left unchanged.

Verification: TypeScript noEmit and the Vite production build pass. The focused API suite passes 27/27 tests. Full browser testing was skipped to conserve credits.
