# Dashboard Task 10 — Confidence indicators

Implemented backend-driven confidence indicators in the dashboard.

- The officer header now shows the confidence badge and score returned by `/api/confidence/badge`.
- Demo or synthetic data is clearly labelled when forecast metadata reports it.
- Low-confidence responses show the backend-provided reason; Chilli is explicitly labelled when its SPI confidence is low.
- Confidence failures now show unavailable state instead of invented fallback values.
- No mobile files were changed.

## Verification

- TypeScript type-check passed.
- Production dashboard build passed.
- Focused officer API and decision-history tests passed, including confidence transport/error handling.
