# Dashboard Task 8: adoption

- The adoption page reads observed summary data from `/api/adoption/summary`, simulation scenarios from `/api/simulation/adoption`, and privacy-filtered reports from `/api/feedback/ground-reports`.
- `data_available: false` is shown as an explicit telemetry-unavailable state with the backend message, quality and source metadata. The page does not turn backend zero/no-data responses into fake counts.
- Simulation rows show the backend adoption rate, supply, demand, SPI label and farmgate price, with the backend conclusion when supplied.
- Ground-report privacy suppression is shown with the backend cohort count; individual reports remain hidden when the backend suppresses them.
- Refresh retries all three backend requests. Loading, error and empty states remain separate.
- Preserved the restored light dashboard presentation. No mobile files were changed.

Verification: TypeScript noEmit passes, Vite production build passes, and the focused API suite passes 27/27 tests. Full browser testing was skipped to conserve credits.
