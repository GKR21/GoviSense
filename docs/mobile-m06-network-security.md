# M-06: Production configuration and network policy

The default API origin is `https://api.govisense.lk`, as proposed in the roadmap. `--dart-define=API_BASE_URL=https://your-api-host` overrides it at compile time. This configures an address; it does not deploy the backend, establish domain ownership, or verify that DNS/TLS and production services are live.

Release and profile builds require an HTTPS origin, reject embedded credentials, query strings, fragments and path prefixes, and ignore saved development URLs. Their server-editing card is hidden and runtime overrides are disabled. An invalid build-time origin stops startup before authentication/network calls. Debug builds retain validated HTTP/HTTPS server settings for emulator or LAN testing; a saved debug setting takes precedence over the compile-time default.

The main Android manifest declares INTERNET permission, denies cleartext traffic and references the restrictive main network-security resource. Only the debug resource permits cleartext, with an explicit debug manifest override. Profile inherits the restrictive main policy. See [Android network security configuration](https://developer.android.com/privacy-and-security/security-config).

Authentication and shared API clients also apply a Dart/Dio request guard: non-debug API requests require HTTPS and do not automatically follow redirects. A server redirect is treated as an error rather than risking a downgrade. This supplements native policy because Dart-owned sockets need application-level protection; see the [Flutter network-policy note](https://docs.flutter.dev/release/breaking-changes/network-policy-ios-android). No certificate-verification bypass was added. Native iOS ATS settings remain unchanged; the shared Dart guard applies to iOS API requests too.

For subsequent Android emulator testing, explicitly use `--dart-define=API_BASE_URL=http://10.0.2.2:8000` in a debug run. This task does not launch an emulator or build an APK.

Validation: Flutter analysis reports no issues and all 33 mobile tests pass. Tests cover origin validation, debug persistence, bad saved values, HTTP rejection under the non-debug transport policy, redirect suppression and Android source-policy settings. Android XML parsing passes. A separate configuration test run uses `--dart-define=API_BASE_URL=https://staging.example.test` to verify injection without contacting that reserved test host.

Remaining release verification: confirm the actual production domain, DNS, valid TLS and backend availability; check the merged Android release manifest and HTTP rejection on a device when APK builds are authorized. Unit tests simulate the strict policy; they do not replace release-mode/device verification. Release signing and packaged artifacts remain M-07/M-09.
