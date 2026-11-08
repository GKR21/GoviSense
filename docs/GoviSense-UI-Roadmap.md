# GoviSense — Farmer & Officer UI Roadmap (A–Z)

**Project:** GoviSense (ModelX 2.0 · Phase 1, Team Darkbite)
**Scope:** Dual-platform architecture:
1. **Flutter Mobile App (`mobile/`)**: Primary mobile field client for both **Farmer** (mobile-first, trilingual: Sinhala / Tamil / English) and **Officer** (mobile field dashboard: supply charts, what-if sliders, gap deadlines, and adoption tracking).
2. **React Web App (`frontend/`)**: Responsive web PWA with role-based routing for desktop planning and cross-platform access.
**Legend:** ★ = part of the minimum demo slice (must exist for the demo)

> **Time check:** The proposal sets feature freeze on 7 Nov and demo on 7–9 Nov. If that deadline still holds, only ★ phases are realistic. Everything else is the post-demo path.

---

## Phase 0 — Decisions that unblock everything (½ day) ★

- [ ] Define SPI precisely and show its scope on screen. National big-onion SPI would sit near 0.26 (local supply ≈ ¼ of the 320,000 t requirement), so decide: local-addressable demand, or demand net of baseline imports.
- [ ] Lock roles: Farmer, Officer, Admin.
- [ ] Lock languages: English, Sinhala, Tamil.
- [ ] Separate brand colour from semantic colours (brand green vs "Balanced" green currently collide).
- [ ] Agree the data contract: `crop, district, month, supply_low/mid/high, demand, spi, confidence, data_version, run_id, provenance (plan | reported)`.

**Exit:** a one-page spec signed off by all four members.

---

## Phase 1 — Design system (1 day) ★

