# Dashboard Task 5: supply chart and overview

Implemented the real-data presentation for the officer supply page and overview.

- The overview KPI cards use the selected crop's backend harvest, demand, gap and wholesale values.
- The supply page presents the backend low/mid/high simulation outputs with supply, demand, gap, SPI ratio and classification.
- The supply-pressure strip only colours a month when the backend returned a matching target period and enough values to calculate SPI. Other months are shown as unavailable instead of using catalogue/mock curves.
- The forecast chart no longer scales a local `supplyMonthly` or `demandMonthly` series. The latest forecast endpoint currently returns one target period, so the UI says that a full monthly series was not supplied.
- Existing light dashboard presentation was preserved; mobile files were not changed.

Verification: TypeScript noEmit passes, Vite production build passes, and the four focused simulation transport tests pass. No full browser run was made for this small data-shape change.
