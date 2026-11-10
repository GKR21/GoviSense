# Dashboard Task 4: area/yield simulation

## Changes
- Added SimulationScreen for the Supply pressure page. Area/yield controls start from the backend response, explicitly described as possible model defaults, not observed farm data.
- POST /api/simulate uses the stored bearer token and exact crop, area and yield inputs. Changes are debounced by 300 ms; obsolete responses cannot overwrite newer inputs. A changed request immediately hides previous results.
- Low, mid and high cards show the returned supply, demand, gap, SPI ratio and classification. Zero values remain zero; missing scenarios or numbers remain unavailable.
- Loading, retry, reset, demo and backend-error states are explicit. No fabricated offline simulation or local supply formula is used.
- Removed the mock monthly chart and its fake provenance/confidence from this page, plus the unused assumptions drawer with nonfunctional sliders. The real monthly forecast chart remains Task 5.
- Removed fake Save scenario controls: the simulation endpoint does not provide persistence.
- Vite development and preview /api proxies now target https://govisense-production.up.railway.app with changeOrigin. GOVISENSE_BACKEND_URL can override the proxy target. Restart Vite to load the changed proxy configuration. Production static hosting still needs its own /api proxy or VITE_API_URL at build time.
- The endpoint accepts no district or season filter; the simulation page states that limitation.

## Verification
- Seven focused tests pass (four simulation tests and three decision-history regression tests).
- Production Vite build passes.
- TypeScript remains blocked by existing project errors (118 diagnostics at HEAD). Final checking reports no diagnostics in OfficerScreen or SimulationScreen; obsolete slider setters found during validation were removed.
- Full-app browser testing remains blocked by the existing website farmerService initialFarmerProfile startup error documented in Task 3. No successful interactive UI test is claimed.
- Live schema request to the supplied Railway host returned HTTP 502, Application failed to respond. The implementation follows the repository officer router contract; live authenticated simulation remains unverified.

## Scope
No mobile, farmer-service, backend or database files were modified. Existing mocks elsewhere in the dashboard remain for their corresponding tasks.
