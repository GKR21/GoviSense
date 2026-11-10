# Dashboard Task 3: decision history and logging

## Implemented
- History shows the backend decision ID, run ID and checksum in the table and inspector, and exports run IDs in CSV.
- Uses record_hash when supplied; the current history endpoint returns hash, which is retained as a legacy fallback. These fields are not independently verified or assumed to be interchangeable.
- Missing provenance, versions, district, lead time and status are shown as unavailable. Removed invented feed provenance and certification wording. UTC timestamps are explicit.
- Gap options open a review form requiring season, quantity, unit and rationale. No hardcoded 1,200 MT or season is submitted.
- Writes use the authenticated backend officer_id and the original option identifier. Concurrent form submissions are blocked while pending.
- Only a confirmed server receipt shows success. History is loaded from the server after saving; no local record is fabricated. Failed or ambiguous writes remain visible for review.
- Removed leftover broken local-history code in OfficerScreen and restored its existing forecast-query hook.
- CSV export escapes backend text and guards spreadsheet formula prefixes.

## Validation
- Three isolated decision regression tests pass: provenance mapping, exact request/receipt handling, invalid receipts/HTTP errors, filtering and missing fields.
- Vite production build passes.
- TypeScript check remains blocked by pre-existing errors: HEAD has 147 diagnostics; current tree has 118, with no new diagnostic messages compared with HEAD.
- Existing full API suite cannot initialize because website farmerService references undefined initialFarmerProfile. That service was not modified.
- Browser startup initially timed out in the sandbox. The permitted retry confirmed the app fails before rendering because initialFarmerProfile is undefined in the existing website farmer service; therefore the updated decision-form browser assertions could not run.

## Remaining dependencies
- Auth must expose the actual officer_id for the signed-in officer/admin. Username and numeric user ID are not substitutes.
- The current backend history GET exposes hash, while POST separately returns record_hash. Backend ownership must align persisted receipt hashes if identical POST/GET record_hash values are required.
- Actual account/backend verification remains required; test responses are controlled fixtures.
- No Flutter/mobile, backend, database, deployment or signing files were changed.
