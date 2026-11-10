# M-01: JWT authentication

Implemented credential login with `POST /api/auth/login` (JSON username/password), server role validation with `GET /api/auth/me`, encrypted access token storage, startup restoration, expiry logout, authenticated API headers, 401 logout, and role route guards. Admin accounts use the officer workspace. Passwords are never persisted. Both workspace logout actions clear the saved token.

The mounted JWT auth router precedes the legacy auth router; this implementation uses its username payload and flat user profile. It also accepts the legacy nested `/me` profile.

Tests cover credential validation, server-validated role selection, storage/restoration/logout, and unsupported role rejection.

Validation: Dart formatting and git diff whitespace checks completed. `flutter pub get`, `flutter analyze`, and `flutter test` cannot run because the installed Dart SDK is 3.13.0 while pubspec requires ^3.13.1. Install a compatible Flutter SDK, then rerun those commands from mobile/. Device validation against a running backend remains pending, including app restart and expired-token behavior. Keep the current SDK constraint until a compatible toolchain is available.
