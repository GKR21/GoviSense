# M-05: English, Sinhala and Tamil

Implemented one app-wide language selection, persisted in shared preferences. Use the translation icon on login, farmer or officer screens; farmer profile and alert-inbox language controls update the same preference. Switching retains the current route and form state.

The existing keyed translations remain in `app_translations.dart`. Shared display strings and dynamic sentence templates are catalogued in `ui_translations.dart` and `ui_translations_extra.dart`. `LocalizedText`, `LocalizedSelectableText` and `context.tr` apply the selected language at the display boundary. Stored form choices, crop codes, IDs, receipt hashes, API payloads, personal names and user-entered questions retain their original values. Unknown server-provided free text is preserved rather than machine-translated.

Coverage includes authentication, farmer tabs and planting wizard, cultivation receipts/pass, crop guides, market prices, advisory inbox, officer tabs, policy labels and shared dialogs. Remaining literal-label coverage is checked by an automated source audit. Sinhala and Tamil entries include agronomic terms for seasons, water source, yield, profitability, irrigation and cultivation costs.

Bundled Inter, Noto Sans Sinhala and Noto Sans Tamil variable fonts are declared in pubspec with fallback families. Files and OFL licenses are from the official [Google Fonts repository](https://github.com/google/fonts). Font rendering does not require a runtime download. `python scripts/check_mobile_fonts.py` checks the bundled cmap tables against every Sinhala/Tamil character used in the source.

Responsive fixes let long translated headings, market locations, profile controls, cultivation-guide labels and comparison values wrap instead of overflowing. App bars use compact translation controls. Role-preview shortcuts were removed from the app bars; existing authenticated role routing remains authoritative.

Validation covers catalog parity, placeholder preservation, literal-label coverage, persistent selection, live switching without losing credentials, and phone-width layouts with the actual bundled fonts. Screen tests scroll all farmer/officer tabs and all three wizard steps, plus crop details, market prices and alerts, in each language. Tests use local image fixtures and mocked API responses; no APK or live backend is required.

Final results: Flutter analysis reports no issues; all 27 mobile tests pass. The bundled fonts cover all 55 Sinhala and 42 Tamil characters currently used in the source. Git whitespace checks pass. No APK was built.

Release review still needs native-speaker proofreading of Sinhala/Tamil wording and a real-device visual/accessibility pass. Automated font/overflow checks do not certify linguistic accuracy or every device/text-scale combination. Newly added server messages require corresponding localized fields or catalog entries. Offline report caching/sync remains deferred as requested.
