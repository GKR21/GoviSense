# Dashboard task 01 — API reads

Implemented the first item in Rashmika's website/dashboard assignment. No Flutter,
backend, database schema, deployment or APK changes are included.

## Connected screens

| Screen | Endpoint(s) |
| --- | --- |
| Overview | GET /api/forecasts/latest |
| Price Outlook | GET /api/forecasts/price-outlook |
| Gap Timeline | GET /api/forecasts/gap-timeline |
| History | GET /api/history/decisions |
| Adoption | GET /api/adoption/summary, /api/simulation/adoption, /api/feedback/ground-reports |
| Data Sources | GET /api/catalogue |

These reads go through api.ts. Same-origin query URLs now resolve correctly
when VITE_API_URL is unset; stored bearer credentials are attached to the
dashboard requests. A failed read throws an error instead of returning bundled
forecast/adoption numbers. Collection responses are checked before consumption.
Empty responses remain empty rather than keeping old records.

App.tsx no longer reads or writes govisense_ground_reports in localStorage or
supplies local reports to the officer workspace. There was already no active
INITIAL_GROUND_REPORTS or mocks/officerData import in this checkout; the
remaining localStorage restoration has now been removed. Adoption uses the
server ground-report endpoint directly; History no longer merges local session
entries into the server ledger.

The mock-heavy forecast, price, timeline, adoption and catalogue panels were
replaced with server-backed cards/tables in the existing workspace. The client
does not manufacture heat maps, monthly gap charts, retail multipliers, catalogue
feeds, latency measurements or adoption counts for these screens. Those richer
visuals require the later assigned tasks and actual endpoint fields. Missing
numbers display Not available, including legitimate null price intervals; zero
is retained. Simulated adoption is labelled separately from observed telemetry.

Each query has loading, failure, empty and retry states. Refresh and filter
changes clear previous results; an older response cannot overwrite a newer
request. One failing adoption endpoint does not substitute data for the others.

## Verification

- `npm.cmd --prefix frontend test`: 12 API regression tests pass. They exercise
  actual client functions with controlled HTTP responses, same-origin URL and
  token handling, filters, empty collections, network/503 failures, malformed
  JSON and preservation of actual values.
- `npm.cmd --prefix frontend run build`: production Vite build passes.
- `npm.cmd --prefix frontend run test:browser`: headless Edge checks all six
  screens, initial loading, server values, null values, unavailable adoption,
  failure/retry recovery, empty results and out-of-order crop requests. No
  uncaught browser exceptions. Run the build first. Set CHROMIUM_PATH when Edge
  is not at the default Windows location. Profiles stay in ignored .cache.
- Full `tsc --project frontend/tsconfig.json --noEmit` remains blocked by ten
  pre-existing farmerService.ts diagnostics: profile-field mismatches,
  unsupported season query input, implicit callback type and pending versus
  pending_sync. A read-only compiler overlay of HEAD reproduced these errors
  plus three original API/officer errors (13 total); those three are now fixed.

Browser tests use fixtures under frontend/tests, not a hosted service. The owner
confirmed that the backend is not hosted; deployment, real-data availability
and backend correctness are not established by these checks.

## Remaining assignment

This does not complete tasks 02–14. Decision submission/receipt integrity,
simulation sliders, supply charts, full A4 deadline behavior, model selection
and coverage labels, confidence/demo handling, JWT role gates, cleanup and the
evaluation view still need their respective tasks. In particular, the existing
OfficerScreen decision-write path still needs task 03; connecting read endpoints
does not certify its write behavior. Source age/type is displayed only when
supplied by the catalogue; retrieval date is not claimed to be observation age.
