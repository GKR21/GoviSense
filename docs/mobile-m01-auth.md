# M-01: JWT authentication

Implemented credential login with `POST /api/auth/login` (JSON username/password), server role validation with `GET /api/auth/me`, encrypted access token storage, startup restoration, expiry logout, authenticated API headers, 401 logout, and role route guards. Admin accounts use the officer workspace. Passwords are never persisted. Both workspace logout actions clear the saved token.

The mounted JWT auth router precedes the legacy auth router; this implementation uses its username payload and flat user profile. It also accepts the legacy nested `/me` profile.

Tests cover credential validation, server-validated role selection, storage/restoration/logout, and unsupported role rejection.

Validation: Flutter was updated from 3.47.0 (Dart 3.13.0) to 3.47.9 (Dart 3.13.7), satisfying the existing ^3.13.1 constraint. Dependency resolution succeeds. Flutter analysis reports no issues and all three tests pass. Removed the obsolete demo-login assertions from the widget test and fixed five authentication style findings.

On this Windows installation, native-asset hooks fail when invoked through the SDK path containing spaces. An ignored local junction, `.local-flutter/`, points to the installed SDK and provides a path without spaces. From the repository root, reproduce the passing checks with:

```powershell
Set-Location mobile
& '..\.local-flutter\bin\flutter.bat' pub get
& '..\.local-flutter\bin\flutter.bat' analyze --no-pub
& '..\.local-flutter\bin\flutter.bat' test --no-pub
```

The junction is local machine configuration and is not committed. On another machine, create it pointing to that machine's Flutter SDK, or install Flutter at a path without spaces. Optional Android engine precaching was interrupted after the SDK update; Flutter will fetch any remaining target artifacts when needed. A signed Android build was not tested.

Device validation against a running backend remains pending, including app restart and expired-token behavior. Passing mocked tests does not establish live authentication success.
