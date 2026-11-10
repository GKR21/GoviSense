# M-02: Officer API integration

The officer repository calls GET /api/forecasts/latest?crop=big_onion, POST /api/simulate, and POST /api/history/log-action through the authenticated ApiClient.

Supply view plots the server monthly series and shows the selected period, supply, demand, and SPI. The forecast endpoint now filters by crop and supplies up to 12 available monthly model estimates, using the existing harvest model and SPI engine. These are estimates for the most recent data periods, explicitly labelled as historical estimates rather than future projections or out-of-sample validation. A future 12-month forecasting model is outside this change.

What-if inputs send custom_planted_extent_ha and custom_yield_mt_ha. Requests debounce for 350 ms, clear outdated results immediately, and ignore out-of-order responses. Harvest, SPI ratio, and supply gap come directly from the server. Failures expose retry controls and do not substitute demo values.

Import adjustments, storage buffers, and acreage directives record an action type, entered quantity/unit, verified server identity, and available model/data versions. Success requires a server decision_id, run_id, and 64-character record_hash. The ledger displays the full selectable receipt. A failed/ambiguous response directs the user to check the server ledger before retrying. The app does not claim the logging endpoint broadcasts notifications. The ledger lists confirmed actions from this app session; loading previous server history is not included.

The Supply and What-if tab contents were updated for these API results; the existing profile, navigation, timeline and adoption sections remain. Timeline figures are labelled illustrative. Existing local adoption examples are outside M-02 and are not replaced with server adoption telemetry.

Validation includes mobile repository tests for monthly parsing, debounce, out-of-order responses, verified identity/action payloads, request failures, and malformed audit receipts, plus dependency-free Python unit tests for the monthly adapter. Full FastAPI integration and live device verification require a configured backend runtime; FastAPI is not installed in the default Python runtime here. No APK is built for these checks.
