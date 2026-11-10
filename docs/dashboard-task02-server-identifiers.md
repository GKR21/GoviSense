# Dashboard task 02 — server identifiers and receipts

Removed browser-generated decision/run/report IDs, the hardcoded decision hash,
the fabricated REC-* receipt strings and the sample receipt fallback. Successful
submissions now require an accepted HTTP response, the expected status, actual
server identifiers and (where applicable) a 64-character hexadecimal checksum.
Failed, malformed or incomplete acknowledgements show an error instead of
creating a local success record or claiming offline acceptance.

OfficerScreen displays the returned decision_id, run_id and record_hash after
acceptance. History accepts only rows with server decision IDs, preserves valid
backend checksums, displays unavailable checksums honestly and disables copying
an absent checksum. Its checksum count is computed rather than claiming 100%.
Full decision-ledger/write-payload alignment remains task 03.

The website farmer service now obtains identity from authenticated /api/auth/me.
It accepts only explicit pseudonymous_id/farmer_id or officer_id fields for the
appropriate role. A generic login/user id, username, display name or locally
edited profile is not substituted for a domain identifier. The hardcoded farmer
profile ID and anonymous-ID defaults were removed. Crop IDs are preserved from
backend recommendations; the bundled fallback crop list was removed. Unused
local officer-decision/alert generation was deleted.

Farmer report IDs and receipt checksums are copied from the accepted response;
there is no fabricated pending receipt or automatic-sync claim. The success
screen requires a confirmed receipt, and identity-less submissions have a
visible failure state. This is still an acknowledgement/checksum check, not
independent verification of the hash or government registration.

Task 01 already removed the Data Sources mock ping/sync controls and their
random latency values. A source scan now finds no Math.random, randomUUID,
Date.now-generated IDs, known fake identifier defaults or sample receipt hashes
under frontend/src. Test fixtures retain deliberately artificial identifiers.

## Verification

- `npm.cmd --prefix frontend test`: 27 tests pass, covering server identity,
  exact receipt preservation, missing/invalid IDs and checksums, HTTP/network
  failures, no fabricated reports, and the existing task 01 API reads.
- `tsc --project frontend/tsconfig.json --noEmit`: passes. The farmer service now
  uses the existing canonical profile fields and verified report status, fixing
  the ten diagnostics recorded during task 01.
- `npm.cmd --prefix frontend run build`: production Vite build passes.
- `npm.cmd --prefix frontend run test:browser`: controlled headless Edge checks
  pass, including no success on missing actor ID, HTTP 503 or malformed receipt,
  and unchanged display of actual server receipt fields on success. All task 01
  screen/read/retry/race checks still pass without uncaught browser exceptions.

## Backend dependency — blocked

The current backend UserProfile schema at /api/auth/me does not expose
pseudonymous_id/farmer_id or officer_id. The backend/auth owner needs to provide
these actual identifiers from the existing user/profile tables, bound to the
authenticated identity. Until then, dependent writes intentionally stop with an
identity-unavailable error; the client does not generate a replacement ID.
No backend/auth schema, database or Flutter files were changed. Browser tests
use fixtures and do not establish hosted-service or real-account readiness.

Other existing agronomic defaults, decision quantity/season handling, model
metadata, login/role integration and report workflow refinements are outside
this identifier task and still require their respective assigned tasks.