**Tokens**
- Colour: warm paper background (~#F6F4EE), forest-ink hero surfaces, one brand accent, reserved semantic colours (shortage, balanced, oversupply, info).
- Type: Inter + Noto Sans Sinhala + Noto Sans Tamil; 16px minimum body; ~1.6 line height for Sinhala/Tamil; tabular numerals for data.
- Spacing: 8pt grid. Radii: 8 / 12 / 20–24. Layered soft shadows. Motion with reduced-motion support.

**Components**
- Button, icon button, select, toggle, tabs, chips
- Card, KPI tile, range bar (low–mid–high), pressure ribbon (12 months), supply band chart
- Risk badge, confidence badge, provenance tag (Plan / Farmer-reported), demo-data ribbon
- Bottom sheet, stepper, toast, skeleton, empty / error / outdated / permission-denied states

**Rules**
- Never rely on colour alone: colour + icon + label.
- Farmer risk wording is perspective-aware: "Prices likely firm" vs "Prices may fall at harvest" (not shortage/oversupply).
- 48px minimum touch targets.

**Exit:** a component gallery rendering correctly in all 3 languages.

---

## Phase 2 — Information architecture & flows (½ day) ★

**Farmer flow**
`Onboarding (language + consent) → Home → Compare top-3 → Crop detail → Report planting → Confirmation → Alerts → Profile`

**Officer flow**
`Login → Overview (SPI ribbon) → Crop/month drill-down → Gap timeline + deadlines → What-if sheet → Record decision → Decision history → Adoption → Data sources → Settings`

**Exit:** a clickable flow map with the cut list marked.

---

## Phase 3 — Mock data & service layer (½ day) ★

- Typed mock API built from real Crop Production Programme figures (e.g. Anuradhapura big onion: 2,131 ha → 35,051 t ≈ 16.45 t/ha).
- All screens call a `services/` layer, never inline constants, so swapping to FastAPI later is a one-file change.
- Label all demo data as sample data.

**Exit:** every screen reads from the service layer.

---

## Phase 4 — Farmer app build (1.5 days) ★ [COMPLETED]

| Screen | Key content | Status |
|---|---|---|
| Onboarding | Language choice, consent checkbox, district, land size | Completed (Trilingual EN/SI/TA) |
| Home | Harvest-window ribbon, key alert, shortcut to compare | Completed |
| Compare top-3 | Swipeable cards: profit range, risk, water need, planting window, harvest period, market pressure, confidence badge; "Why these three?" sheet | Completed |
| Crop detail | Profit range bar, calendar, water need, market pressure at harvest, provenance | Completed |
| Report planting | Planned vs actual area, harvest, sale outcome (pseudonymous ID, aggregate-only) | Completed |
| Confirmation | Recorded + versioned feedback, digital cultivation receipt | Completed |
| Alerts | Inbox with Acknowledge and Ask an officer | Completed |
| Profile | Language, district, consent, offline/data status, prototype states | Completed |

**Exit:** the full flow works at 390×844 in all 3 languages (English, Sinhala, Tamil) with a dedicated service layer and smart mobile palette.

---

## Phase 5 — Officer app build (1.5 days) ★

| Screen | Key content |
|---|---|
| Login | Role-based entry |
| Overview | KPI tiles, SPI ribbon (red/amber/green), supply band chart with touch month selection |
| Gap timeline | Gap ranges, decision deadlines (month start − import lead time), options: import now / later / delay / store |
| What-if | Area and yield sliders in a bottom sheet, chart updates instantly |
| Decision record | Save decision with run ID, data version, assumptions |
| History | Decision and run log |
| Adoption | Recommended vs reported area; predicted vs actual |
| Data sources | Source, date, licence, confidence/outdated badges |
| Settings | Adjustable assumptions (SPI bands, import lead time) |

**Exit:** an officer can spot a risk month, change area/yield, and record a decision.

---

## Phase 6 — Feedback loop (½ day) ★

- A farmer planting report updates the officer's supply chart and adoption page.
- Alerts flow from officer decisions to the farmer inbox.
- This is the headline demo moment — protect it.

**Exit:** report in farmer app → visible change in officer chart.

---

## Phase 7 — Quality layer (1 day)

- Loading, empty, error, outdated-data, permission-denied states on every screen.
- Accessibility: contrast, focus order, screen-reader labels, reduced motion.
- PWA: manifest, service worker, honest offline banner (shows last-good data age).
- Sinhala/Tamil overflow and line-height checks.
- Replace remote crop photos with bundled assets for offline use.

---

## Phase 8 — Testing & validation (1 day)

- Unit tests: SPI, decision deadline, what-if formulas.
- Component tests for state variants; one smoke test per flow.
- Real-device checks: low-end Android and a small iPhone.
- 5–10 quick usability sessions with farmers and agrarian officers (matches the proposal's evaluation plan).

---

## Phase 9 — Freeze & demo (½ day) ★

**Demo script**
1. Officer sees an oversupply month on the ribbon.
2. Officer changes planted area and watches SPI shift.
3. Decision deadline appears; officer records a decision.
4. Farmer sees a balanced top-3 and reports planting.
5. Officer's chart updates from the farmer report.

Deliverables: screenshots, screen recording, README with run steps. Bug fixes only.

---

## Phase 10 — Production path (post-demo)

- Connect FastAPI, real auth and roles.
- Persist run/version history.
- Store farmer reports with pseudonymous IDs.
- CI/CD with GitHub Actions; error monitoring.

---

## Cut order if time runs short

1. In-app alerts
2. Adoption tracker (reduce to one form + one chart)

**Never cut:** supply pressure view, gap timeline, optimizer output/comparison view, confidence indicator, decision history.

---

## Suggested repo structure

```
src/
  tokens/          colours, type, spacing, motion
  i18n/            en.ts, si.ts, ta.ts
  components/      shared UI (badges, charts, sheets, states)
  screens/
    farmer/
    officer/
  services/        API layer (mock now, FastAPI later)
  mocks/           typed sample data from official tables
  tests/
```

Refactor the current single-file `App.tsx` into this during Phases 1–3.

---

## Open items to confirm

- [ ] Real demo deadline (drives day-by-day scheduling)
- [ ] SPI scope and demand definition (Phase 0)
- [x] Mobile scope locked: Both Farmer and Officer experiences built in `mobile/` (Flutter) with role-based navigation.
- [ ] Owner per phase (map to roles A–D from the proposal)
