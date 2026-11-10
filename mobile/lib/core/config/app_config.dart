import 'package:flutter/foundation.dart'
    show TargetPlatform, defaultTargetPlatform, kDebugMode, kIsWeb;
import 'package:shared_preferences/shared_preferences.dart';

/// Picks the backend the app talks to.
///
///   flutter run                                   -> deployed Railway backend
///   flutter run --dart-define=API_ENV=local        -> local backend on :8000
///   flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
///                                                  -> any explicit address
///                                                     (e.g. a real phone on LAN)
class AppConfig {
  const AppConfig._();

  static const appName = 'GoviSense';
  static const String deployedUrl =
      'https://govisense-production.up.railway.app';

  /// Local backend as seen from the Android emulator (host machine alias).
  static const String localEmulatorUrl = 'http://10.0.2.2:8000';

  /// Local backend as seen from web, desktop and the iOS simulator.
  static const String localHostUrl = 'http://127.0.0.1:8000';

  static const String _envName = String.fromEnvironment(
    'API_ENV',
    defaultValue: 'deployed',
  );
  static const String _explicitUrl = String.fromEnvironment('API_BASE_URL');

  /// True when the build was started against a local backend.
  static bool get isLocalEnv => _envName.toLowerCase() == 'local';

  /// The local backend address for the platform the app is running on.
  static String get localUrl =>
      (!kIsWeb && defaultTargetPlatform == TargetPlatform.android)
          ? localEmulatorUrl
          : localHostUrl;

  /// Build-time address: API_BASE_URL wins, then API_ENV, then deployed.
  static String get defaultUrl {
    if (_explicitUrl.trim().isNotEmpty) return _explicitUrl;
    return isLocalEnv ? localUrl : deployedUrl;
  }

  static const String _prefKeyBaseUrl = 'govisense_api_base_url';

  static String _activeBaseUrl = deployedUrl;

  static String get apiBaseUrl => _activeBaseUrl;
  static bool get canOverrideApiBaseUrl => kDebugMode;

  static String validateBaseUrl(String value, {bool allowHttp = kDebugMode}) {
    final uri = Uri.tryParse(value.trim());
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/') ||
        (uri.scheme != 'https' && !(allowHttp && uri.scheme == 'http'))) {
      throw const FormatException('Invalid API server address.');
    }
    return uri.replace(path: '').toString();
  }

  /// Load persisted custom base URL from SharedPreferences
  static Future<void> init() async {
    // A bad build-time production address must fail before any request runs.
    _activeBaseUrl = validateBaseUrl(defaultUrl);
    if (!canOverrideApiBaseUrl) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedUrl = prefs.getString(_prefKeyBaseUrl);
      if (savedUrl != null && savedUrl.trim().isNotEmpty) {
        _activeBaseUrl = validateBaseUrl(savedUrl);
      }
    } catch (_) {
      // Fallback to default
    }
  }

  /// Update active base URL and persist
  static Future<void> setBaseUrl(String url) async {
    if (!canOverrideApiBaseUrl) {
      throw StateError('API server overrides are disabled in this build.');
    }
    final cleaned = validateBaseUrl(url);
    _activeBaseUrl = cleaned;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_prefKeyBaseUrl, cleaned);
    } catch (_) {}
  }
}
