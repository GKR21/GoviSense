# Dashboard Task 6: gap timeline

The gap timeline now consumes the backend A4 response directly.

- Decision deadline, remaining days, target period, lead time and best/mid/worst gaps are displayed from `/api/forecasts/gap-timeline`.
- Backend options retain their IDs, labels, feasibility, lead time and capacity. No local option list or deadline is created.
- The decision form records the selected backend option and still requires the officer to enter the real season, quantity, unit and rationale before logging it.
- Invalid timeline responses are rejected instead of rendering partial or invented deadline data.
- The existing light dashboard presentation is preserved. No mobile files were changed.

The A4 endpoint currently derives its deadline from the requested lead time and exposes the options in the `timelines[].options` array. A backend change is still needed if the product requires a different deadline policy or richer option quantities.

Verification: TypeScript noEmit passes, Vite production build passes, and the focused API suite passes 27/27 tests. No full browser run was repeated to conserve credits.
