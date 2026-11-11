# Dashboard Task 9: data sources

- Data Sources reads the backend `/api/catalogue` response and validates dataset IDs and titles before rendering.
- The table shows the returned title, publisher, licence, temporal coverage, retrieval date, primary source URL and calculated age.
- Age is calculated from the backend retrieval date; missing or invalid dates remain unavailable.
- Source type is displayed only when the backend catalogue supplies it. The UI says “Not supplied by catalogue” instead of inventing a type.
- Refresh only re-fetches the catalogue. No fake ping, latency, sync result, confidence value or synthetic source count is created.
- Preserved the restored light dashboard presentation. No mobile files were changed.

Verification: TypeScript noEmit passes, Vite production build passes, and the focused API suite passes 27/27 tests. Full browser testing was skipped to conserve credits.
