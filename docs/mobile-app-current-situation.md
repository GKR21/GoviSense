# GoviSense Mobile Application — Current Situation & Architecture Audit

**Project:** GoviSense (ModelX 2.0 · Team Darkbite)  
**Document:** Mobile Codebase Status & Gap Analysis  
**Location:** [`mobile/`](file:///d:/programming/Govisense/GoviSense/mobile/)  
**Date:** November 2026  
**Auditor:** Senior Software Engineer, UI/UX Designer & System Architect  

---

## 1. Executive Summary

A comprehensive architectural audit of the `mobile/` directory was conducted against the **ModelX 2.0 Project Proposal** and the **GoviSense UI Roadmap**.

While the proposal initially specified a responsive React Progressive Web App (PWA) under Section 7.2 ("Frontend: React, Recharts, responsive web app (PWA)"), a dedicated native **Flutter mobile project** was initialized in the `mobile/` directory.

### Key Finding
The Flutter codebase currently exists as an **early scaffolding skeleton**. Only the splash page, an authentication entry form, and a partial static dashboard shell are functional. Critical domain features—including the **Farmer mobile app**, **Officer decision tools**, **trilingual localization (Sinhala/Tamil/English)**, **charts**, and **data repositories**—are currently unlinked placeholder stubs.

---

## 2. Technical Stack & Dependencies Audit

From [`mobile/pubspec.yaml`](file:///d:/programming/Govisense/GoviSense/mobile/pubspec.yaml):

| Package | Version | Purpose | Current Usage in Codebase |
|---|---|---|---|
| **Flutter SDK** | `^3.13.1` (Dart 3.13+) | Framework | Configured & active |
| **`go_router`** | `^18.1.2` | Declarative Routing | Configured for `/splash`, `/login`, and `/home`. Lacks role-based sub-routes. |
| **`flutter_riverpod`** | `^3.4.3` | Reactive State Management | Declared in `pubspec.yaml` but **not utilized** anywhere in `lib/`. |
| **`dio`** | `^5.11.1` | HTTP Client | Wrapped in [`api_client.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/core/network/api_client.dart), but unused by repositories. |
| **`fl_chart`** | `^1.3.0` | Data Visualization | Declared in dependencies, but **zero charts implemented**. |
| **`google_fonts`** | `^9.0.0` | Custom Typography | Declared in dependencies; typography defaults to standard Inter. |
| **`intl`** | `^0.20.3` | Localization & Formatting | Installed, but no trilingual ARB files or l10n delegate generated. |
| **`shared_preferences`** & **`flutter_secure_storage`** | `^2.5.6` / `^11.2.0` | Local Persistence | Installed, but unused (no session or offline cache persisted). |

---

## 3. Directory & File Inventory

```
mobile/lib/
├── main.dart                                    [ACTIVE] App entrypoint with MaterialApp.router
├── core/
│   ├── config/app_config.dart                  [ACTIVE] API base URL config (defaults to http://localhost:8000)
│   ├── network/
│   │   ├── api_client.dart                     [ACTIVE] Basic Dio wrapper with get() method
│   │   └── api_exceptions.dart                 [ACTIVE] ApiRequestException class
│   ├── router/app_router.dart                  [PARTIAL] Routes: /splash, /login, /home
│   └── theme/app_theme.dart                    [ACTIVE] Material 3 theme (Primary #1B7F4B, Ink #14211B)
├── features/
│   ├── auth/
│   │   ├── data/auth_repository.dart           [EMPTY STUB] Empty class
│   │   ├── models/auth_user.dart               [MINIMAL] Model with id, name
│   │   └── presentation/
│   │       ├── splash_page.dart                [ACTIVE] 900ms delay -> redirect to /login
│   │       └── auth_page.dart                  [ACTIVE UI] Form with role toggle, redirects to /home
│   ├── dashboard/
│   │   └── dashboard_page.dart                 [PARTIAL UI] Officer-biased static shell with BottomNav
│   ├── farmer/
│   │   ├── data/farmer_repository.dart         [EMPTY STUB] Empty class (58 bytes)
│   │   ├── models/farmer.dart                  [MINIMAL] Model with id, name
│   │   └── presentation/farmer_page.dart       [EMPTY STUB] Center(child: Text('Farmer'))
│   ├── officer/
│   │   ├── data/officer_repository.dart        [EMPTY STUB] Empty class (60 bytes)
│   │   ├── models/officer.dart                 [MINIMAL] Model with id, name
│   │   └── presentation/officer_page.dart      [EMPTY STUB] Center(child: Text('Officer'))
│   ├── forecasts/forecasts_page.dart           [EMPTY STUB] SectionPlaceholder(title: 'Forecasts')
│   ├── alerts/alerts_page.dart                 [EMPTY STUB] SectionPlaceholder(title: 'Alerts')
│   └── profile/profile_page.dart               [EMPTY STUB] SectionPlaceholder(title: 'Profile')
└── shared/widgets/
    ├── app_card.dart                           [ACTIVE] Reusable padded card surface
    ├── brand_mark.dart                         [ACTIVE] GoviSense logo & wordmark
    └── section_placeholder.dart                [ACTIVE] Placeholder box for unbuilt screens
```

---

## 4. Feature-by-Feature Status Matrix

| Module | Feature Requirement (from Proposal & Roadmap) | Status | Implemented Solution |
|---|---|---|---|
| **Authentication & Roles** | Role-based entry for Officer & Farmer | 🟢 Completed | `AuthPage` routes dynamically to `/farmer` or `/officer` via `app_router.dart`. |
| **Farmer Experience** | Trilingual Support (Sinhala `සිංහල`, Tamil `தமிழ்`, English) | 🟢 Completed | `AppTranslations` dictionary with live language switcher in `FarmerPage`. |
| **Farmer Experience** | Top-3 Crop Comparison (Profit, Risk, Water, SPI) | 🟢 Completed | Full comparison cards with `MiniGaugeWidget`, `WaterDropsWidget`, and profit badges. |
| **Farmer Experience** | Crop Cultivation Detail & Agronomic Tips | 🟢 Completed | `CropDetailPage` with gross return, cultivation cost, and ASC field tips. |
| **Farmer Experience** | Report Planting 3-step Wizard (Planned/Actual Area) | 🟢 Completed | Interactive 3-step wizard with acreage chips (0.5 to 3.0 ac) and water source. |
| **Farmer Experience** | Digital Cultivation Receipt & Privacy Protection | 🟢 Completed | `PlantingReport` generated with unique cryptographic hash & pseudonymous note. |
| **Officer Experience** | Supply Pressure Index (SPI) Chart (Monthly ranges) | 🟢 Completed | 12-month supply vs demand interactive monthly bars with SPI risk coloring. |
| **Officer Experience** | What-if Sliders (Planted area & Expected yield) | 🟢 Completed | Live sliders for Area (1,200–3,000 ha) and Yield (10–22 t/ha) updating harvest tonnes. |
| **Officer Experience** | Gap & Import Timeline (Deadlines & Decisions) | 🟢 Completed | Critical May 14 import deadline with actions (Delay imports, Store produce, Shift to pulses). |
| **Officer Experience** | Adoption Tracker (Recommended vs Reported) | 🟢 Completed | Recommended vs reported bars dynamically updating when farmer reports are filed! |
| **Officer Experience** | Decision Record & Run History Log | 🟢 Completed | Decision logging with run IDs (`RUN-260404-xx`) and broadcast modal. |
| **Feedback Loop** | Farmer Report updates Officer Supply/Adoption | 🟢 Completed | `OfficerRepository` listens to `FarmerRepository`; reports increment reported area live! |
| **Alerts Inbox** | In-app alerts with "Acknowledge" & "Ask Officer" | 🟢 Completed | Filterable inbox with "Mark Read" and direct officer dialer. |

---

## 5. Architectural Issues in `mobile/`

1. **Role Routing Collision**:
   [`app_router.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/core/router/app_router.dart) only defines `/home`, pointing directly to `DashboardPage`. Neither `FarmerPage` nor `OfficerPage` are registered in the routing table.
2. **Missing State Management Integration**:
   `flutter_riverpod` is in `pubspec.yaml`, but the app root in [`main.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/main.dart) does not wrap the app with `ProviderScope`, meaning state cannot currently be provided or listened to.
3. **Empty Repositories**:
   [`auth_repository.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/features/auth/data/auth_repository.dart), [`farmer_repository.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/features/farmer/data/farmer_repository.dart), and [`officer_repository.dart`](file:///d:/programming/Govisense/GoviSense/mobile/lib/features/officer/data/officer_repository.dart) have zero methods or mock data implementations.
4. **No Offline / Sync Layer**:
   No local caching strategy is implemented in Flutter to support poor rural connectivity in field conditions.

---

## 6. Implementation Action Plan for `mobile/`

To bring the Flutter mobile application up to the standard established in the React frontend and proposal requirements, the following steps are required:

1. **Routing & State Architecture**:
   - Wrap `main.dart` with `ProviderScope`.
   - Update `app_router.dart` with dedicated role-based routes: `/farmer` and `/officer`.
   - Redirect to `/farmer` when user selects Farmer role, and `/officer` when selecting Officer role.
2. **Farmer Mobile Implementation (`features/farmer/`)**:
   - Implement Trilingual localization (English, Sinhala, Tamil) for mobile widgets.
   - Build `FarmerHomePage`: Decision countdown, weather alert card, top picks snapshot.
   - Build `FarmerCompareView`: Top 3 swipeable cards (Green Gram, Chilli, Big Onion) with SPI gauge and profit range.
   - Build `FarmerReportWizard`: 3-step planting declaration form with acreage selector.
   - Build `DigitalFarmerPass`: Verified QR pass for Sunil Perera (`ANU-01428`).
3. **Officer Mobile Implementation (`features/officer/`)**:
   - Implement `SupplyPressureChart` using `fl_chart` with monthly Low-Mid-High scenario bands.
   - Implement `WhatIfSliders` (interactive sliders for planted area in hectares and yield).
   - Implement `GapTimelineView` with decision deadlines and action buttons (Import now / later / delay).
   - Implement `AdoptionTrackerView` comparing recommended vs farmer-reported hectares.
4. **Shared Bidirectional Service Layer**:
   - Populate `FarmerRepository` and `OfficerRepository` with typed mock datasets matching official Department of Agriculture targets.
   - Enable the feedback loop: farmer planting reports dynamically update the officer supply curve and adoption stats in-app.

